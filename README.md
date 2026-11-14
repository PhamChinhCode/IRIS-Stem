# Bộ kit giảng dạy STEM – ESP32-S3 + MicroBlocks

Hệ thống module tái sử dụng để dạy nhà thông minh, robot và IoT cho học sinh 12–18 tuổi, lập trình kéo thả trên MicroBlocks.

Bắt đầu đọc từ [docs/THIET-KE-HE-THONG.md](docs/THIET-KE-HE-THONG.md). Mô hình trực quan: [docs/ban-do-kit-stem.html](docs/ban-do-kit-stem.html).

## Cấu trúc thư mục

```
docs/           Tài liệu thiết kế, bản đồ kit
hardware/       Mạch KiCad
  common/         Thư viện ký hiệu, chân linh kiện, đầu cắm dùng chung
  C1-bo-chu/      Bo chủ ESP32-S3
  C2-nguon-pin/   Nguồn pin 2S
  S1-driver-dong-co/
  S2-do-line/
  S3-imu/
  bo-mang/        Bo mang cho module đơn giản (I1–I14, O1–O7)
firmware/       Firmware STM32G030 của module thông minh
  common/         Khung I2C và bootloader dùng chung
  S1-driver-dong-co/
  S2-do-line/
  S3-imu/
libraries/      Thư viện khối MicroBlocks tự viết
mechanical/     Cơ khí K1–K4
projects/       Chương trình mẫu 25 dự án, theo 5 cấp độ
curriculum/     Giáo án, phiếu bài học
```

`microblocks/` (kho fork MicroBlocks) chưa có; kế hoạch nằm ở mục 12 của tài liệu thiết kế.

## Quy ước

- Mã module (C1, S1, I6, O3...) theo mục 4 của tài liệu thiết kế, dùng làm tiền tố tên thư mục và tên tệp.
- Mỗi module tự thiết kế có thư mục cùng tên ở `hardware/` và `firmware/`.
