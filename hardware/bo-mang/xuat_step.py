"""Xuất mô hình 3D (STEP) của 19 PCB bo mang sang mechanical/STEP/pcb/, gốc toạ độ ở tâm bo.

Chạy: PYTHONUTF8=1 python xuat_step.py     (sau đó kiểm vỏ bằng mechanical/src/kiem_vo.py)
"""
import os
import subprocess

from bo_tri import BO

CLI = "C:/Program Files/KiCad/10.0/bin/kicad-cli.exe"
DAY = os.path.dirname(os.path.abspath(__file__))
RA = os.path.join(DAY, "..", "..", "mechanical", "STEP", "pcb")
os.makedirs(RA, exist_ok=True)
for ma, d in BO.items():
    w, h = d["kt"]
    r = subprocess.run([CLI, "pcb", "export", "step", "--force", "--subst-models", "--no-dnp",
                        "--user-origin", f"{100 + w / 2}x{100 + h / 2}mm",
                        "-o", os.path.join(RA, ma + ".step"), os.path.join(DAY, ma, ma + ".kicad_pcb")],
                       capture_output=True, text=True)
    print(ma, "xong" if r.returncode == 0 else r.stderr[-200:])
