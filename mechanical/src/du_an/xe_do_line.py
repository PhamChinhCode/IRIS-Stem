"""Dự án 11–16: xe hai bánh vi sai. Cấu hình đầy đủ: dò line S2, siêu âm trên servo, OLED, thu hồng ngoại."""
from cadgen import build123d as bd
from cadgen import step

from chi_tiet.de_mat_trau import de_mat_trau
from chi_tiet.ga_servo import ga_servo
from chi_tiet.ga_sieu_am import ga_sieu_am
from lib.chuan import T_TAM, cum, dat, hop, khung, to
from lib.kt import GS_LO, MT_H, MT_LO
from lib.mach import cum_gan, lo_ga, module
from lib.mua_san import SG_DINH, SG_TRUC_X, mat_trau, sg90, tru_do
from lib.xe import Z_DAT, khung_xe


@step(out="../../STEP/du_an/xe_do_line.step")
def xe_do_line():
    de, tren, p = khung_xe()
    p += de.gan(*cum_gan("C2"), 32.0, 0.0, rz=90, ten="C2")
    # bánh mắt trâu phía trước, dưới tấm đế
    p += de.gan([de_mat_trau()], MT_LO, 40.0, 0.0, duoi=True, ten="đệm mắt trâu")
    p += dat(bd.Pos(40.0, 0, -MT_H), mat_trau())
    # S2 treo dưới mũi xe bằng trụ 12 mm, hàng mắt đọc hướng về phía trước
    lo_s2 = [(68.0 - y, x) for (x, y) in lo_ga("S2")]
    de._khop(lo_s2, "S2")
    p += [tru_do(12.0, x, y, -12.0) for (x, y) in lo_s2]
    p.append(bd.Pos(68.0, 0, -13.6) * bd.Rot(0, 0, 90) * module("S2"))
    # tầng trên: OLED, thu hồng ngoại, servo quay cảm biến siêu âm
    p += tren.gan(*cum_gan("O3"), 8.0, -24.0, ten="O3")
    p += tren.gan(*cum_gan("I12"), 12.0, 24.0, ten="I12")
    dau = [ga_sieu_am(), khung((13.0, 0, 13.5), (0, 1, 0), (1, 0, 0)) * module("I11")]
    servo = [ga_servo()] + dat(bd.Pos(0, 0, T_TAM), sg90()) \
        + dat(bd.Pos(SG_TRUC_X, 0, T_TAM + SG_DINH), dau)
    p += tren.gan(servo, GS_LO, 56.0, 0.0, ten="gá servo")
    # sa bàn line (K4)
    p.append(to(hop(360.0, 260.0, 1.0, 20.0, 0, Z_DAT - 1.0), "sa_ban", "trang"))
    p.append(to(hop(360.0, 18.0, 0.2, 20.0, 0, Z_DAT), "vach_line", "den"))
    return cum("xe_do_line", p)


if __name__ == "__main__":
    xe_do_line()
