"""Vỏ bo mang O2: đế. Tệp sinh tự động bởi tao_tep_vo.py; thông số ở hardware/bo-mang/bo_tri.py."""
from cadgen import step, stl

from lib.vo import de


@step(out="../../STEP/vo/vo_O2_de.step")
@stl(out="../../STL/vo/vo_O2_de.stl")
def vo_o2_de():
    return de("O2")


if __name__ == "__main__":
    vo_o2_de()
