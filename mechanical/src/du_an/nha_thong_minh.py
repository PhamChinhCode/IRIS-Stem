"""Dự án 5–10: mô hình nhà thông minh K3 với cấu hình đầy đủ của dự án 10. Mặt trước để hở để nhìn vào trong."""
import math

from cadgen import build123d as bd
from cadgen import step

from chi_tiet.ga_servo import ga_servo
from chi_tiet.gian_phoi import gian_phoi
from chi_tiet.ke_goc import ke_goc
from chi_tiet.nha_canh_cua import nha_canh_cua
from chi_tiet.nha_mai import nha_mai
from chi_tiet.nha_san import nha_san
from chi_tiet.nha_tuong_phai import nha_tuong_phai
from chi_tiet.nha_tuong_sau import nha_tuong_sau
from chi_tiet.nha_tuong_trai import nha_tuong_trai
from chi_tiet.nha_vach_truoc import nha_vach_truoc
from lib.chuan import T_TAM, Tam, cum, dat, khung
from lib.kt import (GS_LO, MAI_L, MAI_W, NHA_H_SAU, NHA_H_TRUOC, NHA_L, NHA_W, SAU_H, SAU_L,
                    TRUOC_H, TRUOC_L, TRUOC_X)
from lib.mach import cum_gan
from lib.mua_san import SG_DINH, SG_TRUC_X, quat_4010, sg90

GOC_CUA = 70.0          # cửa đang mở
QUAT_LO = [(-16.0, -16.0), (-16.0, 16.0), (16.0, -16.0), (16.0, 16.0)]


def _servo(goc=0.0):
    return [ga_servo()] + dat(bd.Pos(0, 0, T_TAM), sg90(goc))


@step(out="../../STEP/du_an/nha_thong_minh.step")
def nha_thong_minh():
    z0 = T_TAM
    h = NHA_H_SAU
    doc = math.atan((NHA_H_SAU - NHA_H_TRUOC) / NHA_W)
    san = Tam("nha_san", nha_san(), NHA_L, NHA_W, T_TAM, mau="laser")
    sau = Tam("nha_tuong_sau", nha_tuong_sau(), SAU_L, SAU_H, T_TAM, o=(0, NHA_W / 2, z0 + SAU_H / 2),
              x_dir=(1, 0, 0), z_dir=(0, -1, 0), mau="laser")
    trai = Tam("nha_tuong_trai", nha_tuong_trai(), NHA_W, h, T_TAM, o=(-NHA_L / 2, 0, z0 + h / 2),
               x_dir=(0, 1, 0), z_dir=(1, 0, 0), mau="laser")
    phai = Tam("nha_tuong_phai", nha_tuong_phai(), NHA_W, h, T_TAM, o=(NHA_L / 2, 0, z0 + h / 2),
               x_dir=(0, -1, 0), z_dir=(-1, 0, 0), mau="laser")
    truoc = Tam("nha_vach_truoc", nha_vach_truoc(), TRUOC_L, TRUOC_H, T_TAM,
                o=(TRUOC_X, -NHA_W / 2 + T_TAM, z0 + TRUOC_H / 2), x_dir=(1, 0, 0), z_dir=(0, -1, 0), mau="laser")
    mai = Tam("nha_mai", nha_mai(), MAI_L, MAI_W, T_TAM, o=(0, 0, z0 + (NHA_H_SAU + NHA_H_TRUOC) / 2),
              x_dir=(1, 0, 0), z_dir=(0, -math.sin(doc), math.cos(doc)), mau="do")
    p = [t.part for t in (san, sau, trai, phai, truoc, mai)]

    # sàn: bo chủ, bếp có cảm biến gas, bàn phím, servo cửa
    p += san.gan(*cum_gan("C1"), 0, 24, ten="C1")
    p += san.gan(*cum_gan("I8"), 88, -32, ten="I8")
    p += san.gan(*cum_gan("I4"), 40, -40, ten="I4")
    p += san.gan(_servo(), GS_LO, -96, -56, rz=-90, ten="servo cửa")
    p.append(bd.Pos(-96, -56 - SG_TRUC_X, z0 + T_TAM + SG_DINH) * bd.Rot(0, 0, GOC_CUA) * nha_canh_cua())
    # tường sau (mặt trong): màn hình, đèn, PIR, nhiệt ẩm, relay
    for ma, (u, v) in {"O3": (4, 0), "O1": (0, 40), "I7": (-48, 32), "I6": (56, 0), "O4": (-84, -16)}.items():
        p += sau.gan(*cum_gan(ma), u, v, ten=ma)
    # tường phải: quạt hút ở mặt trong, MOSFET bên cạnh; giàn phơi ở mặt ngoài
    p += phai.gan(quat_4010(), QUAT_LO, -4, -8, ten="quạt")
    p += phai.gan(*cum_gan("O5"), 36, -4, ten="O5")
    phai._khop([(48 + dy, z - z0 - h / 2) for dy in (-12, 12) for z in (39, 15)], "ke góc")
    ke = khung((NHA_L / 2 + T_TAM, -48, 47), (0, -1, 0), (0, 0, 1))
    gian = [ke_goc()] + dat(bd.Pos(0, 18, T_TAM), _servo(90)) \
        + [bd.Pos(SG_TRUC_X, 18, 2 * T_TAM + SG_DINH) * bd.Rot(0, 0, 90) * gian_phoi()]
    p += dat(ke, gian)
    # vách trước (mặt ngoài): đầu đọc RFID cạnh cửa
    p += truoc.gan(*cum_gan("I13"), 32, 0, ten="I13")
    # mái: cảm biến mưa và ánh sáng
    p += mai.gan(*cum_gan("I10"), 64, 0, ten="I10")
    p += mai.gan(*cum_gan("I5"), -60, 0, ten="I5")
    return cum("nha_thong_minh", p)


if __name__ == "__main__":
    nha_thong_minh()
