"""Chuyển tệp 3D (STEP, STL) thành dữ liệu cho trang stem-kit-map (index.html, ban-do.js), và xuất hình sơ đồ, PCB từ KiCad.

Chạy trong thư mục stem-kit-map:
    python update_3d.py              chỉ chuyển các tệp mới hoặc vừa sửa
    python update_3d.py --tat-ca     chuyển lại toàn bộ
    python update_3d.py xe_do_line   chỉ chuyển mô hình có tên này

Nguồn, theo thứ tự ưu tiên (mô hình trùng tên ở nguồn trước thắng nguồn sau):
    1. nguon-3d/*.step | *.stp | *.stl            tệp thả tay, tên bất kỳ theo HUONG-DAN.md
    2. ../projects/**/Project<số>.step            mô hình lắp ráp của riêng một dự án, ví dụ Project11.step
    3. ../hardware/**/<mã module>.step            mạch + vỏ đã ghép của một module, ví dụ hardware/C1-bo-chu/C1.step
    4. ../mechanical/STEP/du_an/*.step            7 cụm dự án dựng từ mã CAD
    5. ../mechanical/STEP/module/*.step           25 module (mechanical/src/xuat_module.py)
Kết quả: mo-hinh/<tên>.js (mỗi mô hình một tệp) và mo-hinh/danh-sach.js; hinh/<mã>-so-do.svg, hinh/<mã>-pcb.svg (xuất bằng kicad-cli từ
hardware/**/<mã module>.kicad_sch và .kicad_pcb, chỉ khi tệp KiCad mới hơn hình);
tai-lieu/<mã>.pdf (chép từ hardware/**/<mã module>.pdf, ví dụ hardware/bo-mang/I1/I1.pdf).
Hướng dẫn đầy đủ: HUONG-DAN.md.
"""
import base64
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

DAY = Path(__file__).resolve().parent
GOC = DAY.parent
DUOI = (".step", ".stp", ".stl")
MA_MODULE = re.compile(r"^[CSIOK]\d{1,2}$")              # C1, S2, I14, O7...
TEN_DU_AN = re.compile(r"^project[ _-]?(\d{1,2})$", re.I)   # Project11, project_11, Project-11
RA = DAY / "mo-hinh"
KICAD_CLI = Path(os.environ.get("KICAD_DIR", "C:/Program Files/KiCad/10.0")) / "bin" / "kicad-cli.exe"
DUNG_SAI, DUNG_SAI_GOC = 0.4, 0.9
NGUONG_NANG = 150000         # chỉ để cảnh báo: mô hình nhiều tam giác hơn mức này làm trang tải chậm
MAU_STL = "#3a7bd5"          # tệp STL không mang màu: cả mô hình một màu


def _hex(c):
    if c is None:
        return "#999999"
    r, g, b = [max(0.0, min(1.0, v)) for v in tuple(c)[:3]]
    f = lambda v: round(255 * (12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055))  # noqa: E731
    return "#%02x%02x%02x" % (f(r), f(g), f(b))


def _la(shape, mau=None, vi_tri=None):
    """Các khối lá kèm màu. Vị trí của khối con tính theo cụm cha (tệp STEP của KiCad đặt mỗi linh kiện trong một cụm
    có vị trí riêng), nên phải cộng dồn vị trí các cụm cha vào khối lá."""
    c = getattr(shape, "color", None) or mau
    con = list(getattr(shape, "children", []) or [])
    if not con:
        if vi_tri is not None:
            shape = shape.moved(vi_tri)
        ds = shape.solids()
        return [(x, c) for x in ds] if ds else [(shape, c)]      # tệp chỉ có mặt (surface): vẫn vẽ các mặt đó
    xuong = shape.location if vi_tri is None else vi_tri * shape.location
    kq = []
    for k in con:
        kq += _la(k, c, xuong)
    return kq


def _luoi(shape, sai_so):
    """(đỉnh, tam giác, số mặt bỏ qua) của một khối. Mặt nào bộ chia lưới không xử lý được thì bỏ qua thay vì dừng cả tệp."""
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_Orientation
    from OCP.TopLoc import TopLoc_Location
    BRepMesh_IncrementalMesh(shape.wrapped, sai_so, False, DUNG_SAI_GOC, True)
    vs, ts, bo = [], [], 0
    for face in shape.faces():
        loc = TopLoc_Location()
        poly = BRep_Tool.Triangulation_s(face.wrapped, loc)
        if poly is None:
            bo += 1
            continue
        trsf = loc.Transformation()
        dao = face.wrapped.Orientation() == TopAbs_Orientation.TopAbs_REVERSED
        n0 = len(vs)
        for i in range(1, poly.NbNodes() + 1):
            v = poly.Node(i).Transformed(trsf)
            vs.append((v.X(), v.Y(), v.Z()))
        for t in poly.Triangles():
            a, b, c = t.Value(1) + n0 - 1, t.Value(2) + n0 - 1, t.Value(3) + n0 - 1
            ts.append((a, c, b) if dao else (a, b, c))
    return vs, ts, bo


def doc_step(tep):
    """{màu: (đỉnh, tam giác)} từ tệp STEP; giữ màu của từng khối. Bước lưới cố định DUNG_SAI cho mọi mô hình."""
    from build123d import import_step
    nhom, bo, so_tam = {}, 0, 0
    for khoi, c in _la(import_step(str(tep))):
        vs, ts, b = _luoi(khoi, DUNG_SAI)
        bo += b
        so_tam += len(ts)
        g = nhom.setdefault(_hex(c), ([], []))
        n0 = len(g[0])
        g[0].extend(vs)
        g[1].extend((a + n0, b2 + n0, d + n0) for (a, b2, d) in ts)
    if bo:
        print(f"   chú ý: bỏ qua {bo} mặt không chia lưới được trong {tep.name} (mô hình có thể thiếu vài mặt nhỏ)")
    if so_tam > NGUONG_NANG:
        print(f"   chú ý: {tep.name} có {so_tam} tam giác, trang sẽ tải chậm; nên giản lược mô hình (dưới {NGUONG_NANG})")
    return nhom


def doc_stl(tep):
    """{màu: (đỉnh, tam giác)} từ tệp STL nhị phân hoặc văn bản."""
    d = tep.read_bytes()
    tam = []
    n = struct.unpack_from("<I", d, 80)[0] if len(d) >= 84 else 0
    if len(d) == 84 + 50 * n and n:
        for k in range(n):
            v = struct.unpack_from("<9f", d, 84 + 50 * k + 12)
            tam.append((v[0:3], v[3:6], v[6:9]))
    else:
        so = [float(x) for dong in d.decode("utf-8", "replace").splitlines() if dong.strip().startswith("vertex")
              for x in dong.split()[1:4]]
        tam = [(tuple(so[i:i + 3]), tuple(so[i + 3:i + 6]), tuple(so[i + 6:i + 9])) for i in range(0, len(so) - 8, 9)]
    chi_so, vs, ts = {}, [], []
    for t in tam:
        ts.append(tuple(chi_so.setdefault(tuple(round(c, 4) for c in p), len(chi_so)) for p in t))
    vs = [None] * len(chi_so)
    for p, i in chi_so.items():
        vs[i] = p
    return {MAU_STL: (vs, ts)}


def chuyen(tep):
    nhom = doc_stl(tep) if tep.suffix.lower() == ".stl" else doc_step(tep)
    pts = [p for g in nhom.values() for p in g[0]]
    if not pts:
        raise ValueError("tệp không có khối đặc nào")
    lo = [min(p[k] for p in pts) for k in range(3)]
    hi = [max(p[k] for p in pts) for k in range(3)]
    s = max(max(hi[k] - lo[k] for k in range(3)), 1e-6) / 65000.0
    luoi, so_tam = [], 0
    for mau, (vs, ts) in nhom.items():
        q = [round((p[k] - lo[k]) / s) - 32500 for p in vs for k in range(3)]
        idx = [i for t in ts for i in t]
        so_tam += len(ts)
        nho = len(vs) < 65536
        luoi.append({"c": mau, "p": base64.b64encode(struct.pack(f"<{len(q)}h", *q)).decode(), "w": 2 if nho else 4,
                     "i": base64.b64encode(struct.pack(f"<{len(idx)}{'H' if nho else 'I'}", *idx)).decode()})
    return {"s": s, "o": [lo[k] + 32500 * s for k in range(3)], "m": luoi,
            "kt": [round(hi[k] - lo[k], 1) for k in range(3)]}, len(pts), so_tam


def xuat_hinh(tat_ca):
    """Xuất hình sơ đồ và mạch in thẳng từ tệp KiCad hardware/**/<mã module>.kicad_sch | .kicad_pcb vào hinh/.
    Chỉ xuất lại khi tệp KiCad mới hơn hình. Trả về ({tên hình: số phiên bản}, số hình vừa xuất)."""
    ra = DAY / "hinh"
    ra.mkdir(exist_ok=True)
    nguon = {}                                          # tên hình -> tệp KiCad
    if (GOC / "hardware").is_dir():
        for f in sorted((GOC / "hardware").rglob("*.kicad_*")):
            duoi = {".kicad_sch": "-so-do", ".kicad_pcb": "-pcb"}.get(f.suffix)
            if duoi and MA_MODULE.match(f.stem.upper()) and ".history" not in f.parts and "-backups" not in str(f.parent):
                nguon[f.stem.upper() + duoi] = f
    can = [t for t, f in nguon.items()
           if tat_ca or not (ra / (t + ".svg")).exists() or (ra / (t + ".svg")).stat().st_mtime < f.stat().st_mtime]
    n = 0
    if can and not KICAD_CLI.exists():
        print(f"CẢNH BÁO: không thấy {KICAD_CLI} nên {len(can)} hình chưa được xuất lại "
              "(đặt biến môi trường KICAD_DIR nếu KiCad cài ở chỗ khác)")
        can = []
    for t in can:
        f, dich = nguon[t], ra / (t + ".svg")
        with tempfile.TemporaryDirectory() as tam:
            if f.suffix == ".kicad_sch":
                lenh = [str(KICAD_CLI), "sch", "export", "svg", "-o", tam, str(f)]
                kq = Path(tam) / (f.stem + ".svg")
            else:
                kq = Path(tam) / "pcb.svg"
                lenh = [str(KICAD_CLI), "pcb", "export", "svg", "--layers", "F.Cu,F.SilkS,Edge.Cuts", "--page-size-mode", "2",
                        "--exclude-drawing-sheet", "-o", str(kq), str(f)]
            r = subprocess.run(lenh, cwd=f.parent, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if not kq.exists():
                print(f"LỖI hình {t} ({f.name}): {(r.stderr or r.stdout).strip()[-300:]}")
                continue
            shutil.copyfile(kq, dich)
        n += 1
        print(f"hình {t}: từ {f.relative_to(GOC).as_posix()}")
    return {p.stem: int(p.stat().st_mtime) for p in sorted(ra.glob("*.svg"))}, n


def chep_tai_lieu():
    """Chép hardware/**/<mã module>.pdf vào tai-lieu/<MÃ>.pdf. Trả về ({mã: số phiên bản}, số tệp mới chép)."""
    ra = DAY / "tai-lieu"
    ra.mkdir(exist_ok=True)
    nguon = {}
    if (GOC / "hardware").is_dir():
        for f in sorted((GOC / "hardware").rglob("*.pdf")):
            ma = f.stem.upper()
            if MA_MODULE.match(ma) and ".history" not in f.parts:
                if ma not in nguon or nguon[ma].stat().st_mtime < f.stat().st_mtime:
                    nguon[ma] = f
    n = 0
    for ma, f in nguon.items():
        dich = ra / (ma + ".pdf")
        if not dich.exists() or dich.stat().st_mtime < f.stat().st_mtime:
            shutil.copyfile(f, dich)
            n += 1
            print(f"tài liệu {ma}: từ {f.relative_to(GOC).as_posix()}")
    for cu in ra.glob("*.pdf"):                         # tài liệu không còn nguồn: gỡ khỏi trang
        if cu.stem not in nguon:
            cu.unlink()
            print(f"gỡ tai-lieu/{cu.name}: không còn tệp nguồn")
    return {ma: int((ra / (ma + ".pdf")).stat().st_mtime) for ma in sorted(nguon)}, n


def tim_nguon():
    """{tên mô hình: tệp nguồn}. Nguồn xét sau ghi đè nguồn xét trước, nên xếp từ ưu tiên thấp đến cao."""
    tep = {}

    def nhan(ten, f):
        cu = tep.get(ten)
        # cùng một nguồn có hai tệp trùng tên mô hình: lấy tệp sửa gần nhất
        if cu is not None and cu.parent == f.parent and cu.stat().st_mtime > f.stat().st_mtime:
            return
        tep[ten] = f

    for thu_muc in (GOC / "mechanical" / "STEP" / "module", GOC / "mechanical" / "STEP" / "du_an"):
        if thu_muc.is_dir():
            for f in sorted(thu_muc.iterdir()):
                if f.suffix.lower() in DUOI:
                    nhan(f.stem, f)
    if (GOC / "hardware").is_dir():                    # <mã module>.step ở bất kỳ đâu trong hardware/
        for f in sorted((GOC / "hardware").rglob("*")):
            if f.suffix.lower() in DUOI and MA_MODULE.match(f.stem.upper()) and ".history" not in f.parts:
                nhan(f.stem.upper(), f)
    if (GOC / "projects").is_dir():                    # Project<số>.step ở bất kỳ đâu trong projects/
        for f in sorted((GOC / "projects").rglob("*")):
            m = TEN_DU_AN.match(f.stem) if f.suffix.lower() in DUOI else None
            if m:
                nhan(f"du_an_{int(m.group(1))}", f)
    if (DAY / "nguon-3d").is_dir():
        for f in sorted((DAY / "nguon-3d").iterdir()):
            if f.suffix.lower() in DUOI:
                m = TEN_DU_AN.match(f.stem)
                nhan(f"du_an_{int(m.group(1))}" if m else f.stem, f)
    return tep


def main():
    tat_ca = "--tat-ca" in sys.argv
    chon = [a for a in sys.argv[1:] if not a.startswith("--")]
    RA.mkdir(exist_ok=True)
    (DAY / "nguon-3d").mkdir(exist_ok=True)
    tep = tim_nguon()
    so = RA / "nguon.json"                              # tệp nguồn đã dùng cho từng mô hình ở lần chạy trước
    dau_cu = json.loads(so.read_text(encoding="utf-8")) if so.exists() else {}
    moi = {}
    loi = 0
    for ten, f in sorted(tep.items()):
        if chon and ten not in chon:
            continue
        dich = RA / (ten + ".js")
        dau = [f.relative_to(GOC).as_posix(), f.stat().st_mtime]
        if not tat_ca and not chon and dich.exists() and dau_cu.get(ten) == dau:
            moi[ten] = dau                              # cùng tệp nguồn, chưa sửa: giữ nguyên
            continue
        try:
            d, so_dinh, so_tam = chuyen(f)
        except Exception as e:      # noqa: BLE001
            print(f"LỖI {ten} ({f.name}): {e}")
            loi += 1
            continue
        moi[ten] = dau
        dich.write_text(f"(window.MO_HINH=window.MO_HINH||{{}})[{json.dumps(ten)}]=" + json.dumps(d, separators=(",", ":")) + ";\n",
                        encoding="utf-8")
        print(f"{ten}: {so_dinh} đỉnh, {so_tam} tam giác, {dich.stat().st_size / 1e6:.2f} MB  (từ {f.relative_to(GOC).as_posix()})")
    for cu in RA.glob("*.js"):                          # mô hình không còn nguồn: gỡ khỏi trang
        if cu.stem != "danh-sach" and cu.stem not in tep:
            cu.unlink()
            print(f"gỡ {cu.name}: không còn tệp nguồn")
    for ten in tep:                                     # mô hình không chạy lượt này: giữ dấu cũ
        moi.setdefault(ten, dau_cu.get(ten))
    so.write_text(json.dumps({k: v for k, v in moi.items() if v}, ensure_ascii=False, indent=1), encoding="utf-8")
    ds = sorted(p.stem for p in RA.glob("*.js") if p.stem != "danh-sach")
    # kèm số phiên bản (thời điểm ghi tệp) để trình duyệt không dùng lại bản cũ đã lưu đệm
    phien = {t: int((RA / (t + ".js")).stat().st_mtime) for t in ds}
    tai_lieu, so_tl = chep_tai_lieu()
    hinh, so_hinh = xuat_hinh(tat_ca)
    (RA / "danh-sach.js").write_text("window.MO_HINH_DS=" + json.dumps(ds) + ";\nwindow.MO_HINH_V=" + json.dumps(phien)
                                     + ";\nwindow.TAI_LIEU=" + json.dumps(tai_lieu)
                                     + ";\nwindow.HINH_V=" + json.dumps(hinh) + ";\n", encoding="utf-8")
    print(f"{len(ds)} mô hình trong mo-hinh/; {len(hinh)} hình trong hinh/ ({so_hinh} vừa xuất từ KiCad); "
          f"{len(tai_lieu)} tài liệu PDF trong tai-lieu/ ({so_tl} mới)")
    return 1 if loi else 0


if __name__ == "__main__":
    sys.exit(main())
