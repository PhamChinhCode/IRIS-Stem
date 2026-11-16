"""Sinh thư viện KiCad dùng chung của IRIS-Stem: IRIS.kicad_sym và IRIS.pretty.

Chạy: python tao_thu_vien.py   (cần KiCad 10; đặt biến KICAD_DIR nếu cài ở chỗ khác)

Nguồn chuẩn:
- thứ tự chân các cổng: docs/THIET-KE-HE-THONG.md mục 3
- kích thước bo, lỗ gá:  docs/THIET-KE-CO-KHI.md mục 2 và 3.1 (phải khớp mechanical/src/lib/mach.py)
"""
import os
import re
import subprocess
from pathlib import Path

DAY = Path(__file__).parent
KICAD = Path(os.environ.get("KICAD_DIR", "C:/Program Files/KiCad/10.0"))
FP_GOC = KICAD / "share/kicad/footprints"
PRETTY = DAY / "IRIS.pretty"

# ---------------------------------------------------------------- chân đầu cắm
# tên trong IRIS: (thư viện gốc của KiCad, tên gốc)
DAU_CAM = {
    "Cong_PH_4P_Ngang": ("Connector_JST", "JST_PH_S4B-PH-K_1x04_P2.00mm_Horizontal"),
    "Cong_PH_4P_Dung": ("Connector_JST", "JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical"),
    "Cong_PH_6P_Ngang": ("Connector_JST", "JST_PH_S6B-PH-K_1x06_P2.00mm_Horizontal"),
    "Cong_XH_6P_Ngang": ("Connector_JST", "JST_XH_S6B-XH-A_1x06_P2.50mm_Horizontal"),
    "Cong_XH_2P_Ngang": ("Connector_JST", "JST_XH_S2B-XH-A_1x02_P2.50mm_Horizontal"),
    "Cong_Servo_1x03": ("Connector_PinHeader_2.54mm", "PinHeader_1x03_P2.54mm_Vertical"),
    "Cong_XT30_Duc": ("Connector_AMASS", "AMASS_XT30UPB-M_1x02_P5.0mm_Vertical"),
    "Cong_XT30_Cai": ("Connector_AMASS", "AMASS_XT30UPB-F_1x02_P5.0mm_Vertical"),
}

# ---------------------------------------------------------------- khung bo
# tên cỡ: (rộng, cao, module dùng cỡ này)
KHUNG = {
    "S": (24, 32, "I1 I2 I5 I6 I7 I12 I14 O1 O5"),
    "M": (32, 48, "I3 I8 I10 O3 O4"),
    "L": (48, 64, "I4 I13 O7"),
    "T": (64, 24, "I11 O2"),
    "S3": (32, 32, "S3"),
    "S1": (48, 48, "S1"),
    "S2": (80, 24, "S2"),
    "C2": (96, 48, "C2"),
    "C1": (64, 48, "C1"),
    "Que": (24, 96, "I9"),
}
D_LO = 3.2     # lỗ gá M3
MEP = 4.0      # tâm lỗ cách mép
R_CAM = 2.75   # vùng cấm quanh lỗ = trụ đỡ và đầu vít Ø5,5; thân linh kiện giữ cách tâm lỗ 3 mm
R_GOC = 2.0    # bo tròn góc bo mạch
THU = 0.25     # đường cắt thu vào mỗi cạnh so với kích thước danh nghĩa, để hai bo sát nhau hở 0,5 mm


def lo_ga(co):
    w, h, _ = KHUNG[co]
    if co == "Que":
        return [(MEP, h - MEP), (w - MEP, h - MEP)]
    if co == "S":      # hai lỗ phía đầu cắm lùi lên 12 mm: đầu PH 4 chân không lọt giữa hai trụ cách nhau 16 mm
        return [(x, y) for x in (MEP, w - MEP) for y in (12.0, h - MEP)]
    return [(x, y) for x in (MEP, w - MEP) for y in (MEP, h - MEP)]


def n(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


def khung_fp(co):
    """Khung bo: đường cắt + lỗ gá. Gốc = góc dưới trái của bo danh nghĩa, như trong tài liệu cơ khí.

    KiCad có trục Y hướng xuống, nên điểm (x, y) của tài liệu nằm ở (x, -y).
    """
    w, h, dung = KHUNG[co]
    ten = f"Khung_{co}_{w}x{h}"
    r, k = R_GOC, R_GOC * (1 - 0.5 ** 0.5)
    net = '(stroke (width 0.1) (type solid)) (layer "Edge.Cuts")'
    font = "(effects (font (size 1 1) (thickness 0.15)))"
    s = [
        f'(footprint "{ten}" (version 20240108) (generator "iris_tao_thu_vien") (layer "F.Cu")',
        f'  (descr "Khung bo cỡ {co}, danh nghĩa {w} x {h} mm (đường cắt {n(w - 2 * THU)} x {n(h - 2 * THU)}), lỗ gá Ø{n(D_LO)} theo lưới 8 mm. Dùng cho: {dung}")',
        '  (tags "IRIS khung bo")',
        f'  (property "Reference" "REF**" (at {n(w / 2)} {n(-h / 2 - 1)} 0) (layer "F.Fab") {font})',
        f'  (property "Value" "{ten}" (at {n(w / 2)} {n(-h / 2 + 1)} 0) (layer "F.Fab") {font})',
        "  (attr exclude_from_pos_files exclude_from_bom)",
    ]
    a0, a1, b0, b1 = THU, w - THU, -THU, -h + THU      # mép trái, phải, dưới, trên của đường cắt
    for (x1, y1, x2, y2) in ((a0 + r, b0, a1 - r, b0), (a1, b0 - r, a1, b1 + r),
                             (a1 - r, b1, a0 + r, b1), (a0, b1 + r, a0, b0 - r)):
        s.append(f"  (fp_line (start {n(x1)} {n(y1)}) (end {n(x2)} {n(y2)}) {net})")
    # bốn góc bo tròn: (đầu, giữa, cuối)
    for (a, m, b) in (((a0, b0 - r), (a0 + k, b0 - k), (a0 + r, b0)), ((a1 - r, b0), (a1 - k, b0 - k), (a1, b0 - r)),
                      ((a1, b1 + r), (a1 - k, b1 + k), (a1 - r, b1)), ((a0 + r, b1), (a0 + k, b1 + k), (a0, b1 + r))):
        s.append(f"  (fp_arc (start {n(a[0])} {n(a[1])}) (mid {n(m[0])} {n(m[1])}) (end {n(b[0])} {n(b[1])}) {net})")
    for (x, y) in lo_ga(co):
        for lop in ("F.CrtYd", "B.CrtYd"):
            s.append(f"  (fp_circle (center {n(x)} {n(-y)}) (end {n(x + R_CAM)} {n(-y)}) "
                     f'(stroke (width 0.05) (type solid)) (fill none) (layer "{lop}"))')
        s.append(f'  (pad "" np_thru_hole circle (at {n(x)} {n(-y)}) (size {n(D_LO)} {n(D_LO)}) '
                 f'(drill {n(D_LO)}) (layers "*.Cu" "*.Mask"))')
    s.append(")")
    return ten, "\n".join(s) + "\n"


def aht20_fp():
    """AHT20, DFN 3 x 3 mm 6 chân: pad 0,8 x 0,5, bước 1,0, hai hàng cách nhau 2,0 (datasheet ASAIR V1.0, hình 8)."""
    ten = "AHT20_DFN6_3x3"
    s = [f'(footprint "{ten}" (version 20240108) (generator "iris_tao_thu_vien") (layer "F.Cu")',
         '  (descr "IRIS AHT20 DFN-6 3x3 mm, pad 0.8x0.5, pitch 1.0")', "  (attr smd)",
         '  (fp_text reference "REF**" (at 0 -2.5) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
         f'  (fp_text value "{ten}" (at 0 2.5) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
         '  (fp_rect (start -1.5 -1.5) (end 1.5 1.5) (stroke (width 0.1) (type solid)) (fill none) (layer "F.Fab"))',
         '  (fp_rect (start -2.05 -1.75) (end 2.05 1.75) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))',
         '  (fp_line (start -1.5 -1.65) (end 1.5 -1.65) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))',
         '  (fp_line (start -1.5 1.65) (end 1.5 1.65) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))']
    for so, x, y in (("1", -1.4, -1.0), ("2", -1.4, 0.0), ("3", -1.4, 1.0), ("4", 1.4, 1.0), ("5", 1.4, 0.0), ("6", 1.4, -1.0)):
        s.append(f'  (pad "{so}" smd rect (at {x} {y}) (size 0.8 0.5) (layers "F.Cu" "F.Paste" "F.Mask"))')
    s.append(")")
    return "\n".join(s) + "\n"


# ---------------------------------------------------------------- ký hiệu
# tên: (chân, chân linh kiện mặc định, bộ lọc chân linh kiện, mô tả)
CONG = {
    "Cong_DA": (["GND", "5V", "S1", "S2"], "Cong_PH_4P_Ngang", "Cong_PH_4P*",
                "Cổng D/A 4 chân, JST PH2.0, đầu cắm màu trắng. Tín hiệu 3,3 V."),
    "Cong_I2C": (["GND", "5V", "SDA", "SCL"], "Cong_PH_4P_Ngang", "Cong_PH_4P*",
                 "Cổng I2C 4 chân, JST PH2.0, đầu cắm màu xanh. Kéo lên 3,3 V chỉ đặt trên bo chủ."),
    "Cong_SPI": (["GND", "5V", "SCK", "MOSI", "MISO", "CS"], "Cong_PH_6P_Ngang", "Cong_PH_6P*",
                 "Cổng SPI 6 chân, JST PH2.0, đầu cắm màu vàng."),
    "Cong_Servo": (["GND", "5V", "PWM"], "Cong_Servo_1x03", "Cong_Servo*",
                   "Cổng servo, hàng rào 3 chân 2,54 mm."),
    "Cong_DongCo": (["M+", "M-", "GND", "3V3", "EncA", "EncB"], "Cong_XH_6P_Ngang", "Cong_XH_6P*",
                    "Cổng động cơ encoder 6 chân trên S1, JST XH2.5, đầu cắm màu đỏ."),
    "Cong_Nguon_5V": (["GND", "5V"], "Cong_XH_2P_Ngang", "Cong_XH_2P*",
                      "Nguồn 5 V/3 A từ C2 về bo chủ, JST XH2.5 2 chân."),
    "Cong_Nguon_XT30": (["GND", "VBAT"], "Cong_XT30_Duc", "Cong_XT30*",
                        "Nguồn động lực XT30. Bên cấp (C2) dùng đầu cái, bên nhận (S1) dùng đầu đực."),
}
FONT = "(effects (font (size 1.27 1.27)))"
AN = "(effects (font (size 1.27 1.27)) (hide yes))"


def thuoc_tinh(ref, ten, fp, mo_ta, loc, y):
    s = [
        f'    (property "Reference" "{ref}" (at 0 {n(y + 1.27)} 0) {FONT})',
        f'    (property "Value" "{ten}" (at 0 {n(-y - 1.27)} 0) {FONT})',
        f'    (property "Footprint" "IRIS:{fp}" (at 0 0 0) {AN})',
        f'    (property "Datasheet" "" (at 0 0 0) {AN})',
        f'    (property "Description" "{mo_ta}" (at 0 0 0) {AN})',
        f'    (property "ki_keywords" "IRIS" (at 0 0 0) {AN})',
    ]
    if loc:
        s.append(f'    (property "ki_fp_filters" "{loc}" (at 0 0 0) {AN})')
    return s


def cong_sym(ten):
    chan, fp, loc, mo_ta = CONG[ten]
    y0 = 1.27 * (len(chan) - 1)
    nua = y0 + 1.27
    s = [f'  (symbol "{ten}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)']
    s += thuoc_tinh("J", ten, fp, mo_ta, loc, nua)
    s += [f'    (symbol "{ten}_0_1" (rectangle (start -5.08 {n(nua)}) (end 5.08 {n(-nua)}) '
          "(stroke (width 0.254) (type default)) (fill (type background))))",
          f'    (symbol "{ten}_1_1"']
    # chân kiểu thụ động: cùng một ký hiệu dùng cho cả bên cấp lẫn bên nhận
    for i, c in enumerate(chan):
        s.append(f"      (pin passive line (at -7.62 {n(y0 - 2.54 * i)} 0) (length 2.54) "
                 f'(name "{c}" {FONT}) (number "{i + 1}" {FONT}))')
    s += ["    )", "  )"]
    return s


def mat_sym():
    """Mắt phản xạ ITR8307 với chân kiểu thụ động.

    Ký hiệu gốc của KiCad khai cực E là open_emitter, ERC báo lỗi khi nối xuống GND có PWR_FLAG.
    """
    ten = "Mat_ITR8307"
    s = [f'  (symbol "{ten}" (pin_names (offset 0.508)) (exclude_from_sim no) (in_bom yes) (on_board yes)']
    s += thuoc_tinh("OP", ten, "", "Mắt phản xạ hồng ngoại Everlight ITR8307: LED (A, K) và phototransistor (C, E).", "*ITR8307*", 3.81)
    s[3] = s[3].replace('"IRIS:"', '"OptoDevice:Everlight_ITR8307"')
    s += [f'    (symbol "{ten}_0_1" (rectangle (start -5.08 3.81) (end 5.08 -3.81) '
          "(stroke (width 0.254) (type default)) (fill (type background))))",
          f'    (symbol "{ten}_1_1"']
    for so, c, x, y, goc in (("1", "K", -7.62, -2.54, 0), ("2", "A", -7.62, 2.54, 0),
                             ("3", "C", 7.62, 2.54, 180), ("4", "E", 7.62, -2.54, 180)):
        s.append(f"      (pin passive line (at {x} {y} {goc}) (length 2.54) "
                 f'(name "{c}" {FONT}) (number "{so}" {FONT}))')
    s += ["    )", "  )"]
    return s


# tên: (ref, chân linh kiện, mô tả, chân trái, chân phải, chân dưới); mỗi chân là (số, tên)
IC = {
    "IP2326": ("U", "Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.5x2.5mm",
               "Injoinic IP2326: sạc tăng áp pin lithium 2/3 cell nối tiếp, 15 W, có cân bằng 2 cell. QFN-24 4x4.",
               [("13", "VIN"), ("12", "EN"), ("2", "DP"), ("1", "DM"), ("11", "ISET"), ("3", "VSET"), ("4", "NTC"),
                ("7", "TIME_SET"), ("8", "VIN_UVSET"), ("9", "VIN_OVSET"), ("10", "CON_SEL")],
               [("14", "BST"), ("15", "LX"), ("16", "LX"), ("17", "LX"), ("19", "VSYS"), ("20", "VSYS"),
                ("21", "VOUT"), ("22", "VOUT"), ("23", "VBATM"), ("24", "VBAT_GND"), ("5", "BAT_STAT"),
                ("6", "LED"), ("18", "PGND")],
               [("25", "GND")]),
    "AHT20": ("U", "IRIS:AHT20_DFN6_3x3",
              "ASAIR AHT20: cảm biến nhiệt độ, độ ẩm I2C (0x38). DFN 3x3 6 chân, số chân và chân linh kiện theo datasheet V1.0.",
              [("2", "VDD"), ("5", "GND")], [("3", "SCL"), ("4", "SDA"), ("1", "NC"), ("6", "NC")], []),
    # Sơ đồ chân HY2120 và 8205A ghi theo trí nhớ, CHƯA đối chiếu datasheet: xem THIET-KE-MACH.md mục 7.4
    "HY2120": ("U", "Package_TO_SOT_SMD:SOT-23-6",
               "HYCON HY2120: bảo vệ pin lithium 2 cell nối tiếp. SOT-23-6. Số chân CHƯA đối chiếu datasheet.",
               [("5", "VDD"), ("4", "VC"), ("6", "VSS")], [("1", "OD"), ("2", "OC"), ("3", "CS")], []),
    "FET_Kep_8205": ("Q", "Package_SO:TSSOP-8_4.4x3mm_P0.65mm",
                     "MOSFET N kép chung cực D kiểu 8205A (20 V, 6 A), TSSOP-8. Số chân CHƯA đối chiếu datasheet.",
                     [("4", "G1"), ("5", "G2")],
                     [("2", "S1"), ("3", "S1"), ("1", "D"), ("8", "D"), ("6", "S2"), ("7", "S2")], []),
}


def ic_sym(ten):
    """Ký hiệu IC dạng hộp, mọi chân kiểu thụ động, bước chân 2,54 mm."""
    ref, fp, mo_ta, trai, phai, duoi = IC[ten]
    nua = 1.27 * max(len(trai), len(phai)) + 1.27
    s = [f'  (symbol "{ten}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)']
    s += thuoc_tinh(ref, ten, "", mo_ta, "", nua)
    s[3] = s[3].replace('"IRIS:"', f'"{fp}"')
    s += [f'    (symbol "{ten}_0_1" (rectangle (start -12.7 {n(nua)}) (end 12.7 {n(-nua)}) '
          "(stroke (width 0.254) (type default)) (fill (type background))))",
          f'    (symbol "{ten}_1_1"']
    for ds, x, goc in ((trai, -15.24, 0), (phai, 15.24, 180)):
        y0 = 1.27 * (len(ds) - 1)
        for i, (so, c) in enumerate(ds):
            s.append(f"      (pin passive line (at {x} {n(y0 - 2.54 * i)} {goc}) (length 2.54) "
                     f'(name "{c}" {FONT}) (number "{so}" {FONT}))')
    for i, (so, c) in enumerate(duoi):
        s.append(f"      (pin passive line (at {n(2.54 * i)} {n(-nua - 2.54)} 90) (length 2.54) "
                 f'(name "{c}" {FONT}) (number "{so}" {FONT}))')
    s += ["    )", "  )"]
    return s


def khung_sym(co):
    w, h, dung = KHUNG[co]
    ten = f"Khung_{co}_{w}x{h}"
    net = "(stroke (width 0.254) (type default)) (fill (type none))"
    s = [f'  (symbol "{ten}" (pin_names (offset 1.016)) (exclude_from_sim yes) (in_bom no) (on_board yes)']
    s += thuoc_tinh("KH", ten, ten, f"Khung bo cỡ {co}, {w} x {h} mm: đường cắt và lỗ gá. Dùng cho: {dung}", "", 3.81)
    s += [f'    (symbol "{ten}_0_1"', f"      (rectangle (start -5.08 3.81) (end 5.08 -3.81) {net})"]
    s += [f"      (circle (center {x} {y}) (radius 0.635) {net})" for x in (-3.81, 3.81) for y in (-2.54, 2.54)]
    s += ["    )", "  )"]
    return s


def main():
    PRETTY.mkdir(exist_ok=True)
    for cu in PRETTY.glob("*.kicad_mod"):
        cu.unlink()
    for ten, (lib, goc) in DAU_CAM.items():
        t = (FP_GOC / f"{lib}.pretty" / f"{goc}.kicad_mod").read_text(encoding="utf-8")
        assert t.count(f'"{goc}"') == 2, goc      # tên chân linh kiện và thuộc tính Value
        t = t.replace(f'"{goc}"', f'"{ten}"')
        t = re.sub(r'\(descr "', f'(descr "IRIS {ten}, sao từ {lib}:{goc}. ', t, count=1)
        (PRETTY / f"{ten}.kicad_mod").write_text(t, encoding="utf-8", newline="\n")
    for co in KHUNG:
        ten, t = khung_fp(co)
        (PRETTY / f"{ten}.kicad_mod").write_text(t, encoding="utf-8", newline="\n")
    (PRETTY / "AHT20_DFN6_3x3.kicad_mod").write_text(aht20_fp(), encoding="utf-8", newline="\n")

    s = ['(kicad_symbol_lib (version 20231120) (generator "iris_tao_thu_vien") (generator_version "1.0")']
    for ten in CONG:
        s += cong_sym(ten)
    for co in KHUNG:
        s += khung_sym(co)
    s += mat_sym()
    for ten in IC:
        s += ic_sym(ten)
    s.append(")")
    sym = DAY / "IRIS.kicad_sym"
    sym.write_text("\n".join(s) + "\n", encoding="utf-8", newline="\n")

    # để KiCad đọc lại và ghi theo định dạng hiện hành; lỗi cú pháp sẽ lộ ra ở đây
    cli = str(KICAD / "bin/kicad-cli")
    subprocess.run([cli, "fp", "upgrade", "--force", str(PRETTY)], check=True)
    subprocess.run([cli, "sym", "upgrade", "--force", str(sym)], check=True)
    print(f"{len(list(PRETTY.glob('*.kicad_mod')))} chân linh kiện, {len(CONG) + len(KHUNG) + 1 + len(IC)} ký hiệu")


if __name__ == "__main__":
    main()
