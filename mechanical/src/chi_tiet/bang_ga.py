"""Bảng gá thực hành 160 x 128 x 3, lưới 20 x 16 lỗ."""
from cadgen import step, stl

from lib.chuan import T_TAM, tam_luoi, to
from lib.kt import BG_L, BG_W


@step(out="../../STEP/chi_tiet/bang_ga.step")
@stl(out="../../STL/bang_ga.stl")
def bang_ga():
    return to(tam_luoi(BG_L, BG_W, T_TAM, r=6.0), "bang_ga", "in3d")


if __name__ == "__main__":
    bang_ga()
