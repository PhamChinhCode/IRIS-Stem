"""K2 – đệm bánh mắt trâu 32 x 16 x 9,5; 4 lỗ M3 theo lưới 24 x 8."""
from cadgen import step, stl

from lib.chuan import D_M3, hop, to, tru
from lib.kt import MT_H, MT_LO


@step(out="../../STEP/chi_tiet/de_mat_trau.step")
@stl(out="../../STL/de_mat_trau.stl")
def de_mat_trau():
    s = hop(32.0, 16.0, MT_H)
    for (x, y) in MT_LO:
        s -= tru(D_M3, MT_H + 2, x, y, -1)
    for x in (-10.0, 10.0):
        s -= tru(2.0, 6.0, x, 0, -1)
    return to(s, "de_mat_trau", "in3d2")


if __name__ == "__main__":
    de_mat_trau()
