# Bản thiết kế hệ thống giảng dạy STEM – ESP32-S3 + MicroBlocks

Phiên bản 0.2 – 14/11/2026 (bản thiết kế mức hệ thống, chưa có sơ đồ mạch)

Mô hình trực quan (dự án, sơ đồ nối, mô hình 3D):
- Tệp trong thư mục này: [ban-do-kit-stem.html](ban-do-kit-stem.html), mở bằng trình duyệt.
- Bản trực tuyến: https://claude.ai/artifact/GxmSu1H3DpPqMNoMUkfT9W

## 1. Phạm vi và các quyết định đã chốt

| Hạng mục | Quyết định |
|---|---|
| Đối tượng | Học sinh 12–18 tuổi, học theo nhóm 2–3 em |
| Mô hình | Bán kit kèm giáo án cho trường và trung tâm; giáo viên khác sẽ dạy |
| Lập trình | Kéo thả trên MicroBlocks, bo trung tâm ESP32-S3 |
| Ngân sách linh kiện | Trên 3 triệu đồng cho bộ đầy đủ |
| Module thông minh | Chỉ phần khó: driver động cơ, dò line, IMU. Cảm biến đơn giản cắm thẳng vào chân ESP32-S3 |
| Động cơ | Hỗ trợ cả N20 và JGA25-370 có encoder, chọn theo kinh phí |

Hệ quả của mô hình bán kit:
- Cắm sai không được làm hỏng thiết bị, và tốt nhất là không cắm sai được.
- Giáo viên không chuyên phải dạy được: mỗi module có khối lệnh riêng bằng tiếng Việt và phiếu bài học riêng.
- Kit chia thành gói để trường mua dần.

## 2. Kiến trúc tổng thể

```
   Máy tính / Chromebook / máy tính bảng (MicroBlocks)
                │ USB-C hoặc Bluetooth
        ┌───────┴────────┐
        │  C1  BO CHỦ    │ ⇠ WiFi ⇢ MQTT / bảng điều khiển trên điện thoại
        │  ESP32-S3      │
        └┬─────┬─────┬──┬┘
         │     │     │  └── Cổng SPI (6 chân, khóa riêng) ── RFID
         │     │     └───── Cổng Servo (3 chân) ×4 ───────── servo
         │     └─────────── Cổng D/A (4 chân) ×6 ─────────── module đơn giản (D3 kiêm UART)
         └───────────────── Bus I2C (4 chân) ×4, nối chuỗi ─ module thông minh,
                                                              OLED, AHT20...
        ┌────────────────┐
        │ C2 NGUỒN PIN 2S│── 5 V ──► bo chủ
        └───────┬────────┘
                └── 7,4 V (cổng nguồn 2 chân) ──► S1 driver động cơ, PCA9685
```

Ba tầng tái sử dụng:
1. **Phần cứng**: module cắm rời theo 4 loại cổng chuẩn.
2. **Phần mềm**: mỗi module một thư viện khối MicroBlocks; các thư viện thuật toán (PID, IoT) dùng chung cho nhiều dự án.
3. **Bài giảng**: mỗi module một phiếu bài học; dự án là tổ hợp các phiếu.

## 3. Chuẩn kết nối

Mọi cổng trên bo chủ chỉ cấp **một nguồn 5 V**, còn **tín hiệu luôn là 3,3 V**. Module nào cần 3,3 V thì tự hạ áp bằng IC ổn áp nhỏ trên chính nó. Chân 1 luôn là GND, chân 2 luôn là 5 V, nên cắm nhầm giữa cổng D/A và cổng I2C chỉ không chạy chứ không hỏng. Các loại cổng phân biệt bằng màu đầu cắm và nhãn in trên bo. Cổng D/A, I2C và SPI dùng đầu JST PH2.0 có khóa chống ngược; cổng servo dùng hàng rào 3 chân chuẩn servo.

| Cổng | Số chân | Thứ tự chân | Màu | Số lượng trên bo chủ |
|---|---|---|---|---|
| D/A | 4 | GND, 5V, S1, S2 | trắng | 6 (3 analog + 3 số; cổng D3 kiêm UART) |
| I2C | 4 | GND, 5V, SDA, SCL | xanh | 4 (chung một bus) |
| Servo | 3 | GND, 5V, PWM | đen (hàng rào chuẩn servo) | 4 |
| SPI | 6 (khóa lệch so với cổng động cơ) | GND, 5V, SCK, MOSI, MISO, CS | vàng | 1 |
| Động cơ (trên S1) | 6 | M+, M-, GND, 3V3, EncA, EncB | đỏ | 2 trên mỗi S1 |
| Nguồn động lực | 2 (XT30) | GND, VBAT | – | C2 → S1 |

Quy tắc điện:
- Không module nào được đưa 5 V lên chân tín hiệu. Nút bấm kéo xuống GND; biến trở, joystick, cảm biến analog lấy điện áp chuẩn từ ổn áp 3,3 V trên module; module chạy 5 V (MQ-2, siêu âm) có phân áp trên đường tín hiệu ra.
- Mỗi module thông minh có 2 cổng I2C (vào/ra) để nối chuỗi. Điện trở kéo lên chỉ đặt trên bo chủ và kéo lên 3,3 V.
- Cổng 4 chân này tương thích với module Grove và M5Stack bán sẵn. Ngoại lệ phải ghi trong tài liệu: module I2C của hãng khác có điện trở kéo lên 5 V không được cắm trực tiếp.
- Mọi IC giao tiếp I2C (INA219, PCA9685, PCF8574, AHT20...) phải cấp nguồn 3,3 V từ ổn áp trên module. Nếu cấp 5 V, ngưỡng mức cao của chúng (khoảng 3,5 V) vượt quá tín hiệu 3,3 V của bus.
- Cổng analog A1–A3 dùng được như cổng số, nên module số cắm được vào cả 6 cổng D/A.
- Ngân sách dòng 5 V: cổng USB máy tính chỉ cấp khoảng 500 mA, không đủ cho MQ-2 + NeoPixel + servo cùng lúc. Dự án nhà thông minh và IoT dùng adapter 5 V/2 A trở lên; thư viện NeoPixel giới hạn sẵn độ sáng; cổng servo trên bo chủ chỉ dùng tối đa 2 servo nhỏ, nhiều hơn thì dùng O7.
- An toàn điện: relay O4 chỉ đóng cắt tải điện áp thấp (đến 24 V). Tài liệu và nhãn trên module cấm nối điện lưới 220 V.
- Cổng D3 kiêm UART (S1 = TX, S2 = RX), dùng chung chuẩn cổng D/A nên không thêm loại đầu cắm mới. Module UART chạy 5 V phải có phân áp trên đường TX của nó về chân RX của bo chủ.
- Chân TX của cổng D3 phát thông báo khởi động của ESP32-S3 mỗi lần reset: không cắm relay hay còi vào cổng này; ưu tiên cho UART và cảm biến đầu vào.
- Cổng SPI và cổng động cơ cùng 6 chân: phải dùng hai họ đầu cắm khác nhau (ví dụ SPI dùng PH2.0, động cơ dùng ZH1.5 hoặc XH2.54) để không cắm nhầm.

### Phân chân ESP32-S3 (sơ bộ, chốt khi vẽ mạch)

| Chức năng | GPIO |
|---|---|
| I2C | SDA 8, SCL 9 |
| Cổng analog A1, A2, A3 | (1, 2), (4, 5), (6, 7) – thuộc ADC1, đọc được khi bật WiFi |
| Cổng số D1, D2 | (14, 21), (38, 39) |
| Cổng D3 / UART | TX 43, RX 44 (tạm; chốt sau khi thử thư viện Serial của MicroBlocks) |
| SPI | CS 10, MOSI 11, SCK 12, MISO 13 |
| Servo 1–4 | 15, 16, 17, 18 |
| Trên bo: nút A, nút B, còi, LED RGB | 41, 42, 40, 48 |
| Dự phòng | 47 |
| Không dùng | 0, 3, 45, 46 (strapping); 19, 20 (USB); 35–37 (bộ nhớ của module N16R8) |

### Bản đồ địa chỉ I2C

| Địa chỉ | Module |
|---|---|
| 0x20 | Bàn phím 4x4 (PCF8574; không dùng bản PCF8574A vì dải địa chỉ của nó trùng 0x38–0x3F) |
| 0x30–0x33 | S1 driver động cơ (chọn bằng cầu hàn) |
| 0x34 | S2 dò line |
| 0x36 | S3 IMU |
| 0x38 | AHT20 nhiệt ẩm |
| 0x39 | APDS9960 màu/cử chỉ |
| 0x3C | OLED SSD1306 |
| 0x40 | INA219 trên C2 |
| 0x41 | PCA9685 (đặt cầu hàn A0) |

## 4. Danh mục module

### 4.1. Module trung tâm

**C1 – Bo chủ**
- ESP32-S3-WROOM-1 N16R8 hàn trực tiếp, USB-C.
- Tích hợp: 2 nút, còi, LED RGB, nút reset; các cổng như mục 3.
- Bảo vệ: cầu chì tự phục hồi trên 5 V, chống ngược nguồn, điện trở nối tiếp trên mọi chân tín hiệu.

**C2 – Nguồn pin 2S**
- 2 cell 18650, mạch bảo vệ và cân bằng, sạc qua USB-C.
- Ra 7,4 V cho động lực và 5 V/3 A cho bo chủ; công tắc; INA219 đo áp và dòng qua I2C.
- Dự án đặt cố định (nhà thông minh, IoT) dùng adapter USB-C thay cho C2.

### 4.2. Module thông minh tự thiết kế

Cả ba dùng chung vi điều khiển STM32G030K8T6, chung khung firmware I2C (thanh ghi 0x00 = mã loại, 0x01 = phiên bản) và chung mạch nạp. S2 và S3 có ổn áp 3,3 V riêng lấy từ 5 V của cổng I2C; S1 lấy từ nguồn pin. Firmware cập nhật được qua I2C từ bo chủ nhờ bootloader riêng, để giáo viên không cần mạch nạp.

**S1 – Driver động cơ encoder 2 kênh**
- TB6612FNG, cấp 6–12 V từ C2, đếm encoder bằng timer phần cứng.
- PID vận tốc 1 kHz, vòng vị trí có giới hạn gia tốc.
- Chế độ: dừng, PWM thô, vận tốc, vị trí. Tự dừng sau 500 ms mất lệnh.
- Số xung encoder và tỉ số truyền là tham số lưu trong flash, nên cùng một module chạy được N20 lẫn JGA25-370.
- Khối lệnh: `đặt tốc độ trái ◯ phải ◯`, `đi thẳng ◯ cm`, `quay ◯ độ`, `đã tới đích?`, `quãng đường`.

**S2 – Dò line 8 mắt**
- 8 cảm biến phản xạ, tự hiệu chuẩn đen/trắng, lưu vào flash.
- Trả về: vị trí line (-100..100), mặt nạ 8 bit, cờ ngã tư/mất line, giá trị thô từng mắt.
- Khối lệnh: `hiệu chuẩn`, `vị trí line`, `gặp ngã tư?`, `mất line?`.

**S3 – IMU trả góc**
- Cảm biến 6 trục, bộ lọc chạy 1 kHz trên vi điều khiển.
- Trả về: góc nghiêng trước–sau, trái–phải, góc xoay, vận tốc góc, cờ rung/va chạm.
- Khối lệnh: `góc nghiêng`, `góc xoay`, `đặt lại góc`, `bị rung?`.

### 4.3. Module đơn giản (cắm thẳng vào bo chủ)

Không có vi điều khiển, chỉ là bo mang có đầu cắm chuẩn và lỗ gá. Module nào cần 3,3 V thì có IC ổn áp riêng.

| Mã | Module | Cổng | Ghi chú |
|---|---|---|---|
| I1 | Nút bấm đôi | D/A | 2 nút trên một module |
| I2 | Biến trở xoay | D/A (analog) | |
| I3 | Joystick 2 trục | D/A (analog) | |
| I4 | Bàn phím 4x4 | I2C | qua PCF8574 |
| I5 | Ánh sáng (LDR) | D/A (analog) | |
| I6 | Nhiệt ẩm AHT20 | I2C | |
| I7 | Chuyển động PIR | D/A | |
| I8 | Khí gas MQ-2 | D/A (analog) | dùng 5 V, có phân áp |
| I9 | Độ ẩm đất điện dung | D/A (analog) | |
| I10 | Cảm biến mưa | D/A (analog) | |
| I11 | Siêu âm | D/A | S1 = trig, S2 = echo, có phân áp |
| I12 | Thu hồng ngoại + điều khiển | D/A | |
| I13 | RFID RC522 | SPI | RC522 chạy 3,3 V, có ổn áp trên bo mang |
| I14 | Màu/cử chỉ APDS9960 | I2C | |
| O1 | LED đơn (đỏ, vàng, xanh) | D/A | 2 LED trên một module |
| O2 | Thanh NeoPixel 8 LED | D/A | |
| O3 | OLED 0,96" SSD1306 | I2C | |
| O4 | Relay 1 kênh | D/A | có cách ly quang |
| O5 | MOSFET công suất | D/A (PWM) | kèm quạt 5 V, bơm mini |
| O6 | Servo SG90/MG90S | Servo | |
| O7 | PCA9685 16 kênh servo | I2C + nguồn | cho cánh tay robot; có mạch hạ áp 6 V/3 A riêng cho servo, vì servo nhỏ không chịu được 7,4 V của C2 |

### 4.4. Cơ khí

| Mã | Hạng mục | Nội dung |
|---|---|---|
| K1 | Cụm truyền động | 2 động cơ encoder + gá + bánh; bản N20 và bản JGA25-370, cùng đầu cắm 6 chân |
| K2 | Khung xe đa năng | lắp ngang + bánh mắt trâu = xe dò line; lắp đứng = xe cân bằng |
| K3 | Mô hình nhà | tấm cắt laser, lỗ gá module theo lưới 8 mm |
| K4 | Phụ kiện | sa bàn line, thẻ RFID, cánh tay robot, băng tải mini |

Mọi module có 4 lỗ bắt vít theo cùng lưới 8 mm với K2 và K3.

### 4.5. Module mở rộng qua cổng D3/UART

Không nằm trong 25 dự án chuẩn; dành cho dự án mở (dự án 25) và các gói bán thêm sau này.

| Module | Ứng dụng |
|---|---|
| Cảm biến vân tay | cửa thông minh, điểm danh |
| GPS | định vị, đo quãng đường ngoài trời |
| Cảm biến bụi PM2.5, CO2 | trạm chất lượng không khí |
| Phát nhạc MP3, nhận dạng giọng nói | nhà thông minh điều khiển bằng giọng nói |
| Camera AI (kiểu HuskyLens) | nhận dạng vật thể, xe bám theo vật |
| LoRa, RS485 | IoT tầm xa, nối nhiều bo chủ |

## 5. Các dự án học tập

### Cấp 1 – Làm quen (12–13 tuổi, 8 buổi)

| # | Dự án | Kiến thức STEM | Module |
|---|---|---|---|
| 1 | Đèn giao thông | mạch điện, tuần tự, thời gian | C1, O1, O2, I1 |
| 2 | Đàn điện tử | tần số âm thanh, biến, vòng lặp | C1 (còi), I1, I2 |
| 3 | Đo phản xạ | đo thời gian, số ngẫu nhiên, trung bình | C1, I1, O2, O3 |
| 4 | Nhiệt ẩm kế | cảm biến, đơn vị đo, hiển thị | C1, I6, O3 |

### Cấp 2 – Nhà thông minh (12–15 tuổi, 10 buổi)

| # | Dự án | Kiến thức STEM | Module |
|---|---|---|---|
| 5 | Đèn tự động | ngưỡng, logic VÀ/HOẶC, tiết kiệm điện | C1, I5, I7, O1, O4 |
| 6 | Cửa thông minh | nhận dạng, mật khẩu, danh sách | C1, I13, I4, O6, O3 |
| 7 | Báo cháy, rò gas | nồng độ khí, cảnh báo, an toàn | C1, I8, I6, O2, O5 |
| 8 | Quạt theo nhiệt độ | PWM, điều khiển tỉ lệ, đồ thị | C1, I6, I2, O5, O3 |
| 9 | Giàn phơi tự động | máy trạng thái, cơ cấu truyền động | C1, I10, I5, O6 (hoặc S1) |
| 10 | Nhà thông minh IoT | WiFi, MQTT, tích hợp hệ thống | C1 + module của dự án 5–9 |

### Cấp 3 – Robot di động (13–16 tuổi, 12 buổi)

| # | Dự án | Kiến thức STEM | Module |
|---|---|---|---|
| 11 | Xe điều khiển từ xa | vận tốc, chuyển động vi sai | C1, C2, S1, K1, K2, I12 |
| 12 | Xe tránh vật cản | vận tốc âm thanh, đo khoảng cách | + I11, O6 |
| 13 | Xe dò line cơ bản | phản xạ ánh sáng, điều khiển bật–tắt | + S2 |
| 14 | Xe dò line PID | sai số, P–I–D, thực nghiệm chỉnh tham số | + S2, O3 |
| 15 | Xe vẽ hình | chu vi, góc, quãng đường = vận tốc × thời gian | + S3 |
| 16 | Xe giao hàng | ngã tư, bản đồ, trạm RFID, báo cáo qua mạng | + S2, I13 |

### Cấp 4 – IoT (14–17 tuổi, 8 buổi)

| # | Dự án | Kiến thức STEM | Module |
|---|---|---|---|
| 17 | Trạm thời tiết online | thu thập dữ liệu, đồ thị, thống kê | C1, I6, I5, I10, O3 |
| 18 | Vườn thông minh | độ ẩm đất, tưới tự động, điều khiển từ xa | C1, I9, I6, O5, O4, O3 |
| 19 | Giám sát năng lượng | điện áp, dòng, công suất, dung lượng pin | C1, C2 (INA219), O3 |
| 20 | Điểm danh RFID | cơ sở dữ liệu, giao tiếp máy chủ | C1, I13, O3, O2 |

### Cấp 5 – Nâng cao (16–18 tuổi, 10 buổi)

| # | Dự án | Kiến thức STEM | Module |
|---|---|---|---|
| 21 | Xe cân bằng 2 bánh | con lắc ngược, trọng tâm, PID lồng nhau | C1, C2, S1, S3, K1, K2 |
| 22 | Xe cân bằng điều khiển qua điện thoại | chỉnh tham số từ xa, đo đạc | + thư viện IoT |
| 23 | Cánh tay robot | động học, góc khớp, ghi và phát lại chuyển động | C1, C2, O7, O6 ×4, I3 |
| 24 | Băng tải phân loại màu | ánh sáng và màu, tự động hóa dây chuyền | C1, C2, S1, I14, O6, O3 |
| 25 | Dự án mở (thi khoa học kỹ thuật) | quy trình thiết kế kỹ thuật | tự chọn |

## 6. Mỗi module dùng ở đâu và nối như thế nào

| Module | Nối vào | Dự án sử dụng |
|---|---|---|
| C1 Bo chủ | – | tất cả |
| C2 Nguồn pin | 5 V → C1; 7,4 V → S1/O7; I2C → C1 | 11–16, 19, 21–24 |
| S1 Driver động cơ | I2C ← C1; nguồn ← C2; 2 cổng động cơ → K1 | 9, 11–16, 21, 22, 24 |
| S2 Dò line | I2C (nối chuỗi sau S1) | 13, 14, 16 |
| S3 IMU | I2C (nối chuỗi) | 15, 21, 22 |
| I1 Nút bấm | cổng D | 1, 2, 3 |
| I2 Biến trở | cổng A | 2, 8 |
| I3 Joystick | cổng A | 23 |
| I4 Bàn phím | I2C | 6, 10 |
| I5 Ánh sáng | cổng A | 5, 9, 10, 17 |
| I6 Nhiệt ẩm | I2C | 4, 7, 8, 10, 17, 18 |
| I7 PIR | cổng D | 5, 10 |
| I8 Gas | cổng A | 7, 10 |
| I9 Độ ẩm đất | cổng A | 18 |
| I10 Mưa | cổng A | 9, 10, 17 |
| I11 Siêu âm | cổng D | 12 |
| I12 Hồng ngoại | cổng D | 11 |
| I13 RFID | cổng SPI | 6, 10, 16, 20 |
| I14 Màu | I2C | 24 |
| O1 LED | cổng D | 1, 5 |
| O2 NeoPixel | cổng D | 1, 3, 7, 20 |
| O3 OLED | I2C | 3, 4, 6, 8, 10, 14, 17, 18, 19, 20, 24 |
| O4 Relay | cổng D | 5, 10, 18 |
| O5 MOSFET + quạt/bơm | cổng D (PWM) | 7, 8, 10, 18 |
| O6 Servo | cổng Servo (hoặc O7) | 6, 9, 10, 12, 23, 24 |
| O7 PCA9685 | I2C ← C1; nguồn ← C2 | 23 |

### Sơ đồ nối của bốn cấu hình tiêu biểu

**Nhà thông minh (dự án 10)**
```
Adapter USB-C ─► C1 ─┬─ I2C ──► O3 OLED ──► I6 nhiệt ẩm ──► I4 bàn phím
                     ├─ A1 ───► I5 ánh sáng
                     ├─ A2 ───► I8 gas
                     ├─ A3 ───► I10 mưa
                     ├─ D1 ───► O4 relay (đèn)
                     ├─ D2 ───► O5 MOSFET (quạt)
                     ├─ D3 ───► I7 PIR
                     ├─ SPI ──► I13 RFID
                     └─ Servo ► O6 cửa, O6 giàn phơi
```

Dự án này dùng hết cả 6 cổng D/A. Cảnh báo dùng còi và LED RGB có sẵn trên bo chủ, không dùng thanh NeoPixel.

**Xe dò line (dự án 14)**
```
C2 ── 5 V ──► C1 ── I2C ──► S1 ──► S2 dò line ──► O3 OLED
C2 ── 7,4 V ─────────────► S1 ══► 2 động cơ encoder (K1)
```

**Xe cân bằng (dự án 21)**
```
C2 ── 5 V ──► C1 ── I2C ──► S1 ──► S3 IMU
C2 ── 7,4 V ─────────────► S1 ══► 2 động cơ encoder (K1), khung K2 lắp đứng
```

**Vườn thông minh (dự án 18)**
```
Adapter USB-C ─► C1 ─┬─ I2C ─► I6 nhiệt ẩm ─► O3 OLED
                     ├─ A1 ──► I9 độ ẩm đất
                     ├─ D1 ──► O5 MOSFET ─► bơm mini
                     └─ WiFi ─► MQTT ─► bảng điều khiển
```

## 7. Thư viện khối MicroBlocks

| Thư viện | Dùng cho | Dự án |
|---|---|---|
| Động cơ (S1) | di chuyển, quãng đường, góc quay | 9, 11–16, 21, 22, 24 |
| Dò line (S2) | vị trí line, ngã tư | 13, 14, 16 |
| Góc nghiêng (S3) | góc, rung | 15, 21, 22 |
| PID | một khối tính PID dùng chung | 8, 14, 21, 22 |
| IoT | WiFi, MQTT, bảng điều khiển | 10, 16–20, 22 |
| Thiết bị nhà | đèn, quạt, cửa, cảm biến theo tên gọi | 5–10, 18 |
| Nguồn (C2) | % pin, dòng, công suất | 19, cảnh báo pin yếu ở các xe |

## 8. Đóng gói sản phẩm

| Gói | Thành phần | Làm được dự án |
|---|---|---|
| Cơ bản | C1, I1, I2, I5, I6, O1, O2, O3 | 1–4 |
| Nhà thông minh | I4, I7, I8, I10, I13, O4, O5, O6 ×2, K3 | 5–10 |
| Robot | C2, S1, S2, S3, K1, K2, I11, I12, O6 | 11–16, 21, 22 |
| IoT | I9, bơm mini, tài liệu máy chủ MQTT cho giáo viên | 17–20 |
| Nâng cao | O7, O6 ×4, I3, I14, K4 | 23, 24 |

Gói Robot có hai bản: động cơ N20 (rẻ hơn) và JGA25-370 (khuyến nghị nếu dạy xe cân bằng).

Phụ thuộc giữa các gói:
- Mọi gói đều cần gói Cơ bản.
- Gói IoT cần gói Nhà thông minh (dùng lại I10, I13, O4, O5); dự án 19 cần thêm C2 của gói Robot.
- Gói Nâng cao cần gói Robot (C2, S1).
- Dự án 16 cần RFID (I13) của gói Nhà thông minh.

## 9. Những điểm phải kiểm chứng bằng bản mẫu

1. **Xe cân bằng trên MicroBlocks**: vòng đọc góc S3 → PID → gửi lệnh S1 cần đạt khoảng 100 Hz trở lên qua I2C. Chưa đo.
2. **Firmware MicroBlocks trên ESP32-S3-WROOM-1 N16R8**: nạp firmware, kết nối USB/BLE, và chân I2C mặc định có đúng là 8/9 hay không.
3. **RFID RC522 qua SPI** với thư viện có sẵn của MicroBlocks trên S3.
4. **MQTT và HTTP có mã hóa**: nếu MicroBlocks không hỗ trợ TLS, các dự án IoT cần máy chủ MQTT nội bộ đặt trên máy giáo viên.
5. **N20 cho xe cân bằng**: mô-men có đủ với khung K2 và pin 2S hay không.
6. **Nhiễu động cơ lên bus I2C** khi nối chuỗi dài 3–4 module.
7. **Chân UART trong MicroBlocks**: thư viện Serial trên ESP32-S3 dùng cặp chân nào và có đổi được không; cổng D3 phải đi dây theo đúng cặp đó.
8. **Có cần PSRAM không**: nếu MicroBlocks không dùng PSRAM, đổi sang module ESP32-S3-WROOM-1 N16 (không PSRAM) sẽ rẻ hơn và giải phóng GPIO35–37, đủ thêm một cổng D4. Dự án 10 hiện dùng hết 6 cổng D/A nên cổng thứ bảy rất có giá trị.
9. **Dòng tiêu thụ thực tế trên đường 5 V** của cấu hình nặng nhất (dự án 10) khi cấp bằng adapter và bằng cổng USB máy tính.
10. **Pin lithium trong sản phẩm bán cho trường**: yêu cầu an toàn, vận chuyển và bảo quản; cân nhắc bán kit không kèm cell pin.
11. **TB6612 với JGA25-370**: dòng kẹt trục của động cơ ở 7,4 V có nằm trong giới hạn của TB6612 hay không.

## 10. Thứ tự triển khai

1. Bản mẫu S1 (driver động cơ) và thử điểm 1, 2 ở mục 9 bằng bo ESP32-S3 mua sẵn.
2. Thiết kế C1, chốt phân chân và chuẩn cổng.
3. S3, S2 dùng lại khung firmware của S1.
4. C2 và các bo đầu cắm cho module đơn giản.
5. Cơ khí K1–K4.
6. Thư viện MicroBlocks, chương trình mẫu cho 25 dự án.
7. Giáo án, dạy thử tại một trường, chỉnh sửa, sản xuất loạt.

## 11. Định hướng mở rộng

### 11.1. Những thứ phải giữ cố định để mở rộng không phá tương thích

- Chuẩn cổng ở mục 3 (thứ tự chân, một nguồn 5 V, tín hiệu 3,3 V) và lưới lỗ gá 8 mm.
- Khung thanh ghi I2C của module thông minh: 0x00 = mã loại, 0x01 = phiên bản firmware.
- Bản đồ địa chỉ I2C: để dành 0x35, 0x37 và dải 0x44–0x4F cho module thông minh mới.
- Bootloader I2C có ngay từ lô đầu, để module đã bán vẫn nhận được firmware mới.

### 11.2. Module phần cứng mới

| Hướng | Module | Dự án mở ra |
|---|---|---|
| Thiếu cổng | Bộ mở rộng cổng qua I2C (thêm chân số và kênh analog) | nhà thông minh nhiều phòng |
| Chuyển động chính xác | Driver động cơ bước (module thông minh, cùng khung G030) | máy vẽ, máy CNC mini, băng tải định vị |
| Robot 4 bánh | Hai S1 + bánh mecanum | xe đa hướng, robot đá bóng, robot sumo |
| Thị giác | Camera AI qua cổng D3/UART | xe bám vật, phân loại bằng hình ảnh, nhận diện biển báo |
| Giao diện | Màn hình màu cảm ứng | bảng điều khiển nhà thông minh, máy chơi game |
| Âm thanh | MP3, micro, nhận dạng giọng nói | trợ lý giọng nói, đo độ ồn |
| Đo lường khoa học | Cân loadcell, pH, nhịp tim, cảm biến lực, cổng quang đo thời gian | thí nghiệm Vật lý, Hóa, Sinh |
| Năng lượng | Tấm pin mặt trời + mạch sạc, đo công suất | trạm IoT tự cấp nguồn, bài học năng lượng tái tạo |
| Truyền xa | LoRa, RS485 | nông nghiệp thông minh, mạng cảm biến toàn trường |

### 11.3. Bo chủ thế hệ sau

- Giữ nguyên chuẩn cổng, chỉ đổi vi điều khiển, để toàn bộ module cũ dùng tiếp được.
- Bản "Mini" ít cổng, giá thấp, cho học sinh mua cá nhân.
- Bản hỗ trợ Thread/Zigbee/Matter (dòng ESP32-C6 hoặc H2) cho nhà thông minh kết nối với thiết bị thương mại.
- Nhiều bo chủ nói chuyện với nhau qua MQTT hoặc ESP-NOW: mỗi phòng một bo, hoặc đội robot phối hợp.

### 11.4. Phần mềm

- **Lộ trình ngôn ngữ**: MicroBlocks (12–15 tuổi) → MicroPython → Arduino C++ (16–18 tuổi) trên cùng phần cứng. Viết thư viện cùng tên hàm cho cả ba, để học sinh đổi ngôn ngữ mà không đổi bộ kit.
- **Nền tảng IoT cho trường**: máy chủ MQTT và bảng điều khiển cài sẵn (một máy tính mini hoặc Raspberry Pi) để lớp học không phụ thuộc Internet.
- **Ứng dụng điện thoại riêng**: điều khiển xe, chỉnh PID, xem đồ thị cảm biến.
- **Công cụ cho giáo viên**: chương trình kiểm tra nhanh từng module, cập nhật firmware hàng loạt.
- **AI**: nhận dạng giọng nói và hình ảnh chạy trên module ngoài; bài học thu thập dữ liệu và huấn luyện mô hình đơn giản.

### 11.5. Chương trình giảng dạy

- Bài học liên môn bám chương trình phổ thông: Vật lý (chuyển động, điện, âm, nhiệt), Toán (hàm số, thống kê, hình học), Sinh học (cây trồng, môi trường), Công nghệ, Tin học.
- Bộ đề thi đấu: dò line tốc độ, sumo, giao hàng tự động, nhà thông minh sáng tạo.
- Khóa đào tạo và chứng nhận giáo viên; ngân hàng bài giảng và video.
- Kho dự án cộng đồng để trường chia sẻ chương trình và thiết kế cơ khí.

### 11.6. Hệ sinh thái

- Công bố chuẩn cổng và khung thanh ghi để bên thứ ba làm module tương thích.
- Tận dụng module Grove và M5Stack có sẵn cho các cảm biến ít dùng, thay vì tự thiết kế tất cả.
- Bộ linh kiện thay thế và dịch vụ sửa chữa cho trường (dây, đầu cắm, động cơ, servo là các thứ hỏng nhiều nhất).

### 11.7. Thứ tự ưu tiên đề xuất

1. Bootloader I2C và chương trình kiểm tra module (phải có trước khi bán lô đầu).
2. Bộ mở rộng cổng và xe mecanum (rẻ, dùng lại gần hết thứ đã có).
3. Thư viện MicroPython.
4. Camera AI và nền tảng IoT cho trường.
5. Bộ cảm biến đo lường khoa học và bài học liên môn.
6. Bo chủ thế hệ sau.

## 12. Kế hoạch clone và tùy biến MicroBlocks

Trạng thái (14/11/2026): đã chọn **mức 3, fork cả phần mềm lập trình**. Bản fork đang nằm trên một máy khác và **chưa tích hợp vào dự án này**. Khi tích hợp, đặt nó ở `microblocks/` (thư mục này đã được khai báo trong `.gitignore` của kho bộ kit).

### 12.1. Nguồn

- Kho mã chính thức: https://bitbucket.org/john_maloney/smallvm
- Các nhánh hiện có (đã kiểm tra ngày 14/11/2026): `stable`, `pilot`, `dev`, `old-dev`.
- Vị trí dự kiến khi clone: thư mục `microblocks/` ở gốc dự án, là một kho git riêng (fork), không trộn lịch sử với kho của bộ kit.

Lệnh clone khi cần:

```bash
git clone https://bitbucket.org/john_maloney/smallvm.git microblocks
```

### 12.2. Phải làm rõ trước khi sửa

- **Giấy phép**: tôi nhớ MicroBlocks dùng giấy phép MPL 2.0 nhưng chưa đọc tệp LICENSE trong kho. Phải kiểm tra điều kiện về công bố mã đã sửa và về việc dùng tên, logo MicroBlocks trên sản phẩm bán ra.
- **Phạm vi "thiết kế lại"** chưa chốt. Ba mức, từ nhẹ đến nặng:
  1. Chỉ viết thư viện khối riêng (thư mục `libraries/`), dùng nguyên MicroBlocks gốc. Không cần fork.
  2. Fork firmware: thêm cấu hình cho bo chủ C1 (chân mặc định I2C, UART, nút, còi, LED), có thể thêm khối gốc cho việc cần tốc độ như vòng cân bằng.
  3. Fork cả phần mềm lập trình: đổi giao diện, tên, ngôn ngữ mặc định tiếng Việt, cài sẵn thư viện của bộ kit.
- **Chi phí bảo trì**: mức 2 và 3 phải tự hợp nhất các bản cập nhật từ kho gốc. Khuyến nghị bắt đầu ở mức 1, chỉ lên mức 2 khi các điểm kiểm chứng ở mục 9 (I2C, UART, tốc độ vòng cân bằng) cho thấy cần sửa firmware.

### 12.3. Việc cần làm khi clone

1. Đọc LICENSE và ghi kết luận vào mục này.
2. Chọn nhánh làm gốc (dự kiến `stable`).
3. Thử build firmware cho ESP32-S3 nguyên bản trước khi sửa bất cứ thứ gì.
4. Ghi lại cấu trúc thư mục của kho và chỗ cần sửa cho từng mức ở 12.2.

## 13. Cấu trúc thư mục dự án

| Thư mục | Nội dung |
|---|---|
| `docs/` | Tài liệu thiết kế này, bản đồ kit, chuẩn cổng, bản đồ địa chỉ I2C |
| `hardware/` | Thiết kế mạch KiCad: `C1-bo-chu`, `C2-nguon-pin`, `S1-driver-dong-co`, `S2-do-line`, `S3-imu`, `bo-mang` (bo mang cho module đơn giản), `common` (thư viện ký hiệu, chân linh kiện, đầu cắm dùng chung) |
| `firmware/` | Firmware STM32G030 cho `S1`, `S2`, `S3`; `common` chứa khung I2C và bootloader dùng chung |
| `libraries/` | Thư viện khối MicroBlocks tự viết (Động cơ, Dò line, Góc nghiêng, PID, IoT, Thiết bị nhà, Nguồn) |
| `mechanical/` | Thiết kế cơ khí K1–K4 |
| `projects/` | Chương trình mẫu của 25 dự án, chia theo 5 cấp độ |
| `curriculum/` | Giáo án, phiếu bài học, tài liệu giáo viên |
| `microblocks/` | Chưa có. Kho fork MicroBlocks, xem mục 12 |
