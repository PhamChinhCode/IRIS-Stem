"""Các khối sơ đồ dùng chung: lõi STM32G030 (S2, S3), ổn áp 3V3, cổng I2C, buck 5,45 V (C2, O7).

Thiết kế: ../THIET-KE-MACH.md mục 2. Toạ độ theo lưới 1,27 mm.
"""
from sch import FP

C0805 = FP["C0805"]


def tu_treo(s, ref, gt, x, y_ray, fp=None, lib="Device:C_Small"):
    """Tụ treo từ thanh nguồn nằm ngang (x, y_ray) xuống GND."""
    _, tren, duoi = s.doc(lib, ref, gt, x, y_ray + 4, fp or FP["C"])
    s.w((x, y_ray), tren)
    s.nguon("GND", duoi)


def khoi_ldo(s, x0, y0, vao="+5V", refs=("U2", "C1", "C2"), tieu_de="NGUỒN LOGIC 3V3 (từ 5 V của cổng I2C)"):
    """Ổn áp 3,3 V AP2112K từ `vao` (ký hiệu nguồn nếu bắt đầu bằng '+', còn lại là nhãn). Khung 114 × 36."""
    s.khoi(x0, y0, x0 + 114, y0 + 36, tieu_de, [
        f"{refs[0]} AP2112K-3.3: vào tối đa 6 V, 600 mA; EN nối VIN",
    ])
    y = y0 + 14
    if vao.startswith("+"):
        s.nguon(vao, (x0 + 6, y))
    else:
        s.nhan(vao, (x0 + 12, y), "trai")
    s.co_nguon((x0 + 15, y))
    u2 = s.dat("Regulator_Linear:AP2112K-3.3", refs[0], "AP2112K-3.3", x0 + 40, y + 2, 0, MPN="AP2112K-3.3TRG1")
    s.w((x0 + (6 if vao.startswith("+") else 12), y), u2.p("VIN"))
    tu_treo(s, refs[1], "10u/25V", x0 + 23, y, C0805)
    s.w(u2.p("EN"), (x0 + 30, u2.p("EN")[1]), (x0 + 30, y))
    s.nguon("GND", u2.p("GND"))
    s.nc(u2.p("NC"))
    s.w(u2.p("VOUT"), (x0 + 62, y))
    tu_treo(s, refs[2], "10u/25V", x0 + 54, y, C0805)
    s.nguon("+3V3", (x0 + 62, y))
    s.nguon("GND", (x0 + 78, y + 6))
    s.w((x0 + 78, y + 6), (x0 + 78, y + 2))
    s.co_nguon((x0 + 78, y + 2))


def gop(s, k, chan, dich, dai=4, cuc_bo=False, cuoi=False):
    """Gộp các chân liền nhau cùng phía của k (góc 0) về một nhãn / ký hiệu nguồn ở hàng chân đầu (hoặc cuối)."""
    dx, dy = k.huong(chan[0])
    assert dy == 0
    ds = [k.p(c) for c in chan]
    x = ds[0][0] + dx * dai
    for a in ds:
        s.w(a, (x, a[1]))
    s.w((x, ds[0][1]), (x, ds[-1][1]))
    yb = ds[-1 if cuoi else 0][1]
    b = (x + 2 * dx, yb)
    s.w((x, yb), b)
    h = "phai" if dx > 0 else "trai"
    if dich == "GND" or dich.startswith("+"):
        s.nguon(dich, b, h)
    elif cuc_bo:
        s.ten_day(dich, b, h)
    else:
        s.nhan(dich, b, h)


def khoi_buck(s, x0, y0, vao, ra, u, cuon, tu, tro, co_ra=False):
    """Buck TPS563201 ra 5,45 V / 3 A. tu: 7 ref (3 vào, bootstrap, 3 ra); tro: 4 ref (EN, 2 trên, dưới). Khung 124 × 46."""
    s.khoi(x0, y0, x0 + 124, y0 + 46, "BUCK 5,45 V / 3 A (TPS563201, 580 kHz)", [
        f"Vout = 0,768 × (1 + (51k + 10k) / 10k) = 5,45 V.  ΔI = 1,0 A ở 8,4 V vào; {cuon}: I_sat ≥ 4,5 A, có che chắn",
        "Tụ ra 22 µF / 16 V 0805.  Tụ vào đặt sát chân VIN–GND; đường SW ngắn; 2 A liên tục, 3 A là đỉnh ngắn (nhiệt)",
    ])
    y = y0 + 14
    s.nhan(vao, (x0 + 12, y), "trai")
    ic = s.dat("Regulator_Switching:TPS563201", u, "TPS563201", x0 + 56, y + 2, 0, vt_ref=(-4, -7), vt_gt=(-7, 7.5),
               MPN="TPS563201DDCR", LCSC="C116592", Manufacturer="Texas Instruments")
    assert ic.p("VIN") == (x0 + 48, y) and ic.p("SW") == (x0 + 64, y), (ic.p("VIN"), ic.p("SW"))
    s.w((x0 + 12, y), ic.p("VIN"))
    tu_treo(s, tu[0], "10u/25V", x0 + 14, y, C0805)
    tu_treo(s, tu[1], "10u/25V", x0 + 23, y, C0805)
    tu_treo(s, tu[2], "100n", x0 + 32, y)
    r = s.dat("Device:R_Small", tro[0], "100k", x0 + 44, y + 2, 0, FP["R"], vt_ref=(-2.6, -1.1), vt_gt=(-3.4, 1.1))
    s.w(r.p("2"), ic.p("EN"))
    s.nguon("GND", ic.p("GND"))
    # bootstrap: VBST – tụ – SW
    cb = s.dat("Device:C_Small", tu[3], "100n", x0 + 69, y + 2, 90, FP["C"], vt_ref=(1, 2.6), vt_gt=(1, 4.8))
    s.w(ic.p("VBST"), cb.p("1"))
    s.w(cb.p("2"), (x0 + 72, y + 2), (x0 + 72, y))
    L = s.dat("Device:L", cuon, "3u3", x0 + 79, y, 90, "Inductor_SMD:L_Sunlord_SWPA6045S", vt_ref=(0, -2.4), vt_gt=(0, 2.4))
    s.w(ic.p("SW"), L.p("1"))
    s.w(L.p("2"), (x0 + 114, y))
    # phân áp phản hồi
    X = x0 + 87
    _, t, d = s.R(tro[1], "51k", X, y + 4)
    s.w((X, y), t)
    _, t2, d2 = s.R(tro[2], "10k", X, y + 9)
    s.w(d, t2)
    _, t3, d3 = s.R(tro[3], "10k", X, y + 17)
    s.w(d2, t3)
    s.nguon("GND", d3)
    f = ic.p("VFB")
    s.w(f, (x0 + 66, f[1]), (x0 + 66, y + 13), (X, y + 13))
    for i in range(3):
        tu_treo(s, tu[4 + i], "22u", x0 + 95 + 6 * i, y, C0805)
    if co_ra:
        s.co_nguon((x0 + 112, y))
    if ra.startswith("+"):
        s.nguon(ra, (x0 + 114, y), "phai")
    else:
        s.nhan(ra, (x0 + 114, y))


def khoi_i2c(s, x0, y0):
    """Hai cổng I2C song song J1, J2, ESD U3, điện trở nối tiếp R1, R2. Khung 114 × 54."""
    s.khoi(x0, y0, x0 + 114, y0 + 54, "CỔNG I2C VÀO / RA + ESD", [
        "Hai cổng nối song song cả 4 chân để nối chuỗi module",
        "Không đặt điện trở kéo lên I2C trên module (chỉ bo chủ C1 có)",
    ])
    for ref, y in (("J1", y0 + 12), ("J2", y0 + 28)):
        j = s.dat("IRIS:Cong_I2C", ref, "I2C", x0 + 10, y, 180, vt_ref=(-2, -7), vt_gt=(-2, 7))
        for chan, dich in (("GND", "GND"), ("5V", "+5V"), ("SDA", "SDA_BUS"), ("SCL", "SCL_BUS")):
            a = j.p(chan)
            b = (a[0] + 4, a[1])
            s.w(a, b)
            if dich[0] in "G+":
                s.nguon(dich, b, "phai")
            else:
                s.nhan(dich, b)
    u3 = s.dat("Power_Protection:SRV05-4", "U3", "SRV05-4", x0 + 56, y0 + 20, 0, MPN="SRV05-4")
    s.chia(u3, {"1": "SDA_BUS", "3": "SCL_BUS", "4": None, "6": None, "5": "+3V3", "2": "GND"})
    for ref, y, ten in (("R1", y0 + 12, "SDA"), ("R2", y0 + 28, "SCL")):
        _, tr, ph = s.R(ref, "100R", x0 + 92, y, ngang=True)
        s.w((x0 + 88, y), tr)
        s.nhan(ten + "_BUS", (x0 + 88, y), "trai")
        s.w(ph, (x0 + 96, y))
        s.nhan(ten, (x0 + 96, y))


def khoi_mcu(s, x0, y0, bang, ghi_chu, tps=("+3V3", "SWDIO", "SWCLK", "NRST", "GND")):
    """STM32G030K8T6 U1 cùng tụ tách C3, C4, NRST C5, kéo xuống BOOT0 R3, LED1 + R4, điểm nạp.

    bang: {số chân: tên lưới | None}; các chân nguồn, NRST, SWD, I2C được điền sẵn. Khung 120 × 136.
    """
    s.khoi(x0, y0, x0 + 120, y0 + 136, "VI ĐIỀU KHIỂN STM32G030K8T6", ghi_chu)
    day_du = {str(i): None for i in range(1, 33)}
    day_du.update({"4": "+3V3", "5": "GND", "6": "NRST", "24": "SWDIO", "25": "SWCLK", "30": "SCL", "31": "SDA"})
    day_du.update(bang)
    u1 = s.dat("MCU_ST_STM32G0:STM32G030K8Tx", "U1", "STM32G030K8T6", x0 + 74, y0 + 62, 0,
               MPN="STM32G030K8T6", LCSC="C431631", Manufacturer="STMicroelectronics")
    s.chia(u1, day_du)
    X = x0 + 10
    for ref, gt, x, fp in (("C3", "100n", X, None), ("C4", "10u/25V", X + 9, C0805)):
        _, t, d = s.C(ref, gt, x, y0 + 14, fp)
        s.nguon("+3V3", t)
        s.nguon("GND", d)
    _, t, d = s.C("C5", "100n", X, y0 + 30)
    s.w(t, (X, y0 + 26), (X + 4, y0 + 26))
    s.nhan("NRST", (X + 4, y0 + 26))
    s.nguon("GND", d)
    _, t, d = s.R("R3", "10k", X, y0 + 44)
    s.w(t, (X, y0 + 40), (X + 4, y0 + 40))
    s.nhan("SWCLK", (X + 4, y0 + 40))
    s.nguon("GND", d)
    y = y0 + 56
    s.nhan("LED", (X + 4, y), "trai")
    _, tr, ph = s.R("R4", "1k", X + 8, y, ngang=True)
    s.w((X + 4, y), tr)
    led1 = s.dat("Device:LED_Small", "LED1", "STATUS", X + 15, y, 180, FP["LED"], vt_ref=(0, -2.4), vt_gt=(0, 2.6))
    s.w(ph, led1.p("2"))
    s.w(led1.p("1"), (X + 19, y))
    s.nguon("GND", (X + 19, y), "phai")
    for i, ten in enumerate(tps):
        y = y0 + 92 - 6 * (len(tps) - 5) + 6 * i
        tp = s.dat("Connector:TestPoint", f"TP{i + 1}", ten, X + 12, y, 0, FP["TP"], vt_ref=(3.5, -2), vt_gt=(3.5, 0))
        tp.an_gt = True
        s.w((X + 4, y), tp.p("1"))
        if ten[0] in "G+":
            s.nguon(ten, (X + 4, y), "trai")
        else:
            s.nhan(ten, (X + 4, y), "trai")
    return u1


def tep_du_an(thu_muc, ten, chung="../common"):
    """Ghi sym-lib-table, fp-lib-table và .kicad_pro tối thiểu nếu chưa có. `chung`: đường tới thư mục common."""
    import os
    bang = ('(%s_lib_table\n  (version 7)\n  (lib (name "IRIS") (type "KiCad") (uri "${KIPRJMOD}/' + chung +
            '/IRIS.%s") (options "") (descr "Thư viện chung IRIS-Stem"))\n)\n')
    nd = {
        "sym-lib-table": bang % ("sym", "kicad_sym"),
        "fp-lib-table": bang % ("fp", "pretty"),
        ten + ".kicad_pro": '{\n  "meta": { "filename": "%s.kicad_pro", "version": 3 }\n}\n' % ten,
    }
    for t, n in nd.items():
        d = os.path.join(thu_muc, t)
        if not os.path.exists(d):
            open(d, "w", encoding="utf-8", newline="\n").write(n)


