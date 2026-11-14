"""Linh kiện mua sẵn, dựng dạng khối bao để kiểm tra lắp ráp (không phải mô hình chính xác của hãng)."""
from cadgen import build123d as bd

from lib.chuan import hop, to, tru, tru_y

# Servo SG90 / MG90S
SG_L, SG_W, SG_H = 22.5, 12.2, 22.7     # thân
SG_TAI_Z, SG_TAI_T, SG_TAI_L = 15.9, 2.5, 32.3   # tai bắt vít: cao độ đáy tai, dày, dài
SG_TAI_LO = 27.8                         # khoảng cách 2 lỗ tai
SG_TRUC_X = 5.35                         # trục ra lệch tâm thân
SG_DINH = 31.0                           # mặt trên cần servo so với đáy thân

# Động cơ N20 có encoder
N20_HOP, N20_THAN, N20_ENC, N20_TRUC = 9.0, 15.0, 8.0, 10.0
N20_W, N20_H = 12.0, 10.0

BANH_D, BANH_W = 65.0, 26.0
MAT_TRAU_H = 12.0


def tru_do(h, x=0.0, y=0.0, z=0.0):
    return to(tru(5.5, h, x, y, z), "tru_M3", "dong")


def sg90(goc=0.0):
    """Servo đứng: tâm đáy thân ở gốc, trục ra hướng +Z tại x = SG_TRUC_X."""
    than = hop(SG_L, SG_W, SG_H) + hop(SG_TAI_L, SG_W, SG_TAI_T, z=SG_TAI_Z) \
        + tru(11.8, 4.2, x=SG_TRUC_X, z=SG_H) + tru(4.8, 2.6, x=SG_TRUC_X, z=SG_H + 4.2)
    can = tru(7.0, 1.5) + hop(16.0, 5.0, 1.5, x=8.0)
    can = bd.Pos(SG_TRUC_X, 0, SG_DINH - 1.5) * bd.Rot(0, 0, goc) * can
    return [to(than, "servo_SG90", "xanh"), to(can, "can_servo", "trang")]


def sg90_truc(goc=0.0):
    """Servo với gốc đặt tại tâm trục, mặt ngoài cần servo ở z = 0, thân nằm phía -Z."""
    return [bd.Pos(-SG_TRUC_X, 0, -SG_DINH) * p for p in sg90(goc)]


def n20():
    """Động cơ N20: trục dọc +Y, gốc ở mặt trước hộp số (nơi trục ra)."""
    hs = bd.Pos(0, -N20_HOP / 2, 0) * bd.Box(N20_W, N20_HOP, N20_H)
    than = tru_y(N20_W, N20_THAN, y=-N20_HOP - N20_THAN) & \
        (bd.Pos(0, -N20_HOP - N20_THAN / 2, 0) * bd.Box(N20_W, N20_THAN, N20_H))
    enc = bd.Pos(0, -N20_HOP - N20_THAN - N20_ENC / 2, 0) * bd.Box(N20_W, N20_ENC, N20_W)
    truc = tru_y(3.0, N20_TRUC)
    return [to(hs, "N20_hop_so", "dong"), to(than, "N20_than", "bac"),
            to(enc, "N20_encoder", "den"), to(truc, "N20_truc", "bac")]


def jga25():
    """Động cơ JGA25-370 có encoder: trục dọc +Y, gốc ở mặt trước hộp số."""
    return [to(tru_y(25.0, 21.0, y=-21.0), "JGA25_hop_so", "dong"),
            to(tru_y(24.4, 31.0, y=-52.0), "JGA25_than", "bac"),
            to(tru_y(24.0, 12.0, y=-64.0), "JGA25_encoder", "den"),
            to(tru_y(7.0, 2.5) + tru_y(4.0, 12.0), "JGA25_truc", "bac")]


def banh_xe():
    """Bánh Ø65 x 26, trục dọc Y, tâm ở gốc."""
    lop = tru_y(BANH_D, BANH_W, y=-BANH_W / 2) - tru_y(BANH_D - 12, BANH_W + 2, y=-BANH_W / 2 - 1)
    mam = tru_y(BANH_D - 12, BANH_W - 6, y=-BANH_W / 2 + 3) - tru_y(3.0, BANH_W + 2, y=-BANH_W / 2 - 1)
    return [to(lop, "lop_banh", "den"), to(mam, "mam_banh", "vang")]


def mat_trau():
    """Bánh mắt trâu mini: mặt bắt vít ở z = 0, bi chạm đất ở z = -MAT_TRAU_H."""
    vo = hop(28.0, 12.0, 2.0, z=-2.0) + tru(15.0, 6.0, z=-8.0)
    bi = bd.Pos(0, 0, -MAT_TRAU_H + 5.0) * bd.Sphere(5.0)
    return [to(vo, "mat_trau_vo", "trang"), to(bi, "mat_trau_bi", "bac")]


def quat_4010():
    """Quạt 40x40x10, tâm ở gốc, mặt gá z = 0, thổi theo +Z."""
    vo = hop(40.0, 40.0, 10.0) - tru(37.0, 12.0, z=-1.0)
    for sx in (-16, 16):
        for sy in (-16, 16):
            vo -= tru(3.2, 12.0, sx, sy, -1.0)
    canh = tru(16.0, 8.0, z=1.0) + hop(34.0, 5.0, 1.5, z=4.0) + hop(5.0, 34.0, 1.5, z=4.0)
    return [to(vo, "quat_vo", "den"), to(canh, "quat_canh", "xam")]


def bom_mini():
    """Bơm chìm mini 3–5 V: đứng, đáy ở z = 0."""
    return [to(tru(24.0, 33.0) + tru(7.0, 12.0, x=6.0, z=33.0), "bom_mini", "trang")]
