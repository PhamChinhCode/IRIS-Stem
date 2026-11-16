"""Sinh lại và kiểm cả 19 bo mang: ERC, lưới, PDF/SVG vào docs/hinh-mach/bo-mang/.

Chạy từ thư mục hardware:  PYTHONUTF8=1 python bo-mang/kt_tat_ca.py [mã bo ...]
"""
import os
import subprocess
import sys

DAY = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(DAY)
sys.path.insert(0, DAY)
import ve_so_do  # noqa: E402

chon = sys.argv[1:] or [f.__name__ for f in ve_so_do.TAT_CA]
xuat = os.path.join(GOC, "..", "docs", "hinh-mach", "bo-mang")
for ma in chon:
    getattr(ve_so_do, ma)()
    sys.stdout.flush()
    subprocess.run([sys.executable, os.path.join(GOC, "common", "kt_sch.py"), "bo-mang/" + ma, ma, xuat], cwd=GOC)
    print("-" * 60)
    sys.stdout.flush()
