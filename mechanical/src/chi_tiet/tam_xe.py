"""K2 – tấm khung xe 160 x 96 x 4, lưới 20 x 12 lỗ, rãnh luồn dây ở giữa."""
from cadgen import step, stl

from lib.chuan import T_XE, ngoai_khoet, tam_luoi, to
from lib.kt import XE_L, XE_W

RANH = [(0.0, 0.0, 32.0, 12.0)]


@step(out="../../STEP/chi_tiet/tam_xe.step")
@stl(out="../../STL/tam_xe.stl")
def tam_xe():
    return to(tam_luoi(XE_L, XE_W, T_XE, r=8.0, khoet=RANH, bo_lo=ngoai_khoet(RANH)), "tam_xe", "in3d")


if __name__ == "__main__":
    tam_xe()
