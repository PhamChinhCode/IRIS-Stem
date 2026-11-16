"""Mọi bo mang kèm vỏ (đế + nắp) bày trên một mặt phẳng để soát lỗ khoét và khe đầu cắm."""
from cadgen import build123d as bd
from cadgen import step

from lib.chuan import cum
from lib.mach import KT, module
from lib.vo import BO, co_nap, de, nap

HANG = [["I4", "I13", "I3", "I8", "I10", "O3", "O4"],
        ["I11", "O2", "I1", "I2", "I5", "I6", "I7"],
        ["I12", "I14", "O1", "O5", "I9"]]


@step(out="../../STEP/mach/vo_module.step")
def vo_module():
    p, y = [], 0.0
    for hang in HANG:
        cao = max(KT[m][1] for m in hang)
        x = 0.0
        for m in hang:
            w = KT[m][0]
            ds = [module(m), de(m)] + ([nap(m)] if co_nap(m) else [])
            p.append(bd.Pos(x + w / 2, y - cao / 2, 0) * cum(f"{m}_co_vo", ds))
            x += w + 20.0
        y -= cao + 28.0
    return cum("vo_module", p)


if __name__ == "__main__":
    vo_module()
