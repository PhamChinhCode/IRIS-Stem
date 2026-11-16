"""Dựng PCB của 19 bo mang từ sơ đồ: đặt linh kiện, đi dây 2 lớp, đổ đồng GND, chạy DRC.

Chạy bằng Python của KiCad 10:
    "C:/Program Files/KiCad/10.0/bin/python.exe" ve_pcb.py [mã bo ...]
Kịch bản ghi đè <mã>/<mã>.kicad_pcb; không chạy lại cho bo đã sửa PCB bằng tay.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

DAY = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(DAY, "..", "common"))
import pcb  # noqa: E402
from bo_tri import BO, lo_ga  # noqa: E402

CLI = pcb.KICAD + "/bin/kicad-cli.exe"
HINH = os.path.join(DAY, "..", "..", "docs", "hinh-mach", "bo-mang")


def mot_bo(ma):
    d = BO[ma]
    w, h = d["kt"]
    thu_muc = os.path.join(DAY, ma)
    tam = tempfile.gettempdir()
    net = os.path.join(tam, ma + ".net")
    subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", net, ma + ".kicad_sch"],
                   cwd=thu_muc, capture_output=True, check=True)
    b = pcb.Bo(ma, net, w, h, lo_ga(d["kt"]))
    for ref, v in d["dat"].items():
        b.dat(ref, v[0], v[1], v[2], len(v) > 3)
    for kieu, luoi, x0, y0, x1, y1 in d.get("dong", ()):
        b.vung_dong(luoi, x0, y0, x1, y1)
    lc = d.get("luoc")
    if lc:
        x, y0, n, p, r = lc["x"], lc["y0"], lc["n"], lc["buoc"], lc["rong"]
        y1 = y0 + (2 * n - 1) * p
        b.day(lc["a"], [(-x, y0), (-x, y1 - p)], r)
        b.day(lc["b"], [(x, y0 + p), (x, y1)], r)
        for k in range(n):
            ya, yb = y0 + 2 * k * p, y0 + (2 * k + 1) * p
            b.day(lc["a"], [(-x, ya), (x - 1.4, ya)], r)
            b.day(lc["b"], [(x, yb), (-x + 1.4, yb)], r)
        b.cam_dat(-x - 1, y0 - 1, x + 1, y1 + 1)
    b.tu_dat(d.get("vung"))
    g = d.get("gnd")
    if g:
        a, c = b.b_(g[0], g[3]), b.b_(g[2], g[1])
        b.gnd = (max(a[0], pcb.THU), max(a[1], pcb.THU), min(c[0], w - pcb.THU), min(c[1], h - pcb.THU))
    tep = os.path.join(thu_muc, ma + ".kicad_pcb")
    ho = b.dung(tep, (f"IRIS {ma}", d.get("chu", (0, 0))[0], d.get("chu", (0, 0))[1]) if "chu" in d else None)
    # bố trí thực tế, để mô hình vỏ kiểm va chạm
    bt = {}
    for ref, (ox, oy, goc, duoi) in b.da_dat.items():
        c = pcb.hinh(b.lk[ref]["fp"], goc, duoi)[0]
        bt[ref] = dict(fp=b.lk[ref]["fp"].split(":")[1], duoi=duoi, goc=goc,
                       khung=[round(c[0] + ox - w / 2, 2), round(h / 2 - (c[3] + oy), 2),
                              round(c[2] + ox - w / 2, 2), round(h / 2 - (c[1] + oy), 2)])
    json.dump(bt, open(os.path.join(thu_muc, ma + "-bo-tri.json"), "w", encoding="utf-8"), indent=1)
    rpt = os.path.join(tam, ma + ".drc")
    subprocess.run([CLI, "pcb", "drc", "--severity-all", "--schematic-parity", "-o", rpt, tep], capture_output=True)
    r = open(rpt, encoding="utf-8").read()
    loai = {}
    for m in re.finditer(r"^\[(\w+)\]", r, re.M):
        loai[m.group(1)] = loai.get(m.group(1), 0) + 1
    os.makedirs(HINH, exist_ok=True)
    for lop, duoi in (("F.Cu,F.SilkS,Edge.Cuts", "tren"), ("B.Cu,B.SilkS,Edge.Cuts", "duoi")):
        subprocess.run([CLI, "pcb", "export", "svg", "--layers", lop, "--page-size-mode", "2", "--exclude-drawing-sheet",
                        "-o", os.path.join(HINH, f"{ma}-pcb-{duoi}.svg"), tep], capture_output=True)
    print(f"{ma}: {len(b.da_dat)} linh kiện, hở {ho}, lỗi {b.loi}, DRC {loai}")
    sys.stdout.flush()
    return ho, b.loi, loai


if __name__ == "__main__":
    for ma in (sys.argv[1:] or list(BO)):
        mot_bo(ma)
