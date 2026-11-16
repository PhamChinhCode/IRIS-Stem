"""Vỏ in 3D cho bo mang: đế ôm mặt dưới + nắp che mặt trên, kẹp bo bằng vít M3 qua 4 lỗ gá.

Quy ước như lib/mach.py: tâm bo ở gốc XY, mặt dưới bo ở z = 0, mặt trên ở z = 1,6.
Thông số từng bo (chiều cao nắp, lỗ khoét, khe đầu cắm) lấy từ hardware/bo-mang/bo_tri.py,
cùng tệp mà bộ dựng PCB dùng để đặt linh kiện, nên lỗ khoét luôn trùng vị trí linh kiện.

Chồng lắp từ trên xuống: đầu vít M3 – nắp – bo – đế – tấm gá – đai ốc.
"""
import json
import os
import sys

from cadgen import build123d as bd

from lib.chuan import D_M3, T_PCB, hop, to, tru

_BM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "hardware", "bo-mang")
sys.path.insert(0, _BM)
from bo_tri import BO, QUE, lo_ga  # noqa: E402

THU = 0.25       # mép bo thu vào so với kích thước danh nghĩa
KHE = 0.4        # khe giữa mép bo và thành vỏ
T = 1.6          # dày thành, sàn và mặt nắp
H_DUOI = 3.0     # khoảng trống dưới bo cho chân linh kiện xuyên lỗ
D_TRU = 6.4      # trụ kẹp quanh lỗ gá
R_GOC = 2.0


def _khung(ma):
    """(x0, y0, x1, y1) của lòng vỏ."""
    d = BO[ma]
    w, h = d["kt"]
    a, b = w / 2 - THU + KHE, h / 2 - THU + KHE
    y0 = -b
    if d["kt"] == QUE:
        y0 = d["vo"]["que"]          # bo que: vỏ chỉ ôm phần đầu, que cắm đất thò ra ngoài
    return -a, y0, a, b


def _hop_bo(x0, y0, x1, y1, z0, z1):
    s = bd.Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * bd.Box(x1 - x0, y1 - y0, z1 - z0)
    return bd.fillet(s.edges().filter_by(bd.Axis.Z), R_GOC)


def _vo(ma, z0, z1, z_san0, z_san1):
    """Hộp rỗng từ z0 đến z1, sàn (hoặc trần) đặc trong khoảng [z_san0, z_san1]."""
    x0, y0, x1, y1 = _khung(ma)
    s = _hop_bo(x0 - T, y0 - T, x1 + T, y1 + T, z0, z1)
    lo, hi = (z_san1, z1 + 1) if z_san0 <= z0 + 1e-6 else (z0 - 1, z_san0)
    return s - hop(x1 - x0, y1 - y0, hi - lo, (x0 + x1) / 2, (y0 + y1) / 2, lo)


def _khe(ma, canh, tam, rong, z0, cao):
    x0, y0, x1, y1 = _khung(ma)
    if canh in "SN":
        y = y0 - T / 2 if canh == "S" else y1 + T / 2
        return hop(rong, T + 2, cao, tam, y, z0)
    x = x0 - T / 2 if canh == "W" else x1 + T / 2
    return hop(T + 2, rong, cao, x, tam, z0)


def de(ma):
    """Đế: sàn + thành cao tới mặt trên bo, 4 trụ đỡ bo có lỗ thông vít M3."""
    v = BO[ma]["vo"]
    hd = v.get("duoi", H_DUOI)
    s = _vo(ma, -hd - T, T_PCB, -hd - T, -hd)
    for x, y in lo_ga(BO[ma]["kt"]):
        s += tru(v.get("tru", D_TRU), hd, x, y, -hd)
        s -= tru(D_M3, hd + T + 2, x, y, -hd - T - 1)
    for k in v.get("day", ()):          # lỗ khoét trên sàn, ví dụ đầu cắm ở mặt sau bo
        s -= hop(k[3], k[4], T + 2, k[1], k[2], -hd - T - 1)
    if BO[ma]["kt"] == QUE:              # thành phía que: hạ xuống ngang mặt dưới bo để bo thò ra
        x0, y0, x1, y1 = _khung(ma)
        s -= hop(x1 - x0, T + 2, T_PCB + 1, 0, y0 - T / 2, 0)
    return to(s, f"vo_{ma}_de", "in3d")


def nap(ma, in3d=False):
    """Nắp: mặt trên + thành xuống tới mặt trên bo, 4 trụ ép lên bo, lỗ khoét cho linh kiện.

    in3d=True: lật úp, mặt trên nằm ở z = 0 để in không cần đỡ.
    """
    v = BO[ma]["vo"]
    cao = v["cao"]
    z1 = T_PCB + cao + T
    s = _vo(ma, T_PCB, z1, T_PCB + cao, z1)
    for x, y in lo_ga(BO[ma]["kt"]):
        s += tru(v.get("tru", D_TRU), cao, x, y, T_PCB)
        s -= tru(D_M3, cao + T + 2, x, y, T_PCB - 1)
    for k in v.get("lo", ()):
        if k[0] == "tr":
            s -= tru(k[3], T + 2, k[1], k[2], T_PCB + cao - 1)
        else:
            s -= hop(k[3], k[4], T + 2, k[1], k[2], T_PCB + cao - 1)
    for canh, tam, rong, h in v.get("canh", [("S", 0.0, 11.0, 6.0)]):
        s -= _khe(ma, canh, tam, rong, T_PCB - 0.01, min(h, cao + T + 1))
    s = to(s, f"vo_{ma}_nap", "in3d2")
    if in3d:
        s = bd.Pos(0, 0, z1) * bd.Rot(180, 0, 0) * s
        s.label = f"vo_{ma}_nap"
    return s


def co_nap(ma):
    return BO[ma]["vo"].get("nap", True)


# chiều cao linh kiện trên mặt bo (mm), theo tên chân linh kiện
_CAO = (("Cong_PH", 4.8), ("Cong_XH", 7.0), ("SW_Push", 7.0), ("Potentiometer", 6.5), ("R_LDR", 5.0),
        ("Vishay_MINICAST", 7.0), ("MQ-6", 16.0), ("Relay", 15.5), ("TerminalBlock", 10.0), ("PinSocket", 0.0),
        ("SMDIP", 4.0), ("D_SMA", 2.4), ("TestPoint", 0.0), ("Khung", 0.0))


def kiem(ma):
    """So bố trí PCB thực tế với nắp: linh kiện cao hơn lòng nắp phải nằm trong lỗ khoét hoặc khe; không chạm trụ."""
    v = BO[ma]["vo"]
    bt = json.load(open(os.path.join(_BM, ma, ma + "-bo-tri.json"), encoding="utf-8"))
    x0, y0, x1, y1 = _khung(ma)
    kq = []
    for ref, d in bt.items():
        if d["duoi"]:
            continue
        cao = next((h for t, h in _CAO if d["fp"].startswith(t)), 2.0)
        a, b, c, e = d["khung"]
        for x, y in lo_ga(BO[ma]["kt"]):
            dx, dy = max(a + 0.25 - x, 0, x - c + 0.25), max(b + 0.25 - y, 0, y - e + 0.25)
            if (dx * dx + dy * dy) ** 0.5 < v.get("tru", D_TRU) / 2 - 0.05 and cao > 0:
                kq.append(f"{ref} cách trụ ({x:g}, {y:g}) {(dx * dx + dy * dy) ** 0.5:.1f} mm")
        if cao <= v["cao"] or not co_nap(ma):
            continue
        cx, cy = (a + c) / 2, (b + e) / 2
        trong = any(abs(cx - k[1]) < k[3] / 2 and abs(cy - k[2]) < (k[4] if k[0] == "cn" else k[3]) / 2 for k in v.get("lo", ()))
        if not trong:
            kq.append(f"{ref} cao {cao} > lòng nắp {v['cao']} mà không có lỗ khoét")
    return kq
