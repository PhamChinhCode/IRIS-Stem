# Bộ kit giảng dạy STEM – ESP32-S3 + MicroBlocks

Hệ thống module tái sử dụng để dạy nhà thông minh, robot và IoT cho học sinh 12–18 tuổi, lập trình kéo thả trên MicroBlocks.

## Đọc từ đâu

| Muốn biết | Mở |
|---|---|
| Kit gồm những gì, 25 dự án dùng module nào | [docs/THIET-KE-HE-THONG.md](docs/THIET-KE-HE-THONG.md) |
| Xem trực quan: dự án, sơ đồ nối dây, mô hình 3D, sơ đồ mạch | [stem-kit-map/index.html](stem-kit-map/index.html) |
| Sơ đồ nguyên lý, linh kiện, mạch in của từng bo | [hardware/THIET-KE-MACH.md](hardware/THIET-KE-MACH.md) |
| Kích thước bo, chi tiết in 3D, vỏ hộp, mô hình lắp ráp | [docs/THIET-KE-CO-KHI.md](docs/THIET-KE-CO-KHI.md) |
| Cách đưa tệp 3D, hình mạch, PDF lên trang web | [stem-kit-map/HUONG-DAN.md](stem-kit-map/HUONG-DAN.md) |

## Cấu trúc thư mục

```
docs/           Tài liệu thiết kế, hình minh hoạ
stem-kit-map/   Trang bản đồ kit (web) và lệnh cập nhật update_3d.py
hardware/       Mạch KiCad; THIET-KE-MACH.md là tài liệu thiết kế mạch
  common/         Thư viện ký hiệu, chân linh kiện, mã dựng sơ đồ và mạch in dùng chung
  C1-bo-chu/      Bo chủ ESP32-S3 (64 × 48 mm)
  C2-nguon-pin/   Nguồn pin 2S
  S1-driver-dong-co/
  S2-do-line/
  S3-imu/
  O7-servo-16-kenh/
  bo-mang/        19 bo mang cho module đơn giản (I1–I14, O1–O5), mỗi bo một thư mục
firmware/       Firmware STM32G030 của module thông minh
  common/         Khung I2C và bootloader dùng chung
  S1-driver-dong-co/
  S2-do-line/
  S3-imu/
libraries/      Thư viện khối MicroBlocks tự viết
mechanical/     Cơ khí: mã CAD tham số (src/), tệp in 3D (STL/)
projects/       Chương trình mẫu và mô hình lắp ráp của 25 dự án, theo 5 cấp độ
curriculum/     Giáo án, phiếu bài học
```

`Iris blocks/` là bản fork MicroBlocks (phần mềm lập trình và firmware máy ảo, giấy phép MPL 2.0). Các thay đổi so với bản gốc ghi trong [Iris blocks/DOC-STNAPP.md](Iris%20blocks/DOC-STNAPP.md); bối cảnh ở mục 12 của tài liệu thiết kế.

## Tình trạng

| Phần | Đã có | Còn thiếu |
|---|---|---|
| Sơ đồ nguyên lý | Đủ 25 bo, ERC không lỗi | Mã LCSC cho phần lớn linh kiện; đối chiếu datasheet HY2120-CB và 8205A trên C2 |
| Mạch in | 19 bo mang đã đi dây | C1, C2, S1, S2, S3, O7; soát tay và xuất Gerber cho 19 bo mang |
| Vỏ in 3D | Đế và nắp cho 19 bo mang (I3, I13 chỉ có đế) | Vỏ cho 6 bo còn lại |
| Mô hình lắp ráp | 7 cụm dự án, không va chạm; cánh tay robot dùng servo MG90S | Mô hình riêng cho từng dự án |
| Trang bản đồ kit | 25 dự án, 25 module, mô hình 3D, hình mạch, tài liệu PDF | |

## Trang bản đồ kit

Trang lấy dữ liệu thẳng từ các thư mục thiết kế. Sau khi sửa mạch hoặc mô hình, chạy một lệnh trong `stem-kit-map/`:

```bash
python update_3d.py
```

Lệnh tìm tệp theo **tên**, nên chỉ cần lưu đúng chỗ và đúng tên:

| Nội dung trên trang | Tệp nguồn | Ví dụ |
|---|---|---|
| Mô hình 3D của module | `hardware/**/<mã>.step` | `hardware/C1-bo-chu/C1.step` |
| Mô hình 3D của dự án | `projects/**/Project<số>.step` | `projects/Project11.step` |
| Sơ đồ nguyên lý | `hardware/**/<mã>.kicad_sch` | `hardware/bo-mang/I1/I1.kicad_sch` |
| Hình mạch in | `hardware/**/<mã>.kicad_pcb` | `hardware/bo-mang/I1/I1.kicad_pcb` |
| Tài liệu PDF | `hardware/**/<mã>.pdf` | `hardware/bo-mang/I1/I1.pdf` |

Module và dự án chưa có tệp riêng thì dùng mô hình dựng từ mã trong `mechanical/src`. Xuất hình mạch cần KiCad 10; đọc tệp STEP cần `cadgen` (xem hướng dẫn).

## Quy ước

- Mã module (C1, S1, I6, O3...) theo mục 4 của tài liệu thiết kế, dùng làm tiền tố tên thư mục và tên tệp.
- Mỗi module tự thiết kế có thư mục cùng tên ở `hardware/` và `firmware/`.
- Tệp trong `mechanical/STEP/` dựng lại được từ mã nên không đưa vào git. Riêng mô hình servo MG90S tải từ step.parts nằm ở `mechanical/STEP/mua_san/`, phải tải lại trên máy mới (tìm «Adafruit 1143» trên step.parts, lưu thành `adafruit_1143_micro_servo_high_torque_metal_gear.step`).
- Các lệnh sinh sơ đồ và mạch in (`ve_so_do.py`, `ve_pcb.py`) **ghi đè** tệp KiCad. Không chạy lại cho bo đã sửa tay.
