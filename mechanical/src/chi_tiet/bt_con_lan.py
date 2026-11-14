"""Con lăn băng tải Ø20 x 46, hai ngõng Ø8; ngõng dài có lỗ Ø3,2 nhận trục N20. Trục dọc Y, tâm ở gốc."""
from cadgen import step, stl

from lib.chuan import to, tru_y


@step(out="../../STEP/chi_tiet/bt_con_lan.step")
@stl(out="../../STL/bt_con_lan.stl")
def bt_con_lan():
    s = tru_y(20.0, 46.0, y=-23.0) + tru_y(8.0, 6.0, y=23.0) + tru_y(8.0, 4.5, y=-27.5)
    s -= tru_y(3.2, 9.0, y=21.0)
    return to(s, "bt_con_lan", "in3d2")


if __name__ == "__main__":
    bt_con_lan()
