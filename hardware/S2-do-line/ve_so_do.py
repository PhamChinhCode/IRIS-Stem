"""Sinh bản sơ đồ nguyên lý đầu tiên của S2 – dò line 8 mắt.

Chạy: PYTHONUTF8=1 python ve_so_do.py
Thiết kế: ../THIET-KE-MACH.md mục 2 và 4. Toạ độ theo lưới 1,27 mm.
Kịch bản ghi đè S2.kicad_sch; không chạy lại sau khi đã sửa sơ đồ bằng tay.
"""
import os
import sys

DAY = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(DAY, "..", "common"))
from sch import SoDo  # noqa: E402
from khoi_chung import khoi_i2c, khoi_ldo, khoi_mcu, tep_du_an  # noqa: E402

s = SoDo("S2", "S2 - Dò line 8 mắt", "A3", "0.1", "2026-11-15")
khoi_ldo(s, 10, 14)
khoi_i2c(s, 10, 54)
bang = {str(7 + i): f"MAT{i + 1}" for i in range(8)}
bang.update({"15": "IR_EN", "18": "LED"})
khoi_mcu(s, 130, 14, bang, [
    "PA0–PA7 = ADC1_IN0…IN7 đọc 8 mắt; PB0 phát xung LED hồng ngoại; I2C 0x34",
    "PA14 = SWCLK kiêm BOOT0: R3 kéo xuống.  Không dùng PA9–PA12",
])

# ================= 8 mắt đọc =================
s.khoi(10, 154, 178, 224, "8 MẮT PHẢN XẠ ITR8307 (MẶT DƯỚI BO, BƯỚC 9 mm)", [
    "LED: 4 chuỗi × 2 LED nối tiếp từ 5 V: (5 − 2×1,2) / 100 Ω ≈ 25 mA, phát xung 20 %.  Tải phototransistor 47k: chỉnh khi thử",
])
for k in range(4):
    x = 34 + 40 * k
    op = []
    for j, y in enumerate((178, 200)):
        n = 2 * k + j + 1
        o = s.dat("IRIS:Mat_ITR8307", f"OP{n}", "ITR8307", x, y, 0, MPN="ITR8307/S17/TR8(B)")
        op.append(o)
        c, e = o.p("C"), o.p("E")
        s.w(c, (x + 13, c[1]))
        _, t, d = s.R(f"R{33 + n}", "47k", x + 10, c[1] - 4)
        s.nguon("+3V3", t)
        s.w(d, (x + 10, c[1]))
        s.nhan(f"MAT{n}", (x + 13, c[1]))
        s.w(e, (e[0] + 2, e[1]))
        s.nguon("GND", (e[0] + 2, e[1]), "phai")
    a = op[0].p("A")
    _, t, d = s.R(f"R{30 + k}", "100R", a[0], a[1] - 6)
    s.nguon("+5V", t)
    s.w(d, a)
    s.w(op[0].p("K"), op[1].p("A"))
    kk = op[1].p("K")
    s.w(kk, (kk[0] - 3, kk[1]))
    s.nhan("IR_K", (kk[0] - 3, kk[1]), "trai")

# ================= đóng cắt LED =================
s.khoi(254, 14, 322, 100, "ĐÓNG CẮT LED HỒNG NGOẠI", [
    "Đo 2 lần mỗi chu kỳ (LED bật / tắt)",
    "rồi trừ nhau để loại ánh sáng nền",
])
q2 = s.dat("Transistor_FET:AO3400A", "Q2", "AO3400A", 296, 44, 0, vt_ref=(7, -1.2), vt_gt=(8, 1.2), MPN="AO3400A")
g, d_, s_ = q2.p("G"), q2.p("D"), q2.p("S")
s.w(d_, (d_[0], 34), (d_[0] + 4, 34))
s.nhan("IR_K", (d_[0] + 4, 34))
s.w(s_, (s_[0], s_[1] + 2))
s.nguon("GND", (s_[0], s_[1] + 2))
s.nhan("IR_EN", (272, 44), "trai")
_, tr, ph = s.R("R42", "100R", 277, 44, ngang=True)
s.w((272, 44), tr)
s.w(ph, g)
_, t, d = s.R("R43", "10k", 285, 48)
s.w((285, 44), t)
s.nguon("GND", d)

# ================= khung bo, ghi chú =================
s.khoi(254, 104, 322, 196, "CƠ KHÍ VÀ GHI CHÚ", [])
s.dat("IRIS:Khung_S2_80x24", "KH1", "Khung_S2_80x24", 288, 122, 0, vt_ref=(0, -6), vt_gt=(0, 6))
for i, g in enumerate((
    "Bo 80 × 24 mm, lỗ gá Ø3,2 (trong KH1).",
    "8 mắt ở mặt dưới: lắp hai mặt hoặc hàn tay.",
    "ITR8307 nhạy nhất ở 1 mm; bản cơ khí",
    "đang để 5,9 mm: phải thử trên bản mẫu.",
    "R, C nhỏ: 0603; tụ 10 µF: 0805 25 V.",
    "Thiết kế: THIET-KE-MACH.md mục 2, 4.",
)):
    s.chu(g, 258, 138 + 4 * i)

tep_du_an(DAY, "S2")
s.ghi(os.path.join(DAY, "S2.kicad_sch"))
print(len([k for k in s.lk if not k.ref.startswith("#")]), "linh kiện")
