"""Sinh bản sơ đồ nguyên lý đầu tiên của C1 – bo chủ ESP32-S3.

Chạy: PYTHONUTF8=1 python ve_so_do.py
Thiết kế: ../THIET-KE-MACH.md mục 6. Toạ độ theo lưới 1,27 mm.
Kịch bản ghi đè C1.kicad_sch; không chạy lại sau khi đã sửa sơ đồ bằng tay.
"""
import os
import sys

DAY = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(DAY, "..", "common"))
from sch import FP, SoDo  # noqa: E402
from khoi_chung import C0805, tep_du_an  # noqa: E402

s = SoDo("C1", "C1 - Bo chủ ESP32-S3", "A2", "0.1", "2026-11-15")
SOT23 = "Package_TO_SOT_SMD:SOT-23"
TS1088 = "Button_Switch_SMD:SW_SPST_TS-1088-xR025"
NUT6 = "Button_Switch_SMD:SW_Push_1TS009xxxx-xxxx-xxxx_6x6x5mm"
PTC = "Fuse:Fuse_1812_4532Metric"


def tu_treo(ref, gt, x, y_ray, fp=None, lib="Device:C_Small"):
    _, tren, duoi = s.doc(lib, ref, gt, x, y_ray + 4, fp or FP["C"])
    s.w((x, y_ray), tren)
    s.nguon("GND", duoi)


def tu_tach(ref, gt, x, y, fp=None):
    """Tụ đứng giữa +3V3 (trên) và GND (dưới), tâm tại (x, y)."""
    _, t, d = s.C(ref, gt, x, y, fp)
    s.nguon("+3V3", t)
    s.nguon("GND", d)


# ================= 1. NGUỒN VÀO =================
s.khoi(10, 14, 160, 90, "NGUỒN VÀO: USB-C VÀ 5 V TỪ C2", [
    "Không có C2: R1 kéo G của Q1 xuống, Q1 dẫn (sụt 0,12 V ở 2 A).  Có C2 (5,45 V): Q1 khoá, D1 dẫn",
    "D1 chặn dòng từ USB chảy ngược về C2.  CC1, CC2 mỗi chân một điện trở 5k1",
])
usb = s.dat("Connector:USB_C_Receptacle_USB2.0_16P", "J1", "USB-C", 26, 44, 0,
            "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", vt_ref=(-4, -17), vt_gt=(4, -17), MPN="TYPE-C-31-M-12")
Y = 32
assert usb.p("A4") == (38, Y), usb.p("A4")
q1 = s.dat("Transistor_FET:AO3401A", "Q1", "AO3401A", 64, Y + 2, 90, SOT23, vt_ref=(-2, -6.5), vt_gt=(5, -6.5), MPN="AO3401A")
assert q1.p("D") == (60, Y) and q1.p("S") == (68, Y), (q1.p("D"), q1.p("S"))
s.w(usb.p("A4"), q1.p("D"))
s.nguon("VBUS", (43, Y))
s.co_nguon((51, Y))
s.w(usb.p("A5"), (58, 36), (58, 40))
_, t, d = s.R("R2", "5k1", 58, 42)
s.nguon("GND", d)
s.w(usb.p("B5"), (53, 38), (53, 46))
_, t, d = s.R("R3", "5k1", 53, 48)
s.nguon("GND", d)
for ten, a, b in (("USB_D-", "A7", "B7"), ("USB_D+", "A6", "B6")):
    pa, pb = usb.p(a), usb.p(b)
    s.w(pa, (41, pa[1]), (41, pb[1]), pb)
    s.nhan(ten, (41, pa[1] if ten.endswith("-") else pb[1]))
s.nc(usb.p("A8"))
s.nc(usb.p("B8"))
g, sh = usb.p("A1"), usb.p("SH")
s.w(g, (g[0], g[1] + 2))
s.w(sh, (sh[0], sh[1] + 2), (g[0], g[1] + 2))
s.nguon("GND", (g[0], g[1] + 2))
# đường +5V_SYS
s.w(q1.p("S"), (150, Y))
s.co_nguon((75, Y))
tu_treo("C6", "10u/25V", 84, Y, C0805)
s.nhan("5V_SYS", (150, Y))
# 5 V từ C2
j2 = s.dat("IRIS:Cong_Nguon_5V", "J2", "5V từ C2", 20, 75, 180, vt_ref=(-2, -5), vt_gt=(-2, 5))
assert j2.p("5V") == (26, 74), j2.p("5V")
s.w(j2.p("5V"), (98, 74))
s.ten_day("5V_EXT", (30, 74))
s.w(j2.p("GND"), (30, 76), (30, 79))
s.nguon("GND", (30, 79))
s.w(q1.p("G"), (64, 74))
_, t, d = s.R("R1", "100k", 74, 78)
s.w((74, 74), t)
s.nguon("GND", d)
d1 = s.dat("Device:D_Schottky_Small", "D1", "SS54", 100, 74, 180, "Diode_SMD:D_SMA", vt_ref=(0, -2.6), vt_gt=(0, 2.6), MPN="SS54")
assert d1.p("A") == (98, 74)
s.w(d1.p("K"), (110, 74), (110, Y))
u3 = s.dat("Power_Protection:SRV05-4", "U3", "SRV05-4", 134, 60, 0, MPN="SRV05-4")
s.chia(u3, {"1": "USB_D+", "3": "USB_D-", "4": None, "6": None, "5": "VBUS", "2": "GND"})

# ================= 2. CẦU CHÌ VÀ 3V3 =================
s.khoi(10, 94, 160, 150, "CẦU CHÌ TỰ PHỤC HỒI VÀ ỔN ÁP 3V3", [
    "F1 1,5 A cho 2 cổng servo; F2 1,1 A cho các cổng D/A, I2C, SPI",
    "U2: LDO 1 A vỏ SOT-223, sụt áp thấp (TLV1117LV33): 0,6 W khi ESP32 phát WiFi liên tục",
])
for ref, gt, y, tu, tu_gt, dich in (("F1", "1,5A", 108, "C1", "220u/16V", "5V_SERVO"), ("F2", "1,1A", 128, "C2", "10u/25V", None)):
    s.nhan("5V_SYS", (24, y), "trai")
    _, tr, ph = s.ngang("Device:Polyfuse_Small", ref, gt, 30, y, PTC)
    s.w((24, y), tr)
    s.w(ph, (54, y))
    if dich:
        tu_treo(tu, tu_gt, 42, y, "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", "Device:C_Polarized_Small")
        s.nhan(dich, (54, y))
    else:
        tu_treo(tu, tu_gt, 40, y, C0805)
        s.co_nguon((48, y))
        s.nguon("+5V", (54, y), "phai")
s.nhan("5V_SYS", (84, 108), "trai")
u2 = s.dat("Regulator_Linear:AMS1117-3.3", "U2", "TLV1117LV33", 104, 108, 0, MPN="TLV1117LV33DCYR")
s.w((84, 108), u2.p("VI"))
tu_treo("C3", "10u/25V", 90, 108, C0805)
s.nguon("GND", u2.p("GND"))
s.w(u2.p("VO"), (136, 108))
tu_treo("C4", "10u/25V", 118, 108, C0805)
tu_treo("C5", "10u/25V", 127, 108, C0805)
s.nguon("+3V3", (136, 108))
s.co_nguon((148, 112))
s.w((148, 112), (148, 116))
s.nguon("GND", (148, 116))
s.nguon("+3V3", (86, 136), "trai")
_, tr, ph = s.R("R9", "1k", 92, 136, ngang=True)
s.w((86, 136), tr)
led2 = s.dat("Device:LED_Small", "LED2", "NGUỒN", 99, 136, 180, FP["LED"], vt_ref=(0, -2.4), vt_gt=(0, 2.6))
s.w(ph, led2.p("2"))
s.w(led2.p("1"), (104, 136))
s.nguon("GND", (104, 136), "phai")

# ================= 3. ESP32-S3 =================
s.khoi(166, 14, 300, 150, "ESP32-S3-WROOM-1-N16R8", [
    "USB gốc trên GPIO19/20 (MicroBlocks dùng USB CDC): không cần IC chuyển USB–UART",
    "GPIO0 chỉ nối nút BOOT; GPIO3, 45, 46 (strapping) và GPIO35–37 (PSRAM) để hở",
    "Anten: không đổ đồng, không đi dây ở mọi lớp trong vùng anten",
])
u1 = s.dat("RF_Module:ESP32-S3-WROOM-1", "U1", "ESP32-S3-WROOM-1-N16R8", 240, 78, 0,
           MPN="ESP32-S3-WROOM-1-N16R8", LCSC="C2913202", Manufacturer="Espressif")
s.chia(u1, {
    "2": "+3V3", "1": "GND", "40": "GND", "41": "GND", "3": "EN", "27": "BOOT",
    "39": "A1_S1", "38": "A1_S2", "4": "A2_S1", "5": "A2_S2", "6": "A3_S1", "7": "A3_S2",
    "22": "D1_S1", "23": "D1_S2", "31": "D2_S1", "32": "D2_S2", "37": "D3_S1", "36": "D3_S2",
    "12": "SDA", "17": "SCL", "20": "SPI_SCK", "19": "SPI_MOSI", "21": "SPI_MISO", "18": "SPI_CS",
    "8": "SERVO1", "9": "SERVO2", "10": "SDA2", "11": "SCL2",
    "13": "USB_D-", "14": "USB_D+", "33": "BUZZER", "34": "BTN_A", "35": "BTN_B", "25": "RGB", "24": "IO47",
    "15": None, "26": None, "16": None, "28": None, "29": None, "30": None,
})
X = 182
tu_tach("C7", "10u/25V", X, 28, C0805)
tu_tach("C8", "10u/25V", X + 10, 28, C0805)
tu_tach("C9", "100n", X + 20, 28)
_, t, d = s.R("R4", "10k", X, 46)
s.nguon("+3V3", t)
_, t2, d2 = s.C("C10", "1u", X, 54)
s.w(d, t2)
s.w((X, 50), (X + 4, 50))
s.nhan("EN", (X + 4, 50))
s.nguon("GND", d2)
for ref, ten, gt, y in (("SW3", "EN", "RESET", 68), ("SW4", "BOOT", "BOOT", 80)):
    s.nhan(ten, (X, y), "trai")
    sw = s.dat("Switch:SW_Push", ref, gt, X + 6, y, 0, TS1088, vt_ref=(0, -4), vt_gt=(0, 2.6))
    s.w((X, y), sw.p("1"))
    s.nguon("GND", sw.p("2"), "phai")
s.nhan("IO47", (X, 92), "trai")
tp = s.dat("Connector:TestPoint", "TP1", "IO47", X + 8, 92, 0, FP["TP"], vt_ref=(3.5, -2), vt_gt=(3.5, 0))
tp.an_gt = True
s.w((X, 92), tp.p("1"))

# ================= 4. NÚT, CÒI, LED RGB =================
s.khoi(166, 154, 300, 226, "NÚT A, B · CÒI · LED RGB", [
    "LED RGB cấp 3V3 (cấp 5 V thì ngưỡng mức cao 3,5 V vượt tín hiệu 3,3 V)",
    "Còi thụ động, Q2 đóng cắt, D2 dập xung ngược",
])
for ref, ten, r, c, y in (("SW1", "BTN_A", "R5", "C11", 174), ("SW2", "BTN_B", "R6", "C12", 198)):
    s.nhan(ten, (182, y), "trai")
    sw = s.dat("Switch:SW_Push", ref, ten[-1], 200, y, 0, NUT6, vt_ref=(0, -4), vt_gt=(0, 2.6))
    s.w((182, y), sw.p("1"))
    _, t, d = s.R(r, "10k", 186, y - 4)
    s.nguon("+3V3", t)
    s.w(d, (186, y))
    _, t, d = s.C(c, "100n", 191, y + 4)
    s.w((191, y), t)
    s.nguon("GND", d)
    s.nguon("GND", sw.p("2"), "phai")
y = 182
s.nhan("BUZZER", (232, y), "trai")
_, tr, ph = s.R("R7", "100R", 238, y, ngang=True)
s.w((232, y), tr)
q2 = s.dat("Transistor_FET:AO3400A", "Q2", "AO3400A", 252, y, 0, SOT23, vt_ref=(7, 2), vt_gt=(8, 4.4), MPN="AO3400A")
s.w(ph, q2.p("G"))
_, t, d = s.R("R8", "10k", 244, y + 4)
s.w((244, y), t)
s.nguon("GND", d)
s.nguon("GND", q2.p("S"))
bz = s.dat("Device:Buzzer", "BZ1", "Còi thụ động", 268, 170, 0, "Buzzer_Beeper:Buzzer_Mallory_AST1109MLTRQ",
           vt_ref=(2, -5), vt_gt=(2, 5))
cong, tru = bz.p("1"), bz.p("2")
dq = q2.p("D")
s.w(dq, (dq[0], tru[1]), tru)
s.w(cong, (dq[0], cong[1]))
s.nguon("+3V3", (dq[0], cong[1]))
d2 = s.dat("Device:D_Small", "D2", "1N4148W", 260, 170, 270, "Diode_SMD:D_SOD-123", vt_ref=(-4.5, -1), vt_gt=(-5.5, 1), MPN="1N4148W")
assert d2.p("K") == (260, cong[1]) and d2.p("A") == (260, tru[1]), (d2.p("K"), d2.p("A"), cong, tru)
rgb = s.dat("LED:WS2812B-2020", "LED1", "WS2812B-2020", 280, 204, 0, MPN="WS2812B-2020")
s.nhan("RGB", (270, 204), "trai")
s.w((270, 204), rgb.p("DIN"))
s.nc(rgb.p("DOUT"))
s.nguon("+3V3", rgb.p("VDD"))
s.nguon("GND", rgb.p("VSS"))
tu_tach("C13", "100n", 292, 206)

# ================= 5. CỔNG =================
s.khoi(306, 14, 460, 92, "CỔNG RA: 6 D/A · 2 I2C1 + 2 I2C2 · SPI · 2 SERVO", [
    "Chân 1 = GND, chân 2 = 5 V ở mọi cổng.  D3 kiêm UART 1: S1 = TX (GPIO43), S2 = RX (GPIO44).  D2 kiêm UART 2: S1 = TX (GPIO38), S2 = RX (GPIO39)",
    "I2C1 (GPIO8/9, 100 kHz): module thường.  I2C2 (GPIO17/18, 400 kHz): module cần tốc độ cao (S1, S3)",
])


def cong(lib, ref, gt, x, y, chan):
    j = s.dat(lib, ref, gt, x, y, 0, vt_ref=(1, -(len(chan) + 3)), vt_gt=(1, len(chan) + 3))
    for ten, dich in chan:
        a = j.p(ten)
        if dich == "GND":
            b = (a[0] - 2, a[1])
            s.nguon("GND", b, "trai")
        elif dich == "+5V":
            b = (a[0] - 8, a[1])
            s.nguon("+5V", b, "trai")
        elif dich.startswith("G:"):
            b = (a[0] - 3, a[1])
            s.nhan(dich[2:], b, "trai")
        else:
            b = (a[0] - 3, a[1])
            s.ten_day(dich, b, "trai")
        s.w(a, b)


cot = [330 + 30 * i for i in range(5)]
da = ["A1", "A2", "A3", "D1", "D2", "D3"]
for i, t in enumerate(da):
    x, y = (cot[i], 32) if i < 5 else (cot[0], 54)
    cong("IRIS:Cong_DA", f"J{3 + i}", t, x, y, [("GND", "GND"), ("5V", "+5V"), ("S1", f"{t}_S1_J"), ("S2", f"{t}_S2_J")])
for i in range(4):
    b = "" if i < 2 else "2"
    cong("IRIS:Cong_I2C", f"J{9 + i}", f"I2C{i // 2 + 1}-{'AB'[i % 2]}", cot[1 + i], 54,
         [("GND", "GND"), ("5V", "+5V"), ("SDA", f"SDA{b}_J"), ("SCL", f"SCL{b}_J")])
cong("IRIS:Cong_SPI", "J13", "SPI", cot[0], 78, [("GND", "GND"), ("5V", "+5V"), ("SCK", "SPI_SCK_J"),
                                                 ("MOSI", "SPI_MOSI_J"), ("MISO", "SPI_MISO_J"), ("CS", "SPI_CS_J")])
for i in range(2):
    cong("IRIS:Cong_Servo", f"J{14 + i}", f"SERVO {i + 1}", cot[1 + i], 78,
         [("GND", "GND"), ("5V", "G:5V_SERVO"), ("PWM", f"SERVO{i + 1}_J")])

# ================= 6. ĐIỆN TRỞ NỐI TIẾP =================
s.khoi(306, 96, 460, 172, "ĐIỆN TRỞ NỐI TIẾP VÀ KÉO LÊN I2C", [
    "Thứ tự bắt buộc: đầu cắm → điện trở → (SRV05-4, chân ESP32).  Lỗi đưa 5 V vào: (5 − 3,3 − 0,7) / 220 = 4,5 mA",
    "Kéo lên 2k2 cho từng bus I2C, đặt phía đầu cắm; chỉ bo chủ có điện trở kéo lên",
])
tin = [f"{t}_S{k}" for t in da for k in (1, 2)] + [f"SERVO{i}" for i in range(1, 3)]
tin = [(t, "220R") for t in tin] + [(t, "100R") for t in ("SDA", "SCL", "SDA2", "SCL2", "SPI_SCK", "SPI_MOSI", "SPI_MISO", "SPI_CS")]
for i, (t, gt) in enumerate(tin):
    x0, y = 326 + 52 * (i // 8), 108 + 7 * (i % 8)
    s.nhan(t, (x0, y), "trai")
    _, tr, ph = s.R(f"R{30 + i}", gt, x0 + 4, y, ngang=True)
    s.w((x0, y), tr)
    s.w(ph, (x0 + 8, y))
    s.ten_day(t + "_J", (x0 + 8, y))
for ref, t, x in (("R20", "SDA_J", 434), ("R21", "SCL_J", 447), ("R22", "SDA2_J", 404), ("R23", "SCL2_J", 418)):
    _, tr, d = s.R(ref, "2k2", x, 158)
    s.nguon("+3V3", tr)
    s.w(d, (x, 163))
    s.ten_day(t, (x, 163))

# ================= 7. ESD =================
s.khoi(306, 176, 460, 246, "CHỐNG TĨNH ĐIỆN (SRV05-4, VP = +3V3)", [
    "Đặt sát chân ESP32, sau điện trở nối tiếp",
])
nhom = [t for t, _ in tin] + [None, None]
for i in range(6):
    x, y = 336 + 50 * (i % 3), 194 + 30 * (i // 3)
    u = s.dat("Power_Protection:SRV05-4", f"U{4 + i}", "SRV05-4", x, y, 0, MPN="SRV05-4")
    b = dict(zip(("1", "3", "4", "6"), nhom[4 * i:4 * i + 4]))
    b.update({"5": "+3V3", "2": "GND"})
    s.chia(u, b)

# ================= khung bo, ghi chú =================
s.khoi(10, 154, 160, 226, "CƠ KHÍ VÀ GHI CHÚ", [])
s.dat("IRIS:Khung_C1_64x48", "KH1", "Khung_C1_64x48", 30, 174, 0, vt_ref=(0, -6), vt_gt=(0, 6))
for i, g in enumerate((
    "Bo 64 × 48 mm, lỗ gá Ø3,2 theo lưới 8 mm (nằm trong chân linh kiện KH1).",
    "Mọi R, C nhỏ: 0603 1 % / 50 V; tụ 10 µF: 0805 25 V.",
    "Không đặt tụ lọc trên cổng A1–A3: còn dùng làm cổng số tốc độ cao.",
    "GPIO43 (D3-S1) phát thông báo khởi động của ROM mỗi lần reset.",
    "I2C1 100 kHz (2k2, bus 300 pF: lên 560 ns).  I2C2 400 kHz: bus tối đa 150 pF (lên 280 ns).",
    "Chân linh kiện của còi là tạm: chọn còi thụ động SMD rồi đổi cho khớp.",
    "Thiết kế: hardware/THIET-KE-MACH.md mục 6.",
)):
    s.chu(g, 44, 166 + 4 * i)

tep_du_an(DAY, "C1")
s.ghi(os.path.join(DAY, "C1.kicad_sch"))
print(len([k for k in s.lk if not k.ref.startswith("#")]), "linh kiện")
