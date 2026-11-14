"""Khung xe K2 dùng chung cho xe dò line (nằm ngang) và xe cân bằng (dựng đứng).

Hệ toạ độ xe: +X là đầu xe, +Z là phía trên, z = 0 là mặt dưới tấm đế.
"""
from cadgen import build123d as bd

from chi_tiet.ga_n20 import ga_n20
from chi_tiet.tam_xe import tam_xe
from lib.chuan import T_XE, Tam, dat
from lib.kt import N20_LO, N20_TAM, XE_L, XE_W
from lib.mach import cum_gan
from lib.mua_san import BANH_D, BANH_W, banh_xe, n20, tru_do

X_TRUC = -56.0                 # vị trí trục bánh theo X
Z_TRUC = T_XE + N20_TAM        # cao độ trục bánh so với mặt dưới tấm đế
Z_DAT = Z_TRUC - BANH_D / 2    # cao độ mặt đất
H_TANG = 40.0                  # trụ giữa tấm đế và tấm trên
Y_BANH = XE_W / 2 + 2.0 + BANH_W / 2


def khung_xe():
    """Trả về (tấm đế, tấm trên, danh sách khối): hai tấm, trụ, cụm truyền động K1, S1 và C1."""
    de = Tam("tam_de", tam_xe(), XE_L, XE_W, T_XE)
    tren = Tam("tam_tren", tam_xe(), XE_L, XE_W, T_XE, o=(0, 0, T_XE + H_TANG))
    p = [de.part, tren.part]
    for x in (-76.0, 76.0):
        for y in (-44.0, 44.0):
            p.append(tru_do(H_TANG, x, y, T_XE))
    for sy, rz in ((1, 0), (-1, 180)):
        p += de.gan([ga_n20()], N20_LO, X_TRUC, sy * 44.0, rz=rz, ten="gá N20")
        p += dat(bd.Pos(X_TRUC, sy * XE_W / 2, Z_TRUC) * bd.Rot(0, 0, rz), n20())
        p += dat(bd.Pos(X_TRUC, sy * Y_BANH, Z_TRUC), banh_xe())
    p += de.gan(*cum_gan("S1"), -24.0, 0.0, ten="S1")
    p += tren.gan(*cum_gan("C1"), -40.0, 0.0, rz=90, ten="C1")
    return de, tren, p
