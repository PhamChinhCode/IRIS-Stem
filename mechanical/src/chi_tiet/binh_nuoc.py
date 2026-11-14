"""Bình nước 56 x 56 x 60 cho bơm mini, thành 2,4 mm, 4 lỗ M3 cách 40 x 40."""
from cadgen import step, stl

from lib.chuan import D_M3, hop, to, tru


@step(out="../../STEP/chi_tiet/binh_nuoc.step")
@stl(out="../../STL/binh_nuoc.stl")
def binh_nuoc():
    s = hop(56.0, 56.0, 60.0) - hop(51.2, 51.2, 60.0, z=3.0)
    for sx in (-20.0, 20.0):
        for sy in (-20.0, 20.0):
            s -= tru(D_M3, 5.0, sx, sy, -1)
    return to(s, "binh_nuoc", "in3d2")


if __name__ == "__main__":
    binh_nuoc()
