"""Toàn bộ bo mạch của kit bày trên một mặt phẳng để so kích thước và vị trí đầu cắm."""
from cadgen import build123d as bd
from cadgen import step

from lib.chuan import cum
from lib.mach import KT, module

HANG = [["C1", "C2", "S1", "S2", "S3"],
        ["I4", "I13", "O7", "I3", "I8", "I10", "O3", "O4"],
        ["I11", "O2", "I1", "I2", "I5", "I6", "I7", "I12", "I14", "O1", "O5", "I9"]]


@step(out="../../STEP/mach/bo_module.step")
def bo_module():
    p, y = [], 0.0
    for hang in HANG:
        cao = max(KT[m][1] for m in hang)
        x = 0.0
        for m in hang:
            w, h, _ = KT[m]
            p.append(bd.Pos(x + w / 2, y - cao / 2, 0) * module(m))
            x += w + 16.0
        y -= cao + 24.0
    return cum("bo_module", p)


if __name__ == "__main__":
    bo_module()
