"""Vỏ bo mang I8: nắp (đã lật úp để in). Tệp sinh tự động bởi tao_tep_vo.py; thông số ở hardware/bo-mang/bo_tri.py."""
from cadgen import step, stl

from lib.vo import nap


@step(out="../../STEP/vo/vo_I8_nap.step")
@stl(out="../../STL/vo/vo_I8_nap.stl")
def vo_i8_nap():
    return nap("I8", in3d=True)


if __name__ == "__main__":
    vo_i8_nap()
