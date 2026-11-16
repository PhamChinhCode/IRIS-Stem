"""Kiểm va chạm trong các cụm dự án: thể tích giao nhau giữa mọi cặp khối cấp một.

Chạy từ mechanical/src:  PYTHONUTF8=1 python kiem_va_cham.py [tên cụm ...]
Bỏ qua các cặp cùng một module (bo với đế, nắp của chính nó) và giao nhau dưới NGUONG mm³.
"""
import importlib
import re
import sys

import os

_relpath = os.path.relpath


def _relpath_an_toan(path, start=None):
    """cadgen 0.5.1 gọi relpath giữa hai ổ đĩa (mã ở D:, Python ở C:) và dừng; trả lại đường dẫn gốc."""
    try:
        return _relpath(path, start) if start else _relpath(path)
    except ValueError:
        return path


os.path.relpath = _relpath_an_toan

CUM = ["ban_thuc_hanh", "nha_thong_minh", "xe_do_line", "xe_can_bang", "vuon_thong_minh", "canh_tay_robot", "bang_tai"]
NGUONG = 2.0


def ma_bo(ten):
    m = re.search(r"(?:^|_)([CSIO]\d+)(?:_|$)", ten or "")
    return m.group(1) if m else None


def kiem(ten):
    f = getattr(importlib.import_module("du_an." + ten), ten)
    c = getattr(f, "__wrapped__", f)()
    ds = []
    for k in c.children:
        s = k.solids()
        if s:
            ds.append((k.label or "?", k.bounding_box(), s))
    kq = []
    for i in range(len(ds)):
        ti, bi, si = ds[i]
        for j in range(i + 1, len(ds)):
            tj, bj, sj = ds[j]
            if (bi.max.X < bj.min.X + 0.05 or bj.max.X < bi.min.X + 0.05 or bi.max.Y < bj.min.Y + 0.05 or
                    bj.max.Y < bi.min.Y + 0.05 or bi.max.Z < bj.min.Z + 0.05 or bj.max.Z < bi.min.Z + 0.05):
                continue
            if ma_bo(ti) and ma_bo(ti) == ma_bo(tj):
                continue
            the = 0.0
            for a in si:
                ba = a.bounding_box()
                for b in sj:
                    bb = b.bounding_box()
                    if (ba.max.X < bb.min.X or bb.max.X < ba.min.X or ba.max.Y < bb.min.Y or bb.max.Y < ba.min.Y or
                            ba.max.Z < bb.min.Z or bb.max.Z < ba.min.Z):
                        continue
                    try:
                        g = a & b
                        the += sum(x.volume for x in g.solids()) if g else 0.0
                    except Exception:       # noqa: BLE001
                        the += 0.0
            if the > NGUONG:
                kq.append((the, ti, tj))
    print(f"{ten}: {len(ds)} khối, {len(kq)} cặp giao nhau")
    for the, a, b in sorted(kq, reverse=True):
        print(f"   {a} ∩ {b}: {the:.0f} mm³")
    sys.stdout.flush()


if __name__ == "__main__":
    chon = sys.argv[1:] or CUM
    sys.argv = sys.argv[:1]          # cadgen tự đọc tham số dòng lệnh khi dựng chi tiết con
    for t in chon:
        kiem(t)
