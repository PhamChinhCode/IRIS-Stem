"""K3 – sàn nhà 240 x 160 x 3: lưới 8 mm, rãnh mộng cho tường sau, hai tường bên và vách trước."""
from cadgen import step

from lib.chuan import T_TAM, tam_luoi, to
from lib.kt import MONG, MONG_BEN, MONG_SAU, MONG_TRUOC, NHA_L, NHA_W, TRUOC_X


@step(out="../../STEP/chi_tiet/nha_san.step")
def nha_san():
    ranh = [(x, NHA_W / 2 - 1.5, MONG + 0.2, T_TAM + 0.2) for x in MONG_SAU]
    ranh += [(sx * (NHA_L / 2 - 1.5), y, T_TAM + 0.2, MONG + 0.2) for sx in (-1, 1) for y in MONG_BEN]
    ranh += [(TRUOC_X + u, -NHA_W / 2 + 1.5, MONG + 0.2, T_TAM + 0.2) for u in MONG_TRUOC]
    vien = lambda x, y: abs(x) > NHA_L / 2 - 8 or abs(y) > NHA_W / 2 - 8
    return to(tam_luoi(NHA_L, NHA_W, T_TAM, r=3.0, khoet=ranh, bo_lo=vien), "nha_san", "laser")


if __name__ == "__main__":
    nha_san()
