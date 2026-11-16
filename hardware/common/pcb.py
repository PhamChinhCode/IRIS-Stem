"""Bộ dựng PCB 2 lớp bằng mã cho các bo nhỏ: nạp netlist, đặt linh kiện, đi dây, đổ đồng GND.

Chạy bằng Python của KiCad 10 (có module pcbnew):
    "C:/Program Files/KiCad/10.0/bin/python.exe" ve_pcb.py
Toạ độ đầu vào là toạ độ cơ khí: gốc ở tâm bo, x sang phải, y lên trên, đơn vị mm
(trùng mechanical/src/lib/mach.py). Bộ đi dây chạy trên lưới 0,25 mm, chỉ đi ngang và dọc.
"""
import heapq
import math
import os
import re
from array import array

import pcbnew

KICAD = "C:/Program Files/KiCad/10.0"
FP_GOC = KICAD + "/share/kicad/footprints"
IRIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "IRIS.pretty")
PX, PY = 100.0, 100.0          # góc trên trái của bo (kích thước danh nghĩa) trên trang
G = 0.25                       # bước lưới đi dây
W_DAY, KHE = 0.4, 0.2          # bề rộng dây, khe hở
VIA_D, VIA_K = 0.6, 0.3
THU = 0.25                     # mép bo thu vào so với kích thước danh nghĩa
R_LO = 1.6                     # bán kính lỗ gá
R_CAM = 3.0                    # vùng cấm linh kiện quanh lỗ gá (đầu vít M3, trụ vỏ)
NGUON = ("GND", "+5V", "+3V3")
mm = pcbnew.FromMM


def doc_netlist(tep):
    s = open(tep, encoding="utf-8").read()
    lk = {}
    for k in re.split(r"\(comp\s+\(ref ", s[s.find("(components"):s.find("(libparts")])[1:]:
        ref = re.match(r'"([^"]+)"', k).group(1)
        fp = re.search(r'\(footprint "([^"]*)"', k)
        ts = re.findall(r'\(tstamps "([^"]+)"', k)
        lk[ref] = {"gt": re.search(r'\(value "([^"]*)"', k).group(1), "fp": fp.group(1) if fp else "", "ts": ts[-1],
                   "truong": re.findall(r'\(field\s+\(name "([^"]+)"\)\s+"([^"]*)"\)', k),
                   "ngoai_bom": bool(re.search(r'\(property\s+\(name "exclude_from_bom"\)', k))}
    luoi = {}
    for p in re.split(r"\(net\s+\(code", s[s.find("(nets"):])[1:]:
        ten = re.search(r'\(name "([^"]*)"', p).group(1)
        luoi[ten] = re.findall(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', p)
    return lk, luoi


def _nap(fp):
    lib, ten = fp.split(":")
    m = pcbnew.FootprintLoad(IRIS if lib == "IRIS" else f"{FP_GOC}/{lib}.pretty", ten)
    assert m is not None, f"không nạp được {fp}"
    m.SetFPID(pcbnew.LIB_ID(lib, ten))
    return m


_hinh = {}
_tam = pcbnew.BOARD()


def hinh(fp, goc, duoi=False):
    """(khung courtyard, [(số pad, x, y)]) quanh gốc chân linh kiện, mm, trục y hướng xuống."""
    k = (fp, goc, duoi)
    if k not in _hinh:
        m = _nap(fp)
        m.SetPosition(pcbnew.VECTOR2I(0, 0))
        if duoi:
            _tam.Add(m)       # lật chỉ chạy được khi chân linh kiện đã thuộc một bo
            m.Flip(m.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        m.SetOrientationDegrees(goc)
        bb = m.GetCourtyard(pcbnew.B_CrtYd if duoi else pcbnew.F_CrtYd).BBox()
        pads = [(p.GetNumber(), pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)) for p in m.Pads()]
        if bb.GetWidth() <= 0:
            xs, ys = [p[1] for p in pads], [p[2] for p in pads]
            crt = (min(xs) - 1, min(ys) - 1, max(xs) + 1, max(ys) + 1)
        else:
            crt = tuple(pcbnew.ToMM(v) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom()))
        _hinh[k] = (crt, pads)
    return _hinh[k]


class Bo:
    def __init__(self, ma, tep_net, w, h, lo, khung="KH1"):
        self.ma, self.w, self.h = ma, w, h
        self.lk, self.luoi = doc_netlist(tep_net)
        self.luoi_cua = {}
        for ten, ds in self.luoi.items():
            for ref, pin in ds:
                self.luoi_cua[(ref, pin)] = ten
        self.lo = [self.b_(x, y) for x, y in lo]
        self.da_dat = {}          # ref: (x gốc, y gốc, góc, mặt dưới)
        self.khung_lk = []        # (x0, y0, x1, y1, mặt dưới)
        self.cam = []             # vùng cấm đặt linh kiện tự động (x0, y0, x1, y1)
        self.dong = []            # đồng cố định: ("day", lưới, [(x, y), ...], rộng) | ("vung", lưới, (x0, y0, x1, y1))
        self.khung = khung
        self.loi = []

    def b_(self, x, y):
        """Toạ độ cơ khí → toạ độ bo (gốc góc trên trái, y xuống)."""
        return (x + self.w / 2, self.h / 2 - y)

    # ---------------------------------------------------------------- đặt linh kiện
    def dat(self, ref, x, y, goc=0, duoi=False):
        """Đặt linh kiện sao cho tâm courtyard nằm tại (x, y) cơ khí."""
        crt, _ = hinh(self.lk[ref]["fp"], goc, duoi)
        bx, by = self.b_(x, y)
        ox, oy = bx - (crt[0] + crt[2]) / 2, by - (crt[1] + crt[3]) / 2
        self._ghi(ref, ox, oy, goc, duoi)

    def _ghi(self, ref, ox, oy, goc, duoi):
        crt, _ = hinh(self.lk[ref]["fp"], goc, duoi)
        self.da_dat[ref] = (ox, oy, goc, duoi)
        self.khung_lk.append((crt[0] + ox, crt[1] + oy, crt[2] + ox, crt[3] + oy, duoi))

    def _pad_da_dat(self):
        kq = {}
        for ref, (ox, oy, goc, duoi) in self.da_dat.items():
            for so, x, y in hinh(self.lk[ref]["fp"], goc, duoi)[1]:
                t = self.luoi_cua.get((ref, so))
                if t:
                    kq.setdefault(t, []).append((x + ox, y + oy))
        for d in self.dong:
            pts = d[2] if d[0] == "day" else [((d[2][0] + d[2][2]) / 2, (d[2][1] + d[2][3]) / 2)]
            kq.setdefault(d[1], []).extend(pts)
        return kq

    def _hop_le(self, r, vung, k=0.7):
        x0, y0, x1, y1 = r
        if x0 < vung[0] or y0 < vung[1] or x1 > vung[2] or y1 > vung[3]:
            return False
        for a in self.khung_lk:
            if x0 < a[2] + k and a[0] - k < x1 and y0 < a[3] + k and a[1] - k < y1:
                return False
        for a in self.cam:
            if x0 < a[2] and a[0] < x1 and y0 < a[3] and a[1] < y1:
                return False
        for cx, cy in self.lo:
            dx, dy = max(x0 - cx, 0, cx - x1), max(y0 - cy, 0, cy - y1)
            if dx * dx + dy * dy < R_CAM * R_CAM:
                return False
        return True

    def tu_dat(self, vung=None, bo_qua=()):
        """Đặt các linh kiện còn lại: gần pad cùng lưới đã đặt nhất, không chồng courtyard."""
        if vung:
            a, b = self.b_(vung[0], vung[3]), self.b_(vung[2], vung[1])
            vung = (a[0], a[1], b[0], b[1])
        else:
            vung = (THU + 0.7, THU + 0.7, self.w - THU - 0.7, self.h - THU - 0.7)
        con = [r for r in self.lk if r not in self.da_dat and r != self.khung and r not in bo_qua]
        while con:
            pads = self._pad_da_dat()

            def diem(r):
                n = set(self.luoi_cua.get((r, so)) for so, _, _ in hinh(self.lk[r]["fp"], 0)[1])
                c = hinh(self.lk[r]["fp"], 0)[0]
                return (sum(1 for t in n if t and t not in NGUON and t in pads), (c[2] - c[0]) * (c[3] - c[1]))
            con.sort(key=diem, reverse=True)
            ref = con.pop(0)
            fp = self.lk[ref]["fp"]
            tot = None
            for khe, goc in [(k, g) for k in (0.7, 0.4, 0.15) for g in (0, 90, 180, 270)]:
                if tot is not None and khe < 0.7:
                    break       # chỉ thu hẹp khe khi không còn chỗ
                crt, pd = hinh(fp, goc)
                if goc >= 180 and len(pd) == 2 and abs(pd[0][1] + pd[1][1]) < 1e-6 and abs(pd[0][1] - pd[1][1]) < 1e-6:
                    pass      # linh kiện 2 chân vẫn thử cả 4 góc: đổi đầu có thể rút ngắn dây
                y = vung[1] - crt[1]
                while y + crt[3] <= vung[3]:
                    x = vung[0] - crt[0]
                    while x + crt[2] <= vung[2]:
                        if self._hop_le((crt[0] + x, crt[1] + y, crt[2] + x, crt[3] + y), vung, khe):
                            c = 0.0
                            noi = False
                            for so, px, py in pd:
                                t = self.luoi_cua.get((ref, so))
                                if t in pads:
                                    d = min(abs(px + x - a) + abs(py + y - b) for a, b in pads[t])
                                    c += d * (0.15 if t == "GND" else 0.4 if t in NGUON else 1.0)
                                    noi = noi or t not in NGUON
                            if not noi:
                                c += 0.1 * (abs(x - self.w / 2) + abs(y - self.h / 2))
                            if tot is None or c < tot[0]:
                                tot = (c, x, y, goc)
                        x += 0.5
                    y += 0.5
            if tot is None:
                self.loi.append(f"không còn chỗ đặt {ref}")
                continue
            self._ghi(ref, tot[1], tot[2], tot[3], False)

    def day(self, luoi, pts, rong=0.6):
        """Dây đồng cố định trên lớp trên (toạ độ cơ khí), ví dụ răng lược cảm biến mưa."""
        self.dong.append(("day", luoi, [self.b_(x, y) for x, y in pts], rong))

    def vung_dong(self, luoi, x0, y0, x1, y1, cam=True):
        """Mảng đồng đặc trên lớp trên, ví dụ bản cực cảm biến độ ẩm đất."""
        a, b = self.b_(x0, y1), self.b_(x1, y0)
        self.dong.append(("vung", luoi, (a[0], a[1], b[0], b[1])))
        if cam:
            self.cam.append((a[0] - 0.5, a[1] - 0.5, b[0] + 0.5, b[1] + 0.5))

    def cam_dat(self, x0, y0, x1, y1):
        a, b = self.b_(x0, y1), self.b_(x1, y0)
        self.cam.append((a[0], a[1], b[0], b[1]))

    # ---------------------------------------------------------------- dựng bo
    def dung(self, tep, chu=None):
        b = self.b = pcbnew.BOARD()
        self.ma_luoi = {}
        for ten in self.luoi:
            n = pcbnew.NETINFO_ITEM(b, ten)
            b.Add(n)
            self.ma_luoi[ten] = n
        ds = dict(self.da_dat)
        ds[self.khung] = (0.0, self.h, 0, False)
        for ref, (ox, oy, goc, duoi) in ds.items():
            k = self.lk[ref]
            m = _nap(k["fp"])
            m.SetReference(ref)
            m.SetValue(k["gt"])
            m.SetPath(pcbnew.KIID_PATH("/" + k["ts"]))
            for ten, gt in k["truong"]:
                if ten not in ("Footprint", "Datasheet", "Description"):
                    m.SetField(ten, gt)
                    m.GetField(ten).SetVisible(False)
            m.SetExcludedFromBOM(k["ngoai_bom"])
            m.SetPosition(pcbnew.VECTOR2I(mm(PX + ox), mm(PY + oy)))
            b.Add(m)
            if duoi:
                m.Flip(m.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
            m.SetOrientationDegrees(goc)
            for p in m.Pads():
                t = self.luoi_cua.get((ref, p.GetNumber()))
                if t:
                    p.SetNet(self.ma_luoi[t])
            if ref[0] not in "JK" and not ref.startswith("RV"):
                m.Reference().SetVisible(False)      # bo nhỏ không đủ chỗ in tên linh kiện
            for g in list(m.GraphicalItems()):
                if g.GetClass() == "PCB_TEXT" and g.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
                    m.Remove(g)
        for d in self.dong:
            if d[0] == "day":
                for p, q in zip(d[2], d[2][1:]):
                    t = pcbnew.PCB_TRACK(b)
                    t.SetStart(pcbnew.VECTOR2I(mm(PX + p[0]), mm(PY + p[1])))
                    t.SetEnd(pcbnew.VECTOR2I(mm(PX + q[0]), mm(PY + q[1])))
                    t.SetWidth(mm(d[3]))
                    t.SetLayer(pcbnew.F_Cu)
                    t.SetNet(self.ma_luoi[d[1]])
                    try:
                        t.SetHasSolderMask(True)      # để trần đồng
                    except AttributeError:
                        pass
                    b.Add(t)
            else:
                self._vung(d[1], d[2], pcbnew.F_Cu)
        if chu:
            t = pcbnew.PCB_TEXT(b)
            t.SetText(chu[0])
            x, y = self.b_(chu[1], chu[2])
            t.SetPosition(pcbnew.VECTOR2I(mm(PX + x), mm(PY + y)))
            t.SetLayer(pcbnew.F_SilkS)
            t.SetTextSize(pcbnew.VECTOR2I(mm(1.0), mm(1.0)))
            t.SetTextThickness(mm(0.15))
            b.Add(t)
        self._di_day()
        if "GND" in self.ma_luoi:
            self._vung("GND", getattr(self, "gnd", (THU, THU, self.w - THU, self.h - THU)), pcbnew.B_Cu)
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        b.BuildConnectivity()
        ho = b.GetConnectivity().GetUnconnectedCount(False)
        pcbnew.SaveBoard(tep, b)
        return ho

    def _vung(self, luoi, r, lop):
        z = pcbnew.ZONE(self.b)
        z.SetLayer(lop)
        z.SetNet(self.ma_luoi[luoi])
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        o = z.Outline()
        o.NewOutline()
        for x, y in ((r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])):
            o.Append(mm(PX + x), mm(PY + y))
        self.b.Add(z)

    # ---------------------------------------------------------------- đi dây
    def _di_day(self):
        nx, ny = int(round(self.w / G)) + 1, int(round(self.h / G)) + 1
        self.nx, self.ny = nx, ny
        blk = self.blk = [array("h", [0]) * (nx * ny) for _ in range(2)]
        ma = {t: i + 1 for i, t in enumerate(self.luoi)}

        def to_o(x0, y0, x1, y1, lop, n):
            """Đánh dấu các ô có tâm trong hình chữ nhật (mm, toạ độ bo) là của lưới n (-1: cấm mọi lưới)."""
            i0, i1 = max(0, math.ceil(x0 / G - 1e-6)), min(nx - 1, math.floor(x1 / G + 1e-6))
            j0, j1 = max(0, math.ceil(y0 / G - 1e-6)), min(ny - 1, math.floor(y1 / G + 1e-6))
            a = blk[lop]
            for j in range(j0, j1 + 1):
                for i in range(i0, i1 + 1):
                    c = a[j * nx + i]
                    if c == 0:
                        a[j * nx + i] = n
                    elif c != n:
                        a[j * nx + i] = -1

        le = THU + W_DAY / 2 + 0.3
        for lop in (0, 1):
            to_o(0, 0, self.w, le - 0.01, lop, -1)
            to_o(0, self.h - le + 0.01, self.w, self.h, lop, -1)
            to_o(0, 0, le - 0.01, self.h, lop, -1)
            to_o(self.w - le + 0.01, 0, self.w, self.h, lop, -1)
        nut = {t: [] for t in self.luoi}      # lưới: [tập ô (lớp, chỉ số) của từng pad]
        d = KHE + W_DAY / 2 + 0.06
        for m in self.b.GetFootprints():
            for p in m.Pads():
                bb = p.GetBoundingBox()
                x0, y0 = pcbnew.ToMM(bb.GetLeft()) - PX, pcbnew.ToMM(bb.GetTop()) - PY
                x1, y1 = pcbnew.ToMM(bb.GetRight()) - PX, pcbnew.ToMM(bb.GetBottom()) - PY
                t = p.GetNetname()
                n = ma.get(t, -1)
                lops = [l for l, L in ((0, pcbnew.F_Cu), (1, pcbnew.B_Cu)) if p.IsOnLayer(L)] or [0, 1]
                if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                    lops, n = [0, 1], -1
                for lop in lops:
                    to_o(x0 - d, y0 - d, x1 + d, y1 + d, lop, n)
                if n > 0:
                    o = set()
                    i0, i1 = math.ceil(x0 / G + 0.2), math.floor(x1 / G - 0.2)
                    j0, j1 = math.ceil(y0 / G + 0.2), math.floor(y1 / G - 0.2)
                    cx, cy = pcbnew.ToMM(p.GetPosition().x) - PX, pcbnew.ToMM(p.GetPosition().y) - PY
                    ic, jc = int(round(cx / G)), int(round(cy / G))
                    tron = p.GetShape() not in (pcbnew.PAD_SHAPE_RECT, pcbnew.PAD_SHAPE_ROUNDRECT)
                    if tron or i0 > i1 or j0 > j1:
                        # pad tròn / ô van hoặc quá hẹp: chỉ nhận ô sát tâm, nối bằng một đoạn dây ngắn về đúng tâm
                        i0 = i1 = ic
                        j0 = j1 = jc
                        if abs(ic * G - cx) + abs(jc * G - cy) > 1e-4:
                            for lop in lops:
                                st = pcbnew.PCB_TRACK(self.b)
                                st.SetStart(p.GetPosition())
                                st.SetEnd(pcbnew.VECTOR2I(mm(PX + ic * G), mm(PY + jc * G)))
                                st.SetWidth(mm(W_DAY))
                                st.SetLayer(pcbnew.F_Cu if lop == 0 else pcbnew.B_Cu)
                                st.SetNet(self.ma_luoi[t])
                                self.b.Add(st)
                    for lop in lops:
                        for j in range(j0, j1 + 1):
                            for i in range(i0, i1 + 1):
                                o.add((lop, j * nx + i))
                    nut[t].append(o)
        for dg in self.dong:
            n = ma[dg[1]]
            o = set()
            if dg[0] == "vung":
                x0, y0, x1, y1 = dg[2]
                to_o(x0 - d, y0 - d, x1 + d, y1 + d, 0, n)
                for j in range(math.ceil(y0 / G), math.floor(y1 / G) + 1):
                    for i in range(math.ceil(x0 / G), math.floor(x1 / G) + 1):
                        o.add((0, j * nx + i))
            else:
                r = dg[3] / 2
                for p, q in zip(dg[2], dg[2][1:]):
                    x0, x1 = sorted((p[0], q[0]))
                    y0, y1 = sorted((p[1], q[1]))
                    to_o(x0 - r - d, y0 - r - d, x1 + r + d, y1 + r + d, 0, n)
                    for j in range(math.ceil((y0 - r) / G + 0.2), math.floor((y1 + r) / G - 0.2) + 1):
                        for i in range(math.ceil((x0 - r) / G + 0.2), math.floor((x1 + r) / G - 0.2) + 1):
                            o.add((0, j * nx + i))
            nut[dg[1]].append(o)

        goc = [array("h", x) for x in blk]
        co_ban = sorted(self.luoi, key=lambda t: (t == "GND", t in NGUON, len(nut[t])))
        thu_tu = [co_ban,
                  sorted(self.luoi, key=lambda t: (t != "GND", t in NGUON, len(nut[t]))),
                  sorted(self.luoi, key=lambda t: (t not in NGUON, t != "GND", len(nut[t]))),
                  sorted(self.luoi, key=lambda t: (t == "GND", -len(nut[t])))]
        import random
        rd = random.Random(1)
        for _ in range(8):
            x = list(co_ban)
            rd.shuffle(x)
            thu_tu.append(x)
        tot = None
        for k, tt in enumerate(thu_tu + [None]):
            if tt is None:
                tt = thu_tu[tot[1]]       # không thứ tự nào đi hết: dùng lại thứ tự ít lỗi nhất
            for l in (0, 1):
                blk[l][:] = goc[l]
            self.moi = []
            loi = self._di_mot_luot(tt, nut, ma)
            if not loi or k == len(thu_tu):
                self.loi += loi
                break
            if tot is None or len(loi) < tot[0]:
                tot = (len(loi), k)
            for x in self.moi:
                self.b.Remove(x)

    def _them(self, x):
        self.b.Add(x)
        self.moi.append(x)

    def _di_mot_luot(self, thu_tu, nut, ma):
        nx = self.nx
        loi = []
        for t in thu_tu:
            ds = nut[t]
            if len(ds) < 2:
                continue
            n = ma[t]
            cay = set(ds[0])
            con = ds[1:]
            while con:
                # pad gần cây nhất đi trước
                def kc(o):
                    l, c = next(iter(o))
                    return min(abs(c % nx - a % nx) + abs(c // nx - a // nx) for _, a in list(cay)[::max(1, len(cay) // 60)])
                con.sort(key=kc)
                dich = con.pop(0)
                duong = self._tim(cay, dich, n)
                if duong is None:
                    l0, c0 = next(iter(dich))
                    loi.append(f"không đi được dây lưới {t} tới ({c0 % nx * G - self.w / 2:.2f}, {self.h / 2 - c0 // nx * G:.2f})"
                               f" ô đích {[self.blk[l][c] for l, c in sorted(dich)][:6]} mã {n}")
                    cay |= dich
                    continue
                self._ve(duong, t, n)
                cay |= set(duong) | dich
        return loi

    def _tu_do(self, lop, c, n):
        v = self.blk[lop][c]
        return v == 0 or v == n

    def _via_duoc(self, c, n):
        nx = self.nx
        i, j = c % nx, c // nx
        if i < 2 or j < 2 or i > nx - 3 or j > self.ny - 3:
            return False
        for lop in (0, 1):
            a = self.blk[lop]
            for dj in (-1, 0, 1):
                for di in (-1, 0, 1):
                    v = a[c + dj * nx + di]
                    if v != 0 and v != n:
                        return False
        return True

    def _tim(self, nguon, dich, n):
        nx, ny = self.nx, self.ny
        ti = [c % nx for _, c in dich]
        tj = [c // nx for _, c in dich]
        bi0, bi1, bj0, bj1 = min(ti), max(ti), min(tj), max(tj)

        def h(c):
            i, j = c % nx, c // nx
            return max(bi0 - i, 0, i - bi1) + max(bj0 - j, 0, j - bj1)
        pq, tot, truoc = [], {}, {}
        for lop, c in nguon:
            s = (lop, c, 0)
            tot[s] = 0
            heapq.heappush(pq, (h(c), 0, s))
        buoc = ((1, 0, 1), (-1, 0, 2), (0, 1, 3), (0, -1, 4))
        while pq:
            f, g, s = heapq.heappop(pq)
            if g > tot.get(s, 1e9):
                continue
            lop, c, hg = s
            if (lop, c) in dich:
                kq = []
                while s in truoc:
                    kq.append((s[0], s[1]))
                    s = truoc[s]
                kq.append((s[0], s[1]))
                return kq[::-1]
            i, j = c % nx, c // nx
            for di, dj, h2 in buoc:
                a, b2 = i + di, j + dj
                if a < 0 or b2 < 0 or a >= nx or b2 >= ny:
                    continue
                c2 = b2 * nx + a
                if not self._tu_do(lop, c2, n):
                    continue
                g2 = g + (1.0 if lop == 0 else 1.15) + (1.5 if hg and hg != h2 else 0)
                s2 = (lop, c2, h2)
                if g2 < tot.get(s2, 1e9):
                    tot[s2] = g2
                    truoc[s2] = s
                    heapq.heappush(pq, (g2 + h(c2), g2, s2))
            l2 = 1 - lop
            if self._tu_do(l2, c, n) and self._via_duoc(c, n):
                s2 = (l2, c, 0)
                g2 = g + 16
                if g2 < tot.get(s2, 1e9):
                    tot[s2] = g2
                    truoc[s2] = s
                    heapq.heappush(pq, (g2 + h(c), g2, s2))
        return None

    def _ve(self, duong, ten, n):
        nx = self.nx
        net = self.ma_luoi[ten]

        def tam(c):
            return pcbnew.VECTOR2I(mm(PX + (c % nx) * G), mm(PY + (c // nx) * G))

        def chan(lop, c, r):
            i, j = c % nx, c // nx
            for l in ((0, 1) if lop is None else (lop,)):
                a = self.blk[l]
                for jj in range(max(0, j - r), min(self.ny - 1, j + r) + 1):
                    for ii in range(max(0, i - r), min(nx - 1, i + r) + 1):
                        v = a[jj * nx + ii]
                        if v == 0:
                            a[jj * nx + ii] = n
                        elif v != n:
                            a[jj * nx + ii] = -1
        doan, cu = [], [duong[0]]
        for o in duong[1:]:
            if o[0] != cu[-1][0]:
                doan.append(cu)
                v = pcbnew.PCB_VIA(self.b)
                v.SetPosition(tam(o[1]))
                v.SetWidth(pcbnew.F_Cu, mm(VIA_D))
                v.SetDrill(mm(VIA_K))
                v.SetNet(net)
                self._them(v)
                chan(None, o[1], 2)
                cu = [o]
            else:
                cu.append(o)
        doan.append(cu)
        for cu in doan:
            pts = [c for _, c in cu]
            dau = 0
            for k in range(1, len(pts)):
                if k == len(pts) - 1 or pts[k + 1] - pts[k] != pts[k] - pts[k - 1]:
                    t = pcbnew.PCB_TRACK(self.b)
                    t.SetStart(tam(pts[dau]))
                    t.SetEnd(tam(pts[k]))
                    t.SetWidth(mm(W_DAY))
                    t.SetLayer(pcbnew.F_Cu if cu[0][0] == 0 else pcbnew.B_Cu)
                    t.SetNet(net)
                    self._them(t)
                    dau = k
        for lop, c in duong:
            chan(lop, c, 2)
