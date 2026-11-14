"""Dự án 24: băng tải phân loại màu. Bảng A gá băng tải, cổng cảm biến màu và cần gạt; bảng E gá mạch."""
from cadgen import build123d as bd
from cadgen import step

from chi_tiet.bang_ga import bang_ga
from chi_tiet.bt_can_gat import bt_can_gat
from chi_tiet.bt_con_lan import bt_con_lan
from chi_tiet.bt_cong_mau import bt_cong_mau
from chi_tiet.bt_khay import bt_khay
from chi_tiet.bt_thanh_ben import bt_thanh_ben
from chi_tiet.ga_n20 import ga_n20
from chi_tiet.ga_servo import ga_servo
from chi_tiet.thanh_noi import thanh_noi
from lib.chuan import G, T_TAM, Tam, chan_de, cum, dat, hop, to
from lib.kt import BG_L, BG_W, BT_TRUC_Z, BT_X, GS_LO, N20_LO, N20_TAM
from lib.mach import cum_gan
from lib.mua_san import SG_DINH, SG_TRUC_X, n20, sg90, tru_do

GOC_GAT = 50.0
H_TRU_DC = BT_TRUC_Z - N20_TAM       # trụ nâng gá N20 cho đồng trục với con lăn


def _day_bang_tai():
    with bd.BuildSketch() as sk:
        bd.SlotCenterToCenter(2 * BT_X, 22.0)
        bd.SlotCenterToCenter(2 * BT_X, 20.0, mode=bd.Mode.SUBTRACT)
    return bd.Rot(90, 0, 0) * bd.extrude(sk.sketch, 20.0, both=True)


@step(out="../../STEP/du_an/bang_tai.step")
def bang_tai():
    a = Tam("bang_ga_bang_tai", bang_ga(), BG_L, BG_W, T_TAM)
    e = Tam("bang_ga_mach", bang_ga(), BG_L, BG_W, T_TAM, o=(-BG_L, 0, 0))
    p = [a.part, e.part] + chan_de(BG_L, BG_W) + chan_de(BG_L, BG_W, ox=-BG_L)
    for y in (-32.0, 32.0):
        p.append(bd.Pos(-BG_L / 2, y, -T_TAM) * thanh_noi())
    z0 = T_TAM
    zt = z0 + BT_TRUC_Z
    a._khop([(-76.0 + G * i, s * 20.0) for i in range(20) for s in (-1, 1)], "thanh bên")
    p += [bd.Pos(0, 0, z0) * bt_thanh_ben(), bd.Pos(0, 0, z0) * bd.Rot(0, 0, 180) * bt_thanh_ben()]
    p += [bd.Pos(-BT_X, 0, zt) * bt_con_lan(), bd.Pos(BT_X, 0, zt) * bd.Rot(0, 0, 180) * bt_con_lan()]
    p.append(to(bd.Pos(0, 0, zt) * _day_bang_tai(), "day_bang_tai", "den"))
    # động cơ N20 kéo con lăn chủ động, gá trên trụ 15 mm
    lo_dc = [(-BT_X + x, 36.0) for (x, _) in N20_LO]
    a._khop(lo_dc, "gá N20")
    p += [tru_do(H_TRU_DC, x, y, z0) for (x, y) in lo_dc]
    p.append(bd.Pos(-BT_X, 36.0, z0 + H_TRU_DC) * ga_n20())
    p += dat(bd.Pos(-BT_X, 31.0, zt) * bd.Rot(0, 0, 180), n20())
    # cổng cảm biến màu
    a._khop([(x, y) for x in (-4.0, 4.0) for y in (-36.0, 36.0)], "cổng màu")
    p.append(bd.Pos(0, 0, z0) * bt_cong_mau())
    p += dat(bd.Pos(0, 0, z0 + 66.0) * bd.Rot(180, 0, 0), cum_gan("I14")[0])
    # servo gạt
    p += a.gan([ga_servo()] + dat(bd.Pos(0, 0, T_TAM), sg90(0)), GS_LO, 32, -48, rz=90, ten="servo gạt")
    p.append(bd.Pos(32, -48 + SG_TRUC_X, z0 + T_TAM + SG_DINH) * bd.Rot(0, 0, GOC_GAT) * bt_can_gat())
    p += a.gan(*cum_gan("O3"), -40, -48, rz=90, ten="O3")
    # khay hứng và vật mẫu
    p.append(bd.Pos(52, 52, z0) * bt_khay())
    p.append(bd.Pos(106, 0, -6.0) * bt_khay())
    p.append(to(hop(16.0, 16.0, 16.0, -24, 0, zt + 11.0), "vat_mau_do", "do"))
    p.append(to(hop(16.0, 16.0, 16.0, 30, 0, zt + 11.0), "vat_mau_xanh", "xanh"))
    # bảng mạch
    p += e.gan(*cum_gan("C1"), 0, 32, ten="C1")
    p += e.gan(*cum_gan("C2"), 16, -40, ten="C2")
    p += e.gan(*cum_gan("S1"), -56, -40, ten="S1")
    return cum("bang_tai", p)


if __name__ == "__main__":
    bang_tai()
