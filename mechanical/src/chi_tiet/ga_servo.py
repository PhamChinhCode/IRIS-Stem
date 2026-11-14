"""Gá servo SG90/MG90S đứng: đế 34 x 32, 4 lỗ M3 cách 24 x 24, hai trụ đỡ tai servo."""
from cadgen import step, stl

from lib.chuan import D_M3, T_TAM, hop, to, tru
from lib.kt import GS_L, GS_LO, GS_W
from lib.mua_san import SG_TAI_LO, SG_TAI_Z


@step(out="../../STEP/chi_tiet/ga_servo.step")
@stl(out="../../STL/ga_servo.stl")
def ga_servo():
    s = hop(GS_L, GS_W, T_TAM)
    for (x, y) in GS_LO:
        s -= tru(D_M3, T_TAM + 2, x, y, -1)
    for sx in (-1, 1):
        s += hop(5.6, 12.0, SG_TAI_Z, sx * 14.2, 0, T_TAM)
        s -= tru(1.8, 9.0, sx * SG_TAI_LO / 2, 0, T_TAM + SG_TAI_Z - 8.0)
    return to(s, "ga_servo", "in3d2")


if __name__ == "__main__":
    ga_servo()
