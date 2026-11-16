"""Bộ dựng sơ đồ nguyên lý KiCad 10 bằng mã.

Dùng để tạo bản sơ đồ đầu tiên của mỗi bo từ một kịch bản `ve_so_do.py`.
Toạ độ tính theo đơn vị lưới u = 1,27 mm, gốc ở góc trên trái trang, trục y hướng xuống.
Sau khi đã sửa sơ đồ bằng tay trong KiCad thì không chạy lại kịch bản nữa: nó ghi đè cả tệp.
"""
import glob
import math
import os
import re
import uuid

U = 1.27
KICAD = "C:/Program Files/KiCad/10.0"
THU_VIEN_GOC = KICAD + "/share/kicad/symbols"
IRIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "IRIS.kicad_sym")

FP = {
    "R": "Resistor_SMD:R_0603_1608Metric",
    "C": "Capacitor_SMD:C_0603_1608Metric",
    "C0805": "Capacitor_SMD:C_0805_2012Metric",
    "LED": "LED_SMD:LED_0603_1608Metric",
    "FB": "Inductor_SMD:L_0805_2012Metric",
    "JP2": "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",
    "TP": "TestPoint:TestPoint_Pad_D1.5mm",
}


def _khoi(s, i):
    """Trả về chỉ số kết thúc (bao gồm) của khối ngoặc bắt đầu tại i."""
    d = 0
    trong_chuoi = False
    j = i
    while j < len(s):
        c = s[j]
        if trong_chuoi:
            if c == "\\":
                j += 1
            elif c == '"':
                trong_chuoi = False
        elif c == '"':
            trong_chuoi = True
        elif c == "(":
            d += 1
        elif c == ")":
            d -= 1
            if d == 0:
                return j
        j += 1
    raise ValueError("khối ngoặc không đóng")


_tep = {}


def _doc(duong):
    if duong not in _tep:
        _tep[duong] = open(duong, encoding="utf-8").read()
    return _tep[duong]


def _tim_ky_hieu(lib, ten):
    if lib == "IRIS":
        ds = [IRIS]
    else:
        ds = [f"{THU_VIEN_GOC}/{lib}.kicad_sym"] + glob.glob(f"{THU_VIEN_GOC}/{lib}/{ten}.kicad_sym")
    for d in ds:
        if not os.path.exists(d):
            continue
        s = _doc(d)
        m = re.search(r'\(symbol "%s"\s' % re.escape(ten), s)
        if m:
            return s[m.start():_khoi(s, m.start()) + 1]
    raise KeyError(f"không tìm thấy ký hiệu {lib}:{ten}")


def _thuoc_tinh(khoi):
    """Danh sách (tên, đầu, cuối) của các khối property cấp một."""
    kq = []
    for m in re.finditer(r'\n\t{2,3}\(property "([^"]+)"', khoi):
        i = m.start() + m.group(0).index("(")
        kq.append((m.group(1), i, _khoi(khoi, i) + 1))
    return kq


def ky_hieu_thu_vien(lib, ten):
    """Khối ký hiệu để nhúng vào lib_symbols, đã gộp ký hiệu cha nếu có `extends`."""
    k = _tim_ky_hieu(lib, ten)
    m = re.search(r'\(extends "([^"]+)"\)', k)
    if m:
        cha_ten = m.group(1)
        cha = _tim_ky_hieu(lib, cha_ten)
        con = dict((t, k[a:b]) for t, a, b in _thuoc_tinh(k))
        for t, a, b in reversed(_thuoc_tinh(cha)):
            if t in con:
                cha = cha[:a] + con.pop(t) + cha[b:]
        tt = _thuoc_tinh(cha)
        cha = cha[:tt[-1][2]] + "".join("\n\t\t" + v for v in con.values()) + cha[tt[-1][2]:]
        cha = cha.replace(f'(symbol "{cha_ten}"', f'(symbol "{ten}"', 1)
        cha = cha.replace(f'(symbol "{cha_ten}_', f'(symbol "{ten}_')
        k = cha
    return k.replace(f'(symbol "{ten}"', f'(symbol "{lib}:{ten}"', 1)


def _chan(khoi):
    kq = []
    for m in re.finditer(r"\(pin \w+ \w+", khoi):
        b = khoi[m.start():_khoi(khoi, m.start()) + 1]
        at = re.search(r"\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)", b)
        ten = re.search(r'\(name "([^"]*)"', b).group(1)
        so = re.search(r'\(number "([^"]*)"', b).group(1)
        kq.append((so, ten, float(at.group(1)), float(at.group(2)), float(at.group(3) or 0)))
    return kq


class LinhKien:
    def __init__(self, sd, lib_id, ref, gia_tri, x, y, goc, fp, truong):
        self.sd, self.lib_id, self.ref, self.gia_tri = sd, lib_id, ref, gia_tri
        self.x, self.y, self.goc, self.fp, self.truong = x, y, goc, fp, truong
        self.chan = _chan(sd.thu_vien[lib_id])
        self.vt_ref = self.vt_gt = None

    def _doi(self, px, py):
        a = math.radians(self.goc)
        xr = px * math.cos(a) - py * math.sin(a)
        yr = px * math.sin(a) + py * math.cos(a)
        return (round(self.x + xr / U, 3), round(self.y - yr / U, 3))

    def p(self, ten):
        """Toạ độ đầu chân (đơn vị u) theo số chân hoặc tên chân."""
        for so, t, px, py, _ in self.chan:
            if so == str(ten) or t == ten:
                return self._doi(px, py)
        raise KeyError(f"{self.ref}: không có chân {ten}")

    def huong(self, so):
        """Vectơ đơn vị hướng ra ngoài thân linh kiện tại chân (chỉ đúng khi góc = 0)."""
        for s, _, _, _, a in self.chan:
            if s == str(so):
                r = math.radians(a)
                return (-round(math.cos(r)), round(math.sin(r)))
        raise KeyError(so)

    def khung(self):
        xs = [self._doi(c[2], c[3])[0] for c in self.chan] or [self.x]
        ys = [self._doi(c[2], c[3])[1] for c in self.chan] or [self.y]
        return min(xs), min(ys), max(xs), max(ys)


class SoDo:
    def __init__(self, ten, tieu_de, kho="A3", ban="0.1", ngay=""):
        self.ten, self.tieu_de, self.kho, self.ban, self.ngay = ten, tieu_de, kho, ban, ngay
        self.thu_vien = {}
        self.lk, self.day, self.muc = [], [], []
        self._dem = 0
        self._pwr = 0
        self._flg = 0
        self.goc_uuid = self._uuid()

    def _uuid(self):
        self._dem += 1
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"iris-stem/{self.ten}/{self._dem}"))

    # ---------- linh kiện ----------
    def dat(self, lib_id, ref, gia_tri, x, y, goc=0, fp="", vt_ref=None, vt_gt=None, **truong):
        if lib_id not in self.thu_vien:
            lib, ten = lib_id.split(":")
            self.thu_vien[lib_id] = ky_hieu_thu_vien(lib, ten)
        if not fp:
            m = re.search(r'\(property "Footprint" "([^"]*)"', self.thu_vien[lib_id])
            fp = m.group(1) if m else ""
        k = LinhKien(self, lib_id, ref, gia_tri, x, y, goc, fp, truong)
        k.vt_ref, k.vt_gt = vt_ref, vt_gt
        self.lk.append(k)
        return k

    def doc(self, lib_id, ref, gia_tri, x, y, fp="", **truong):
        """Linh kiện 2 chân đặt dọc tại tâm (x, y). Trả về (linh kiện, chân trên, chân dưới)."""
        lech = lambda t: 1.6 + 0.47 * len(t)  # chữ căn giữa, đẩy sang phải theo độ dài
        k = self.dat(lib_id, ref, gia_tri, x, y, 0, fp, vt_ref=(lech(ref), -1.1), vt_gt=(lech(gia_tri), 1.1), **truong)
        return k, k.p("1"), k.p("2")

    def ngang(self, lib_id, ref, gia_tri, x, y, fp="", **truong):
        """Linh kiện 2 chân đặt ngang tại tâm (x, y). Trả về (linh kiện, chân trái, chân phải)."""
        k = self.dat(lib_id, ref, gia_tri, x, y, 90, fp, vt_ref=(0, -2.2), vt_gt=(0, 2.2), **truong)
        return k, k.p("1"), k.p("2")

    def R(self, ref, gt, x, y, ngang=False):
        return (self.ngang if ngang else self.doc)("Device:R_Small", ref, gt, x, y, FP["R"])

    def C(self, ref, gt, x, y, fp=None):
        return self.doc("Device:C_Small", ref, gt, x, y, fp or FP["C"])

    def nguon(self, loai, pt, huong="mac_dinh"):
        """Ký hiệu nguồn tại pt. huong: 'len', 'xuong', 'trai', 'phai' là hướng ký hiệu chĩa ra."""
        dat = loai == "GND"
        if huong == "mac_dinh":
            huong = "xuong" if dat else "len"
        goc = {"xuong": 0, "phai": 90, "len": 180, "trai": 270}[huong] if dat else \
              {"len": 0, "trai": 90, "xuong": 180, "phai": 270}[huong]
        self._pwr += 1
        d = {"len": (0, -3.0), "xuong": (0, 3.0), "trai": (-5.2, 0), "phai": (5.2, 0)}[huong]
        k = self.dat(f"power:{loai}", f"#PWR{self._pwr:03d}", loai, pt[0], pt[1], goc, vt_gt=d)
        k.an_gt = dat
        return k

    def co_nguon(self, pt):
        self._flg += 1
        return self.dat("power:PWR_FLAG", f"#FLG{self._flg:02d}", "PWR_FLAG", pt[0], pt[1], 0, vt_gt=(0, -3.6))

    # ---------- dây, nhãn ----------
    def w(self, *pts):
        """Dây đi qua các điểm; mỗi đoạn phải ngang hoặc dọc."""
        for a, b in zip(pts, pts[1:]):
            if a == b:
                continue
            assert abs(a[0] - b[0]) < 1e-6 or abs(a[1] - b[1]) < 1e-6, f"dây chéo {a} {b}"
            self.day.append((tuple(a), tuple(b)))

    def L(self, a, b):
        """Dây chữ L: đi ngang trước rồi đi dọc."""
        self.w(a, (b[0], a[1]), b)

    def nhan(self, ten, pt, huong="phai"):
        goc = {"phai": 0, "len": 90, "trai": 180, "xuong": 270}[huong]
        self.muc.append(("nhan", ten, pt, goc))

    def ten_day(self, ten, pt, huong="phai"):
        """Nhãn cục bộ (chữ nằm trên dây), neo tại pt, chữ chạy về phía `huong`."""
        self.muc.append(("ten", ten, pt, 0 if huong == "phai" else 180))

    def nc(self, pt):
        self.muc.append(("nc", pt))

    def chu(self, noi_dung, x, y, co=1.27, dam=False):
        self.muc.append(("chu", noi_dung, (x, y), co, dam))

    def khoi(self, x0, y0, x1, y1, tieu_de, ghi_chu=()):
        self.muc.append(("khung", (x0, y0), (x1, y1)))
        self.chu(tieu_de, x0 + 1.5, y0 + 2.5, 2.0, True)
        for i, g in enumerate(ghi_chu):
            self.chu(g, x0 + 1.5, y1 - 2 - 2 * (len(ghi_chu) - 1 - i))

    def chia(self, k, bang, dai=4, cuc_bo=False):
        """Kéo dây ngắn ra từ từng chân của linh kiện k (góc 0) rồi gắn nhãn / nguồn / NC.

        bang: {số chân: 'TEN_LUOI' | '+3V3' | 'GND' | None (không nối)}
        """
        for so, dich in bang.items():
            a = k.p(so)
            if dich is None:
                self.nc(a)
                continue
            dx, dy = k.huong(so)
            b = (a[0] + dx * dai, a[1] + dy * dai)
            self.w(a, b)
            h = {(1, 0): "phai", (-1, 0): "trai", (0, -1): "len", (0, 1): "xuong"}[(dx, dy)]
            if dich == "GND" or dich.startswith("+"):
                self.nguon(dich, b, h)
            elif cuc_bo and h in ("trai", "phai"):
                self.ten_day(dich, b, h)
            else:
                self.nhan(dich, b, h)

    # ---------- ghi tệp ----------
    def _noi(self):
        """Cắt dây tại các điểm chạm và trả về (đoạn dây, điểm nối)."""
        diem = set()
        for a, b in self.day:
            diem.add(a)
            diem.add(b)
        for k in self.lk:
            for c in k.chan:
                diem.add(k._doi(c[2], c[3]))
        for m in self.muc:
            if m[0] in ("nhan", "ten"):
                diem.add(tuple(m[2]))
        doan = []
        for a, b in self.day:
            tren = [p for p in diem if p != a and p != b and _nam_tren(p, a, b)]
            tren.sort(key=lambda p: (p[0] - a[0]) ** 2 + (p[1] - a[1]) ** 2)
            cu = a
            for p in tren + [b]:
                doan.append((cu, p))
                cu = p
        doan = list(dict.fromkeys((min(a, b), max(a, b)) for a, b in doan))
        bac = {}
        for a, b in doan:
            bac[a] = bac.get(a, 0) + 1
            bac[b] = bac.get(b, 0) + 1
        for k in self.lk:
            for p in set(k._doi(c[2], c[3]) for c in k.chan):
                if p in bac:
                    bac[p] += 1
        return doan, [p for p, n in bac.items() if n >= 3]

    def ghi(self, duong):
        o = []
        mm = lambda v: f"{v * U:.4f}".rstrip("0").rstrip(".")
        font = lambda co=1.27, dam=False: f"(font (size {co} {co}){' (bold yes)' if dam else ''})"
        o.append(f'(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0")\n'
                 f'(uuid "{self.goc_uuid}") (paper "{self.kho}")\n'
                 f'(title_block (title "{self.tieu_de}") (date "{self.ngay}") (rev "{self.ban}") (company "IRIS-Stem"))\n'
                 "(lib_symbols\n" + "\n".join(self.thu_vien.values()) + "\n)")
        doan, noi = self._noi()
        for p in noi:
            o.append(f'(junction (at {mm(p[0])} {mm(p[1])}) (diameter 0) (color 0 0 0 0) (uuid "{self._uuid()}"))')
        for a, b in doan:
            o.append(f'(wire (pts (xy {mm(a[0])} {mm(a[1])}) (xy {mm(b[0])} {mm(b[1])})) '
                     f'(stroke (width 0) (type default)) (uuid "{self._uuid()}"))')
        for m in self.muc:
            if m[0] == "nhan":
                _, ten, p, goc = m
                can = "right" if goc in (180, 270) else "left"
                o.append(f'(global_label "{ten}" (shape passive) (at {mm(p[0])} {mm(p[1])} {goc}) (fields_autoplaced yes) '
                         f'(effects {font()} (justify {can})) (uuid "{self._uuid()}") '
                         f'(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {mm(p[0])} {mm(p[1])} 0) (hide yes) '
                         f'(effects {font()} (justify {can}))))')
            elif m[0] == "ten":
                _, ten, p, goc = m
                can = "right" if goc == 180 else "left"
                o.append(f'(label "{ten}" (at {mm(p[0])} {mm(p[1])} {goc}) '
                         f'(effects {font()} (justify {can} bottom)) (uuid "{self._uuid()}"))')
            elif m[0] == "nc":
                o.append(f'(no_connect (at {mm(m[1][0])} {mm(m[1][1])}) (uuid "{self._uuid()}"))')
            elif m[0] == "chu":
                _, nd, p, co, dam = m
                nd = nd.replace("\\", "\\\\").replace('"', '\\"')
                o.append(f'(text "{nd}" (exclude_from_sim no) (at {mm(p[0])} {mm(p[1])} 0) '
                         f'(effects {font(co, dam)} (justify left)) (uuid "{self._uuid()}"))')
            elif m[0] == "khung":
                o.append(f'(rectangle (start {mm(m[1][0])} {mm(m[1][1])}) (end {mm(m[2][0])} {mm(m[2][1])}) '
                         f'(stroke (width 0.3) (type dash) (color 0 0 132 1)) (fill (type none)) (uuid "{self._uuid()}"))')
        for k in self.lk:
            o.append(self._ghi_lk(k, mm, font))
        o.append('(sheet_instances (path "/" (page "1")))\n(embedded_fonts no)\n)')
        with open(duong, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(o) + "\n")

    def _ghi_lk(self, k, mm, font):
        nguon = k.lib_id.startswith("power:")
        x0, y0, x1, y1 = k.khung()
        gf = 90 if k.goc in (90, 270) else 0
        vr = k.vt_ref or ((x0 + x1) / 2 - k.x, y0 - k.y - 2.5)
        vg = k.vt_gt or ((x0 + x1) / 2 - k.x, y1 - k.y + 2.5)
        an_ref = nguon
        an_gt = getattr(k, "an_gt", False)

        def tt(ten, gt, vt, an):
            return (f'(property "{ten}" "{gt}" (at {mm(k.x + vt[0])} {mm(k.y + vt[1])} {gf}) '
                    f'{"(hide yes) " if an else ""}(effects {font()}))')

        s = [f'(symbol (lib_id "{k.lib_id}") (at {mm(k.x)} {mm(k.y)} {k.goc}) (unit 1) (body_style 1) '
             f'(exclude_from_sim no) (in_bom {"no" if nguon or k.ref.startswith("KH") else "yes"}) '
             f'(on_board {"no" if nguon else "yes"}) (in_pos_files yes) (dnp no) (uuid "{self._uuid()}")',
             tt("Reference", k.ref, vr, an_ref), tt("Value", k.gia_tri, vg, an_gt),
             tt("Footprint", k.fp, (0, 0), True), tt("Datasheet", "", (0, 0), True), tt("Description", "", (0, 0), True)]
        for ten, gt in k.truong.items():
            s.append(tt(ten, gt, (0, 0), True))
        for so in dict.fromkeys(c[0] for c in k.chan):
            s.append(f'(pin "{so}" (uuid "{self._uuid()}"))')
        s.append(f'(instances (project "{self.ten}" (path "/{self.goc_uuid}" (reference "{k.ref}") (unit 1)))))')
        return "\n".join(s)


def _nam_tren(p, a, b):
    if abs(a[0] - b[0]) < 1e-6:
        return abs(p[0] - a[0]) < 1e-6 and min(a[1], b[1]) < p[1] < max(a[1], b[1])
    return abs(p[1] - a[1]) < 1e-6 and min(a[0], b[0]) < p[0] < max(a[0], b[0])
