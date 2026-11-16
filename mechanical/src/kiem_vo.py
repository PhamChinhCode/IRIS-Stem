"""Kiểm vỏ bo mang với mô hình 3D thật của PCB (xuất từ KiCad): phần giao nhau giữa vỏ và từng linh kiện.

Chạy từ mechanical/src:  PYTHONUTF8=1 python kiem_vo.py [mã bo ...]
Cần mechanical/STEP/pcb/<mã>.step, xuất bằng hardware/bo-mang/xuat_step.py.
"""
import json
import os
import sys

from cadgen import build123d as bd

from lib.vo import BO, co_nap, de, nap

PCB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "STEP", "pcb")
BM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "hardware", "bo-mang")


def la(p, ma):
    """Các khối đặc (toạ độ toàn cục) kèm tên linh kiện, tra theo vị trí trong tệp bố trí của PCB."""
    bt = json.load(open(os.path.join(BM, ma, ma + "-bo-tri.json"), encoding="utf-8"))
    kq = []
    for x in p.solids():
        b = x.bounding_box()
        cx, cy = (b.min.X + b.max.X) / 2, (b.min.Y + b.max.Y) / 2
        ten = "bo mạch" if b.max.X - b.min.X > BO[ma]["kt"][0] - 2 else next(
            (r for r, d in bt.items() if d["khung"][0] - 0.3 <= cx <= d["khung"][2] + 0.3 and d["khung"][1] - 0.3 <= cy <= d["khung"][3] + 0.3), "?")
        kq.append((ten, x))
    return kq


def kiem(ma):
    p = bd.import_step(os.path.join(PCB, ma + ".step"))
    bb = p.bounding_box()
    ds = la(p, ma)
    kq = [f"{ma}: PCB x[{bb.min.X:.1f},{bb.max.X:.1f}] y[{bb.min.Y:.1f},{bb.max.Y:.1f}] z[{bb.min.Z:.1f},{bb.max.Z:.1f}], {len(ds)} khối"]
    vo = [("đế", de(ma))] + ([("nắp", nap(ma))] if co_nap(ma) else [])
    for ten_vo, v in vo:
        vb = v.bounding_box()
        for ten, s in ds:
            b = s.bounding_box()
            if b.max.X < vb.min.X or b.min.X > vb.max.X or b.max.Y < vb.min.Y or b.min.Y > vb.max.Y or b.max.Z < vb.min.Z or b.min.Z > vb.max.Z:
                continue
            try:
                g = v & s
                the = sum(x.volume for x in g.solids()) if g else 0.0
            except Exception as e:      # noqa: BLE001
                the = -1.0
            if the > 0.05 or the < 0:
                gb = g.bounding_box() if the > 0 else b
                kq.append(f"   {ten_vo} ∩ {ten}: {the:.1f} mm³ tại x[{gb.min.X:.1f},{gb.max.X:.1f}] y[{gb.min.Y:.1f},{gb.max.Y:.1f}] z[{gb.min.Z:.1f},{gb.max.Z:.1f}]"
                          f"  (linh kiện z tới {b.max.Z:.1f})")
        # linh kiện nhô ra ngoài vỏ mà không qua lỗ khoét đã được tính ở trên; in thêm linh kiện cao nhất
    cao = max(ds, key=lambda t: t[1].bounding_box().max.Z)
    kq.append(f"   cao nhất: {cao[0]} z = {cao[1].bounding_box().max.Z:.1f}; trần nắp trong z = {1.6 + BO[ma]['vo']['cao']:.1f}")
    return kq


if __name__ == "__main__":
    for ma in (sys.argv[1:] or list(BO)):
        print("\n".join(kiem(ma)), flush=True)
