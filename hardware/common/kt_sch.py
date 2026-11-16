"""Sinh lại sơ đồ một bo rồi kiểm: ERC, liệt kê lưới, xuất PDF và SVG.

Chạy từ thư mục hardware:  PYTHONUTF8=1 python common/kt_sch.py S1-driver-dong-co S1 [thư mục xuất]
"""
import os
import re
import subprocess
import sys

KICAD_CLI = "C:/Program Files/KiCad/10.0/bin/kicad-cli.exe"
GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def luoi(tep):
    s = open(tep, encoding="utf-8").read()
    kq = {}
    for p in re.split(r"\(net\s+\(code", s[s.find("(nets"):])[1:]:
        ten = re.search(r'\(name "([^"]*)"', p).group(1)
        kq[ten] = re.findall(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)(?:\s+\(pinfunction "([^"]*)"\))?', p)
    return kq


def main():
    thu_muc, ten = sys.argv[1], sys.argv[2]
    xuat = sys.argv[3] if len(sys.argv) > 3 else os.path.join(GOC, "..", "docs", "hinh-mach")
    d = os.path.join(GOC, thu_muc)
    sch = ten + ".kicad_sch"
    if os.path.exists(os.path.join(d, "ve_so_do.py")):     # bo mang dùng chung một kịch bản ở thư mục cha
        subprocess.run([sys.executable, "ve_so_do.py"], cwd=d, check=True)
    tam = os.environ.get("TEMP", d)
    rpt, net = os.path.join(tam, ten + ".rpt"), os.path.join(tam, ten + ".net")
    subprocess.run([KICAD_CLI, "sch", "erc", "--severity-all", "-o", rpt, sch], cwd=d, capture_output=True)
    r = open(rpt, encoding="utf-8").read()
    for m in re.finditer(r"^\[.*\n.*\n.*", r, re.M):
        print(m.group(0))
    print(re.search(r"ERC messages.*", r).group(0))
    subprocess.run([KICAD_CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", net, sch], cwd=d, capture_output=True)
    for t, nut in luoi(net).items():
        if t.startswith("unconnected"):
            continue
        print(t, ":", " ".join(f"{a}.{b}" + (f"({f.rsplit('_', 1)[0]})" if f and a[0] in "UJQO" else "") for a, b, f in nut))
    os.makedirs(xuat, exist_ok=True)
    subprocess.run([KICAD_CLI, "sch", "export", "pdf", "-o", os.path.join(xuat, ten + ".pdf"), sch], cwd=d, capture_output=True)
    subprocess.run([KICAD_CLI, "sch", "export", "svg", "-o", xuat, sch], cwd=d, capture_output=True)


if __name__ == "__main__":
    main()
