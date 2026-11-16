"""Khâu 2 cánh tay (cẳng tay): dài 64 mm, đầu xa có ô lắp servo kẹp MG90S và hàm kẹp cố định."""
from cadgen import step, stl

from lib.chuan import T_TAM, hop, to
from lib.kt import TAY_L2
from lib.tay import lo_can, o_servo


@step(out="../../STEP/chi_tiet/tay_khau_2.step")
@stl(out="../../STL/tay_khau_2.stl")
def tay_khau_2():
    L = TAY_L2
    s = hop(L + 22.0, T_TAM, 22.0, x=(L + 2.0) / 2, y=T_TAM / 2, z=-11.0)
    for z in (-11.0, 8.0):
        s += hop(L - 38.0, 4.0, 3.0, x=L / 2 - 4.0, y=T_TAM + 2.0, z=z)
    s += hop(46.0, T_TAM, 6.0, x=L + 34.0, y=T_TAM / 2, z=-11.0)        # thanh nối ra hàm cố định
    s += hop(36.0, 27.0, T_TAM, x=L + 38.0, y=7.5, z=-11.0)             # má kẹp cố định
    s -= o_servo(L)
    s -= lo_can()
    return to(s, "tay_khau_2", "in3d")


if __name__ == "__main__":
    tay_khau_2()
