"""Khâu 2 cánh tay (cẳng tay): dài 64 mm, đầu xa có ô lắp servo kẹp và hàm kẹp cố định."""
from cadgen import step, stl

from lib.chuan import T_TAM, hop, to, tru_y
from lib.kt import SG_O, TAY_L2
from lib.mua_san import SG_TAI_LO, SG_TRUC_X


@step(out="../../STEP/chi_tiet/tay_khau_2.step")
@stl(out="../../STL/tay_khau_2.stl")
def tay_khau_2():
    L = TAY_L2
    s = hop(L + 20.0, T_TAM, 22.0, x=(L + 4.0) / 2, y=T_TAM / 2, z=-11.0)
    s += hop(46.0, T_TAM, 6.0, x=L + 34.0, y=T_TAM / 2, z=-11.0)
    s += hop(36.0, 27.0, T_TAM, x=L + 38.0, y=7.5, z=-11.0)
    s -= hop(SG_O[1] - SG_O[0], T_TAM + 2, 2 * SG_O[2], L + (SG_O[0] + SG_O[1]) / 2, T_TAM / 2, -SG_O[2])
    for sx in (-1, 1):
        s -= tru_y(1.8, T_TAM + 2, L - SG_TRUC_X + sx * SG_TAI_LO / 2, -1, 0)
    s -= tru_y(2.5, T_TAM + 2, 0, -1, 0)
    for x in (8.0, 14.0):
        s -= tru_y(2.0, T_TAM + 2, x, -1, 0)
    return to(s, "tay_khau_2", "in3d")


if __name__ == "__main__":
    tay_khau_2()
