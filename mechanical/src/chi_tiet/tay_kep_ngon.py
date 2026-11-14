"""Ngón kẹp động gắn lên cần servo kẹp: thanh 62 x 8 x 3 và má kẹp 36 x 27."""
from cadgen import step, stl

from lib.chuan import T_TAM, hop, to, tru_y


@step(out="../../STEP/chi_tiet/tay_kep_ngon.step")
@stl(out="../../STL/tay_kep_ngon.stl")
def tay_kep_ngon():
    s = hop(62.0, T_TAM, 8.0, x=25.0, y=T_TAM / 2, z=-4.0) + hop(36.0, 27.1, T_TAM, x=38.0, y=-10.55, z=-4.0)
    s -= tru_y(2.5, T_TAM + 2, 0, -1, 0)
    s -= tru_y(2.0, T_TAM + 2, 8.0, -1, 0)
    return to(s, "tay_kep_ngon", "in3d2")


if __name__ == "__main__":
    tay_kep_ngon()
