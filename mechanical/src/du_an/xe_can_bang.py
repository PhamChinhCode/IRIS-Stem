"""Dự án 21–22: xe cân bằng hai bánh. Cùng khung K2 dựng đứng: bỏ mắt trâu và S2, pin C2 chuyển sang mặt sau tấm đế."""
from cadgen import build123d as bd
from cadgen import step

from lib.chuan import cum, dat, hop, to
from lib.mach import cum_gan
from lib.mua_san import BANH_D
from lib.xe import X_TRUC, Z_TRUC, khung_xe


@step(out="../../STEP/du_an/xe_can_bang.step")
def xe_can_bang():
    de, tren, p = khung_xe()
    p += de.gan(*cum_gan("C2"), 40.0, 0.0, rz=90, duoi=True, ten="C2")
    p += tren.gan(*cum_gan("S3"), 8.0, 0.0, ten="S3")
    p += tren.gan(*cum_gan("O3"), 48.0, 0.0, ten="O3")
    dung = bd.Pos(0, 0, BANH_D / 2) * bd.Rot(0, -90, 0) * bd.Pos(-X_TRUC, 0, -Z_TRUC)
    p = dat(dung, p)
    p.append(to(hop(240.0, 240.0, 1.0, 0, 0, -1.0), "mat_san", "trang"))
    return cum("xe_can_bang", p)


if __name__ == "__main__":
    xe_can_bang()
