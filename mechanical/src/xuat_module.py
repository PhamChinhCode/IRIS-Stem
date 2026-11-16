"""Xuất mô hình 3D của từng module (bo mạch, kèm đế và nắp nếu có vỏ) ra STEP/module/<mã>.step.

Chạy từ mechanical/src:  PYTHONUTF8=1 python xuat_module.py [mã ...]
Các tệp này là nguồn cho tab Module của trang stem-kit-map (xem stem-kit-map/HUONG-DAN.md).
"""
import os
import sys

from cadgen import build123d as bd

from lib.chuan import cum
from lib.mach import KT, cum_gan

RA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "STEP", "module")

if __name__ == "__main__":
    os.makedirs(RA, exist_ok=True)
    for ma in (sys.argv[1:] or list(KT)):
        bd.export_step(cum(ma, cum_gan(ma)[0]), os.path.join(RA, ma + ".step"))
        print(ma, flush=True)
