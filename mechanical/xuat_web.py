"""Xuất các cụm dự án STEP thành lưới tam giác gọn (JSON) để nhúng vào docs/ban-do-kit-stem.html.

Chạy từ thư mục mechanical sau khi đã dựng STEP:  python xuat_web.py
Kết quả: ../docs/mo-hinh-3d.js định nghĩa biến toàn cục MO_HINH = {tên: {s, o, m: [{c, p, w, i}]}} (w: số byte mỗi chỉ số).
Toạ độ lượng tử hoá Int16 (toạ độ thật = p * s + o), gom các khối cùng màu thành một lưới.
"""
import base64
import json
import struct
import sys
from pathlib import Path

from build123d import import_step

TEN = ["ban_thuc_hanh", "nha_thong_minh", "xe_do_line", "vuon_thong_minh", "xe_can_bang",
       "canh_tay_robot", "bang_tai"]
DUNG_SAI, DUNG_SAI_GOC = 0.4, 0.9


def la(shape, mau=None):
    c = getattr(shape, "color", None) or mau
    kids = list(getattr(shape, "children", []) or [])
    if not kids:
        return [(s, c) for s in shape.solids()]
    out = []
    for k in kids:
        out += la(k, c)
    return out


def hex_mau(c):
    if c is None:
        return "#999999"
    r, g, b = [max(0.0, min(1.0, v)) for v in tuple(c)[:3]]
    f = lambda v: round(255 * (12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055))
    return "#%02x%02x%02x" % (f(r), f(g), f(b))


def xuat(ten):
    nhom = {}
    for solid, c in la(import_step(f"STEP/du_an/{ten}.step")):
        vs, ts = solid.tessellate(DUNG_SAI, DUNG_SAI_GOC)
        g = nhom.setdefault(hex_mau(c), ([], []))
        n0 = len(g[0])
        g[0].extend((v.X, v.Y, v.Z) for v in vs)
        g[1].extend((a + n0, b + n0, c2 + n0) for (a, b, c2) in ts)
    pts = [p for g in nhom.values() for p in g[0]]
    lo = [min(p[k] for p in pts) for k in range(3)]
    hi = [max(p[k] for p in pts) for k in range(3)]
    s = max(hi[k] - lo[k] for k in range(3)) / 65000.0
    meshes, tri = [], 0
    for mau, (vs, ts) in nhom.items():
        q = [round((p[k] - lo[k]) / s) - 32500 for p in vs for k in range(3)]
        idx = [i for t in ts for i in t]
        tri += len(ts)
        meshes.append({"c": mau,
                       "p": base64.b64encode(struct.pack(f"<{len(q)}h", *q)).decode(),
                       "w": 2 if len(vs) < 65536 else 4,
                       "i": base64.b64encode(struct.pack(f"<{len(idx)}{'H' if len(vs) < 65536 else 'I'}", *idx)).decode()})
    print(f"{ten}: {len(pts)} đỉnh, {tri} tam giác, {len(meshes)} màu", file=sys.stderr)
    return {"s": s, "o": [lo[k] + 32500 * s for k in range(3)], "m": meshes}


if __name__ == "__main__":
    data = {t: xuat(t) for t in TEN}
    out = Path("../docs/mo-hinh-3d.js")
    out.write_text("window.MO_HINH=" + json.dumps(data, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"{out}: {out.stat().st_size / 1e6:.2f} MB", file=sys.stderr)
