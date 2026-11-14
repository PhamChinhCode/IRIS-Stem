"""Dự án 1–4, 17, 19, 20: bảng gá thực hành với bo chủ và các module đặt trên bàn."""
from cadgen import step

from chi_tiet.bang_ga import bang_ga
from lib.chuan import T_TAM, Tam, chan_de, cum
from lib.kt import BG_L, BG_W
from lib.mach import cum_gan

# module: (u, v) trên bảng gá
BO_TRI = {"C1": (-32, 32), "O3": (40, 40), "I6": (68, 48), "I1": (-68, -48), "O1": (-44, -48),
          "I2": (-20, -48), "I5": (4, -48), "O2": (48, -52)}


@step(out="../../STEP/du_an/ban_thuc_hanh.step")
def ban_thuc_hanh():
    bg = Tam("bang_ga", bang_ga(), BG_L, BG_W, T_TAM)
    p = [bg.part] + chan_de(BG_L, BG_W)
    for ma, (u, v) in BO_TRI.items():
        p += bg.gan(*cum_gan(ma), u, v, ten=ma)
    return cum("ban_thuc_hanh", p)


if __name__ == "__main__":
    ban_thuc_hanh()
