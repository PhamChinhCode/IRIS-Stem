"""Dự án 18: vườn thông minh. Bảng A gá mạch, bảng B gá khay cây và bình nước; hai bảng nối bằng thanh nối."""
from cadgen import build123d as bd
from cadgen import step

from chi_tiet.bang_ga import bang_ga
from chi_tiet.binh_nuoc import binh_nuoc
from chi_tiet.khay_cay import khay_cay
from chi_tiet.thanh_noi import thanh_noi
from lib.chuan import T_TAM, Tam, chan_de, cum, dat, hop, khung, to
from lib.kt import BG_L, BG_W
from lib.mach import cum_gan, module
from lib.mua_san import bom_mini

MACH = {"C1": (-32, 32), "O3": (40, 40), "I6": (68, 48), "O4": (-64, -40), "O5": (-28, -48)}
KHAY_LO = [(sx * 40.0, sy * 24.0) for sx in (-1, 1) for sy in (-1, 1)]
BINH_LO = [(sx * 20.0, sy * 20.0) for sx in (-1, 1) for sy in (-1, 1)]


@step(out="../../STEP/du_an/vuon_thong_minh.step")
def vuon_thong_minh():
    a = Tam("bang_ga_mach", bang_ga(), BG_L, BG_W, T_TAM)
    b = Tam("bang_ga_vuon", bang_ga(), BG_L, BG_W, T_TAM, o=(BG_L, 0, 0))
    p = [a.part, b.part] + chan_de(BG_L, BG_W) + chan_de(BG_L, BG_W, ox=BG_L)
    for y in (-32.0, 32.0):
        p.append(bd.Pos(BG_L / 2, y, -T_TAM) * thanh_noi())
    for ma, (u, v) in MACH.items():
        p += a.gan(*cum_gan(ma), u, v, ten=ma)
    dat_trong = to(hop(91.0, 59.0, 34.0, z=3.0), "dat_trong", "nau")
    que = khung((0, 0, 3.0 + 8.0 + 48.0), (1, 0, 0), (0, -1, 0)) * module("I9")
    p += b.gan([khay_cay(), dat_trong, que], KHAY_LO, -28, 28, ten="khay cây")
    nuoc = to(hop(51.0, 51.0, 40.0, z=3.0), "nuoc", "nuoc")
    p += b.gan([binh_nuoc(), nuoc] + dat(bd.Pos(0, 0, 3.0), bom_mini()), BINH_LO, 48, -32, ten="bình nước")
    return cum("vuon_thong_minh", p)


if __name__ == "__main__":
    vuon_thong_minh()
