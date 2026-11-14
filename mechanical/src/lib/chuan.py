"""Chuẩn cơ khí của bộ kit và các hàm dựng hình dùng chung.

Đơn vị mm. Mọi tấm gá dùng lưới lỗ 8 mm, lỗ Ø3,4 cho vít M3.
Quy ước tấm: mặt dưới ở z = 0, mặt trên ở z = dày, tâm tấm ở gốc XY.
"""
from cadgen import build123d as bd
from cadgen import srgb

G = 8.0          # bước lưới
D_M3 = 3.4       # lỗ thông vít M3 trên chi tiết in/cắt
D_PCB = 3.2      # lỗ gá trên bo mạch
T_TAM = 3.0      # dày tấm cắt laser / tấm in mỏng
T_XE = 4.0       # dày tấm khung xe
T_PCB = 1.6
H_TRU = 6.0      # trụ đỡ bo mạch mặc định

MAU = {
    "in3d": "#F28C28", "in3d2": "#3A7BD5", "laser": "#D8B47A", "pcb": "#1E6B45",
    "den": "#22252A", "trang": "#F2F2EE", "xam": "#8A9099", "bac": "#C9CED6",
    "do": "#C8372D", "vang": "#E8B923", "xanh": "#2E78C7", "la": "#3FA34D",
    "nau": "#6B4A2B", "nuoc": "#6FB7E8", "dong": "#B8862B",
}


def to(shape, ten, mau):
    """Gắn nhãn và màu cho một khối lá."""
    shape.label = ten
    shape.color = srgb(MAU.get(mau, mau))
    return shape


def cum(ten, parts):
    return bd.Compound(label=ten, children=list(parts))


def hop(lx, ly, lz, x=0.0, y=0.0, z=0.0):
    """Hộp có tâm XY tại (x, y), đáy tại z."""
    return bd.Pos(x, y, z + lz / 2) * bd.Box(lx, ly, lz)


def tru(d, h, x=0.0, y=0.0, z=0.0):
    """Trụ đứng đường kính d, đáy tại z."""
    return bd.Pos(x, y, z + h / 2) * bd.Cylinder(d / 2, h)


def tru_y(d, h, x=0.0, y=0.0, z=0.0):
    """Trụ nằm dọc trục Y, bắt đầu tại y, dài h về phía +Y."""
    return bd.Pos(x, y + h / 2, z) * bd.Rot(90, 0, 0) * bd.Cylinder(d / 2, h)


def tru_x(d, h, x=0.0, y=0.0, z=0.0):
    """Trụ nằm dọc trục X, bắt đầu tại x, dài h về phía +X."""
    return bd.Pos(x + h / 2, y, z) * bd.Rot(0, 90, 0) * bd.Cylinder(d / 2, h)


def khung(o, x_dir, z_dir):
    """Phép đặt: gốc o, trục X và pháp tuyến Z cục bộ cho trước."""
    return bd.Plane(origin=o, x_dir=x_dir, z_dir=z_dir).location


def dat(loc, parts):
    return [loc * p for p in parts]


def toa_do_luoi(lx, ly, buoc=G):
    nx, ny = int(lx // buoc), int(ly // buoc)
    xs = [(i - (nx - 1) / 2) * buoc for i in range(nx)]
    ys = [(j - (ny - 1) / 2) * buoc for j in range(ny)]
    return xs, ys


def tam_luoi(lx, ly, t=T_TAM, r=4.0, d=D_M3, khoet=(), tron=(), bo_lo=None,
             da_giac=None, buoc=G):
    """Tấm lưới lỗ. khoet: [(x, y, rộng, cao)]; tron: [(x, y, đường kính)];
    bo_lo(x, y) -> True để bỏ lỗ lưới; da_giac: biên ngoài thay cho chữ nhật."""
    xs, ys = toa_do_luoi(lx, ly, buoc)
    pts = [(x, y) for x in xs for y in ys if not (bo_lo and bo_lo(x, y))]
    with bd.BuildSketch() as sk:
        if da_giac:
            bd.Polygon(*da_giac, align=None)
        else:
            bd.RectangleRounded(lx, ly, r)
        if pts:
            with bd.Locations(*pts):
                bd.Circle(d / 2, mode=bd.Mode.SUBTRACT)
        for (x, y, w, h) in khoet:
            with bd.Locations((x, y)):
                bd.Rectangle(w, h, mode=bd.Mode.SUBTRACT)
        for (x, y, dd) in tron:
            with bd.Locations((x, y)):
                bd.Circle(dd / 2, mode=bd.Mode.SUBTRACT)
    return bd.extrude(sk.sketch, t)


def ngoai_khoet(khoet=(), tron=(), le=2.0):
    """Hàm bo_lo: bỏ các lỗ lưới chạm vào vùng khoét."""
    def f(x, y):
        for (cx, cy, w, h) in khoet:
            if abs(x - cx) < w / 2 + le and abs(y - cy) < h / 2 + le:
                return True
        for (cx, cy, dd) in tron:
            if (x - cx) ** 2 + (y - cy) ** 2 < (dd / 2 + le) ** 2:
                return True
        return False
    return f


class Tam:
    """Một tấm lưới đã đặt trong không gian, biết kiểm tra lỗ gá có trùng lưới không."""

    def __init__(self, ten, shape, lx, ly, t, o=(0, 0, 0), x_dir=(1, 0, 0),
                 z_dir=(0, 0, 1), mau="in3d"):
        self.lx, self.ly, self.t = lx, ly, t
        self.loc = khung(o, x_dir, z_dir)
        self.xs, self.ys = toa_do_luoi(lx, ly)
        self.part = to(self.loc * shape, ten, mau)

    def _khop(self, pts, ten):
        for (x, y) in pts:
            ok = any(abs(x - a) < 0.01 for a in self.xs) and any(abs(y - b) < 0.01 for b in self.ys)
            if not ok:
                raise ValueError(f"{ten}: lỗ gá ({x:.1f}, {y:.1f}) không trùng lưới 8 mm của tấm")

    def gan(self, parts, lo, u, v, rz=0, duoi=False, ten="chi tiết"):
        """Đặt cụm chi tiết (gốc ở mặt gá, +Z hướng ra) lên tấm tại (u, v).
        lo: toạ độ lỗ gá của cụm; duoi=True gắn vào mặt dưới."""
        r = bd.Rot(0, 0, rz)
        if duoi:
            f = bd.Pos(u, v, 0) * bd.Rot(180, 0, 0) * r
        else:
            f = bd.Pos(u, v, self.t) * r
        pts = []
        for (x, y) in lo:
            p = (f * bd.Pos(x, y, 0)).position
            pts.append((p.X, p.Y))
        self._khop(pts, ten)
        return dat(self.loc * f, parts)


def chan_de(lx, ly, h=6.0, ox=0.0, oy=0.0):
    """Bốn chân cao su dưới tấm (mặt dưới tấm ở z = 0)."""
    return [to(tru(10.0, h, ox + sx * (lx / 2 - 12), oy + sy * (ly / 2 - 12), -h), "chan_cao_su", "den")
            for sx in (-1, 1) for sy in (-1, 1)]
