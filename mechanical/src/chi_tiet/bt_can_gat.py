"""Cần gạt phân loại gắn lên cần servo: moay-ơ Ø14 và lá gạt 50 x 3 x 14."""
from cadgen import step, stl

from lib.chuan import T_TAM, hop, to, tru


@step(out="../../STEP/chi_tiet/bt_can_gat.step")
@stl(out="../../STL/bt_can_gat.stl")
def bt_can_gat():
    s = tru(14.0, T_TAM) + hop(50.0, T_TAM, 14.0, x=27.0)
    s -= tru(2.5, T_TAM + 2, 0, 0, -1)
    s -= tru(2.0, T_TAM + 2, 8.0, 0, -1)
    return to(s, "bt_can_gat", "do")


if __name__ == "__main__":
    bt_can_gat()
