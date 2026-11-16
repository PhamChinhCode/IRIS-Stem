"""Khâu 1 cánh tay (bắp tay): dài 80 mm giữa trục vai và trục khuỷu, đầu xa có ô lắp servo khuỷu MG90S.

Gốc ở trục vai, trục dọc Y; tấm dày 3 mm nằm từ y = 0 đến y = 3, hai gân dọc 3 x 4 ở mép trên và mép dưới.
"""
from cadgen import step, stl

from lib.chuan import T_TAM, hop, to
from lib.kt import TAY_L1
from lib.tay import lo_can, o_servo


@step(out="../../STEP/chi_tiet/tay_khau_1.step")
@stl(out="../../STL/tay_khau_1.stl")
def tay_khau_1():
    L = TAY_L1
    s = hop(L + 22.0, T_TAM, 22.0, x=(L + 2.0) / 2, y=T_TAM / 2, z=-11.0)
    for z in (-11.0, 8.0):
        s += hop(L - 38.0, 4.0, 3.0, x=L / 2 - 4.0, y=T_TAM + 2.0, z=z)
    s -= o_servo(L)
    s -= lo_can()
    return to(s, "tay_khau_1", "in3d2")


if __name__ == "__main__":
    tay_khau_1()
