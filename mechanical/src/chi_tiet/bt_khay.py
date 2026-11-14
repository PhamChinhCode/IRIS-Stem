"""Khay hứng vật 48 x 48 x 24, thành 2 mm."""
from cadgen import step, stl

from lib.chuan import hop, to


@step(out="../../STEP/chi_tiet/bt_khay.step")
@stl(out="../../STL/bt_khay.stl")
def bt_khay():
    return to(hop(48.0, 48.0, 24.0) - hop(44.0, 44.0, 24.0, z=2.0), "bt_khay", "in3d")


if __name__ == "__main__":
    bt_khay()
