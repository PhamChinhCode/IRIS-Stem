"""Sinh bản sơ đồ nguyên lý đầu tiên của C2 – nguồn pin 2S.

Chạy: PYTHONUTF8=1 python ve_so_do.py
Thiết kế: ../THIET-KE-MACH.md mục 7. Toạ độ theo lưới 1,27 mm.
Kịch bản ghi đè C2.kicad_sch; không chạy lại sau khi đã sửa sơ đồ bằng tay.
"""
import os
import sys

DAY = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(DAY, "..", "common"))
from sch import FP, SoDo  # noqa: E402
from khoi_chung import C0805, gop, khoi_buck, khoi_ldo, tep_du_an, tu_treo  # noqa: E402

s = SoDo("C2", "C2 - Nguồn pin 2S", "A2", "0.1", "2026-11-15")
SO8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
CUON = "Inductor_SMD:L_Sunlord_SWPA6045S"
_dem = {"R": 0, "C": 0}


def ref(loai):
    _dem[loai] += 1
    return f"{loai}{_dem[loai]}"


def hang(y, x, trai, gt, phai, fp=None, lib="Device:R_Small"):
    """Một hàng ngang: nhãn `trai` → linh kiện 2 chân → `phai` (nhãn, hoặc GND)."""
    s.nhan(trai, (x, y), "trai")
    k, a, b = s.ngang(lib, ref("C" if "C_" in lib else "R"), gt, x + 4, y, fp or FP["C" if "C_" in lib else "R"])
    s.w((x, y), a)
    s.w(b, (x + 8, y))
    if phai == "GND":
        s.nguon("GND", (x + 8, y), "phai")
    else:
        s.nhan(phai, (x + 8, y))
    return k


# ================= 1. USB-C VÀO SẠC =================
s.khoi(10, 14, 130, 76, "USB-C VÀO SẠC", [
    "D+/D− nối về IP2326 để xin sạc nhanh (tối đa 7 V với pin 2 cell).  CC1, CC2 mỗi chân một điện trở 5k1",
    "Mọi linh kiện trên VIN_CHG chịu ≥ 16 V (tụ 25 V)",
])
usb = s.dat("Connector:USB_C_Receptacle_USB2.0_16P", "J1", "USB-C", 26, 44, 0,
            "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", vt_ref=(-4, -17), vt_gt=(4, -17), MPN="TYPE-C-31-M-12")
Y = 32
assert usb.p("A4") == (38, Y), usb.p("A4")
s.w(usb.p("A4"), (84, Y))
s.co_nguon((66, Y))
tu_treo(s, ref("C"), "10u/25V", 74, Y, C0805)
s.nhan("VIN_CHG", (84, Y))
s.w(usb.p("A5"), (58, 36), (58, 40))
_, t, d = s.R(ref("R"), "5k1", 58, 42)
s.nguon("GND", d)
s.w(usb.p("B5"), (53, 38), (53, 46))
_, t, d = s.R(ref("R"), "5k1", 53, 48)
s.nguon("GND", d)
for ten, a, b in (("USB_DM", "A7", "B7"), ("USB_DP", "A6", "B6")):
    pa, pb = usb.p(a), usb.p(b)
    s.w(pa, (41, pa[1]), (41, pb[1]), pb)
    s.nhan(ten, (41, pa[1] if ten.endswith("M") else pb[1]))
s.nc(usb.p("A8"))
s.nc(usb.p("B8"))
g, sh = usb.p("A1"), usb.p("SH")
s.w(g, (g[0], g[1] + 2))
s.w(sh, (sh[0], sh[1] + 2), (g[0], g[1] + 2))
s.nguon("GND", (g[0], g[1] + 2))

# ================= 2. PIN VÀ BẢO VỆ =================
s.khoi(10, 80, 130, 190, "PIN 2 CELL 18650 VÀ MẠCH BẢO VỆ (HY2120-CB + 2 × 8205A)", [
    "GND của bo = cực âm sau FET bảo vệ.  BAT− chỉ nối tới U2, Q1, Q2",
    "Q1 ∥ Q2: FET nửa 1 (cổng OD) cắt xả, nửa 2 (cổng OC) cắt sạc; tổng khoảng 25 mΩ",
    "SỐ CHÂN U2, Q1, Q2 GHI THEO TRÍ NHỚ – PHẢI ĐỐI CHIẾU DATASHEET TRƯỚC KHI LAYOUT",
])
pin = "Battery:BatteryHolder_Keystone_1042_1x18650"
bt1 = s.dat("Device:Battery_Cell", "BT1", "18650", 24, 102, 0, pin, vt_ref=(-6, -2), vt_gt=(-7, 1))
bt2 = s.dat("Device:Battery_Cell", "BT2", "18650", 24, 118, 0, pin, vt_ref=(-6, -2), vt_gt=(-7, 1))
a = bt1.p("+")
s.w(a, (24, 94), (34, 94))
s.nhan("BAT+", (34, 94))
s.w(bt1.p("-"), bt2.p("+"))
s.w((24, 108), (34, 108))
s.nhan("BATM", (34, 108))
b = bt2.p("-")
s.w(b, (24, 126), (34, 126))
s.nhan("BAT-", (34, 126))
u2 = s.dat("IRIS:HY2120", "U2", "HY2120-CB", 84, 100, 0, vt_ref=(0, -6), vt_gt=(0, 6),
           MPN="HY2120-CB", LCSC="C116509", Manufacturer="HYCON")
s.chia(u2, {"5": "HY_VDD", "4": "HY_VC", "6": "BAT-", "1": "OD", "2": "OC", "3": "HY_CS"})
for y, vao, ra in ((118, "BAT+", "HY_VDD"), (132, "BATM", "HY_VC")):
    s.nhan(vao, (60, y), "trai")
    _, tr, ph = s.R(ref("R"), "330R", 64, y, ngang=True)
    s.w((60, y), tr)
    s.w(ph, (78, y))
    s.nhan(ra, (78, y))
    _, t, d = s.C(ref("C"), "100n", 72, y + 4)
    s.w((72, y), t)
    s.w(d, (72, y + 8), (78, y + 8))
    s.nhan("BAT-", (78, y + 8))
hang(118, 104, "HY_CS", "2k", "GND")
for i, y in enumerate((154, 174)):
    q = s.dat("IRIS:FET_Kep_8205", f"Q{i + 1}", "8205A", 64, y, 0, vt_ref=(-4, -8), vt_gt=(4, -8), MPN="8205A")
    s.chia(q, {"4": "OD", "5": "OC"})
    gop(s, q, ["2", "3"], "BAT-")
    gop(s, q, ["1", "8"], "FET_D")
    gop(s, q, ["6", "7"], "GND")

# ================= 3. SẠC IP2326 =================
s.khoi(136, 14, 276, 130, "SẠC TĂNG ÁP 2 CELL IP2326 (8,4 V · 1 A · CÓ CÂN BẰNG)", [
    "I_sạc = 90000 / R_ISET = 90000 / 91k ≈ 1,0 A.  VSET, VIN_OVSET, CON_SEL để hở: 8,4 V, quá áp vào 8,75 V, chế độ 2 cell",
    "TIME_SET 120k: hết giờ sau 12 h.  VIN_UVSET 120k: giữ áp vào ≥ 4,45 V.  NTC 51k: không dùng nhiệt điện trở",
    "Cân bằng: mở ở 4,1 V/cell, dòng = V_cell / R_CB (100 Ω → 40 mA).  Cắt JP1 để tắt cân bằng",
])
u1 = s.dat("IRIS:IP2326", "U1", "IP2326", 206, 72, 0, vt_ref=(-6, -16.5), vt_gt=(6, -16.5),
           MPN="IP2326", LCSC="C2832094", Manufacturer="Injoinic")
s.chia(u1, {"13": "CHG_VIN", "12": "CHG_EN", "2": "USB_DP", "1": "USB_DM", "11": "ISET", "3": None, "4": "NTC",
            "7": "TIME_SET", "8": "VIN_UV", "9": None, "10": None,
            "14": "BST", "23": "VBATM", "24": "GND", "5": None, "6": "CHG_LED", "18": "GND", "25": "GND"})
gop(s, u1, ["15", "16", "17"], "LX")
gop(s, u1, ["19", "20"], "VSYS")
gop(s, u1, ["21", "22"], "VPACK")
# đường vào: VIN_CHG → L1 → LX
Y = 30
s.nhan("VIN_CHG", (152, Y), "trai")
s.w((152, Y), (175, Y))
tu_treo(s, ref("C"), "10u/25V", 155, Y, C0805)
_, t, d = s.R(ref("R"), "5k1", 166, Y + 2)
s.nguon("GND", d)
l1 = s.dat("Device:L", "L1", "2u2", 178, Y, 90, CUON, vt_ref=(0, -2.4), vt_gt=(0, 2.4))
s.w(l1.p("2"), (184, Y))
s.nhan("LX", (184, Y))
# lọc chân VIN
Y = 46
s.nhan("VIN_CHG", (152, Y), "trai")
_, tr, ph = s.R(ref("R"), "0R5", 156, Y, ngang=True)
s.w((152, Y), tr)
s.w(ph, (174, Y))
tu_treo(s, ref("C"), "10u/25V", 164, Y, C0805)
s.nhan("CHG_VIN", (174, Y))
# điện trở đặt chế độ
hang(100, 150, "ISET", "91k", "GND")
hang(107, 150, "NTC", "51k", "GND")
hang(114, 150, "TIME_SET", "120k", "GND")
hang(100, 176, "VIN_UV", "120k", "GND")
hang(107, 176, "CHG_VIN", "10k", "CHG_EN")
# phía ra
hang(28, 240, "BST", "100n", "LX", lib="Device:C_Small")
Y = 40
s.nhan("VSYS", (240, Y), "trai")
s.w((240, Y), (254, Y))
tu_treo(s, ref("C"), "22u/25V", 244, Y, C0805)
tu_treo(s, ref("C"), "22u/25V", 254, Y, C0805)
Y = 56
s.nhan("VPACK", (240, Y), "trai")
s.w((240, Y), (254, Y))
tu_treo(s, ref("C"), "10u/25V", 244, Y, C0805)
tu_treo(s, ref("C"), "10u/25V", 254, Y, C0805)
# cân bằng
Y = 82
s.nhan("BATM", (236, Y), "trai")
jp = s.dat("Jumper:SolderJumper_2_Bridged", "JP1", "CÂN BẰNG", 241, Y, 0,
           "Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm", vt_ref=(0, -3), vt_gt=(0, 3))
s.w((236, Y), jp.p("1"))
_, tr, ph = s.ngang("Device:R_Small", ref("R"), "100R", 250, Y, "Resistor_SMD:R_1206_3216Metric")
s.w(jp.p("2"), tr)
s.w(ph, (266, Y))
s.nhan("VBATM", (266, Y))
_, t, d = s.C(ref("C"), "100n", 258, Y - 5)
s.w(d, (258, Y))
s.w(t, (258, Y - 10), (262, Y - 10))
s.nhan("VPACK", (262, Y - 10))
tu_treo(s, ref("C"), "100n", 258, Y)
# LED sạc
Y = 104
s.nhan("CHG_LED", (240, Y), "trai")
_, tr, ph = s.R(ref("R"), "330R", 244, Y, ngang=True)
s.w((240, Y), tr)
led1 = s.dat("Device:LED_Small", "LED1", "SẠC", 251, Y, 180, FP["LED"], vt_ref=(0, -2.4), vt_gt=(0, 2.6))
s.w(ph, led1.p("2"))
s.w(led1.p("1"), (255, Y))
s.nguon("GND", (255, Y), "phai")

# ================= 4. ĐO DÒNG, ÁP + CỔNG I2C =================
s.khoi(282, 14, 410, 100, "ĐO DÒNG, ÁP PIN (INA219, 0x40) + CỔNG I2C", [
    "Shunt 10 mΩ: 7,2 A → 72 mV, 0,52 W.  Dòng xả dương, dòng sạc âm.  Dây đo đi kiểu Kelvin từ mép trong pad",
    "Chân 5 V của J4 để hở; VP của U6 để hở: bus I2C không bị kéo sập khi C2 tắt mà C1 còn điện",
])
Y = 28
s.nhan("VPACK", (292, Y), "trai")
_, tr, ph = s.ngang("Device:R_Small", ref("R"), "10mR", 302, Y, "Resistor_SMD:R_2512_6332Metric")
s.w((292, Y), tr)
s.w(ph, (312, Y))
s.nhan("BAT+", (312, Y))
u3 = s.dat("Sensor_Energy:INA219AxD", "U3", "INA219AIDR", 330, 48, 0, vt_ref=(-5, -9), vt_gt=(7, 9),
           MPN="INA219AIDR", LCSC="C138706", Manufacturer="Texas Instruments")
ip, im = u3.p("IN+"), u3.p("IN-")
s.w((308, Y), (308, ip[1]), ip)
s.w((296, Y), (296, im[1]), im)
s.chia(u3, {"3": "SDA", "4": "SCL", "5": "+3V3", "6": "GND"})
gop(s, u3, ["1", "2"], "GND")
_, t, d = s.C(ref("C"), "100n", 348, 34)
s.nguon("+3V3", t)
s.nguon("GND", d)
j4 = s.dat("IRIS:Cong_I2C", "J4", "I2C", 292, 76, 180, vt_ref=(-2, -7), vt_gt=(-2, 7))
for chan, dich in (("GND", "GND"), ("5V", None), ("SDA", "SDA_BUS"), ("SCL", "SCL_BUS")):
    a = j4.p(chan)
    if dich is None:
        s.nc(a)
        continue
    b = (a[0] + 4, a[1])
    s.w(a, b)
    if dich == "GND":
        s.nguon("GND", b, "phai")
    else:
        s.nhan(dich, b)
hang(70, 330, "SDA_BUS", "100R", "SDA")
hang(78, 330, "SCL_BUS", "100R", "SCL")
u6 = s.dat("Power_Protection:SRV05-4", "U6", "SRV05-4", 384, 48, 0, MPN="SRV05-4")
s.chia(u6, {"1": "SDA_BUS", "3": "SCL_BUS", "4": None, "6": None, "5": None, "2": "GND"})

# ================= 5. CÔNG TẮC NGUỒN =================
s.khoi(282, 104, 410, 160, "CÔNG TẮC NGUỒN (Q3 P-FET) VÀ CỔNG XT30", [
    "SW1 chỉ dẫn dòng cực G.  Bật: V_GS = −V_pin × 100k / 110k.  Tụ G–S 100 nF làm Q3 mở chậm, hạn dòng nạp tụ tải",
    "Q3: 7,2 A đỉnh → 1,0 W; 2 A điển hình → 80 mW",
])
Y = 122
s.nhan("VPACK", (292, Y), "trai")
q3 = s.dat("Transistor_FET:IRF7404", "Q3", "AO4435", 320, Y - 2, 270, SO8, vt_ref=(-3, 5), vt_gt=(4, 5), MPN="AO4435")
assert q3.p("1") == (316, Y) and q3.p("5") == (324, Y) and q3.p("4") == (320, Y - 6), (q3.p("1"), q3.p("5"), q3.p("4"))
s.w((292, Y), q3.p("1"))
YG = Y - 10
_, t, d = s.C(ref("C"), "100n", 298, Y - 5)
s.w(d, (298, Y))
s.w(t, (298, YG))
_, t, d = s.R(ref("R"), "100k", 307, Y - 5)
s.w(d, (307, Y))
s.w(t, (307, YG))
s.w((298, YG), (320, YG), q3.p("4"))
_, tr, ph = s.R(ref("R"), "10k", 330, YG, ngang=True)
s.w((320, YG), tr)
sw = s.dat("Switch:SW_SPDT", "SW1", "NGUỒN", 342, YG, 0, "Button_Switch_SMD:SW_SPDT_PCM12", vt_ref=(0, -5), vt_gt=(0, 6))
s.w(ph, sw.p("B"))
s.nguon("GND", sw.p("A"), "phai")
s.nc(sw.p("C"))
s.w(q3.p("5"), (372, Y))
s.co_nguon((336, Y))
tu_treo(s, ref("C"), "10u/25V", 344, Y, C0805)
_, t, d = s.R(ref("R"), "10k", 358, Y + 4)
s.w((358, Y), t)
led2 = s.dat("Device:LED_Small", "LED2", "NGUỒN", 358, Y + 10, 90, FP["LED"], vt_ref=(4, -1.1), vt_gt=(5, 1.1))
s.w(d, led2.p("2"))
s.nguon("GND", led2.p("1"))
s.nhan("VBAT", (372, Y))
j2 = s.dat("IRIS:Cong_Nguon_XT30", "J2", "XT30 cái", 396, 139, 0, "IRIS:Cong_XT30_Cai", vt_ref=(1, -5), vt_gt=(1, 5))
a = j2.p("VBAT")
s.w(a, (a[0] - 3, a[1]))
s.nhan("VBAT", (a[0] - 3, a[1]), "trai")
a = j2.p("GND")
s.w(a, (a[0] - 2, a[1]))
s.nguon("GND", (a[0] - 2, a[1]), "trai")

# ================= 6. BUCK, 3V3, CỔNG 5 V =================
khoi_buck(s, 136, 134, "VBAT", "5V_OUT", "U4", "L2", [ref("C") for _ in range(7)], [ref("R") for _ in range(4)])
khoi_ldo(s, 136, 184, vao="5V_OUT", refs=("U5", ref("C"), ref("C")), tieu_de="NGUỒN 3V3 CHO INA219 (từ 5,45 V của buck)")
s.khoi(282, 164, 410, 220, "CỔNG RA 5,45 V VỀ BO CHỦ C1 (XH 2 CHÂN)", [
    "Đặt 5,45 V để bù sụt áp của D1 (SS54) trên C1",
])
j3 = s.dat("IRIS:Cong_Nguon_5V", "J3", "5V ra C1", 320, 187, 0, vt_ref=(1, -5), vt_gt=(1, 5))
a = j3.p("5V")
s.w(a, (a[0] - 3, a[1]))
s.nhan("5V_OUT", (a[0] - 3, a[1]), "trai")
a = j3.p("GND")
s.w(a, (a[0] - 2, a[1]))
s.nguon("GND", (a[0] - 2, a[1]), "trai")

# ================= khung bo, ghi chú =================
s.khoi(10, 194, 130, 250, "CƠ KHÍ VÀ GHI CHÚ", [])
s.dat("IRIS:Khung_C2_96x48", "KH1", "Khung_C2_96x48", 24, 212, 0, vt_ref=(0, -6), vt_gt=(0, 6))
for i, g in enumerate((
    "Bo 96 × 48 mm, lỗ gá Ø3,2 theo lưới 8 mm (trong KH1).",
    "R, C nhỏ: 0603; tụ 10 µF, 22 µF: 0805 25 V (riêng tụ ra buck 16 V).",
    "L1 2,2 µH: I_sat ≥ 5 A, DCR < 20 mΩ.  L2 3,3 µH: I_sat ≥ 4,5 A.",
    "IP2326 toả khoảng 0,6 W ở 1 A: pad tản nhiệt nối GND bằng nhiều via.",
    "Đường LX, SW ngắn; tụ VSYS (22 µF × 2) sát chân 19, 20.",
    "Mạch IP2326 theo datasheet V1.2, hình 5.",
    "Thiết kế: hardware/THIET-KE-MACH.md mục 7.",
)):
    s.chu(g, 38, 206 + 4 * i)

tep_du_an(DAY, "C2")
s.ghi(os.path.join(DAY, "C2.kicad_sch"))
print(len([k for k in s.lk if not k.ref.startswith("#")]), "linh kiện")
