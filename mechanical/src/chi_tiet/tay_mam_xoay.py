"""Mâm xoay cánh tay: đĩa Ø56 x 3 bắt lên cần servo đế, vách đứng có ô lắp servo vai MG90S (trục dọc Y, cao 25 mm)."""
from cadgen import step, stl

from lib.chuan import T_TAM, hop, to, tru
from lib.kt import TAY_VAI_Y, TAY_VAI_Z
from lib.mua_san import MG_VACH
from lib.tay import o_servo


@step(out="../../STEP/chi_tiet/tay_mam_xoay.step")
@stl(out="../../STL/tay_mam_xoay.stl")
def tay_mam_xoay():
    y_vach = TAY_VAI_Y - MG_VACH - T_TAM            # mặt sau vách; tai servo tì lên mặt trước
    s = tru(56.0, T_TAM) + hop(42.0, T_TAM, TAY_VAI_Z + 10.0 - T_TAM, x=-5.0, y=y_vach + T_TAM / 2, z=T_TAM)
    for x in (-24.5, 14.5):                         # hai gân chống ở mặt sau vách, ngoài vùng thân servo
        s += hop(T_TAM, 10.0, 14.0, x, y_vach - 5.0, T_TAM)
    s -= o_servo(0.0, y_vach, TAY_VAI_Z)
    s -= tru(2.5, T_TAM + 2, 0, 0, -1)
    for x in (8.0, 14.0):
        s -= tru(2.0, T_TAM + 2, x, 0, -1)
    return to(s, "tay_mam_xoay", "in3d")


if __name__ == "__main__":
    tay_mam_xoay()
