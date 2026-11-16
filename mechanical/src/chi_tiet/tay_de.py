"""Đế cánh tay: gá servo MG90S đứng. Đế 38 x 32, 4 lỗ M3 cách 24 x 24, hai trụ cao 18,8 đỡ tai servo."""
from cadgen import step, stl

from lib.chuan import D_M3, T_TAM, hop, to
from lib.kt import GS_LO, MG_KHE, TD_L, TD_W
from lib.mua_san import MG_L, MG_LO, MG_TAI_Z, MG_TRUC_X


@step(out="../../STEP/chi_tiet/tay_de.step")
@stl(out="../../STL/tay_de.stl")
def tay_de():
    from lib.chuan import tru
    s = hop(TD_L, TD_W, T_TAM)
    for (x, y) in GS_LO:
        s -= tru(D_M3, T_TAM + 2, x, y, -1)
    for sx, lo, huong in ((-1, MG_LO[0], 1), (1, MG_LO[1], -1)):
        x0 = sx * (MG_L / 2 + 0.3)                      # mép trong trụ, cách thân 0,3
        x1 = sx * TD_L / 2
        s += hop(abs(x1 - x0), 12.0, MG_TAI_Z, (x0 + x1) / 2, 0, T_TAM)
        tam = MG_TRUC_X + lo + huong * (MG_KHE - 1.8) / 2
        s -= hop(MG_KHE, 1.8, 9.0, tam, 0, T_TAM + MG_TAI_Z - 8.0)
    s -= hop(4.0, 5.0, 3.0, MG_L / 2 + 2.0, 0, T_TAM)       # rãnh thoát dây servo ở chân trụ phía trục
    return to(s, "tay_de", "in3d2")


if __name__ == "__main__":
    tay_de()
