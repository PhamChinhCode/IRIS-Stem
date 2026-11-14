"""Mâm xoay cánh tay: đĩa Ø56 x 3 bắt lên cần servo đế, vách đứng có ô lắp servo vai (trục dọc Y, cao 25 mm)."""
from cadgen import step, stl

from lib.chuan import T_TAM, hop, to, tru, tru_y
from lib.kt import SG_O, SG_VACH, TAY_VAI_Y, TAY_VAI_Z
from lib.mua_san import SG_TAI_LO, SG_TRUC_X


@step(out="../../STEP/chi_tiet/tay_mam_xoay.step")
@stl(out="../../STL/tay_mam_xoay.stl")
def tay_mam_xoay():
    y_vach = TAY_VAI_Y - SG_VACH - T_TAM            # mặt sau vách
    s = tru(56.0, T_TAM) + hop(41.0, T_TAM, TAY_VAI_Z + 10.3 - T_TAM, x=-5.5, y=y_vach + T_TAM / 2, z=T_TAM)
    for x in (-24.5, 13.5):
        s += hop(T_TAM, 13.0, 12.0, x, y_vach + T_TAM + 6.5, T_TAM)
    s -= hop(SG_O[1] - SG_O[0], T_TAM + 2, 2 * SG_O[2], (SG_O[0] + SG_O[1]) / 2, y_vach + T_TAM / 2, TAY_VAI_Z - SG_O[2])
    for sx in (-1, 1):
        s -= tru_y(1.8, T_TAM + 2, -SG_TRUC_X + sx * SG_TAI_LO / 2, y_vach - 1, TAY_VAI_Z)
    s -= tru(2.5, T_TAM + 2, 0, 0, -1)
    s -= tru(2.0, T_TAM + 2, 8.0, 0, -1)
    return to(s, "tay_mam_xoay", "in3d")


if __name__ == "__main__":
    tay_mam_xoay()
