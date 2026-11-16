"""Vỏ bo mang I7: đế. Tệp sinh tự động bởi tao_tep_vo.py; thông số ở hardware/bo-mang/bo_tri.py."""
from cadgen import step, stl

from lib.vo import de


@step(out="../../STEP/vo/vo_I7_de.step")
@stl(out="../../STL/vo/vo_I7_de.stl")
def vo_i7_de():
    return de("I7")


if __name__ == "__main__":
    vo_i7_de()
