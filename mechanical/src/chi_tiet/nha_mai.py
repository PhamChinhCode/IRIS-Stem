"""K3 – mái dốc một chiều 256 x 176 x 3, hai vùng lỗ gá cảm biến mưa và ánh sáng."""
from cadgen import step

from lib.chuan import T_TAM, tam_luoi, to
from lib.kt import MAI_L, MAI_W


@step(out="../../STEP/chi_tiet/nha_mai.step")
def nha_mai():
    vung = lambda u, v: not (abs(abs(u) - 64) < 30 and abs(v) < 34)
    return to(tam_luoi(MAI_L, MAI_W, T_TAM, r=3.0, bo_lo=vung), "nha_mai", "do")


if __name__ == "__main__":
    nha_mai()
