"""Ke góc 90 độ: mặt ngang 40 x 36 (lỗ 24 x 24), mặt đứng 40 x 39 áp vào tường."""
from cadgen import step, stl

from lib.chuan import D_M3, T_TAM, hop, to, tru, tru_y
from lib.kt import KE_LO


@step(out="../../STEP/chi_tiet/ke_goc.step")
@stl(out="../../STL/ke_goc.stl")
def ke_goc():
    s = hop(40.0, 36.0, T_TAM, y=18.0) + hop(40.0, T_TAM, 39.0, y=-T_TAM / 2, z=-36.0)
    for (x, y) in KE_LO:
        s -= tru(D_M3, T_TAM + 2, x, y, -1)
    for x in (-12.0, 12.0):
        for z in (-8.0, -32.0):
            s -= tru_y(D_M3, T_TAM + 2, x, -T_TAM - 1, z)
    return to(s, "ke_goc", "in3d2")


if __name__ == "__main__":
    ke_goc()
