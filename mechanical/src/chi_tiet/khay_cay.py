"""Khay trồng cây 96 x 64 x 44, thành 2,4 mm, đáy 3 mm, 4 lỗ M3 cách 80 x 48."""
from cadgen import step, stl

from lib.chuan import D_M3, hop, to, tru


@step(out="../../STEP/chi_tiet/khay_cay.step")
@stl(out="../../STL/khay_cay.stl")
def khay_cay():
    s = hop(96.0, 64.0, 44.0) - hop(91.2, 59.2, 44.0, z=3.0)
    for sx in (-40.0, 40.0):
        for sy in (-24.0, 24.0):
            s -= tru(D_M3, 5.0, sx, sy, -1)
    return to(s, "khay_cay", "in3d")


if __name__ == "__main__":
    khay_cay()
