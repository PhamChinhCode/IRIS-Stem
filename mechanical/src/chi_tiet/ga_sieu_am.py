"""Gá cảm biến siêu âm lên cần servo: đế 26 x 24 bắt vào cần, mặt đứng 64 x 27 giữ bo I11."""
from cadgen import step, stl

from lib.chuan import D_M3, T_TAM, hop, to, tru, tru_x


@step(out="../../STEP/chi_tiet/ga_sieu_am.step")
@stl(out="../../STL/ga_sieu_am.stl")
def ga_sieu_am():
    s = hop(26.0, 24.0, T_TAM) + hop(T_TAM, 64.0, 27.0, x=11.5)
    s -= tru(2.5, T_TAM + 2, 0, 0, -1)
    s -= tru(2.0, T_TAM + 2, -8.0, 0, -1)
    s -= hop(T_TAM + 2, 12.0, 9.0, 11.5, 0, 9.0)
    for y in (-28.0, 28.0):
        for z in (5.5, 21.5):
            s -= tru_x(D_M3, T_TAM + 2, 9.0, y, z)
    return to(s, "ga_sieu_am", "in3d2")


if __name__ == "__main__":
    ga_sieu_am()
