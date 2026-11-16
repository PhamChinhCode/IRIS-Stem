"""Vỏ bo mang O5: nắp (đã lật úp để in). Tệp sinh tự động bởi tao_tep_vo.py; thông số ở hardware/bo-mang/bo_tri.py."""
from cadgen import step, stl

from lib.vo import nap


@step(out="../../STEP/vo/vo_O5_nap.step")
@stl(out="../../STL/vo/vo_O5_nap.stl")
def vo_o5_nap():
    return nap("O5", in3d=True)


if __name__ == "__main__":
    vo_o5_nap()
