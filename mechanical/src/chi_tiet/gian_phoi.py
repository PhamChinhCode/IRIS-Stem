"""Giàn phơi chữ T gắn lên cần servo: tay 110 mm, thanh ngang 90 mm."""
from cadgen import step, stl

from lib.chuan import T_TAM, hop, to, tru


@step(out="../../STEP/chi_tiet/gian_phoi.step")
@stl(out="../../STL/gian_phoi.stl")
def gian_phoi():
    s = tru(14.0, T_TAM) + hop(110.0, 10.0, T_TAM, x=55.0) + hop(6.0, 90.0, T_TAM, x=107.0)
    s -= tru(2.5, T_TAM + 2, 0, 0, -1)
    s -= tru(2.0, T_TAM + 2, 8.0, 0, -1)
    return to(s, "gian_phoi", "in3d2")


if __name__ == "__main__":
    gian_phoi()
