"""Khối bao của các bo mạch trong kit: kích thước bo, lỗ gá, vị trí đầu cắm và linh kiện cao.

Quy ước: tâm bo ở gốc XY, mặt dưới bo ở z = 0, linh kiện ở mặt trên (z > 1,6).
Lỗ gá: 4 lỗ Ø3,2, tâm cách mép 4 mm, nên khoảng cách lỗ luôn là bội số của 8 mm.
"""
from cadgen import build123d as bd

from lib.chuan import D_PCB, H_TRU, T_PCB, cum, hop, to, tru
from lib.mua_san import tru_do

_S, _M, _L, _T = (24, 32), (32, 48), (48, 64), (64, 24)

# mã: (rộng X, cao Y, tên)
KT = {
    "C1": (96, 64, "Bo chủ ESP32-S3"), "C2": (96, 48, "Nguồn pin 2S"),
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
    return [(sx * (w / 2 - 4), sy * (h / 2 - 4)) for sx in (-1, 1) for sy in (-1, 1)]


def _jst(ma, n, loai, canh, lech=0.0):
    """Đầu JST PH nằm ngang n chân, áp sát mép bo. canh: S, N, W, E."""
    w, h, _ = KT[ma]
    rong, sau, cao = 2.0 * n + 1.9, 7.5, 5.0
    if canh in "SN":
        y = (-h / 2 + sau / 2) if canh == "S" else (h / 2 - sau / 2)
        b = hop(rong, sau, cao, lech, y, T_PCB)
    else:
        x = (-w / 2 + sau / 2) if canh == "W" else (w / 2 - sau / 2)
        b = hop(sau, rong, cao, x, lech, T_PCB)
    return to(b, f"cong_{loai}_{canh}{int(lech)}", MAU_CONG[loai])


def _b(ten, mau, lx, ly, lz, x=0.0, y=0.0, z=T_PCB):
    return to(hop(lx, ly, lz, x, y, z), ten, mau)


def _t(ten, mau, d, h, x=0.0, y=0.0, z=T_PCB):
    return to(tru(d, h, x, y, z), ten, mau)


def _linh_kien(ma):
    w, h, _ = KT[ma]
    if ma == "C1":
        p = [_jst(ma, 4, "DA", "S", -32.5 + 13 * i) for i in range(6)]
        p += [_jst(ma, 4, "I2C", "N", -32.5 + 13 * i) for i in range(4)]
        p += [_jst(ma, 6, "SPI", "N", 25.0),
              _b("ESP32_S3_WROOM", "bac", 19.0, 18.0, 3.2, 31.0, 0),
              _b("anten", "den", 6.5, 18.0, 1.0, 44.75, 0),
              _b("USB_C", "bac", 7.4, 9.0, 3.2, -44.3, 0),
              _b("cong_nguon_5V", "trang", 7.5, 8.0, 6.0, -44.25, 16),
              _b("nut_reset", "den", 4.0, 4.0, 2.0, -44.0, -16),
              _b("nut_A", "do", 6.0, 6.0, 5.0, -30, -8), _b("nut_B", "xanh", 6.0, 6.0, 5.0, -16, -8),
              _t("coi", "den", 9.0, 5.5, 2, -10), _b("LED_RGB", "trang", 5.0, 5.0, 1.6, 2, 8),
              _b("hang_rao_servo_4x3", "den", 10.2, 7.6, 8.5, -22, 9)]
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
        return [_t("dau_phat", "bac", 16.0, 12.0, -13, 0), _t("dau_thu", "bac", 16.0, 12.0, 13, 0),
                to(hop(9.9, 6.0, 7.5, 0, 0, -7.5), "cong_DA_sau", "trang")]
    loai = "I2C" if ma in ("I4", "I6", "I14", "O3", "O7") else ("SPI" if ma == "I13" else "DA")
    p = [_jst(ma, 6 if loai == "SPI" else 4, loai, "S")]
    if ma == "I1":
        for i, (x, m) in enumerate(((-5.5, "do"), (5.5, "xanh"))):
            p += [_b(f"nut_{i + 1}", "den", 6.0, 6.0, 3.5, x, 4), _t(f"mu_nut_{i + 1}", m, 3.5, 1.5, x, 4, T_PCB + 3.5)]
    elif ma == "I2":
        p += [_b("bien_tro", "xanh", 9.5, 11.0, 6.5, 0, 4), _t("truc_bien_tro", "trang", 6.0, 10.0, 0, 4, T_PCB + 6.5)]
    elif ma == "I3":
        p += [_b("joystick", "den", 16.0, 16.0, 12.0, 0, 6), _t("can_joystick", "den", 5.0, 8.0, 0, 6, T_PCB + 12),
              _t("mu_joystick", "xam", 18.0, 4.0, 0, 6, T_PCB + 20)]
    elif ma == "I4":
        p += [_b(f"phim_{r}{c}", "xam", 7.0, 7.0, 4.5, -15 + 10 * c, 21 - 10 * r) for r in range(4) for c in range(4)]
    elif ma == "I5":
        p += [_t("LDR", "do", 5.0, 2.0, 0, 6)]
    elif ma == "I6":
        p += [_b("AHT20", "trang", 3.0, 3.0, 1.0, 0, 8), _b("on_ap_3V3", "den", 3.0, 3.0, 1.2, 5, 0)]
    elif ma == "I7":
        p += [_t("PIR_de", "trang", 10.0, 4.0, 0, 5),
              to(bd.Pos(0, 5, T_PCB + 5) * bd.Sphere(5.0), "PIR_vom", "trang")]
    elif ma == "I8":
        p += [_t("MQ2", "bac", 19.0, 16.0, 0, 6), _b("phan_ap", "den", 3.0, 6.0, 1.0, 0, -9)]
    elif ma == "I10":
        p += [_b("luoc_cam_bien_mua", "bac", 26.0, 30.0, 0.1, 0, 6)]
    elif ma == "I12":
        p += [_b("mat_thu_hong_ngoai", "den", 5.0, 3.0, 7.0, 0, 8)]
    elif ma == "I13":
        p += [_b("anten_RFID", "dong", 40.0, 40.0, 0.1, 0, 8), _b("RC522", "den", 5.0, 5.0, 1.0, 0, -16)]
    elif ma == "I14":
        p += [_b("APDS9960", "den", 4.0, 2.0, 1.4, 0, 6), _b("LED_chieu_sang", "trang", 3.0, 3.0, 1.2, 0, 11)]
    elif ma == "O1":
        p += [_t("LED_1", "do", 5.0, 8.6, -5, 5), _t("LED_2", "la", 5.0, 8.6, 5, 5)]
    elif ma == "O2":
        p += [_b(f"LED_{i + 1}", "trang", 5.0, 5.0, 1.6, -24.5 + 7 * i, 5) for i in range(8)]
    elif ma == "O3":
        p += [_b("OLED_bo", "xanh", 27.0, 27.0, 1.2, 0, 6, T_PCB + 2.5), _b("OLED_kinh", "den", 25.0, 15.0, 1.5, 0, 9, T_PCB + 3.7)]
    elif ma == "O4":
        p += [_b("relay", "xanh", 15.5, 19.0, 15.0, 0, 2), _b("cau_dau_tai", "la", 15.0, 7.5, 10.0, 0, 19.5)]
    elif ma == "O5":
        p += [_b("MOSFET", "den", 10.0, 9.0, 4.5, 0, 0), _b("cau_dau_tai", "la", 10.0, 7.5, 10.0, 0, 11.5)]
    elif ma == "O7":
        p += [_jst(ma, 4, "I2C", "N"), _b("hang_rao_16_kenh", "den", 7.6, 40.6, 8.5, 14, 0),
              _b("PCA9685", "den", 7.8, 9.7, 1.8, 0, 0), _b("cau_dau_nguon", "la", 7.5, 10.0, 10.0, -19, 12),
              _b("ha_ap_6V", "xam", 7.0, 7.0, 4.0, -16, -8)]
    return p


def bo(ma):
    """Danh sách khối lá của một bo: tấm mạch + linh kiện."""
    w, h, _ = KT[ma]
    tam = hop(w, h, T_PCB)
    for (x, y) in lo_ga(ma):
        tam -= tru(D_PCB, T_PCB + 2, x, y, -1)
    return [to(tam, f"{ma}_bo_mach", "pcb")] + _linh_kien(ma)


def module(ma):
    return cum(ma, bo(ma))


def cum_gan(ma, h=H_TRU):
    """Bo kèm 4 trụ đỡ, gốc ở mặt gá. Trả về (danh sách khối, toạ độ lỗ gá)."""
    lo = lo_ga(ma)
    parts = [tru_do(h, x, y) for (x, y) in lo] + [bd.Pos(0, 0, h) * module(ma)]
    return parts, lo
