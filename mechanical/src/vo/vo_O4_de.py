"""Vỏ bo mang O4: đế. Tệp sinh tự động bởi tao_tep_vo.py; thông số ở hardware/bo-mang/bo_tri.py."""
from cadgen import step, stl

from lib.vo import de


@step(out="../../STEP/vo/vo_O4_de.step")
@stl(out="../../STL/vo/vo_O4_de.stl")
def vo_o4_de():
    return de("O4")


if __name__ == "__main__":
    vo_o4_de()
