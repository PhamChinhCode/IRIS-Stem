"""K3 – tường sau 234 x 135 x 3, lưới 8 mm, 3 mộng đáy."""
from cadgen import step

from lib.chuan import T_TAM, hop, tam_luoi, to
from lib.kt import MONG, MONG_SAU, SAU_H, SAU_L


@step(out="../../STEP/chi_tiet/nha_tuong_sau.step")
def nha_tuong_sau():
    s = tam_luoi(SAU_L, SAU_H, T_TAM, r=1.0)
    for x in MONG_SAU:
        s += hop(MONG, T_TAM + 0.5, T_TAM, x, -SAU_H / 2 - T_TAM / 2 + 0.25)
    return to(s, "nha_tuong_sau", "laser")


if __name__ == "__main__":
    nha_tuong_sau()
