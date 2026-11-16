"""Hình cắt dùng chung cho các chi tiết cánh tay robot lắp servo MG90S nằm ngang (trục dọc Y)."""
from lib.chuan import T_TAM, hop, tru_y
from lib.kt import MG_KHE, MG_O
from lib.mua_san import MG_LO


def o_servo(x, y=0.0, z=0.0):
    """Ô lắp thân MG90S xuyên vách dày T_TAM (vách nằm trong mặt XZ, từ y đến y + T_TAM), trục servo tại (x, z).

    Gồm ô chữ nhật cho thân và hai khe vít tai. Khe dài MG_KHE, mép ngoài trùng lỗ tai của mô hình,
    kéo vào trong để nhận cả servo có lỗ tai gần nhau hơn.
    """
    s = hop(MG_O[1] - MG_O[0], T_TAM + 2, 2 * MG_O[2], x + (MG_O[0] + MG_O[1]) / 2, y + T_TAM / 2, z - MG_O[2])
    for lo, huong in zip(MG_LO, (1, -1)):
        tam = x + lo + huong * (MG_KHE - 1.8) / 2
        s += hop(MG_KHE, T_TAM + 2, 1.8, tam, y + T_TAM / 2, z - 0.9)
    return s


def lo_can(x=0.0, y=0.0, z=0.0):
    """Lỗ bắt cần servo: lỗ giữa Ø2,5 cho vít trục và hai lỗ Ø2 cho vít tự ren của cần."""
    s = tru_y(2.5, T_TAM + 2, x, y - 1, z)
    for dx in (8.0, 14.0):
        s += tru_y(2.0, T_TAM + 2, x + dx, y - 1, z)
    return s
