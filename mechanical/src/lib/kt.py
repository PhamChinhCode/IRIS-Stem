"""Kích thước và toạ độ lỗ gá của các chi tiết in 3D, dùng chung giữa chi tiết và cụm lắp."""
XE_L, XE_W = 160.0, 96.0        # tấm khung xe
BG_L, BG_W = 160.0, 128.0       # bảng gá thực hành
GS_L, GS_W = 34.0, 32.0         # đế gá servo
GS_LO = [(-12.0, -12.0), (-12.0, 12.0), (12.0, -12.0), (12.0, 12.0)]
KE_LO = [(-12.0, 6.0), (12.0, 6.0), (-12.0, 30.0), (12.0, 30.0)]
N20_TAM = 7.0                   # cao độ tâm trục N20 so với mặt gá
JGA_TAM = 16.0                  # cao độ tâm trục JGA25 so với mặt gá
N20_LO = [(-12.0, 0.0), (12.0, 0.0)]
JGA_LO = [(-16.0, -11.0), (16.0, -11.0), (-16.0, -19.0), (16.0, -19.0)]
MT_LO = [(-12.0, -4.0), (-12.0, 4.0), (12.0, -4.0), (12.0, 4.0)]
MT_H = 9.5                      # đệm mắt trâu: 21,5 (gầm xe) - 12 (mắt trâu)

# Nhà K3 (tấm cắt laser 3 mm). Sàn 240 x 160, mặt trên sàn ở z = 3.
NHA_L, NHA_W = 240.0, 160.0
NHA_H_TRUOC, NHA_H_SAU = 96.0, 136.0     # cao tường bên ở mép trước / mép sau
SAU_L, SAU_H = 234.0, 135.0              # tường sau
TRUOC_L, TRUOC_H = 128.0, 96.0           # vách trước (bên trái), có ô cửa 40 x 72
TRUOC_X = -53.0                          # tâm vách trước theo X
CUA = (-24.0, -12.0, 40.0, 72.0)         # ô cửa trong toạ độ vách trước
MAI_L, MAI_W = 256.0, 176.0
MONG = 16.0                              # dài mộng
MONG_SAU = [-72.0, 0.0, 72.0]            # vị trí mộng tường sau (theo X)
MONG_BEN = [-40.0, 40.0]                 # mộng tường bên (theo Y)
MONG_TRUOC = [-56.0, 32.0]               # mộng vách trước (toạ độ vách)

# Cánh tay robot (servo MG90S, số đo ở lib/mua_san.py)
TAY_VAI_Z = 25.0        # cao độ trục vai so với đáy mâm xoay
TAY_VAI_Y = 8.0         # mặt cần servo vai
TAY_L1, TAY_L2 = 80.0, 64.0
MG_O = (-16.85, 6.25, 6.2)   # ô lắp thân MG90S: x min, x max, nửa cao (so với trục), hở 0,2–0,25 mỗi phía
MG_KHE = 3.0            # khe vít tai dài 3 mm: nhận khoảng cách lỗ từ 27,2 đến 29,6 mm
TD_L, TD_W = 38.0, 32.0 # đế cánh tay

# Băng tải
BT_TRUC_Z = 22.0        # cao độ trục con lăn so với mặt bảng gá
BT_X = 64.0             # con lăn ở x = ±64
BT_L = 160.0
