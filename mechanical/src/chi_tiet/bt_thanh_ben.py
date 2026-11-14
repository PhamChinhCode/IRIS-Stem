"""Thanh bên băng tải dài 160: vách 3 x 30 có 2 lỗ Ø8,4 đỡ trục con lăn, chân đế quay vào trong với 20 lỗ lưới. Bên kia dùng cùng chi tiết xoay 180 độ."""
from cadgen import step, stl

from lib.chuan import D_M3, G, T_TAM, hop, to, tru, tru_y
from lib.kt import BT_L, BT_TRUC_Z, BT_X


@step(out="../../STEP/chi_tiet/bt_thanh_ben.step")
@stl(out="../../STL/bt_thanh_ben.stl")
def bt_thanh_ben():
    s = hop(BT_L, T_TAM, 30.0, y=25.5) + hop(BT_L, 12.0, T_TAM, y=18.0)
    for i in range(20):
        s -= tru(D_M3, T_TAM + 2, -76.0 + G * i, 20.0, -1)
    for x in (-BT_X, BT_X):
        s -= tru_y(8.4, T_TAM + 2, x, 23.0, BT_TRUC_Z)
    return to(s, "bt_thanh_ben", "in3d")


if __name__ == "__main__":
    bt_thanh_ben()
