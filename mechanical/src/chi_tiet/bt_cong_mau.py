"""Cổng đỡ cảm biến màu bắc qua băng tải: hai chân cách 62, dầm 24 x 66 ở cao 66 mm, 4 lỗ gá bo I14."""
from cadgen import step, stl

from lib.chuan import D_M3, T_TAM, hop, to, tru


@step(out="../../STEP/chi_tiet/bt_cong_mau.step")
@stl(out="../../STL/bt_cong_mau.stl")
def bt_cong_mau():
    s = hop(24.0, 66.0, T_TAM, z=66.0)
    for sy in (-1, 1):
        s += hop(16.0, 12.0, T_TAM, y=sy * 35.0) + hop(16.0, 4.0, 66.0, y=sy * 31.0)
        for x in (-4.0, 4.0):
            s -= tru(D_M3, T_TAM + 2, x, sy * 36.0, -1)
    for x in (-8.0, 8.0):
        for y in (-12.0, 12.0):
            s -= tru(D_M3, T_TAM + 2, x, y, 65.0)
    return to(s, "bt_cong_mau", "in3d2")


if __name__ == "__main__":
    bt_cong_mau()
