"""Sinh bản sơ đồ nguyên lý đầu tiên của S3 – IMU trả góc.

Chạy: PYTHONUTF8=1 python ve_so_do.py
Thiết kế: ../THIET-KE-MACH.md mục 2 và 5. Toạ độ theo lưới 1,27 mm.
Kịch bản ghi đè S3.kicad_sch; không chạy lại sau khi đã sửa sơ đồ bằng tay.
"""
import os
import sys

DAY = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(DAY, "..", "common"))
from sch import FP, SoDo  # noqa: E402
from khoi_chung import C0805, khoi_i2c, khoi_ldo, khoi_mcu, tep_du_an, tu_treo  # noqa: E402

s = SoDo("S3", "S3 - IMU trả góc", "A3", "0.1", "2026-11-15")
khoi_ldo(s, 10, 14)
khoi_i2c(s, 10, 54)
khoi_mcu(s, 130, 14, {
    "9": "UART_TX", "10": "UART_RX",
    "11": "IMU_CS", "12": "IMU_SCK", "13": "IMU_MISO", "14": "IMU_MOSI", "15": "IMU_INT", "18": "LED",
}, [
    "SPI1 (PA5, PA6, PA7) đọc IMU 1 kHz; I2C1 (PB6, PB7) chỉ làm tớ, địa chỉ 0x36",
    "PA14 = SWCLK kiêm BOOT0: R3 kéo xuống.  Không dùng PA9–PA12",
], tps=("+3V3", "SWDIO", "SWCLK", "NRST", "GND", "UART_TX", "UART_RX"))

# ================= IMU =================
s.khoi(10, 112, 124, 196, "IMU 6 TRỤC LSM6DS3TR-C", [
    "Nguồn riêng V_IMU qua ferrite.  R5 giữ CS cao lúc cấp nguồn để IC vào chế độ SPI",
    "Đặt IC đúng tâm bo, không đi dây và via bên dưới, xa lỗ gá",
])
Y = 126
s.nguon("+3V3", (18, Y))
fb = s.dat("Device:FerriteBead_Small", "FB2", "600R", 26, Y, 90, FP["FB"], vt_ref=(0, -2.4), vt_gt=(0, 2.6))
s.w((18, Y), fb.p("1"))
s.w(fb.p("2"), (52, Y))
s.co_nguon((48, Y))
tu_treo(s, "C20", "10u/25V", 33, Y, C0805)
tu_treo(s, "C21", "100n", 41, Y)
s.nhan("V_IMU", (52, Y))
u5 = s.dat("Sensor_Motion:LSM6DS3", "U5", "LSM6DS3TR-C", 84, 158, 0,
           MPN="LSM6DS3TR-C", LCSC="C967633", Manufacturer="STMicroelectronics")
s.chia(u5, {"1": "IMU_MISO", "12": "IMU_CS", "13": "IMU_SCK", "14": "IMU_MOSI",
            "4": "IMU_INT", "9": None, "10": None, "11": None, "6": "GND"})
# VDDIO (5) và VDD (8) gộp về V_IMU
a, b = u5.p("5"), u5.p("8")
s.w(a, (a[0], a[1] - 3), (b[0] + 4, a[1] - 3))
s.w(b, (b[0], b[1] - 3))
s.nhan("V_IMU", (b[0] + 4, a[1] - 3))
# SDX (2), SCX (3) về GND
a, b = u5.p("2"), u5.p("3")
s.w(a, (a[0] - 3, a[1]), (a[0] - 3, b[1]))
s.w(b, (b[0] - 7, b[1]))
s.nguon("GND", (b[0] - 7, b[1]), "trai")
# kéo lên CS
_, t, d = s.R("R5", "10k", 26, 162)
s.w(t, (26, 158), (30, 158))
s.nhan("V_IMU", (30, 158))
s.w(d, (26, 166), (30, 166))
s.nhan("IMU_CS", (30, 166))

# ================= khung bo, ghi chú =================
s.khoi(130, 154, 250, 196, "CƠ KHÍ VÀ GHI CHÚ", [])
s.dat("IRIS:Khung_S3_32x32", "KH1", "Khung_S3_32x32", 150, 172, 0, vt_ref=(0, -6), vt_gt=(0, 6))
for i, g in enumerate((
    "Bo 32 × 32 mm, lỗ gá Ø3,2 theo lưới 8 mm (nằm trong chân linh kiện KH1).",
    "Mọi R, C nhỏ: 0603 1 % / 50 V; tụ 10 µF: 0805 25 V.",
    "IC thay thế cùng vỏ LGA-14 (ICM-42670-P, BMI270) khác vài chân: phải đối chiếu.",
    "Thiết kế: hardware/THIET-KE-MACH.md mục 2, 5.",
)):
    s.chu(g, 164, 166 + 4 * i)

tep_du_an(DAY, "S3")
s.ghi(os.path.join(DAY, "S3.kicad_sch"))
print(len([k for k in s.lk if not k.ref.startswith("#")]), "linh kiện")
