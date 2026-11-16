"""Vỏ bo mang I5: đế. Tệp sinh tự động bởi tao_tep_vo.py; thông số ở hardware/bo-mang/bo_tri.py."""
from cadgen import step, stl

from lib.vo import de


@step(out="../../STEP/vo/vo_I5_de.step")
@stl(out="../../STL/vo/vo_I5_de.stl")
def vo_i5_de():
    return de("I5")


if __name__ == "__main__":
    vo_i5_de()
