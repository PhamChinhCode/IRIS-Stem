"""K3 – vách trước 128 x 96 x 3 có ô cửa 40 x 72 và vùng gá RFID."""
from cadgen import step

from lib.chuan import T_TAM, hop, ngoai_khoet, tam_luoi, to
from lib.kt import CUA, MONG, MONG_TRUOC, TRUOC_H, TRUOC_L


@step(out="../../STEP/chi_tiet/nha_vach_truoc.step")
def nha_vach_truoc():
    s = tam_luoi(TRUOC_L, TRUOC_H, T_TAM, r=1.0, khoet=[CUA], bo_lo=ngoai_khoet(khoet=[CUA]))
    for u in MONG_TRUOC:
        s += hop(MONG, T_TAM + 0.5, T_TAM, u, -TRUOC_H / 2 - T_TAM / 2 + 0.25)
    return to(s, "nha_vach_truoc", "laser")


if __name__ == "__main__":
    nha_vach_truoc()
