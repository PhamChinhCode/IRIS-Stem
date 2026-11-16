"""Vỏ bo mang I12: nắp (đã lật úp để in). Tệp sinh tự động bởi tao_tep_vo.py; thông số ở hardware/bo-mang/bo_tri.py."""
from cadgen import step, stl

from lib.vo import nap


@step(out="../../STEP/vo/vo_I12_nap.step")
@stl(out="../../STL/vo/vo_I12_nap.stl")
def vo_i12_nap():
    return nap("I12", in3d=True)


if __name__ == "__main__":
    vo_i12_nap()
