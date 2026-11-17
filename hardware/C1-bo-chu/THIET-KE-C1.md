# C1 – Bo chủ ESP32-S3: tài liệu thiết kế chi tiết

Phiên bản 0.2 – 16/11/2026 (bớt còn 2 cổng servo, thêm bus I2C thứ hai, D2 kiêm UART 2). Viết theo sơ đồ [C1.kicad_sch](C1.kicad_sch) (87 linh kiện, ERC 0 lỗi). **Chưa có mạch in, chưa có bản mẫu**: mọi con số dưới đây là tính toán, chưa đo.

Tài liệu liên quan: kiến trúc chung và lý do chọn linh kiện ở [THIET-KE-MACH.md](../THIET-KE-MACH.md) mục 0, 1, 6; chuẩn cổng ở [THIET-KE-HE-THONG.md](../../docs/THIET-KE-HE-THONG.md) mục 3; kích thước và vị trí lắp ở [THIET-KE-CO-KHI.md](../../docs/THIET-KE-CO-KHI.md) mục 3.2.

![Sơ đồ nguyên lý C1](../../stem-kit-map/hinh/C1-so-do.svg)

## 1. Vai trò và thông số chính

C1 là bộ não của kit: chạy máy ảo MicroBlocks, nối máy tính qua USB, cấp nguồn 5 V và tín hiệu 3,3 V cho mọi module.

| Hạng mục | Giá trị |
|---|---|
| Vi điều khiển | ESP32-S3-WROOM-1-N16R8 (16 MB flash, 8 MB PSRAM, anten trên bo) |
| Kích thước | 64 × 48 mm, 4 lỗ gá Ø3,2 tại (4, 4), (60, 4), (4, 44), (60, 44) |
| Nguồn vào | USB-C 5 V, hoặc 5,45 V từ C2 qua cổng XH 2 chân; tự chọn nguồn |
| Nguồn ra cổng | `+5V` (sau cầu chì 1,1 A) cho 11 cổng; `5V_SERVO` (sau cầu chì 1,5 A) cho 2 cổng servo |
| Nguồn logic | 3,3 V, ổn áp 1 A |
| Mức tín hiệu | 3,3 V trên mọi cổng |
| Cổng | 6 D/A (3 analog + 3 số; D3 kiêm UART 1, D2 kiêm UART 2), 2 I2C1 (100 kHz) + 2 I2C2 (400 kHz), 1 SPI, 2 servo |
| Trên bo | nút A, nút B, còi, LED RGB, nút RESET, nút BOOT, LED nguồn |
| Bảo vệ | 2 cầu chì tự phục hồi, 7 IC chống tĩnh điện, điện trở nối tiếp trên 22 đường tín hiệu |

## 2. Sơ đồ khối

```
 J1 USB-C ─┬─ VBUS ─► Q1 AO3401A ──┐
           │                       ├─► 5V_SYS ─┬─► F1 1,5 A ─► 5V_SERVO ─► J14, J15 (servo)
 J2 XH 2 chân (từ C2) ─► D1 SS54 ──┘           ├─► F2 1,1 A ─► +5V ─► J3–J13 (D/A, I2C, SPI)
           │                                   └─► U2 TLV1117LV33 ─► +3V3 ─► U1, kéo lên, còi, LED RGB
           └─ D+/D− ─► U3 (ESD) ─► GPIO20/19 của U1

 U1 ESP32-S3 ─► U4–U9 (ESD) ─► R30–R51 (220 Ω / 100 Ω) ─► đầu cắm
             ─► SW1, SW2 (nút A, B) · Q2 + BZ1 (còi) · LED1 (RGB) · SW3 RESET · SW4 BOOT
```

## 3. Cổng và thứ tự chân

Chân 1 luôn là GND, chân 2 luôn là 5 V. Ký hiệu và chân linh kiện lấy từ thư viện [IRIS](../common/README.md).

| Ký hiệu | Cổng | Đầu cắm | Chân 1 → n |
|---|---|---|---|
| J1 | USB-C | HRO TYPE-C-31-M-12 | USB 2.0, CC1 và CC2 mỗi chân 5k1 xuống GND |
| J2 | 5 V từ C2 | JST XH 2 chân | GND, 5V |
| J3, J4, J5 | A1, A2, A3 | JST PH 4 chân | GND, 5V, S1, S2 |
| J6 | D1 | JST PH 4 chân | GND, 5V, S1, S2 |
| J7 | D2 / UART 2 | JST PH 4 chân | GND, 5V, S1 = TX, S2 = RX |
| J8 | D3 / UART 1 | JST PH 4 chân | GND, 5V, S1 = TX, S2 = RX |
| J9, J10 | I2C1-A, I2C1-B (bus thường, 100 kHz) | JST PH 4 chân | GND, 5V, SDA, SCL |
| J11, J12 | I2C2-A, I2C2-B (bus tốc độ cao, 400 kHz) | JST PH 4 chân | GND, 5V, SDA, SCL |
| J13 | SPI | JST PH 6 chân | GND, 5V, SCK, MOSI, MISO, CS |
| J14, J15 | Servo 1, 2 | hàng rào 3 chân 2,54 mm | GND, 5V, PWM |

Hai bus I2C dùng cùng loại đầu cắm. Cắm nhầm bus không làm hỏng gì, nhưng chương trình sẽ không tìm thấy module. Nhãn in trên bo phải phân biệt rõ hai nhóm cổng.

## 4. Gán chân ESP32-S3

Lấy từ danh sách lưới của sơ đồ. «Chân» là số chân trên module WROOM-1.

| Chức năng | Lưới | GPIO | Chân | Điện trở nối tiếp | IC ESD |
|---|---|---|---|---|---|
| A1 S1 / S2 | `A1_S1`, `A1_S2` | 1, 2 | 39, 38 | R30, R31 (220 Ω) | U4 |
| A2 S1 / S2 | `A2_S1`, `A2_S2` | 4, 5 | 4, 5 | R32, R33 | U4 |
| A3 S1 / S2 | `A3_S1`, `A3_S2` | 6, 7 | 6, 7 | R34, R35 | U5 |
| D1 S1 / S2 | `D1_S1`, `D1_S2` | 14, 21 | 22, 23 | R36, R37 | U5 |
| D2 S1 (TX 2) / S2 (RX 2) | `D2_S1`, `D2_S2` | 38, 39 | 31, 32 | R38, R39 | U6 |
| D3 S1 (TX 1) / S2 (RX 1) | `D3_S1`, `D3_S2` | 43, 44 | 37, 36 | R40, R41 | U6 |
| Servo 1, 2 | `SERVO1`, `SERVO2` | 15, 16 | 8, 9 | R42, R43 (220 Ω) | U7 |
| I2C1 SDA / SCL | `SDA`, `SCL` | 8, 9 | 12, 17 | R44, R45 (100 Ω) | U7 |
| I2C2 SDA / SCL | `SDA2`, `SCL2` | 17, 18 | 10, 11 | R46, R47 (100 Ω) | U8 |
| SPI SCK / MOSI | `SPI_SCK`, `SPI_MOSI` | 12, 11 | 20, 19 | R48, R49 (100 Ω) | U8 |
| SPI MISO / CS | `SPI_MISO`, `SPI_CS` | 13, 10 | 21, 18 | R50, R51 (100 Ω) | U9 |
| USB D− / D+ | `USB_D-`, `USB_D+` | 19, 20 | 13, 14 | không | U3 |
| Nút A / B | `BTN_A`, `BTN_B` | 41, 42 | 34, 35 | – | – |
| Còi | `BUZZER` | 40 | 33 | – | – |
| LED RGB | `RGB` | 48 | 25 | – | – |
| Dự phòng (điểm thử TP1) | `IO47` | 47 | 24 | – | – |
| BOOT | `BOOT` | 0 | 27 | – | – |
| RESET | `EN` | – | 3 | – | – |
| Để hở | – | 3, 45, 46, 35, 36, 37 | 15, 26, 16, 28, 29, 30 | – | – |

Ghi chú về chân:

- A1–A3 (GPIO1–7) thuộc ADC1 nên đọc analog được khi bật WiFi. GPIO14 thuộc ADC2, không dùng làm analog.
- GPIO0, 3, 45, 46 là chân strapping. GPIO0 chỉ nối nút BOOT; ba chân còn lại để hở.
- GPIO35, 36, 37 nối bộ nhớ PSRAM bên trong module N16R8, không dùng được.
- UART trên D2 và D3 là gán bằng phần mềm: ESP32-S3 đưa được UART ra bất kỳ GPIO nào, nên hai cổng này vẫn dùng như cổng D/A thường khi không cần UART.
- GPIO17, 18 (I2C2) trước đây là servo 3 và 4.
- GPIO43 (D3-S1) phát thông báo khởi động của ROM mỗi lần reset: không cắm relay hay còi vào cổng D3.

## 5. Mô tả từng khối

### 5.1. Nguồn vào và chọn nguồn

| Linh kiện | Giá trị | Vai trò |
|---|---|---|
| Q1 | AO3401A (P-MOSFET, SOT-23) | cực D = `VBUS`, cực S = `5V_SYS`, cực G = `5V_EXT` |
| R1 | 100 k | kéo cực G của Q1 xuống GND khi không có C2 |
| D1 | SS54 (Schottky 5 A, SMA) | `5V_EXT` → `5V_SYS`; chặn dòng USB chảy ngược về C2 |
| R2, R3 | 5k1 | CC1, CC2 xuống GND: báo cho nguồn USB-C biết đây là thiết bị nhận |
| C6 | 10 µF 25 V | tụ trên `5V_SYS` |
| U3 | SRV05-4, VP = `VBUS` | chống tĩnh điện cho D+, D− |

Cách chạy:

| Nguồn cắm | Q1 | `5V_SYS` |
|---|---|---|
| Chỉ USB | dẫn (cực G bị R1 kéo xuống) | VBUS − 2 A × 60 mΩ ≈ VBUS − 0,12 V |
| Chỉ C2 | khoá (V_GS ≈ +0,4 V) | 5,45 − 0,4 (D1) ≈ 5,05 V; không có điện áp ngược ra USB |
| Cả hai | khoá | lấy từ C2; diode thân của Q1 không dẫn vì VBUS không cao hơn `5V_SYS` 0,5 V |

Tổn hao: Q1 khoảng 0,24 W ở 2 A. D1 0,6 W ở 1,5 A và 1,35 W ở 3 A, cần vùng đồng tản nhiệt ở hai chân.

### 5.2. Cầu chì và ổn áp 3,3 V

| Linh kiện | Giá trị | Vai trò |
|---|---|---|
| F1 + C1 | PTC 1,5 A giữ (1812) + 220 µF 16 V | `5V_SERVO` cho 2 cổng servo; tụ hoá đỡ dòng khởi động servo |
| F2 + C2 | PTC 1,1 A giữ (1812) + 10 µF | `+5V` cho 6 cổng D/A, 4 cổng I2C, cổng SPI |
| U2 | TLV1117LV33 (SOT-223, 1 A) | `5V_SYS` → `+3V3` |
| C3; C4, C5 | 10 µF 25 V | tụ vào; hai tụ ra của U2 |
| R9 + LED2 | 1 k + LED 0603 | báo có `+3V3` (khoảng 1,3 mA) |

Tính toán:

- F1 giữ 1,5 A: đủ cho 2 servo nhỏ kẹt cùng lúc (2 × 0,65 A). F2 giữ 1,1 A: tải cổng nặng nhất khoảng 0,6 A. PTC sụt 0,1–0,15 V ở 1 A.
- U2 toả (5,0 − 3,3) × 0,12 A = 0,2 W trung bình và 0,6 W khi ESP32 phát WiFi liên tục 350 mA. Với vùng đồng 2 cm² (khoảng 60 °C/W), nhiệt độ tăng 36 °C ở mức xấu nhất.
- Điện áp vào của TLV1117LV33 tối đa 5,5 V. Khi dùng C2, `5V_SYS` khoảng 5,05–5,2 V tuỳ tải; nếu buck của C2 lệch lên 5,6 V (sai số linh kiện) và tải nhẹ thì `5V_SYS` khoảng 5,35 V, còn cách giới hạn 0,15 V. Phải đo điện áp này trên bản mẫu.

### 5.3. Module ESP32-S3 và mạch khởi động

| Linh kiện | Giá trị | Vai trò |
|---|---|---|
| U1 | ESP32-S3-WROOM-1-N16R8 (LCSC C2913202) | chân 2 = `+3V3`; chân 1, 40, 41 = GND |
| C7, C8, C9 | 10 µF, 10 µF, 100 nF | tụ tách, đặt sát chân 2 |
| R4 + C10 | 10 k kéo lên + 1 µF xuống GND | mạch trễ chân EN: chip khởi động đúng khi nguồn lên chậm |
| SW3 | TS-1088 | RESET: kéo EN xuống GND |
| SW4 | TS-1088 | BOOT: kéo GPIO0 xuống GND (chân này có sẵn kéo lên nội) |
| TP1 | điểm thử | GPIO47 dự phòng |

MicroBlocks dùng USB gốc của chip (`ARDUINO_USB_CDC_ON_BOOT`), nên bo không có IC chuyển USB–UART và không có mạch tự nạp. Để vào chế độ nạp bằng tay: giữ BOOT, nhấn rồi nhả RESET, nhả BOOT.

### 5.4. Nút, còi, LED RGB

| Linh kiện | Giá trị | Vai trò |
|---|---|---|
| SW1, SW2 | nút 6 × 6 | nút A (GPIO41), nút B (GPIO42): nhấn = mức thấp |
| R5, R6 + C11, C12 | 10 k kéo lên `+3V3` + 100 nF | mức nghỉ và chống dội (hằng số thời gian 1 ms) |
| BZ1 | còi thụ động SMD | cực + nối `+3V3`, cực − về cực D của Q2 |
| Q2, R7, R8 | AO3400A, 100 Ω cực G, 10 k kéo xuống | đóng cắt còi từ GPIO40; còi im khi chip đang reset |
| D2 | 1N4148W | dập xung ngược của cuộn dây còi |
| LED1 + C13 | WS2812B-2020 + 100 nF | LED RGB trên GPIO48, cấp `+3V3`; chân DOUT để hở |

Còi cấp từ `+3V3` nên dòng của nó đi qua U2. Còi điện từ cỡ 16 Ω kéo đỉnh khoảng 200 mA ở 3,3 V; phải tính lại khi chốt mã còi.

### 5.5. Điện trở nối tiếp, kéo lên I2C và chống tĩnh điện

- Mỗi đường tín hiệu đi theo thứ tự: đầu cắm → điện trở nối tiếp → (SRV05-4 và chân ESP32). Điện trở phải đứng **giữa** đầu cắm và IC chống tĩnh điện.
- 220 Ω cho D/A và servo (R30–R43), 100 Ω cho hai bus I2C và SPI (R44–R51).
- Nếu một module lỗi đưa 5 V lên chân tín hiệu, dòng qua diode kẹp là (5 − 3,3 − 0,7) / 220 = 4,5 mA, chảy vào lưới `+3V3` và được ESP32 tiêu thụ.
- R20, R21 (2k2) kéo `SDA_J`, `SCL_J` của I2C1 lên `+3V3`; R22, R23 (2k2) kéo `SDA2_J`, `SCL2_J` của I2C2. Cả bốn đặt ở **phía đầu cắm**. Module không được có điện trở kéo lên.
- **I2C1, 100 kHz**: bus 300 pF (4–5 module và dây) có thời gian lên 0,85 × 2k2 × 300 pF = 560 ns, đạt chuẩn 100 kHz (1000 ns).
- **I2C2, 400 kHz**: chuẩn cho phép 300 ns, tức bus tối đa khoảng 150 pF với 2k2 (280 ns). Chuỗi S1 → S3 của xe cân bằng khoảng 100 pF (190 ns). Chỉ cắm vào bus này module cần tốc độ và giữ dây ngắn; nếu cần bus dài hơn thì hạ R22, R23 xuống 1k5.
- Hai bus tách rời hẳn: module chậm hay dây dài trên I2C1 không làm chậm vòng điều khiển trên I2C2.
- U4–U9 (6 × SRV05-4, VP = `+3V3`) bảo vệ 22 đường (12 D/A, 2 servo, 4 I2C, 4 SPI); U9 còn 2 kênh trống.
- Không đặt tụ lọc trên A1–A3: các cổng này còn dùng làm cổng số tốc độ cao (NeoPixel).

## 6. Danh sách linh kiện

| Ký hiệu | Số lượng | Giá trị | Vỏ | Mã LCSC |
|---|---|---|---|---|
| U1 | 1 | ESP32-S3-WROOM-1-N16R8 | module | C2913202 |
| U2 | 1 | TLV1117LV33DCYR | SOT-223 | – |
| U3–U9 | 7 | SRV05-4 | SOT-23-6 | – |
| Q1 | 1 | AO3401A | SOT-23 | – |
| Q2 | 1 | AO3400A | SOT-23 | – |
| D1 | 1 | SS54 | SMA | – |
| D2 | 1 | 1N4148W | SOD-123 | – |
| F1, F2 | 2 | PTC 1,5 A; 1,1 A | 1812 | – |
| LED1 | 1 | WS2812B-2020 | 2 × 2 mm | – |
| LED2 | 1 | LED xanh | 0603 | – |
| BZ1 | 1 | còi thụ động | chân linh kiện tạm (Mallory AST1109) | – |
| C1 | 1 | 220 µF 16 V | tụ hoá Ø6,3, bước 2,5 | – |
| C2–C8 | 7 | 10 µF 25 V | 0805 | – |
| C9, C11–C13 | 4 | 100 nF | 0603 | – |
| C10 | 1 | 1 µF | 0603 | – |
| R1 | 1 | 100 k | 0603 | – |
| R2, R3 | 2 | 5k1 | 0603 | – |
| R4, R5, R6, R8 | 4 | 10 k | 0603 | – |
| R9 | 1 | 1 k | 0603 | – |
| R20–R23 | 4 | 2k2 | 0603 | – |
| R30–R43 | 14 | 220 Ω | 0603 | – |
| R7, R44–R51 | 9 | 100 Ω | 0603 | – |
| SW1, SW2 | 2 | nút 6 × 6 × 5 | SMD | – |
| SW3, SW4 | 2 | TS-1088 | SMD 3 × 4 | – |
| J1 | 1 | TYPE-C-31-M-12 | USB-C 16 chân | – |
| J2 | 1 | JST XH 2 chân | xem mục 9 | – |
| J3–J12 | 10 | JST PH 4 chân nằm ngang (S4B-PH-K-S) | xuyên lỗ | – |
| J13 | 1 | JST PH 6 chân nằm ngang | xuyên lỗ | – |
| J14, J15 | 2 | hàng rào 1 × 3, 2,54 mm | xuyên lỗ | – |
| TP1 | 1 | điểm thử Ø1,5 | – | – |

Dấu «–» ở cột LCSC: chưa tra mã. `KH1` (khung bo) không vào BOM.

## 7. Ngân sách dòng

| Đường | Tải | Điển hình | Đỉnh |
|---|---|---|---|
| `+3V3` | ESP32-S3 khi dùng WiFi, cộng còi, LED RGB, kéo lên | 130 mA | 350 mA (chưa tính còi) |
| `+5V` (qua F2) | module trên cổng; dự án 10 không tính servo | 0,6 A | 1,1 A (giới hạn của F2) |
| `5V_SERVO` (qua F1) | 2 servo nhỏ đang chạy | 0,5 A | 1,3 A (2 servo kẹt) |
| `5V_SYS` tổng, dự án 10 | ESP32 + MQ-2 + relay + quạt + OLED + 2 servo | 1,1 A | 1,9 A |

Cổng USB máy tính (0,5 A) không nuôi được dự án 10; dùng adapter 5 V/2 A. C1 có 2 cổng servo, đủ cho mọi dự án không dùng O7 (nhiều nhất là dự án 10: cửa và giàn phơi); cần nhiều servo hơn thì dùng O7.

## 8. Cơ khí và bố trí linh kiện

Gốc toạ độ ở góc dưới trái của bo, X sang phải, Y lên trên (mm). Vị trí lỗ gá và đầu cắm là ràng buộc; linh kiện trong lòng bo được dịch khi đi dây.

| Thành phần | Vị trí |
|---|---|
| A1, A2, A3, D1, D2 (J3–J7) | cạnh dưới, tâm x = 12 / 22 / 32 / 42 / 52 |
| I2C1-A, I2C1-B, I2C2-A, I2C2-B (J9–J12) | cạnh trên, tâm x = 12 / 22 / 32 / 42 |
| D3 (J8) | cạnh trên, tâm x = 52 |
| SPI (J13) | cạnh trái, tâm y = 14,75 |
| USB-C (J1) | cạnh trái, tâm y = 32 |
| Cổng 5 V từ C2 (J2) | trong lòng bo, tâm (12,5; 35,5), cắm từ trên xuống |
| ESP32-S3 (U1) | x từ 38,25 đến 63,75, y từ 15 đến 33; anten sát mép phải |
| Nút RESET | (34, 27) |
| Nút A, nút B | (14, 15), (24, 15) |
| Còi | (32,5; 13,5) |
| LED RGB | (19, 25) |
| Hàng rào servo 2 × 3 chân | tâm (26; 35,5), chiếm 5,1 × 7,6 |

Lòng bo còn trống khoảng 30 × 32 mm cho toàn bộ linh kiện nguồn, 7 IC chống tĩnh điện và 30 điện trở. Nhiều khả năng phải đặt linh kiện cả hai mặt.

## 9. Hướng dẫn đi mạch in

- **Anten**: không đổ đồng, không đi dây ở mọi lớp trong vùng anten và 15 mm hai bên. Module sát mép phải, anten nhô ra ngoài mép bo nếu được.
- **Đường nguồn**: `VBUS`, `5V_EXT`, `5V_SYS`, `5V_SERVO` rộng tối thiểu 1,0 mm (đến 3 A); `+5V` tới các cổng 0,6 mm. Đổ đồng quanh D1 và chân giữa của U2 để tản nhiệt.
- **USB**: D+ và D− đi thành cặp, ngắn, cùng chiều dài; U3 sát đầu USB. Vỏ USB-C nối GND.
- **Tụ tách** C7–C9 sát chân 2 của U1; C10 và R4 sát chân EN.
- **Thứ tự linh kiện trên mỗi đường tín hiệu**: đầu cắm → điện trở → IC chống tĩnh điện → ESP32. Điện trở đặt gần đầu cắm.
- **Lắp ráp**: linh kiện dán ở một mặt nếu xếp vừa; nếu phải dùng hai mặt thì để điện trở và IC chống tĩnh điện ở mặt dưới, giữ nút, LED, còi ở mặt trên.
- Hai lớp, mặt dưới đổ đồng GND. Nếu hai lớp không đi hết thì chuyển sang 4 lớp.

## 10. Phần mềm

- Firmware: bản fork MicroBlocks trong `Iris blocks/`, cấu hình cho ESP32-S3 với USB CDC gốc.
- Việc phải làm trong firmware: khai báo chân mặc định của C1 (I2C1 8/9, UART 1 43/44, nút 41/42, còi 40, LED RGB 48) và tên cổng A1–A3, D1–D3.
- **Bus I2C thứ hai chưa có trong MicroBlocks**: máy ảo hiện chỉ dùng một bus (`Wire` trong `Iris blocks/vm/sensorPrims.cpp`). Phải thêm bus thứ hai trên GPIO17/18 ở 400 kHz, và để thư viện khối của S1, S3 gọi bus này. Chưa làm.
- UART 2 trên D2 (GPIO38/39): cần kiểm MicroBlocks có mở được cổng serial thứ hai không.
- I2C1 để 100 kHz.

## 11. Kiểm thử bản mẫu

Làm theo thứ tự, chưa gắn module nào:

1. Đo trở kháng `5V_SYS`–GND và `+3V3`–GND trước khi cấp điện: không chập.
2. Cấp USB: `5V_SYS` ≈ VBUS − 0,1 V; `+3V3` = 3,3 V ± 3 %; LED2 sáng.
3. Máy tính nhận cổng USB CDC; nạp firmware MicroBlocks; thử lại cách vào chế độ nạp bằng BOOT + RESET.
4. Thử nút A, B, còi, LED RGB bằng khối lệnh.
5. Cấp 5,45 V vào J2 (chưa cắm USB): `5V_SYS` ≈ 5,05 V; đo chân VBUS của J1 phải gần 0 V.
6. Cắm cả hai nguồn: dòng từ USB phải gần 0; rút từng nguồn, bo không reset.
7. Thử từng cổng: D/A (đọc, ghi, analog trên A1–A3), I2C1 và I2C2 (quét địa chỉ với một module trên từng bus), UART trên D3 và D2, SPI (RC522), servo.
8. Thử cầu chì: tải 2 A vào một cổng servo, F1 phải ngắt và tự phục hồi.
9. Đo nhiệt U2 và D1 khi WiFi phát liên tục và tải 2 A.
10. Đo dạng sóng I2C1 với 5 module: thời gian lên dưới 1000 ns. Đo I2C2 ở 400 kHz với S1 + S3: thời gian lên dưới 300 ns.

## 12. Vấn đề mở

| Việc | Ghi chú |
|---|---|
| Cổng J2 | Sơ đồ đang gán chân linh kiện nằm ngang (`Cong_XH_2P_Ngang`); bố trí cơ khí 64 × 48 cần loại cắm đứng (B2B-XH-A). Phải đổi chân linh kiện trước khi đi mạch in |
| Nguồn LED RGB | WS2812B-2020 cấp 3,3 V để nhận được tín hiệu 3,3 V; cần đối chiếu điện áp nguồn tối thiểu trong datasheet và thử trên bản mẫu |
| Còi | Chưa chốt mã; chân linh kiện là tạm. Tính lại dòng trên `+3V3` sau khi chọn |
| GPIO còn trống | 47 (điểm thử TP1) và ba chân strapping 3, 45, 46 |
| Xếp linh kiện | Chưa kiểm 87 linh kiện có vừa bo 64 × 48 hay không |
| Mã LCSC | Mới có mã của U1 |
| Bus I2C thứ hai trong MicroBlocks | Chưa hỗ trợ; phải thêm vào bản fork (mục 10). Trước khi có, các cổng I2C2 không dùng được từ khối lệnh |
| Phân biệt cổng I2C1 và I2C2 | Cùng loại đầu cắm; cần nhãn in rõ, và cân nhắc dùng vỏ đầu cắm khác màu cho I2C2 |
| Chân UART của MicroBlocks | Cặp 43/44 (D3) và 38/39 (D2) là tạm, chốt sau khi thử thư viện Serial |
| PSRAM | Nếu MicroBlocks không cần PSRAM, đổi sang module N16 sẽ giải phóng GPIO35–37 cho một cổng D4 |