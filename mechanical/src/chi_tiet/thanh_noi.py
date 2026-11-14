"""Thanh nối hai bảng gá đặt sát nhau: 32 x 16 x 3, 8 lỗ theo lưới."""
from cadgen import step, stl

from lib.chuan import D_M3, T_TAM, hop, to, tru


@step(out="../../STEP/chi_tiet/thanh_noi.step")
@stl(out="../../STL/thanh_noi.stl")
def thanh_noi():
    s = hop(32.0, 16.0, T_TAM)
    for x in (-12.0, -4.0, 4.0, 12.0):
        for y in (-4.0, 4.0):
            s -= tru(D_M3, T_TAM + 2, x, y, -1)
    return to(s, "thanh_noi", "in3d2")


if __name__ == "__main__":
    thanh_noi()
