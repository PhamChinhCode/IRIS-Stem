"""Khối bao của các bo mạch trong kit: kích thước bo, lỗ gá, vị trí đầu cắm và linh kiện cao.

Quy ước: tâm bo ở gốc XY, mặt dưới bo ở z = 0, linh kiện ở mặt trên (z > 1,6).
Lỗ gá: 4 lỗ Ø3,2, tâm cách mép 4 mm, nên khoảng cách lỗ luôn là bội số của 8 mm.
Riêng cỡ S (24 x 32): hai lỗ phía đầu cắm lùi lên cách mép dưới 12 mm, vì đầu cắm rộng 9,9 mm
không lọt giữa hai trụ đỡ cách nhau 16 mm.
"""
from cadgen import build123d as bd

from lib import vo
from lib.chuan import D_PCB, H_TRU, T_PCB, cum, hop, to, tru
from lib.mua_san import tru_do

H_RAO = 8.5     # hàng rào cái 2,54 mm cho module cắm rời
THU = 0.25      # tấm mạch thu vào mỗi cạnh so với kích thước danh nghĩa; lỗ gá giữ nguyên trên lưới
_S, _M, _L, _T = (24, 32), (32, 48), (48, 64), (64, 24)

# mã: (rộng X, cao Y, tên)
KT = {
    "C1": (64, 48, "Bo chủ ESP32-S3"), "C2": (96, 48, "Nguồn pin 2S"),
    "S1": (48, 48, "Driver động cơ encoder"), "S2": (80, 24, "Dò line 8 mắt"),
    "S3": (32, 32, "IMU trả góc"),
    "I1": (*_S, "Nút bấm đôi"), "I2": (*_S, "Biến trở xoay"), "I3": (*_M, "Joystick"),
    "I4": (*_L, "Bàn phím 4x4"), "I5": (*_S, "Ánh sáng LDR"), "I6": (*_S, "Nhiệt ẩm AHT20"),
    "I7": (*_S, "Chuyển động PIR"), "I8": (*_M, "Khí gas MQ-2"), "I9": (24, 96, "Độ ẩm đất (que)"),
    "I10": (*_M, "Cảm biến mưa"), "I11": (*_T, "Siêu âm"), "I12": (*_S, "Thu hồng ngoại"),
    "I13": (*_L, "RFID RC522"), "I14": (*_S, "Màu/cử chỉ APDS9960"),
    "O1": (*_S, "LED đôi"), "O2": (*_T, "NeoPixel 8 LED"), "O3": (*_M, "OLED 0,96 inch"),
    "O4": (*_M, "Relay 1 kênh"), "O5": (*_S, "MOSFET công suất"), "O7": (*_L, "PCA9685 16 kênh"),
}
MAU_CONG = {"DA": "trang", "I2C": "xanh", "SPI": "vang", "DC": "do"}


def lo_ga(ma):
    w, h, _ = KT[ma]
    if ma == "I9":
        return [(-8.0, h / 2 - 4), (8.0, h / 2 - 4)]
    if (w, h) == _S:
        return [(sx * 8.0, y) for sx in (-1, 1) for y in (-h / 2 + 12, h / 2 - 4)]
    return [(sx * (w / 2 - 4), sy * (h / 2 - 4)) for sx in (-1, 1) for sy in (-1, 1)]


def _jst(ma, n, loai, canh, lech=0.0):
    """Đầu JST PH nằm ngang n chân, áp sát mép bo. canh: S, N, W, E."""
    w, h, _ = KT[ma]
    rong, sau, cao = 2.0 * n + 1.9, 7.5, 5.0
    if canh in "SN":
        y = (-h / 2 + THU + sau / 2) if canh == "S" else (h / 2 - THU - sau / 2)
        b = hop(rong, sau, cao, lech, y, T_PCB)
    else:
        x = (-w / 2 + THU + sau / 2) if canh == "W" else (w / 2 - THU - sau / 2)
        b = hop(sau, rong, cao, x, lech, T_PCB)
    return to(b, f"cong_{loai}_{canh}{int(lech)}", MAU_CONG[loai])


def _b(ten, mau, lx, ly, lz, x=0.0, y=0.0, z=T_PCB):
    return to(hop(lx, ly, lz, x, y, z), ten, mau)


def _t(ten, mau, d, h, x=0.0, y=0.0, z=T_PCB):
    return to(tru(d, h, x, y, z), ten, mau)


def _linh_kien(ma):
    w, h, _ = KT[ma]
    if ma == "C1":
        # bo 64 x 48: mỗi cạnh dài chỉ đủ 5 đầu PH 4 chân (bước 10) giữa hai lỗ gá, nên cổng D/A thứ sáu
        # lên cạnh trên, cổng SPI sang cạnh trái, cổng nguồn 5 V là loại cắm đứng nằm trong lòng bo
        p = [_jst(ma, 4, "DA", "S", -20.0 + 10 * i) for i in range(5)]
        p += [_jst(ma, 4, "I2C", "N", -20.0 + 10 * i) for i in range(4)]
        p += [_jst(ma, 4, "DA", "N", 20.0), _jst(ma, 6, "SPI", "W", -9.25),
              _b("ESP32_S3_WROOM", "bac", 19.0, 18.0, 3.2, 15.75, 0),
              _b("anten", "den", 6.5, 18.0, 1.0, 28.5, 0),
              _b("USB_C", "bac", 7.4, 9.0, 3.2, -28.3, 8),
              _b("cong_nguon_5V", "trang", 7.5, 8.0, 6.0, -19.5, 11.5),
              _b("nut_reset", "den", 4.0, 4.0, 2.0, 2, 3),
              _b("nut_A", "do", 6.0, 6.0, 5.0, -18, -9), _b("nut_B", "xanh", 6.0, 6.0, 5.0, -8, -9),
              _t("coi", "den", 9.0, 5.5, 0.5, -10.5), _b("LED_RGB", "trang", 5.0, 5.0, 1.6, -13, 1),
              _b("hang_rao_servo_4x3", "den", 10.2, 7.6, 8.5, -6, 11.5)]
        return p
    if ma == "C2":
        return [_b("de_pin_2x18650", "den", 77.0, 41.0, 6.0),
                to(bd.Pos(0, -10, T_PCB + 11.5) * bd.Rot(0, 90, 0) * bd.Cylinder(9.2, 65.0), "pin_18650_1", "la"),
                to(bd.Pos(0, 10, T_PCB + 11.5) * bd.Rot(0, 90, 0) * bd.Cylinder(9.2, 65.0), "pin_18650_2", "la"),
                _b("USB_C_sac", "bac", 7.4, 9.0, 3.2, -44.3, -10), _b("cong_tac", "den", 7.0, 9.0, 6.0, -44.5, 10),
                _b("XT30_ra_7V4", "vang", 8.0, 10.2, 10.5, 43.5, 10), _b("cong_5V_ra", "trang", 7.5, 8.0, 6.0, 44.25, -4),
                _jst(ma, 4, "I2C", "E", -15.0)]
    if ma == "S1":
        return [_jst(ma, 4, "I2C", "W", -7.0), _jst(ma, 4, "I2C", "W", 7.0),
                _jst(ma, 6, "DC", "N"), _jst(ma, 6, "DC", "S"),
                _b("XT30_vao", "vang", 8.0, 10.2, 10.5, 20.0, 0),
                _b("TB6612FNG", "den", 8.2, 7.8, 1.8, 2, 6), _b("STM32G030", "den", 7.0, 7.0, 1.4, 2, -7)]
    if ma == "S2":
        p = [_jst(ma, 4, "I2C", "N", -12.0), _jst(ma, 4, "I2C", "N", 12.0),
             _b("STM32G030", "den", 7.0, 7.0, 1.4, 0, -4)]
        p += [to(hop(3.4, 2.7, 1.5, -31.5 + 9 * i, -7.0, -1.5), f"mat_do_line_{i + 1}", "den") for i in range(8)]
        return p
    if ma == "S3":
        return [_jst(ma, 4, "I2C", "S"), _jst(ma, 4, "I2C", "N"),
                _b("IMU_6_truc", "den", 3.0, 3.0, 0.9), _b("STM32G030_QFN", "den", 5.0, 5.0, 0.9, -8, 0)]
    if ma == "I9":
        return [_jst(ma, 4, "DA", "N", 0.0), _b("mach_do", "den", 8.0, 10.0, 1.0, 0, 28)]
    if ma == "I11":
        zm = T_PCB + H_RAO           # module HC-SR04 cắm trên hàng rào cái
        return [_b("hang_rao_cai", "den", 10.2, 2.5, H_RAO, 0, -9.5), _b("HC_SR04", "xanh", 45.0, 20.0, 1.6, 0, -0.8, zm),
                _t("dau_phat", "bac", 16.0, 12.0, -13, -0.8, zm + 1.6), _t("dau_thu", "bac", 16.0, 12.0, 13, -0.8, zm + 1.6),
                to(hop(9.9, 4.5, 6.0, 0, 1.5, -6.0), "cong_DA_sau", "trang")]
    loai = "I2C" if ma in ("I4", "I6", "I14", "O3", "O7") else ("SPI" if ma == "I13" else "DA")
    p = [_jst(ma, 6 if loai == "SPI" else 4, loai, "S")]
    if ma == "I1":
        for i, (x, m) in enumerate(((-5.6, "do"), (5.6, "xanh"))):
            p += [_b(f"nut_{i + 1}", "den", 6.0, 6.0, 3.5, x, 4), _t(f"mu_nut_{i + 1}", m, 3.5, 3.5, x, 4, T_PCB + 3.5)]
    elif ma == "I2":
        p += [_b("bien_tro", "xanh", 9.8, 12.0, 6.5, 0, 5), _t("truc_bien_tro", "trang", 6.0, 10.0, 0, 5.9, T_PCB + 6.5)]
    elif ma == "I3":
        p += [_b("joystick", "den", 16.0, 16.0, 12.0, 0, 6), _t("can_joystick", "den", 5.0, 8.0, 0, 6, T_PCB + 12),
              _t("mu_joystick", "xam", 18.0, 4.0, 0, 6, T_PCB + 20)]
    elif ma == "I4":
        for r in range(4):
            for c in range(4):
                x, y = -15 + 10 * c, 21 - 10 * r
                p += [_b(f"phim_{r}{c}", "den", 6.0, 6.0, 3.5, x, y), _t(f"mu_phim_{r}{c}", "xam", 3.5, 3.5, x, y, T_PCB + 3.5)]
    elif ma == "I5":
        p += [_t("LDR", "do", 5.0, 2.0, 0, 6)]
    elif ma == "I6":
        p += [_b("AHT20", "trang", 3.0, 3.0, 1.0, 0, 8), _b("on_ap_3V3", "den", 3.0, 3.0, 1.2, 5, 0)]
    elif ma == "I7":
        p += [_b("hang_rao_cai", "den", 7.7, 2.5, H_RAO, 0, 5), _t("PIR_de", "trang", 10.0, 3.0, 0, 5, T_PCB + H_RAO),
              to(bd.Pos(0, 5, T_PCB + H_RAO + 3) * bd.Sphere(5.0), "PIR_vom", "trang")]
    elif ma == "I8":
        p += [_t("MQ2", "bac", 19.0, 16.0, 0, 6), _b("phan_ap", "den", 3.0, 6.0, 1.0, 0, -9)]
    elif ma == "I10":
        p += [_b("luoc_cam_bien_mua", "bac", 23.6, 21.9, 0.1, 0, 2.6)]
    elif ma == "I12":
        p += [_b("mat_thu_hong_ngoai", "den", 6.0, 5.0, 10.3, 0, 8)]
    elif ma == "I13":
        p += [_b("anten_RFID", "dong", 40.0, 40.0, 0.1, 0, 8), _b("RC522", "den", 5.0, 5.0, 1.0, 0, -16)]
    elif ma == "I14":
        p += [_b("APDS9960", "den", 4.0, 2.4, 1.4, 0, 6)]
    elif ma == "O1":
        p += [_b("LED_1", "do", 0.8, 1.6, 0.6, -5, 5), _b("LED_2", "la", 0.8, 1.6, 0.6, 5, 5)]
    elif ma == "O2":
        p += [_b(f"LED_{i + 1}", "trang", 5.0, 5.0, 1.6, -25.2 + 7.2 * i, 1.5) for i in range(8)]
    elif ma == "O3":
        p += [_b("hang_rao_cai", "den", 10.2, 2.5, H_RAO, 0, 12.5), _b("OLED_bo", "xanh", 27.0, 27.0, 1.2, 0, 0.5, T_PCB + H_RAO),
              _b("OLED_kinh", "den", 23.0, 12.0, 1.5, 0, 2.5, T_PCB + H_RAO + 1.2)]
    elif ma == "O4":
        p += [_b("relay", "xanh", 15.5, 19.0, 15.6, 0, 1), _b("cau_dau_tai", "la", 15.2, 9.8, 10.0, 0, 18.2)]
    elif ma == "O5":
        p += [_b("MOSFET", "den", 3.0, 1.4, 1.1, 0, 0), _b("cong_tai_XH", "trang", 7.4, 11.5, 7.0, 0, 9.9)]
    elif ma == "O7":
        p += [_jst(ma, 4, "I2C", "N"), _b("hang_rao_16_kenh", "den", 7.6, 40.6, 8.5, 14, 0),
              _b("PCA9685", "den", 7.8, 9.7, 1.8, 0, 0), _b("cau_dau_nguon", "la", 7.5, 10.0, 10.0, -19, 12),
              _b("ha_ap_6V", "xam", 7.0, 7.0, 4.0, -16, -8)]
    return p


def bo(ma):
    """Danh sách khối lá của một bo: tấm mạch + linh kiện."""
    w, h, _ = KT[ma]
    tam = hop(w - 2 * THU, h - 2 * THU, T_PCB)
    for (x, y) in lo_ga(ma):
        tam -= tru(D_PCB, T_PCB + 2, x, y, -1)
    return [to(tam, f"{ma}_bo_mach", "pcb")] + _linh_kien(ma)


def module(ma):
    return cum(ma, bo(ma))


def cum_gan(ma, h=H_TRU):
    """Bo gắn lên mặt gá, gốc ở mặt gá. Trả về (danh sách khối, toạ độ lỗ gá).

    Bo mang có vỏ in 3D: đế đặt thẳng lên mặt gá, bo nằm trong đế, nắp đậy trên (lib/vo.py).
    Bo còn lại: 4 trụ đỡ cao h.
    """
    lo = lo_ga(ma)
    if ma in vo.BO:
        z = vo.BO[ma]["vo"].get("duoi", vo.H_DUOI) + vo.T
        up = bd.Pos(0, 0, z)
        parts = [up * vo.de(ma), up * module(ma)] + ([up * vo.nap(ma)] if vo.co_nap(ma) else [])
        for q, ten in zip(parts, (f"vo_{ma}_de", ma, f"vo_{ma}_nap")):
            q.label = ten
        return parts, lo
    parts = [tru_do(h, x, y) for (x, y) in lo] + [bd.Pos(0, 0, h) * module(ma)]
    return parts, lo
