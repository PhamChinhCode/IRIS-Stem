"""Sinh bản sơ đồ nguyên lý đầu tiên của S1 – driver động cơ encoder 2 kênh.

Chạy: PYTHONUTF8=1 python ve_so_do.py
Thiết kế: ../THIET-KE-MACH.md mục 2 và 3. Toạ độ theo lưới 1,27 mm.
Kịch bản ghi đè S1.kicad_sch; không chạy lại sau khi đã sửa sơ đồ bằng tay.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))
from sch import FP, SoDo  # noqa: E402

s = SoDo("S1", "S1 - Driver động cơ encoder 2 kênh", "A3", "0.1", "2026-11-15")
C0805 = FP["C0805"]


def tu_treo(ref, gt, x, y_ray, fp=None, lib="Device:C_Small"):
    """Tụ treo từ thanh nguồn nằm ngang (x, y_ray) xuống GND."""
    _, tren, duoi = s.doc(lib, ref, gt, x, y_ray + 4, fp or FP["C"])
    s.w((x, y_ray), tren)
    s.nguon("GND", duoi)


# ================= A. NGUỒN ĐỘNG LỰC =================
s.khoi(10, 14, 124, 52, "NGUỒN ĐỘNG LỰC VM (6–12 V)", [
    "Q1 chống ngược cực: D về XT30, S về VM, G xuống GND qua R5",
    "Đo VM: 10k/(100k+10k) = 1/11; 12 V → 1,09 V.  C10–C13 đặt sát U4",
])
Y = 28
j3 = s.dat("IRIS:Cong_Nguon_XT30", "J3", "XT30 đực", 20, Y + 1, 180, vt_ref=(-2, -5), vt_gt=(-2, 5))
s.w(j3.p("VBAT"), (36, Y))
s.w(j3.p("GND"), (29, Y + 2), (29, Y + 4))
s.nguon("GND", (29, Y + 4))
q1 = s.dat("Transistor_FET:IRF7404", "Q1", "AO4435", 40, Y + 2, 90, "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
           vt_ref=(-2, -6.5), vt_gt=(6.5, 5), MPN="AO4435")
assert q1.p("5") == (36, Y) and q1.p("1") == (44, Y), (q1.p("5"), q1.p("1"))
_, t, d = s.R("R5", "100k", 40, Y + 10)
s.w(q1.p("4"), t)
s.nguon("GND", d)
s.w(q1.p("1"), (116, Y))
s.co_nguon((47, Y))
tu_treo("C10", "220u/25V", 52, Y, "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm", "Device:C_Polarized_Small")
tu_treo("C11", "10u/25V", 62, Y, C0805)
tu_treo("C12", "10u/25V", 71, Y, C0805)
tu_treo("C13", "100n", 80, Y)
_, t, d = s.R("R10", "100k", 89, Y + 4)
s.w((89, Y), t)
_, t2, d2 = s.R("R11", "10k", 89, Y + 12)
s.w(d, t2)
s.nguon("GND", d2)
_, t3, d3 = s.C("C15", "100n", 97, Y + 12)
s.w((89, Y + 8), (97, Y + 8), t3)
s.nguon("GND", d3)
s.w((97, Y + 8), (101, Y + 8))
s.nhan("VM_SENSE", (101, Y + 8))
_, t, d = s.R("R21", "10k", 110, Y + 4)
s.w((110, Y), t)
led2 = s.dat("Device:LED_Small", "LED2", "VM", 110, Y + 10, 90, FP["LED"], vt_ref=(4, -1.1), vt_gt=(4, 1.1))
s.w(d, led2.p("2"))
s.nguon("GND", led2.p("1"))
s.nhan("VM", (116, Y))

# ================= B. NGUỒN LOGIC =================
s.khoi(10, 56, 124, 92, "NGUỒN LOGIC 3V3 (từ 5 V của cổng I2C)", [
    "U2 AP2112K-3.3: vào tối đa 6 V, 600 mA; EN nối VIN",
])
Y = 70
s.nguon("+5V", (16, Y))
s.co_nguon((25, Y))
u2 = s.dat("Regulator_Linear:AP2112K-3.3", "U2", "AP2112K-3.3", 50, Y + 2, 0, MPN="AP2112K-3.3TRG1")
s.w((16, Y), u2.p("VIN"))
tu_treo("C1", "10u/25V", 33, Y, C0805)
s.w(u2.p("EN"), (40, u2.p("EN")[1]), (40, Y))
s.nguon("GND", u2.p("GND"))
s.nc(u2.p("NC"))
s.w(u2.p("VOUT"), (72, Y))
tu_treo("C2", "10u/25V", 64, Y, C0805)
s.nguon("+3V3", (72, Y))
s.nguon("GND", (88, Y + 6))
s.w((88, Y + 6), (88, Y + 2))
s.co_nguon((88, Y + 2))

# ================= C. CỔNG I2C =================
s.khoi(10, 96, 124, 150, "CỔNG I2C VÀO / RA + ESD", [
    "Hai cổng nối song song cả 4 chân để nối chuỗi module",
    "Không đặt điện trở kéo lên I2C trên module (chỉ bo chủ C1 có)",
])
for ref, y in (("J1", 108), ("J2", 124)):
    j = s.dat("IRIS:Cong_I2C", ref, "I2C", 20, y, 180, vt_ref=(-2, -7), vt_gt=(-2, 7))
    for chan, dich in (("GND", "GND"), ("5V", "+5V"), ("SDA", "SDA_BUS"), ("SCL", "SCL_BUS")):
        a = j.p(chan)
        b = (a[0] + 4, a[1])
        s.w(a, b)
        if dich[0] in "G+":
            s.nguon(dich, b, "phai")
        else:
            s.nhan(dich, b)
u3 = s.dat("Power_Protection:SRV05-4", "U3", "SRV05-4", 66, 116, 0, MPN="SRV05-4")
s.chia(u3, {"1": "SDA_BUS", "3": "SCL_BUS", "4": None, "6": None, "5": "+3V3", "2": "GND"})
for ref, y, ten in (("R1", 108, "SDA"), ("R2", 124, "SCL")):
    _, tr, ph = s.R(ref, "100R", 102, y, ngang=True)
    s.w((98, y), tr)
    s.nhan(ten + "_BUS", (98, y), "trai")
    s.w(ph, (106, y))
    s.nhan(ten, (106, y))

# ================= D. VI ĐIỀU KHIỂN =================
s.khoi(130, 14, 250, 150, "VI ĐIỀU KHIỂN STM32G030K8T6", [
    "TIM1 (PA8, PB3) và TIM3 (PB4, PB5) đếm encoder; TIM16, TIM17 phát PWM 20 kHz",
    "PA14 = SWCLK kiêm BOOT0: R3 kéo xuống.  Không dùng PA9–PA12 (remap chân 19/21 ↔ 22/23)",
])
u1 = s.dat("MCU_ST_STM32G0:STM32G030K8Tx", "U1", "STM32G030K8T6", 204, 76, 0,
           MPN="STM32G030K8T6", LCSC="C431631", Manufacturer="STMicroelectronics")
s.chia(u1, {
    "4": "+3V3", "5": "GND", "6": "NRST",
    "7": "VM_SENSE", "8": "STBY", "9": "UART_TX", "10": "UART_RX",
    "11": "AIN1", "12": "AIN2", "13": "BIN1", "14": "BIN2",
    "15": "LED", "16": None, "17": "ADDR0",
    "18": "ENC1_A", "19": None, "20": None, "21": None, "22": None, "23": None,
    "24": "SWDIO", "25": "SWCLK", "26": "ADDR1",
    "27": "ENC1_B", "28": "ENC2_A", "29": "ENC2_B",
    "30": "SCL", "31": "SDA", "32": "PWMA", "1": "PWMB",
    "2": None, "3": None,
})
# cột mạch phụ bên trái
X = 140
for ref, gt, x, fp in (("C3", "100n", X, None), ("C4", "10u/25V", X + 9, C0805)):
    _, t, d = s.C(ref, gt, x, 28, fp)
    s.nguon("+3V3", t)
    s.nguon("GND", d)
_, t, d = s.C("C5", "100n", X, 44)
s.w(t, (X, 40), (X + 4, 40))
s.nhan("NRST", (X + 4, 40))
s.nguon("GND", d)
_, t, d = s.R("R3", "10k", X, 58)
s.w(t, (X, 54), (X + 4, 54))
s.nhan("SWCLK", (X + 4, 54))
s.nguon("GND", d)
# LED trạng thái
y = 70
s.nhan("LED", (X + 4, y), "trai")
_, tr, ph = s.R("R4", "1k", X + 8, y, ngang=True)
s.w((X + 4, y), tr)
led1 = s.dat("Device:LED_Small", "LED1", "STATUS", X + 15, y, 180, FP["LED"], vt_ref=(0, -2.4), vt_gt=(0, 2.6))
s.w(ph, led1.p("2"))
s.w(led1.p("1"), (X + 19, y))
s.nguon("GND", (X + 19, y), "phai")
# cầu hàn địa chỉ
for ref, ten, y in (("JP1", "ADDR0", 82), ("JP2", "ADDR1", 92)):
    s.nhan(ten, (X + 4, y), "trai")
    jp = s.dat("Jumper:SolderJumper_2_Open", ref, ten, X + 10, y, 0, FP["JP2"], vt_ref=(0, -3), vt_gt=(0, 3))
    s.w((X + 4, y), jp.p("1"))
    s.w(jp.p("2"), (X + 16, y))
    s.nguon("GND", (X + 16, y), "phai")
s.chu("Địa chỉ I2C = 0x30 + (JP2, JP1); hàn = 1", X - 6, 98)
# điểm nạp và gỡ lỗi
for i, (ref, ten) in enumerate((("TP1", "+3V3"), ("TP2", "SWDIO"), ("TP3", "SWCLK"), ("TP4", "NRST"),
                                ("TP5", "GND"), ("TP6", "UART_TX"), ("TP7", "UART_RX"))):
    y = 106 + 6 * i
    tp = s.dat("Connector:TestPoint", ref, ten, X + 12, y, 0, FP["TP"], vt_ref=(3.5, -2), vt_gt=(3.5, 0))
    tp.an_gt = True
    s.w((X + 4, y), tp.p("1"))
    if ten[0] in "G+":
        s.nguon(ten, (X + 4, y), "trai")
    else:
        s.nhan(ten, (X + 4, y), "trai")

# ================= E. DRIVER =================
s.khoi(10, 154, 124, 222, "DRIVER TB6612FNG", [
    "1,2 A liên tục, 3,2 A đỉnh mỗi kênh; chân vào có sẵn kéo xuống 200k",
    "R12 giữ STBY thấp khi vi điều khiển đang reset",
])
u4 = s.dat("Driver_Motor:TB6612FNG", "U4", "TB6612FNG", 74, 186, 0, MPN="TB6612FNG")
s.chia(u4, {
    "1": "M1+", "2": "M1+", "5": "M1-", "6": "M1-", "11": "M2+", "12": "M2+", "7": "M2-", "8": "M2-",
    "24": "VM", "13": "VM", "14": "VM", "20": "+3V3",
    "3": "GND", "4": "GND", "9": "GND", "10": "GND", "18": "GND",
    "23": "PWMA", "21": "AIN1", "22": "AIN2", "15": "PWMB", "17": "BIN1", "16": "BIN2", "19": "STBY",
})
_, t, d = s.C("C14", "100n", 20, 172)
s.nguon("+3V3", t)
s.nguon("GND", d)
_, t, d = s.R("R12", "10k", 20, 192)
s.w(t, (20, 188), (24, 188))
s.nhan("STBY", (24, 188))
s.nguon("GND", d)

# ================= F. CỔNG ĐỘNG CƠ =================
s.khoi(254, 14, 322, 196, "CỔNG ĐỘNG CƠ + ENCODER", [
    "Kéo lên 10k; lọc 1k + 1n: fc = 160 kHz",
    "(encoder nhanh nhất khoảng 3,5 kHz)",
])
for n, y in ((1, 30), (2, 50)):
    j = s.dat("IRIS:Cong_DongCo", f"J{n + 3}", f"ĐỘNG CƠ {n}", 312, y, 0, vt_ref=(2, -9.5), vt_gt=(2, 9.5))
    for chan, dich in (("M+", f"M{n}+"), ("M-", f"M{n}-"), ("GND", "GND"), ("3V3", "+3V3_ENC"),
                       ("EncA", f"ENC{n}_A_J"), ("EncB", f"ENC{n}_B_J")):
        a = j.p(chan)
        b = (a[0] - 4, a[1])
        s.w(a, b)
        if dich == "GND":
            s.nguon("GND", b, "trai")
        else:
            s.nhan(dich, b, "trai")
y = 66
s.nguon("+3V3", (266, y), "trai")
fb = s.dat("Device:FerriteBead_Small", "FB1", "600R", 272, y, 90, FP["FB"], vt_ref=(0, -2.4), vt_gt=(0, 2.6))
s.w((266, y), fb.p("1"))
s.w(fb.p("2"), (278, y))
s.nhan("+3V3_ENC", (278, y))
k = 13
for i, ten in enumerate(("ENC1_A", "ENC1_B", "ENC2_A", "ENC2_B")):
    y = 84 + 20 * i
    s.nhan(ten + "_J", (272, y), "trai")
    _, t, d = s.R(f"R{k + i}", "10k", 276, y - 4)
    s.nguon("+3V3", t)
    s.w(d, (276, y))
    _, tr, ph = s.R(f"R{k + 4 + i}", "1k", 285, y, ngang=True)
    s.w((272, y), tr)
    s.w(ph, (296, y))
    _, t, d = s.C(f"C{16 + i}", "1n", 291, y + 4)
    s.w((291, y), t)
    s.nguon("GND", d)
    s.nhan(ten, (296, y))
u5 = s.dat("Power_Protection:SRV05-4", "U5", "SRV05-4", 288, 172, 0, MPN="SRV05-4")
s.chia(u5, {"1": "ENC1_A_J", "3": "ENC1_B_J", "4": "ENC2_A_J", "6": "ENC2_B_J", "5": "+3V3", "2": "GND"})

# ================= khung bo, ghi chú =================
s.khoi(130, 154, 250, 196, "CƠ KHÍ VÀ GHI CHÚ", [])
s.dat("IRIS:Khung_S1_48x48", "KH1", "Khung_S1_48x48", 150, 172, 0, vt_ref=(0, -6), vt_gt=(0, 6))
for i, g in enumerate((
    "Bo 48 × 48 mm, lỗ gá Ø3,2 theo lưới 8 mm (nằm trong chân linh kiện KH1).",
    "Mọi R, C nhỏ: 0603 1 % / 50 V; tụ 10 µF: 0805 25 V.",
    "Firmware phải cắt PWM khi encoder đứng yên > 0,5 s (kẹt trục).",
    "Thiết kế: hardware/THIET-KE-MACH.md mục 2, 3.",
)):
    s.chu(g, 164, 166 + 4 * i)

s.ghi(os.path.join(os.path.dirname(os.path.abspath(__file__)), "S1.kicad_sch"))
print(len([k for k in s.lk if not k.ref.startswith("#")]), "linh kiện")
