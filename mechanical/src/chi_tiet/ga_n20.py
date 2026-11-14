"""K1 – gá kẹp hộp số N20: đế 32 x 10, 2 lỗ M3 cách 24, tâm trục cao 7 mm. Trục động cơ dọc Y."""
from cadgen import step, stl

from lib.chuan import D_M3, hop, to, tru
from lib.kt import N20_LO, N20_TAM
from lib.mua_san import N20_H, N20_W


@step(out="../../STEP/chi_tiet/ga_n20.step")
@stl(out="../../STL/ga_n20.stl")
def ga_n20():
    s = hop(32.0, 10.0, 2.0) + hop(18.0, 10.0, 14.0)
    s -= hop(N20_W + 0.3, 12.0, N20_H + 0.3, 0, 0, N20_TAM - (N20_H + 0.3) / 2)
    for (x, y) in N20_LO:
        s -= tru(D_M3, 4.0, x, y, -1)
    return to(s, "ga_n20", "in3d2")


if __name__ == "__main__":
    ga_n20()
