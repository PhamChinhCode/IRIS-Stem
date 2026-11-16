"""Dự án 23: cánh tay robot 4 servo MG90S (đế xoay, vai, khuỷu, kẹp). Bảng A gá mạch, bảng B gá cánh tay và pin."""
from cadgen import build123d as bd
from cadgen import step

from chi_tiet.bang_ga import bang_ga
from chi_tiet.tay_de import tay_de
from chi_tiet.tay_kep_ngon import tay_kep_ngon
from chi_tiet.tay_khau_1 import tay_khau_1
from chi_tiet.tay_khau_2 import tay_khau_2
from chi_tiet.tay_mam_xoay import tay_mam_xoay
from chi_tiet.thanh_noi import thanh_noi
from lib.chuan import T_TAM, Tam, chan_de, cum, dat, khung
from lib.kt import BG_L, BG_W, GS_LO, TAY_L1, TAY_L2, TAY_VAI_Y, TAY_VAI_Z
from lib.mach import cum_gan
from lib.mua_san import MG_DINH, MG_TRUC_X, MG_VACH, mg90s, mg90s_truc

GOC_DE, GOC_VAI, GOC_KHUYU, GOC_KEP = 180.0, 70.0, -100.0, 25.0   # tư thế minh hoạ


def _servo_ngang(x, y):
    """Servo nằm ngang, trục dọc +Y, mặt cần tại (x, y, 0) của khung khâu."""
    return dat(khung((x, y, 0), (1, 0, 0), (0, 1, 0)), mg90s_truc())


@step(out="../../STEP/du_an/canh_tay_robot.step")
def canh_tay_robot():
    a = Tam("bang_ga_mach", bang_ga(), BG_L, BG_W, T_TAM)
    b = Tam("bang_ga_tay", bang_ga(), BG_L, BG_W, T_TAM, o=(-BG_L, 0, 0))
    p = [a.part, b.part] + chan_de(BG_L, BG_W) + chan_de(BG_L, BG_W, ox=-BG_L)
    for y in (-32.0, 32.0):
        p.append(bd.Pos(-BG_L / 2, y, -T_TAM) * thanh_noi())
    p += a.gan(*cum_gan("C1"), 32, 32, ten="C1")
    p += a.gan(*cum_gan("O7"), 48, -32, rz=90, ten="O7")
    p += a.gan(*cum_gan("I3"), -56, -40, ten="I3")
    p += b.gan(*cum_gan("C2"), 0, -40, ten="C2")
    p += b.gan([tay_de()] + dat(bd.Pos(0, 0, T_TAM), mg90s(GOC_DE)), GS_LO, 0, 32, ten="servo đế")

    y_khau = T_TAM + MG_VACH          # mặt cần servo ở đầu xa của mỗi khâu
    vai = bd.Pos(0, TAY_VAI_Y, TAY_VAI_Z) * bd.Rot(0, -GOC_VAI, 0)
    khuyu = vai * bd.Pos(TAY_L1, y_khau, 0) * bd.Rot(0, -GOC_KHUYU, 0)
    kep = khuyu * bd.Pos(TAY_L2, y_khau, 0) * bd.Rot(0, -GOC_KEP, 0)
    tay = [tay_mam_xoay()] + dat(bd.Pos(0, TAY_VAI_Y, TAY_VAI_Z), _servo_ngang(0, 0))
    tay += [vai * tay_khau_1()] + dat(vai, _servo_ngang(TAY_L1, y_khau))
    tay += [khuyu * tay_khau_2()] + dat(khuyu, _servo_ngang(TAY_L2, y_khau))
    tay.append(kep * tay_kep_ngon())
    mam = bd.Pos(-BG_L + MG_TRUC_X, 32, 2 * T_TAM + MG_DINH) * bd.Rot(0, 0, GOC_DE)
    p += dat(mam, tay)
    return cum("canh_tay_robot", p)


if __name__ == "__main__":
    canh_tay_robot()
