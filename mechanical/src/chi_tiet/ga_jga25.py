"""K1 – gá chữ L cho JGA25-370: mặt đứng 40 x 32 có lỗ trục Ø7,5 và 2 lỗ M3 cách 17; đế 4 lỗ 32 x 8."""
from cadgen import step, stl

from lib.chuan import D_M3, T_TAM, hop, to, tru, tru_y
from lib.kt import JGA_LO, JGA_TAM


@step(out="../../STEP/chi_tiet/ga_jga25.step")
@stl(out="../../STL/ga_jga25.stl")
def ga_jga25():
    s = hop(40.0, 24.0, T_TAM, y=-15.0) + hop(40.0, T_TAM, 32.0, y=-T_TAM / 2)
    s -= tru_y(7.5, T_TAM + 2, 0, -T_TAM - 1, JGA_TAM)
    for x in (-8.5, 8.5):
        s -= tru_y(3.2, T_TAM + 2, x, -T_TAM - 1, JGA_TAM)
    for (x, y) in JGA_LO:
        s -= tru(D_M3, T_TAM + 2, x, y, -1)
    return to(s, "ga_jga25", "in3d2")


if __name__ == "__main__":
    ga_jga25()
