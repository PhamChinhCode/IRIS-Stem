"""K3 – cánh cửa gắn lên cần servo: moay-ơ, tay đòn 14 mm và cánh 40 x 67 x 3. Gốc ở trục servo, z = 0 là mặt cần."""
from cadgen import step, stl

from lib.chuan import T_TAM, hop, to, tru


@step(out="../../STEP/chi_tiet/nha_canh_cua.step")
@stl(out="../../STL/nha_canh_cua.stl")
def nha_canh_cua():
    s = tru(14.0, T_TAM) + hop(8.0, 15.0, T_TAM, y=-7.5) + hop(40.0, T_TAM, 67.0, x=19.0, y=-13.65, z=-30.0)
    s -= tru(2.5, T_TAM + 2, 0, 0, -1)
    s -= tru(2.0, T_TAM + 2, 0, -8.0, -1)
    return to(s, "nha_canh_cua", "nau")


if __name__ == "__main__":
    nha_canh_cua()
