"""K3 – tường trái: hình thang 160 x (96 đến 136) x 3, cửa sổ 40 x 40. Trục u: trước (-80) ra sau (+80)."""
from cadgen import step

from lib.chuan import T_TAM, hop, ngoai_khoet, tam_luoi, to
from lib.kt import MONG, MONG_BEN, NHA_H_SAU, NHA_H_TRUOC, NHA_W

H = NHA_H_SAU
KHOET = [(24.0, -4.0, 40.0, 40.0)]     # cửa sổ
TRON = []


@step(out="../../STEP/chi_tiet/nha_tuong_trai.step")
def nha_tuong_trai():
    dau = 1
    dinh = lambda u: (NHA_H_SAU + NHA_H_TRUOC) / 2 - H / 2 + dau * (NHA_H_SAU - NHA_H_TRUOC) / NHA_W * u
    bien = [(-NHA_W / 2, -H / 2), (NHA_W / 2, -H / 2), (NHA_W / 2, dinh(NHA_W / 2)), (-NHA_W / 2, dinh(-NHA_W / 2))]
    trong = ngoai_khoet(khoet=KHOET, tron=TRON)
    bo = lambda u, v: v > dinh(u) - 5 or trong(u, v)
    s = tam_luoi(NHA_W, H, T_TAM, khoet=KHOET, tron=TRON, bo_lo=bo, da_giac=bien)
    for u in MONG_BEN:
        s += hop(MONG, T_TAM + 0.5, T_TAM, u, -H / 2 - T_TAM / 2 + 0.25)
    return to(s, "nha_tuong_trai", "laser")


if __name__ == "__main__":
    nha_tuong_trai()
