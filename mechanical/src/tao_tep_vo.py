"""Sinh các tệp mô hình vỏ bo mang trong vo/: mỗi tệp một chi tiết (đế hoặc nắp), theo quy ước một mô hình một tệp.

Chạy từ mechanical/src:  PYTHONUTF8=1 python tao_tep_vo.py
Sau đó dựng: for f in vo/*.py; do python "$f"; done
"""
import os
import sys

DAY = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(DAY, "..", "..", "hardware", "bo-mang"))
from bo_tri import BO  # noqa: E402

MAU = '''"""Vỏ bo mang {ma}: {ten}. Tệp sinh tự động bởi tao_tep_vo.py; thông số ở hardware/bo-mang/bo_tri.py."""
from cadgen import step, stl

from lib.vo import {ham}


@step(out="../../STEP/vo/vo_{ma}_{loai}.step")
@stl(out="../../STL/vo/vo_{ma}_{loai}.stl")
def vo_{mal}_{loai}():
    return {goi}


if __name__ == "__main__":
    vo_{mal}_{loai}()
'''

os.makedirs(os.path.join(DAY, "vo"), exist_ok=True)
n = 0
for ma, d in BO.items():
    ds = [("de", "đế", "de", f'de("{ma}")')]
    if d["vo"].get("nap", True):
        ds.append(("nap", "nắp (đã lật úp để in)", "nap", f'nap("{ma}", in3d=True)'))
    for loai, ten, ham, goi in ds:
        open(os.path.join(DAY, "vo", f"vo_{ma}_{loai}.py"), "w", encoding="utf-8", newline="\n").write(
            MAU.format(ma=ma, mal=ma.lower(), loai=loai, ten=ten, ham=ham, goi=goi))
        n += 1
print(n, "tệp")
