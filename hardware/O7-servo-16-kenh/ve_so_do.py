"""Sinh bản sơ đồ nguyên lý đầu tiên của O7 – 16 kênh servo.

Chạy: PYTHONUTF8=1 python ve_so_do.py
Thiết kế: ../THIET-KE-MACH.md mục 8. Toạ độ theo lưới 1,27 mm.
Kịch bản ghi đè O7.kicad_sch; không chạy lại sau khi đã sửa sơ đồ bằng tay.
"""
import os
import sys

DAY = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(DAY, "..", "common"))
from sch import FP, SoDo  # noqa: E402
from khoi_chung import C0805, gop, khoi_buck, khoi_i2c, khoi_ldo, tep_du_an, tu_treo  # noqa: E402

s = SoDo("O7", "O7 - 16 kênh servo", "A3", "0.1", "2026-11-15")
khoi_ldo(s, 10, 14)
khoi_i2c(s, 10, 54)

# ================= nguồn động lực =================
s.khoi(10, 112, 134, 150, "NGUỒN ĐỘNG LỰC VÀO (6–8,4 V TỪ C2)", [
    "Q1 chống ngược cực: D về XT30, S về VM, G xuống GND qua R5",
])
Y = 126
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
s.w(q1.p("1"), (92, Y))
s.co_nguon((48, Y))
tu_treo(s, "C5", "10u/25V", 56, Y, C0805)
_, t, d = s.R("R6", "10k", 70, Y + 4)
s.w((70, Y), t)
led1 = s.dat("Device:LED_Small", "LED1", "VM", 70, Y + 10, 90, FP["LED"], vt_ref=(4, -1.1), vt_gt=(4, 1.1))
s.w(d, led1.p("2"))
s.nguon("GND", led1.p("1"))
s.nhan("VM", (92, Y))

# ================= buck =================
khoi_buck(s, 10, 154, "VM", "+5VP", "U4", "L1",
          ["C6", "C7", "C8", "C9", "C10", "C11", "C12"], ["R7", "R8", "R9", "R10"], co_ra=True)

# ================= PCA9685 =================
s.khoi(140, 14, 250, 108, "PCA9685PW – 16 KÊNH PWM 12 BIT", [
    "Địa chỉ 0x41 (A0 = 1); hàn JP1 thành 0x43.  0x40 đã dành cho INA219 trên C2",
    "Phần mềm: MODE2.OUTDRV = 1 (totem-pole), tần số 50 Hz; OE kéo xuống: luôn cho phép ra",
])
u1 = s.dat("Driver_LED:PCA9685PW", "U1", "PCA9685PW", 204, 58, 0, vt_ref=(-8, -19), vt_gt=(10, 19),
           MPN="PCA9685PW", LCSC="C2678753", Manufacturer="NXP")
bang = {"26": "SCL", "27": "SDA", "23": "OE", "1": "+3V3", "2": "A1", "28": "+3V3", "14": "GND"}
bang.update({str(6 + i): f"PWM{i + 1}" for i in range(8)})
bang.update({str(15 + i): f"PWM{i + 9}" for i in range(8)})
s.chia(u1, bang)
gop(s, u1, ["3", "4", "5", "24"], "GND", cuoi=True)
a = u1.p("25")
s.w(a, (a[0] - 10, a[1]))
s.nguon("GND", (a[0] - 10, a[1]), "trai")
X = 150
for ref, gt, x, fp in (("C3", "100n", X, None), ("C4", "10u/25V", X + 9, C0805)):
    _, t, d = s.C(ref, gt, x, 30, fp)
    s.nguon("+3V3", t)
    s.nguon("GND", d)
_, t, d = s.R("R3", "10k", X, 50)
s.w(t, (X, 46), (X + 4, 46))
s.nhan("OE", (X + 4, 46))
s.nguon("GND", d)
_, t, d = s.R("R4", "10k", X, 82)
s.w(t, (X, 76), (X + 4, 76))
s.nhan("A1", (X + 4, 76))
s.nguon("GND", d)
jp = s.dat("Jumper:SolderJumper_2_Open", "JP1", "0x43", X + 12, 70, 0, FP["JP2"], vt_ref=(0, -3), vt_gt=(0, 3))
s.w(jp.p("1"), (X, 70), (X, 76))
s.nguon("+3V3", jp.p("2"), "phai")

# ================= điện trở nối tiếp =================
s.khoi(140, 112, 250, 196, "ĐIỆN TRỞ NỐI TIẾP 16 KÊNH", [
    "220 Ω bảo vệ đầu ra khi cắm nhầm hoặc chập dây tín hiệu servo",
])
for i in range(16):
    x0, y = 158 + 48 * (i // 8), 124 + 8 * (i % 8)
    s.nhan(f"PWM{i + 1}", (x0, y), "trai")
    _, tr, ph = s.R(f"R{20 + i}", "220R", x0 + 4, y, ngang=True)
    s.w((x0, y), tr)
    s.w(ph, (x0 + 8, y))
    s.ten_day(f"SV{i + 1}", (x0 + 8, y))

# ================= cổng servo =================
s.khoi(254, 14, 320, 150, "16 CỔNG SERVO (GND · V+ · PWM)", [
    "V+ = 5,45 V từ buck.  C13 đặt giữa dãy cổng",
])
for i in range(16):
    x, y = 277 + 31 * (i // 8), 28 + 12 * (i % 8)
    j = s.dat("IRIS:Cong_Servo", f"J{4 + i}", f"S{i + 1}", x, y, 0, vt_ref=(7.5, -1.2), vt_gt=(7.5, 1.2))
    for ten, dich in (("GND", "GND"), ("5V", "+5VP"), ("PWM", f"SV{i + 1}")):
        a = j.p(ten)
        if dich == "GND":
            b = (a[0] - 2, a[1])
            s.nguon("GND", b, "trai")
        elif dich == "+5VP":
            b = (a[0] - 8, a[1])
            s.nguon("+5VP", b, "trai")
        else:
            b = (a[0] - 3, a[1])
            s.ten_day(dich, b, "trai")
        s.w(a, b)
_, t, d = s.doc("Device:C_Polarized_Small", "C13", "470u/16V", 268, 132, "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm")
s.nguon("+5VP", t)
s.nguon("GND", d)
_, t, d = s.C("C14", "10u/25V", 284, 132, C0805)
s.nguon("+5VP", t)
s.nguon("GND", d)
_, t, d = s.C("C15", "10u/25V", 300, 132, C0805)
s.nguon("+5VP", t)
s.nguon("GND", d)

# ================= khung bo, ghi chú =================
s.khoi(254, 154, 320, 196, "CƠ KHÍ VÀ GHI CHÚ", [])
s.dat("IRIS:Khung_L_48x64", "KH1", "Khung_L_48x64", 268, 170, 0, vt_ref=(0, -6), vt_gt=(0, 6))
for i, g in enumerate((
    "Bo 48 × 64 mm, lỗ gá Ø3,2 (trong KH1).",
    "Logic lấy 5 V từ cổng I2C; servo lấy từ XT30.",
    "R, C nhỏ: 0603; tụ 10 µF, 22 µF: 0805.",
    "Thiết kế: THIET-KE-MACH.md mục 8.",
)):
    s.chu(g, 280, 166 + 4 * i)

tep_du_an(DAY, "O7")
s.ghi(os.path.join(DAY, "O7.kicad_sch"))
print(len([k for k in s.lk if not k.ref.startswith("#")]), "linh kiện")
