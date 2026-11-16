"""Sinh bản sơ đồ nguyên lý đầu tiên của 19 bo mang (I1–I14, O1–O5).

Chạy: PYTHONUTF8=1 python ve_so_do.py [mã bo ...]     (không ghi mã: sinh tất cả)
Thiết kế: ../THIET-KE-MACH.md mục 10. Toạ độ theo lưới 1,27 mm, khổ A4.
Kịch bản ghi đè <mã>/<mã>.kicad_sch; không chạy lại cho bo đã sửa sơ đồ bằng tay.
"""
import os
import sys

DAY = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(DAY, "..", "common"))
from sch import FP, SoDo  # noqa: E402
from khoi_chung import gop, tep_du_an  # noqa: E402

NUT6 = "Button_Switch_SMD:SW_Push_1TS009xxxx-xxxx-xxxx_6x6x5mm"
HANG = "Connector_PinSocket_2.54mm:PinSocket_1x%02d_P2.54mm_Vertical"
KHUNG = {"S": "Khung_S_24x32", "M": "Khung_M_32x48", "L": "Khung_L_48x64", "T": "Khung_T_64x24", "Que": "Khung_Que_24x96"}
CONG = {"DA": ("IRIS:Cong_DA", ("S1", "S2")), "I2C": ("IRIS:Cong_I2C", ("SDA", "SCL")),
        "SPI": ("IRIS:Cong_SPI", ("SCK", "MOSI", "MISO", "CS"))}
# kiểu: (ký hiệu, chân linh kiện, tiền tố ref, chiều dài ô, góc khi đặt dọc, góc khi đặt ngang)
KIEU = {
    "R": ("Device:R_Small", FP["R"], "R", 8, 0, 90),
    "C": ("Device:C_Small", FP["C"], "C", 8, 0, 90),
    "LED": ("Device:LED_Small", FP["LED"], "LED", 8, 90, 180),
    "D": ("Device:D_Small", "Diode_SMD:D_SOD-123", "D", 8, 90, 180),
    "DS": ("Device:D_Schottky_Small", "Diode_SMD:D_SMA", "D", 8, 90, 180),
    "SW": ("Switch:SW_Push", NUT6, "SW", 12, 90, 0),
    "LDR": ("Device:R_Photo", "OptoDevice:R_LDR_5.1x4.3mm_P3.4mm_Vertical", "R", 8, 0, 90),
}
NGUON = ("GND", "+5V", "+3V3")


class Bo:
    def __init__(self, ma, ten, khung, cong="DA", bo_qua=(), fp_cong=None):
        self.ma = ma
        self.s = s = SoDo(ma, f"{ma} - {ten}", "A4", "0.1", "2026-11-15")
        self.dem = {}
        self.khung, self.ghi_chu = khung, []
        s.khoi(10, 14, 222, 104, ten.upper(), [])
        lib, tin = CONG[cong]
        j = s.dat(lib, "J1", cong, 20, 30, 180, fp_cong or "", vt_ref=(-2, -8), vt_gt=(-2, 8))
        for chan, dich in (("GND", "GND"), ("5V", "+5V")) + tuple((t, None if t in bo_qua else t) for t in tin):
            a = j.p(chan)
            if dich is None:
                s.nc(a)
                continue
            b = (a[0] + 4, a[1])
            s.w(a, b)
            if dich in NGUON:
                s.nguon(dich, b, "phai")
            else:
                s.nhan(dich, b)
        s.nguon("+5V", (16, 56))
        s.w((16, 56), (22, 56))
        s.co_nguon((22, 56))
        s.nguon("GND", (34, 58))
        s.w((34, 58), (34, 54))
        s.co_nguon((34, 54))

    def ref(self, tt):
        self.dem[tt] = self.dem.get(tt, 0) + 1
        return f"{tt}{self.dem[tt]}"

    def chuoi(self, x, y, dau, ds, doc=True):
        """Chuỗi linh kiện 2 chân nối tiếp từ (x, y): dau → [(kiểu, giá trị, lưới sau nó | None), ...].

        Lưới cuối là nhãn hoặc ký hiệu nguồn; lưới giữa (chỉ chuỗi dọc) là nhãn rẽ sang phải.
        """
        s = self.s
        if dau in NGUON:
            s.nguon(dau, (x, y), "len" if doc else "trai")
        else:
            s.nhan(dau, (x, y), "trai")
        p = (x, y)
        for i, (kieu, gt, luoi) in enumerate(ds):
            lib, fp, tt, dai, gd, gn = KIEU[kieu]
            if kieu == "C" and gt[:3] in ("10u", "22u"):
                fp = FP["C0805"]
            r = self.ref(tt)
            if doc:
                tam, cuoi = (x, p[1] + dai / 2), (x, p[1] + dai)
                lech = lambda t: (4 if kieu == "SW" else 1.6) + 0.47 * len(t)
                k = s.dat(lib, r, gt, tam[0], tam[1], gd, fp, vt_ref=(lech(r), -1.1), vt_gt=(lech(gt), 1.1))
            else:
                tam, cuoi = (p[0] + dai / 2, y), (p[0] + dai, y)
                k = s.dat(lib, r, gt, tam[0], tam[1], gn, fp, vt_ref=(0, -3.4 if kieu == "SW" else -2.4), vt_gt=(0, 2.6))
            chan = sorted((k.p("1"), k.p("2")), key=lambda c: c[1] if doc else c[0])
            s.w(p, chan[0])
            s.w(chan[1], cuoi)
            p = cuoi
            if luoi is None:
                continue
            if i == len(ds) - 1:
                if luoi in NGUON:
                    s.nguon(luoi, p, ("xuong" if doc else "phai"))
                else:
                    s.nhan(luoi, p)
            else:
                assert doc, "lưới giữa chỉ dùng cho chuỗi dọc"
                s.w(p, (x + 3, p[1]))
                s.nhan(luoi, (x + 3, p[1]))

    def cot(self, x, y, dau, ds):
        self.chuoi(x, y, dau, ds, True)

    def hang(self, x, y, dau, ds):
        self.chuoi(x, y, dau, ds, False)

    def ic(self, lib, ref, gt, x, y, bang, dai=4, fp="", **kw):
        k = self.s.dat(lib, ref, gt, x, y, 0, fp, **kw)
        self.s.chia(k, bang, dai)
        return k

    def tp(self, x, y, luoi, ten):
        """Điểm hàn / vùng đồng nối với `luoi`."""
        s = self.s
        t = s.dat("Connector:TestPoint", self.ref("TP"), ten, x + 6, y, 0, FP["TP"], vt_ref=(3.5, -2), vt_gt=(5, 0))
        s.w((x, y), t.p("1"))
        if luoi in NGUON:
            s.nguon(luoi, (x, y), "trai")
        else:
            s.nhan(luoi, (x, y), "trai")

    def ldo(self, x=72, y=86, ic="XC6206"):
        """Ổn áp 3,3 V từ 5 V của cổng: XC6206P332MR (200 mA) hoặc AP2112K-3.3 (600 mA)."""
        s = self.s
        s.nguon("+5V", (x - 20, y))
        s.nguon("+3V3", (x + 20, y))
        if ic == "XC6206":
            u = s.dat("Regulator_Linear:XC6206PxxxMR", self.ref("U"), "XC6206P332MR", x, y, 0, MPN="XC6206P332MR")
            vi, vo, gt = u.p("VI"), u.p("VO"), "1u"
        else:
            u = s.dat("Regulator_Linear:AP2112K-3.3", self.ref("U"), "AP2112K-3.3", x, y + 2, 0, MPN="AP2112K-3.3TRG1")
            vi, vo, gt = u.p("VIN"), u.p("VOUT"), "10u/25V"
            s.w(u.p("EN"), (x - 9, u.p("EN")[1]), (x - 9, y))
            s.nc(u.p("NC"))
        s.w((x - 20, y), vi)
        s.w(vo, (x + 20, y))
        s.nguon("GND", u.p("GND"))
        for xc in (x - 14, x + 12):
            _, t, d = s.doc("Device:C_Small", self.ref("C"), gt, xc, y + 4, FP["C0805" if gt[0:2] == "10" else "C"])
            s.w((xc, y), t)
            s.nguon("GND", d)
        self.ghi_chu.append("3V3 tạo tại chỗ từ 5 V của cổng; tín hiệu về bo chủ luôn ở mức 3,3 V.")

    def xong(self, *ghi_chu):
        s = self.s
        s.khoi(10, 108, 140, 156, "CƠ KHÍ VÀ GHI CHÚ", [])
        kh = KHUNG[self.khung]
        s.dat("IRIS:" + kh, "KH1", kh, 24, 126, 0, vt_ref=(0, -6), vt_gt=(0, 6))
        w, h = kh.rsplit("_", 1)[1].split("x")
        ds = [f"Bo {w} × {h} mm (khung {self.khung}), lỗ gá Ø3,2 trong KH1."] + list(ghi_chu) + self.ghi_chu
        ds.append("R, C nhỏ: 0603.  Thiết kế: THIET-KE-MACH.md mục 10.")
        for i, g in enumerate(ds):
            s.chu(g, 38, 118 + 4 * i)
        refs = [k.ref for k in s.lk]
        assert len(refs) == len(set(refs)), sorted(r for r in set(refs) if refs.count(r) > 1)
        d = os.path.join(DAY, self.ma)
        os.makedirs(d, exist_ok=True)
        tep_du_an(d, self.ma, "../../common")
        s.ghi(os.path.join(d, self.ma + ".kicad_sch"))
        print(self.ma, len([k for k in s.lk if not k.ref.startswith("#")]), "linh kiện")


# ============================================================ module vào
def I1():
    b = Bo("I1", "2 nút nhấn", "S")
    for i, x in ((1, 64), (2, 144)):
        t = f"S{i}"
        b.cot(x, 26, "+5V", [("R", "10k", t), ("R", "10k", None), ("R", "10k", "GND")])
        b.cot(x + 26, 34, t, [("C", "100n", "GND")])
        b.cot(x + 44, 34, t, [("SW", "A" if i == 1 else "B", "GND")])
    b.xong("Mức nghỉ = 5 V × 20k / 30k = 3,33 V, không phụ thuộc kéo lên nội của bo chủ.",
           "Nhấn nút: tín hiệu về 0 V.  C1, C2 chống dội (τ ≈ 0,7 ms).")


def I2():
    b = Bo("I2", "Biến trở", "S", bo_qua=("S2",))
    b.ldo()
    b.ic("Device:R_Potentiometer", "RV1", "10k", 70, 36, {"1": "+3V3", "3": "GND", "2": "WIPER"}, 3,
         "Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical", vt_ref=(-5, -1.2), vt_gt=(-5, 1.2))
    b.hang(100, 36, "WIPER", [("R", "1k", "S1")])
    b.cot(130, 36, "S1", [("C", "100n", "GND")])
    b.xong("Con chạy → 1 k → S1; C lọc nhiễu, cũng là nguồn nạp cho tụ lấy mẫu ADC.")


def I3():
    b = Bo("I3", "Joystick 2 trục", "M")
    b.ldo()
    b.ic("Connector_Generic:Conn_01x05", "J2", "Joystick", 76, 36,
         {"1": "GND", "2": "+3V3", "3": "VRX", "4": "VRY", "5": None}, fp=HANG % 5)
    for t, v, y in (("S1", "VRX", 30), ("S2", "VRY", 52)):
        b.hang(104, y, v, [("R", "1k", t)])
        b.cot(134, y, t, [("C", "100n", "GND")])
    b.xong("J2: đế cho module joystick 5 chân (GND, +5V, VRx, VRy, SW); cấp 3V3 vào chân +5V của module.",
           "Nút nhấn của joystick (chân 5) không nối: cổng chỉ có 2 tín hiệu.",
           "Thứ tự chân module phải đối chiếu với module mua thực tế.")


def I4():
    b = Bo("I4", "Bàn phím 4 × 4 (PCF8574)", "L", cong="I2C")
    b.ldo()
    bang = {"16": "+3V3", "8": "GND", "14": "SCL", "15": "SDA", "13": None}
    bang.update({str(4 + i): f"H{i + 1}" for i in range(4)})
    bang.update({str(9 + i): f"C{i + 1}" for i in range(4)})
    u = b.ic("Interface_Expansion:PCF8574T", "U2", "PCF8574T", 80, 44, bang, MPN="PCF8574T")
    gop(b.s, u, ["1", "2", "3"], "GND", cuoi=True)
    b.cot(110, 24, "+3V3", [("C", "100n", "GND")])
    phim = "123A456B789C*0#D"
    for i in range(16):
        r, c = divmod(i, 4)
        b.hang(128 + 22 * c, 46 + 12 * r, f"H{r + 1}", [("SW", phim[i], f"C{c + 1}")])
    b.xong("Địa chỉ 0x20 (A0–A2 = GND).  Không dùng bản PCF8574A (dải địa chỉ khác).",
           "Quét: kéo từng hàng H xuống 0, đọc 4 cột C (cổng gần như hở cực máng, có kéo lên yếu).",
           "Không có diode: nhấn 3 phím cùng lúc có thể ra phím ma.")


def I5():
    b = Bo("I5", "Cảm biến ánh sáng (LDR)", "S", bo_qua=("S2",))
    b.ldo()
    b.cot(72, 26, "+3V3", [("LDR", "GL5528", "S1"), ("R", "10k", "GND")])
    b.xong("Sáng: LDR khoảng 10–20 k → S1 cao.  Tối: LDR trên 1 M → S1 gần 0 V.")


def I6():
    b = Bo("I6", "Nhiệt độ, độ ẩm (AHT20)", "S", cong="I2C")
    b.ldo()
    b.ic("IRIS:AHT20", "U2", "AHT20", 86, 40, {"2": "+3V3", "5": "GND", "3": "SCL", "4": "SDA", "1": None, "6": None},
         vt_ref=(0, -7), vt_gt=(0, 7), MPN="AHT20")
    b.cot(124, 30, "+3V3", [("C", "100n", "GND")])
    b.xong("Địa chỉ 0x38.  Không đặt điện trở kéo lên I2C trên module.",
           "AHT20 chưa có chân linh kiện trong thư viện: vẽ theo datasheet trước khi layout.",
           "Đặt cảm biến xa ổn áp, khoét rãnh cách nhiệt quanh cảm biến.")


def I7():
    b = Bo("I7", "Cảm biến chuyển động (PIR AM312)", "S", bo_qua=("S2",))
    b.ic("Connector_Generic:Conn_01x03", "J2", "AM312", 76, 36, {"1": "+5V", "2": "PIR_OUT", "3": "GND"}, fp=HANG % 3)
    b.hang(104, 36, "PIR_OUT", [("R", "1k", "S1")])
    b.xong("AM312 cấp 2,7–12 V, đầu ra 3 V khi có chuyển động.",
           "Thứ tự chân (+, OUT, −) phải đối chiếu với module mua thực tế.")


def I8():
    b = Bo("I8", "Cảm biến khí gas (MQ-2)", "M", bo_qua=("S2",))
    b.ic("Sensor_Gas:MQ-6", "U1", "MQ-2", 80, 42,
         {"6": "+5V", "4": "+5V", "2": "+5V", "5": "GND", "1": "MQ_OUT", "3": "MQ_OUT"}, MPN="MQ-2")
    b.cot(126, 28, "MQ_OUT", [("R", "4k7", "S1"), ("R", "10k", "GND")])
    b.cot(152, 36, "S1", [("C", "100n", "GND")])
    b.cot(176, 28, "+5V", [("C", "10u/25V", "GND")])
    b.xong("Sợi đốt 5 V, khoảng 160 mA.  Tải 14k7 chia 4k7 / 10 k: S1 tối đa 5 × 10 / 14,7 = 3,4 V.",
           "Cần sấy nóng vài phút trước khi đọc ổn định.")


def I9():
    b = Bo("I9", "Độ ẩm đất điện dung (TLC555)", "Que", bo_qua=("S2",))
    b.ldo()
    u = b.ic("Timer:TLC555xD", "U2", "TLC555CDR", 84, 42,
             {"8": "+3V3", "1": "GND", "4": "+3V3", "5": None, "7": "DISCH", "3": "OUT555"}, MPN="TLC555CDR")
    gop(b.s, u, ["6", "2"], "THRES")
    b.cot(118, 22, "+3V3", [("R", "1k", "DISCH"), ("R", "1k", "THRES"), ("C", "1n", "GND")])
    b.cot(146, 22, "+3V3", [("C", "100n", "GND")])
    b.hang(132, 56, "OUT555", [("R", "10k", "BAN_CUC")])
    b.hang(132, 68, "BAN_CUC", [("D", "1N4148W", "DO")])
    b.cot(166, 68, "DO", [("C", "1u", "GND")])
    b.cot(180, 68, "DO", [("R", "1M", "GND")])
    b.hang(196, 56, "DO", [("R", "1k", "S1")])
    b.tp(176, 30, "BAN_CUC", "Bản cực A")
    b.tp(176, 40, "GND", "Bản cực B")
    b.xong("f = 1,44 / ((R_A + 2 R_B) × C) = 1,44 / (3 k × 1 nF) ≈ 480 kHz.",
           "Đất ẩm → điện dung giữa hai bản cực tăng → biên độ tại bản cực A giảm → S1 giảm.",
           "TP1, TP2 là hai vùng đồng phủ lớp cách điện ở phần que cắm xuống đất (vẽ khi layout).",
           "Giá trị R4, C5, R6 chốt khi thử trên bản mẫu.")


def I10():
    b = Bo("I10", "Cảm biến mưa / mực nước (lược đồng)", "M", bo_qua=("S2",))
    b.ldo()
    b.tp(70, 30, "+3V3", "Lược A")
    b.tp(70, 44, "S1", "Lược B")
    b.cot(110, 30, "S1", [("R", "100k", "GND")])
    b.xong("Khô: S1 = 0 V.  Có nước nối hai lược: S1 tăng theo độ dẫn của nước.",
           "TP1, TP2 là hai lược đồng trần đan vào nhau; mạ ENIG để chống ăn mòn.")


def I11():
    b = Bo("I11", "Siêu âm (đế HC-SR04)", "T", fp_cong="IRIS:Cong_PH_4P_Dung")
    b.ic("Connector_Generic:Conn_01x04", "J2", "HC-SR04", 76, 36, {"1": "+5V", "2": "S1", "3": "ECHO", "4": "GND"}, fp=HANG % 4)
    b.cot(112, 26, "ECHO", [("R", "10k", "S2"), ("R", "10k", None), ("R", "10k", "GND")])
    b.cot(140, 26, "+5V", [("C", "10u/25V", "GND")])
    b.xong("Trig ← S1 (3,3 V đủ ngưỡng).  Echo 5 V × 20k / 30k = 3,33 V → S2.",
           "J1 dùng đầu cắm đứng ở mặt sau (Cong_PH_4P_Dung).")


def I12():
    b = Bo("I12", "Mắt thu hồng ngoại 38 kHz", "S", bo_qua=("S2",))
    b.ldo()
    b.ic("Interface_Optical:TSOP382xx", "U2", "VS1838B", 74, 40, {"1": "S1", "2": "GND", "3": "V_IR"}, MPN="VS1838B")
    b.hang(112, 28, "+3V3", [("R", "100R", "V_IR")])
    b.cot(144, 28, "V_IR", [("C", "10u/25V", "GND")])
    b.s.co_nguon((144, 28))
    b.xong("Cấp 3V3, không cấp 5 V: đầu ra có kéo lên nội về nguồn.",
           "R1 + C3 lọc nguồn cho mắt thu.  Chân: 1 OUT, 2 GND, 3 VCC (đối chiếu linh kiện mua).",
           "Chân linh kiện đang là của TSOP382 (cùng thứ tự chân): đổi theo vỏ VS1838B khi layout.")


def I13():
    b = Bo("I13", "RFID (đế module RC522)", "L", cong="SPI")
    b.ldo(ic="AP2112")
    b.ic("Connector_Generic:Conn_01x08", "J2", "RC522", 80, 40,
         {"1": "CS", "2": "SCK", "3": "MOSI", "4": "MISO", "5": None, "6": "GND", "7": "RC_RST", "8": "+3V3"}, fp=HANG % 8)
    b.cot(120, 26, "+3V3", [("R", "10k", "RC_RST")])
    b.cot(146, 26, "+3V3", [("C", "10u/25V", "GND")])
    b.xong("Module RC522 chỉ chịu 3,3 V.  Chân J2: SDA(CS), SCK, MOSI, MISO, IRQ, GND, RST, 3V3.",
           "IRQ để hở; RST kéo lên 3V3 qua R1.")


def I14():
    b = Bo("I14", "Cử chỉ, màu, khoảng cách (APDS-9960)", "S", cong="I2C")
    b.ldo()
    u = b.ic("Sensor:APDS-9960", "U2", "APDS-9960", 86, 42,
             {"1": "SDA", "7": "SCL", "2": None, "8": "+3V3", "6": "GND", "5": "+3V3"}, MPN="APDS-9960")
    a, c = u.p("3"), u.p("4")
    b.s.w(a, (a[0] + 3, a[1]), (c[0] + 3, c[1]), c)
    b.cot(126, 30, "+3V3", [("C", "100n", "GND")])
    b.cot(142, 30, "+3V3", [("C", "10u/25V", "GND")])
    b.xong("Địa chỉ 0x39.  LDR (3) nối LED_K (4): dùng bộ lái LED hồng ngoại nội.",
           "INT (2) để hở.  C4 10 µF đặt sát LED_A: xung LED tới 100 mA.")


# ============================================================ module ra
def O1():
    b = Bo("O1", "2 LED", "S")
    for i, (mau, r, x) in enumerate((("ĐỎ", "330R", 64), ("XANH", "220R", 144)), 1):
        b.cot(x, 26, "+5V", [("R", r, None), ("LED", mau, f"K{i}")])
        b.ic("Transistor_FET:2N7002", f"Q{i}", "2N7002", x + 32, 58, {"1": f"S{i}", "3": f"K{i}", "2": "GND"},
             vt_ref=(7, -1.2), vt_gt=(8, 1.2), MPN="2N7002")
        b.cot(x + 52, 58, f"S{i}", [("R", "100k", "GND")])
    b.xong("Đỏ: (5 − 2) / 330 = 9 mA.  Xanh: (5 − 3) / 220 = 9 mA.",
           "Cực G kéo xuống 100 k: LED tắt khi cổng chưa được cấu hình.")


def O2():
    b = Bo("O2", "Thanh 8 LED RGB (WS2812B)", "T", bo_qua=("S2",))
    b.ic("74xGxx:74AHCT1G125", "U1", "74AHCT1G125", 78, 34, {"5": "+5V", "3": "GND", "1": "GND", "2": "S1", "4": "BUF"}, 3,
         "Package_TO_SOT_SMD:SOT-23-5", vt_ref=(8, -5), vt_gt=(10, 5), MPN="SN74AHCT1G125DBVR")
    b.hang(104, 44, "BUF", [("R", "330R", "D1")])
    for i in range(8):
        b.ic("LED:WS2812B", f"LED{i + 1}", "WS2812B", 66 + 40 * (i % 4), 66 + 24 * (i // 4),
             {"1": "+5V", "3": "GND", "4": f"D{i + 1}", "2": f"D{i + 2}"}, 3, vt_ref=(6, -7), vt_gt=(8, 7))
    for i in range(10):
        b.cot(126 + 9 * i + (3 if i == 9 else 0), 24, "+5V", [("C", "100n" if i < 8 else "10u/25V", "GND")])
    b.tp(200, 44, "D9", "DOUT")
    b.xong("U1 cấp 5 V nâng tín hiệu 3,3 V lên 5 V (ngưỡng vào của họ AHCT: 2,0 V).",
           "Mỗi LED một tụ 100 nF sát chân; 8 LED sáng trắng tối đa khoảng 0,4 A.",
           "DOUT ra điểm hàn TP1 để nối thanh tiếp theo.")


def O3():
    b = Bo("O3", "Màn hình OLED 0,96 inch (đế 4 chân)", "M", cong="I2C")
    b.ldo()
    b.ic("Connector_Generic:Conn_01x04", "J2", "OLED", 76, 36, {"1": "GND", "2": "+3V3", "3": "SCL", "4": "SDA"}, fp=HANG % 4)
    b.xong("Cấp 3V3 để điện trở kéo lên trên module OLED không kéo bus lên 5 V.",
           "Thứ tự GND / VCC của module khác nhau giữa các nhà bán: đối chiếu trước khi layout.")


def O4():
    b = Bo("O4", "Relay 5 V", "M", bo_qua=("S2",))
    b.hang(62, 28, "S1", [("R", "470R", "OPTO_A")])
    b.ic("Isolator:PC817", "U1", "PC817", 112, 30, {"1": "OPTO_A", "2": "GND", "4": "+5V", "3": "OPTO_E"},
         fp="Package_DIP:SMDIP-4_W9.53mm", MPN="PC817")
    b.hang(62, 50, "OPTO_E", [("R", "1k", "Q_B")])
    b.cot(92, 50, "Q_B", [("R", "10k", "GND")])
    b.ic("Transistor_BJT:SS8050", "Q1", "SS8050", 126, 60, {"1": "Q_B", "2": "GND", "3": "COIL-"},
         vt_ref=(7, -1.2), vt_gt=(8, 1.2), MPN="SS8050")
    b.ic("Relay:SANYOU_SRD_Form_C", "K1", "SRD-05VDC-SL-C", 168, 50, {"5": "+5V", "2": "COIL-", "1": "COM", "3": "K_3", "4": "K_4"},
         vt_ref=(13, -1.2), vt_gt=(17, 1.2))
    b.hang(146, 84, "COIL-", [("D", "1N4148W", "+5V")])
    b.cot(200, 24, "+5V", [("R", "1k", None), ("LED", "BẬT", "COIL-")])
    b.cot(146, 22, "+5V", [("C", "10u/25V", "GND")])
    b.ic("Connector:Screw_Terminal_01x03", "J2", "Tải ≤ 24 V", 206, 76, {"1": "K_4", "2": "COM", "3": "K_3"},
         fp="TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal")
    b.xong("Dòng LED của PC817: (3,3 − 1,2) / (220 + 470) = 3 mA (220 Ω nằm trên bo chủ).",
           "Optocoupler chung nguồn và GND với phần điều khiển: chỉ giảm nhiễu, không phải cách ly an toàn.",
           "Chân 3, 4 của K1 là tiếp điểm thường đóng / thường mở: đối chiếu datasheet rồi in nhãn NO, COM, NC.",
           "Chỉ dùng cho tải tối đa 24 V; in nhãn này lên bo.")


def O5():
    b = Bo("O5", "Đóng cắt tải 5 V (MOSFET)", "S", bo_qua=("S2",))
    b.hang(62, 40, "S1", [("R", "100R", "GATE")])
    b.cot(92, 40, "GATE", [("R", "10k", "GND")])
    b.ic("Transistor_FET:AO3400A", "Q1", "AO3400A", 122, 44, {"1": "GATE", "3": "OUT-", "2": "GND"},
         vt_ref=(7, -1.2), vt_gt=(8, 1.2), MPN="AO3400A")
    b.hang(146, 70, "OUT-", [("DS", "SS54", "+5V")])
    b.ic("Connector_Generic:Conn_01x02", "J2", "Tải 5 V", 186, 40, {"1": "OUT-", "2": "+5V"}, fp="IRIS:Cong_XH_2P_Ngang")
    b.xong("Tải (quạt, bơm, đèn) nối giữa +5V và OUT−; Q1 kéo OUT− xuống GND.",
           "D1 dập xung ngược của tải cảm.  Dòng tải giới hạn bởi cầu chì 1,1 A của bo chủ.",
           "J2: chân 1 = OUT−, chân 2 = +5V (XH 2 chân).")


TAT_CA = [I1, I2, I3, I4, I5, I6, I7, I8, I9, I10, I11, I12, I13, I14, O1, O2, O3, O4, O5]

if __name__ == "__main__":
    chon = set(sys.argv[1:])
    for f in TAT_CA:
        if not chon or f.__name__ in chon:
            f()
