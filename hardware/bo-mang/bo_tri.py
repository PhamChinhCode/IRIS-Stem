"""Bố trí linh kiện chính và thông số vỏ của 19 bo mang. Dùng chung cho ve_pcb.py (KiCad) và mô hình vỏ in 3D.

Toạ độ cơ khí: gốc ở tâm bo, x sang phải, y lên trên, mm (trùng mechanical/src/lib/mach.py).
`dat`: {ref: (x, y, góc[, "B"])} là tâm courtyard của linh kiện đặt tay; linh kiện còn lại do ve_pcb.py tự đặt.
`vo`: cao = khoảng trống trong nắp phía trên mặt bo; lo = lỗ khoét trên mặt nắp
      ("cn", x, y, rộng, dài) hoặc ("tr", x, y, đường kính); canh = khe trên thành (cạnh, tâm, rộng, cao).
"""
S, M, L, T, QUE = (24, 32), (32, 48), (48, 64), (64, 24), (24, 96)


def lo_ga(kt):
    w, h = kt
    if kt == QUE:
        return [(-8.0, h / 2 - 4), (8.0, h / 2 - 4)]
    if kt == S:
        return [(sx * 8.0, y) for sx in (-1, 1) for y in (-h / 2 + 12, h / 2 - 4)]
    return [(sx * (w / 2 - 4), sy * (h / 2 - 4)) for sx in (-1, 1) for sy in (-1, 1)]


def _j1(kt, n=4):
    return (0, -kt[1] / 2 + 4.4, 0)


CONG_S = ("S", 0.0, 11.0, 6.0)        # khe cho đầu JST PH 4 chân ở cạnh dưới
BO = {
    "I1": dict(kt=S, dat={"J1": _j1(S), "SW1": (-5.6, 4, 0), "SW2": (5.6, 4, 0)},
               vo=dict(cao=5.4, lo=[("tr", -5.6, 4, 4.4), ("tr", 5.6, 4, 4.4)])),
    "I2": dict(kt=S, dat={"J1": _j1(S), "RV1": (0, 5.0, 90)},
               vo=dict(cao=7.2, tru=5.0, lo=[("tr", 0, 5.9, 7.6)])),
    "I3": dict(kt=M, dat={"J1": _j1(M), "J2": (0, 6, 90)},
               vo=dict(cao=4.6, lo=[], nap=False)),      # module joystick 26 x 34 rộng hơn khoảng giữa 4 vít
    "I4": dict(kt=L, dat={"J1": _j1(L), "U2": (-14, -18.5, 0),
                          **{f"SW{4 * r + c + 1}": (-15 + 10 * c, 21 - 10 * r, 0) for r in range(4) for c in range(4)}},
               vo=dict(cao=5.4, lo=[("tr", -15 + 10 * c, 21 - 10 * r, 4.4) for r in range(4) for c in range(4)])),
    "I5": dict(kt=S, dat={"J1": _j1(S), "R1": (0, 6, 0)},
               vo=dict(cao=5.4, lo=[("tr", 0, 6, 6.0)])),
    "I6": dict(kt=S, dat={"J1": _j1(S), "U2": (0, 8, 0)},
               vo=dict(cao=5.4, lo=[("cn", 0, 8 + dy, 8.0, 1.2) for dy in (-2.4, 0, 2.4)])),
    "I7": dict(kt=S, dat={"J1": _j1(S), "J2": (0, 5, 90)},
               vo=dict(cao=5.4, lo=[("tr", 0, 5, 11.0)])),
    "I8": dict(kt=M, dat={"J1": _j1(M), "U1": (0, 6, 0)},
               vo=dict(cao=6.0, lo=[("tr", 0, 6, 20.4)])),
    "I9": dict(kt=QUE, dat={"J1": (0, 43.6, 180), "TP1": (-5.75, 7, 0), "TP2": (5.75, 7, 0)},
               vung=(-11, 13, 11, 39.2), gnd=(-12, 11, 12, 48),
               dong=[("vung", "BAN_CUC", -10.5, -46, -1.0, 9), ("vung", "GND", 1.0, -46, 10.5, 9)],
               vo=dict(cao=5.4, tru=5.0, lo=[], canh=[("N", 0.0, 11.0, 6.0)], que=12.0)),
    "I10": dict(kt=M, dat={"J1": _j1(M), "TP1": (-11.5, -8, 0), "TP2": (11.5, 13.25, 0)},
                luoc=dict(a="+3V3", b="S1", x=11.5, y0=-8.0, n=9, buoc=1.25, rong=0.6), vung=(-15, -19, 15, -9.2),
                vo=dict(cao=5.4, lo=[("cn", 0, 3.3, 21.0, 24.0)])),
    "I11": dict(kt=T, dat={"J1": (0, 1.5, 0, "B"), "J2": (0, -9.5, 90)},
                vo=dict(cao=13.8, duoi=8.5, lo=[("tr", -13, -0.8, 16.8), ("tr", 13, -0.8, 16.8)], canh=[],
                        day=[("cn", 0, 1.5, 12.0, 6.5)])),
    "I12": dict(kt=S, dat={"J1": _j1(S), "U2": (0, 8, 0)},
                vo=dict(cao=7.6, lo=[("cn", 0, 8, 8.0, 6.0)])),
    "I13": dict(kt=L, dat={"J1": (0, -27.6, 0), "J2": (0, -17, 90)}, gnd=(-24, -32, 24, -12),
                vo=dict(cao=6.4, lo=[], canh=[("S", 0.0, 15.0, 6.0)], nap=False)),   # module RC522 40 x 60 không lọt giữa 4 vít
    "I14": dict(kt=S, dat={"J1": _j1(S), "U2": (0, 6, 0)},
                vo=dict(cao=5.4, lo=[("cn", 0, 6, 6.0, 5.0)])),
    "O1": dict(kt=S, dat={"J1": _j1(S), "LED1": (-5, 5, 90), "LED2": (5, 5, 90)},
               vo=dict(cao=5.4, lo=[("tr", -5, 5, 3.0), ("tr", 5, 5, 3.0)])),
    "O2": dict(kt=T, dat={"J1": _j1(T), **{f"LED{i + 1}": (-25.2 + 7.2 * i, 1.5, 0) for i in range(8)}},
               vo=dict(cao=5.4, lo=[("cn", 0, 1.5, 56.0, 5.6)])),
    "O3": dict(kt=M, dat={"J1": _j1(M), "J2": (0, 12.5, 90)},
               vo=dict(cao=11.6, lo=[("cn", 0, 2.5, 23.5, 12.5)])),
    "O4": dict(kt=M, dat={"J1": _j1(M), "K1": (0, 1, 90), "J2": (0, 18.2, 180)},
               vo=dict(cao=16.0, lo=[("cn", 0, 18.2, 15.6, 7.0)], canh=[CONG_S, ("N", 0.0, 15.6, 9.0)])),
    "O5": dict(kt=S, dat={"J1": _j1(S), "J2": (0, 9.6, 180)},
               vo=dict(cao=7.6, lo=[], canh=[CONG_S, ("N", 0.0, 8.4, 7.2)])),
}
