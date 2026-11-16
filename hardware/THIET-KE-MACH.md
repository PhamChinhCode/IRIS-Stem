# Thiết kế mạch IRIS-Stem – kiến trúc, linh kiện và nguyên lý

Phiên bản 0.1 – 15/11/2026. Tài liệu này là đầu vào để vẽ sơ đồ nguyên lý trong KiCad 10. Chưa có sơ đồ nào được vẽ, chưa có mạch nào được thử.

Nguồn tham khảo:
- Yêu cầu hệ thống: [THIET-KE-HE-THONG.md](../docs/THIET-KE-HE-THONG.md); kích thước bo: [THIET-KE-CO-KHI.md](../docs/THIET-KE-CO-KHI.md).
- Thư viện đầu cắm và khung bo: [common/README.md](common/README.md).
- Bo mẫu `PID-G4-Master-Control` (dự án driverDC): lấy linh kiện, cách chia khối và quy tắc trong `KICAD_DESIGN_GUIDE.md`.

Ký hiệu trong các bảng linh kiện: cột LCSC chỉ ghi mã **đã đối chiếu** trên lcsc.com/jlcpcb.com ngày 15/11/2026; dấu “–” nghĩa là chưa tra, sẽ điền khi vẽ sơ đồ.

---

## 0. Quy ước chung cho mọi bo

### 0.1. Lấy gì từ bo mẫu

| Hạng mục | Bo mẫu dùng | Áp dụng cho IRIS |
|---|---|---|
| Điện trở | 0603 1 %: 10 Ω, 1 k, 5k1, 10 k, 100 k | giữ nguyên bộ giá trị, thêm 100 Ω, 220 Ω, 2k2, 47 k |
| Tụ gốm | 100 pF, 100 nF 0603 50 V; 10 µF 0805 25 V | giữ nguyên, thêm 1 nF, 1 µF 0603, 22 µF 0805 10 V |
| Ổn áp 3,3 V | AP2112K-3.3 (SOT-23-5, 600 mA, vào tối đa 6 V) | mọi module có vi điều khiển hoặc tải 3,3 V trên 50 mA |
| Chống tĩnh điện | SRV05-4 (SOT-23-6, 4 kênh) | mọi cổng tín hiệu ra ngoài của C1 và module thông minh |
| USB-C | HRO TYPE-C-31-M-12 (16 chân, USB 2.0), CC kéo xuống 5k1 | C1, C2 |
| MOSFET nhỏ | AO3400A (N, SOT-23) | còi, LED hồng ngoại, O5; thêm AO3401A (P) |
| Diode | 1N4148W (SOD-123), SS36 (SMA) | 1N4148W giữ; Schottky đổi sang SS54 (5 A) |
| Nút nhấn | TS-1088 (SMD 3 × 4) | reset, boot |
| LED báo | 0603 xanh + 1 k | giữ |
| Ferrite | 600 Ω @100 MHz 0805 | nguồn cảm biến, nguồn encoder |
| Cầu hàn | SolderJumper 2 chân, 3 chân | chọn địa chỉ I2C |
| Tụ hoá | 220 µF | S1, O7, C1 (bản 16–25 V thay cho 50 V) |

Không dùng lại: LMR51606 (chỉ 0,6 A, không đủ cho đường 5 V/3 A), MT3608, IRS2104 và MOSFET 60 V, STM32G431 (thừa so với nhu cầu, đã chốt STM32G030).

### 0.2. Cách vẽ sơ đồ (theo bo mẫu)

- Mỗi bo một trang phẳng, không dùng trang con: bo lớn nhất (C1) khoảng 110 linh kiện, các bo khác dưới 60. Khổ A3; riêng C1 khổ A2.
- Mỗi khối chức năng nằm trong một khung chữ nhật có tiêu đề in hoa ở góc trên trái và 1–2 dòng ghi chú công thức ngay trong khung (ví dụ `FB: (51k+10k)/10k × 0,768 V → 5,45 V`).
- Khối xếp theo dòng năng lượng từ trái sang phải: nguồn vào và bảo vệ → ổn áp → vi điều khiển → cổng ra. Trong một khối, dây ngắn và thẳng; giữa các khối nối bằng nhãn toàn cục, không kéo dây xuyên khung.
- Tên lưới nguồn dùng một kiểu duy nhất: `GND`, `+5V`, `+3V3`, `VBUS`, `VBAT`. Lưới nguồn đi vào qua đầu cắm phải có `PWR_FLAG` (mọi chân cổng trong thư viện IRIS là *passive*).
- Mỗi linh kiện có đủ trường `MPN`, `Manufacturer`, `LCSC`, `Datasheet`, `Description`. Sơ đồ là nguồn duy nhất của BOM.
- Khung bo `Khung_*` đặt trong sơ đồ như một linh kiện (không vào BOM), để đường cắt và lỗ gá không bị xoá khi cập nhật bo.
- Trước khi chuyển sang layout: `kicad-cli sch erc` không còn lỗi.

### 0.3. Tối ưu cho JLCPCB

- Điện trở, tụ 0603/0805 và phần lớn bán dẫn nhỏ ở trên là linh kiện Basic. Mỗi mã Extended thêm phí khoảng 3 USD cho một đơn, nên các bo dùng chung một bộ mã.
- Lắp máy một mặt (mặt trên). Linh kiện xuyên lỗ (đầu JST, XT30, hàng rào, relay, cầu đấu, tụ hoá) hàn tay hoặc đặt dịch vụ hàn xuyên lỗ. Ngoại lệ: S2 có 8 mắt đọc ở mặt dưới.
- Bo mang cỡ S ghép panel để giảm giá.

---

## 1. Kiến trúc hệ thống

### 1.1. Luồng nguồn

```
                 C2 NGUỒN PIN                                   C1 BO CHỦ
 USB-C 5 V ─► IP2326 sạc tăng áp ─┐                 USB-C ─► Q1 P-FET ──┐
                                  ▼                                     ├─► +5V_SYS ─┬─► F1 1,5 A ─► +5V_SERVO (4 cổng servo)
   2 cell 18650 ─► HY2120 + FET ─► shunt 10 mΩ ─► công tắc (P-FET)      │            ├─► F2 1,1 A ─► +5V (6 D/A, 4 I2C, SPI)
        bảo vệ                    (INA219)            │                 │            └─► LDO 1 A ──► +3V3 (ESP32-S3, kéo lên I2C)
                                                      ├─► buck 5,45 V/3 A ─► XH 2 chân ─► D1 SS54 ─┘
                                                      └─► XT30 (VBAT 6–8,4 V)
                                                              │
                              ┌───────────────────────────────┴───────────────┐
                              ▼                                               ▼
                  S1: P-FET chống ngược ─► VM ─► TB6612          O7: P-FET ─► buck 5,45 V/3 A ─► 16 servo

 Module trên cổng I2C / D/A / SPI: +5V của cổng ─► ổn áp 3,3 V tại chỗ ─► IC và mức tín hiệu
```

### 1.2. Luồng tín hiệu

```
 Máy tính ══ USB (GPIO19/20, CDC gốc của ESP32-S3) ══► C1
 C1 ── I2C 3,3 V (GPIO8/9, kéo lên 2k2 chỉ trên C1) ──► S1 ─► S2 ─► S3 ─► O3 ... (nối chuỗi)
                                                    └─► C2 (INA219), I4, I6, I14, O7
 C1 ── 6 cổng D/A (2 tín hiệu/cổng, 3,3 V) ──► module đơn giản
 C1 ── SPI ──► I13 RFID        C1 ── 4 PWM ──► servo
 S1 ── PWM + chiều ──► TB6612 ══► động cơ;  encoder A/B ──► timer của STM32G030
```

### 1.3. Ngân sách dòng

| Đường | Tải | Điển hình | Đỉnh |
|---|---|---|---|
| +3V3 trên C1 | ESP32-S3 khi dùng WiFi | 120 mA | 350 mA |
| +5V_SYS, dự án 10 (nhà thông minh) | ESP32 120 + MQ-2 160 + relay 72 + quạt 180 + OLED 20 + còi/LED 50 + 2 servo đang chạy 2 × 250 | 1,1 A | 1,9 A (2 servo kẹt) |
| +5V_SYS, dự án 14 (xe dò line) | ESP32 120 + S1 30 + S2 20 + OLED 20 | 0,2 A | 0,4 A |
| VBAT, xe với 2 động cơ N20 | 2 × 0,2 A | 0,4 A | 2 × 1,6 A (kẹt) |
| VBAT, xe với 2 động cơ JGA25-370 | 2 × 0,5 A | 1,0 A | 2 × 2,2 A (kẹt) |
| Pin, trường hợp xấu nhất | buck 3 A ở pin 6,4 V (2,8 A) + 2 động cơ kẹt (4,4 A) | 1,5 A | 7,2 A |

Kết luận:
- Cổng USB máy tính (0,5 A) không nuôi được dự án 10; cần adapter 5 V/2 A, đúng như tài liệu hệ thống đã ghi.
- 2 cell 2600 mAh (19 Wh): xe dò line tiêu thụ khoảng 7 W, chạy được khoảng 2,5 giờ.

---

## 2. Khối lõi dùng chung cho S1, S2, S3

Ba module thông minh dùng chung một khối, vẽ một lần rồi chép sang.

```
 Cổng I2C vào ─┬─ +5V ─► AP2112K-3.3 ─► +3V3 ─► STM32G030K8T6
 Cổng I2C ra ──┘  SDA/SCL ─► SRV05-4 ─► 100 Ω ─► PB7/PB6
                                         SWD (5 điểm thử) · LED trạng thái · cầu hàn địa chỉ
```

| Ký hiệu | Linh kiện | Giá trị / mã | LCSC | Ghi chú |
|---|---|---|---|---|
| U1 | Vi điều khiển | STM32G030K8T6, LQFP-32 | C431631 | 64 KB flash, 8 KB RAM |
| U2 | Ổn áp | AP2112K-3.3TRG1 | – | EN nối VIN |
| U3 | ESD | SRV05-4, VP = +3V3 | – | SDA, SCL và 2 tín hiệu ngoài của bo |
| C1, C2 | Tụ vào/ra ổn áp | 10 µF 25 V 0805 | – | |
| C3, C4 | Tụ tách VDD | 100 nF + 10 µF | – | sát chân 4 (VDD), chân 5 (VSS) |
| C5 | Tụ NRST | 100 nF | – | chân 6 |
| R1, R2 | Nối tiếp SDA, SCL | 100 Ω | – | giữa đầu cắm và vi điều khiển |
| R3 | Kéo xuống PA14-BOOT0 | 10 k | – | xem cảnh báo |
| LED1, R4 | LED trạng thái | xanh 0603 + 1 k | – | |
| TP1–TP5 | Điểm nạp | 3V3, SWDIO (PA13), SWCLK (PA14), NRST, GND | – | hàng 5 điểm bước 2,54 mm, không hàn chân |
| J1, J2 | Cổng I2C | `IRIS:Cong_I2C` | – | hai cổng nối song song cả 4 chân |

Tính toán:
- Dòng 3,3 V: vi điều khiển 5 mA ở 16 MHz, cộng tải riêng từng bo (mục 3–5). Tổn hao ổn áp lớn nhất là ở S1: (5 − 3,3) V × 40 mA = 68 mW, không cần tản nhiệt.
- Không dùng thạch anh: dao động nội HSI16 sai số ±1 %, đủ cho I2C tớ và PWM.
- Không đặt điện trở kéo lên I2C trên module (chỉ C1 có).

Cảnh báo:
- **PA14 vừa là SWCLK vừa là BOOT0.** Nếu bit tuỳ chọn `nBOOT_SEL` = 0, mức cao trên chân này lúc reset đưa chip vào bootloader ROM. Giữ R3 kéo xuống và kiểm tra bit này khi nạp lần đầu.
- **Chân 19 và 21 của vỏ LQFP-32 (PA9, PA10) dùng chung chức năng với chân 22, 23 (PA11, PA12)** qua cơ chế remap. Thiết kế này không dùng bốn chân đó để tránh nhầm.
- Chân NRST có thể bị cấu hình thành GPIO bằng option byte; không được đổi, nếu không sẽ mất đường nạp.
- Vi điều khiển lấy nguồn từ cổng I2C (xem quyết định Q1 ở mục 9), nên nó luôn sống khi bus sống và không kéo sập bus.

---

## 3. S1 – driver động cơ encoder 2 kênh (48 × 48)

### 3.1. Sơ đồ khối

```
 XT30 đực ─► Q1 AO4435 chống ngược ─► VM ─┬─► 220 µF + 2 × 10 µF ─► TB6612FNG ══► cổng động cơ 1, 2
                                          └─► chia áp 100k/10k ─► PA0 (đo VM)
 Cổng I2C ─► khối lõi (mục 2) ─► PWMA/B, AIN1/2, BIN1/2, STBY ─► TB6612FNG
 Cổng động cơ: EncA/EncB ─► kéo lên 10 k ─► 1 k + 1 nF ─► TIM1 / TIM3
               3V3 ─► ferrite ─► nguồn encoder
```

### 3.2. Linh kiện riêng

| Ký hiệu | Linh kiện | Giá trị / mã | LCSC | Ghi chú |
|---|---|---|---|---|
| U4 | Driver | TB6612FNG, SSOP-24 | – | VM 4,5–13,5 V; 1,2 A liên tục, 3,2 A đỉnh mỗi kênh |
| Q1 | P-MOSFET chống ngược cực | AO4435 (−30 V, −10 A, V_GS ±25 V), SOIC-8 | – | D về XT30, S về VM, G xuống GND qua 100 k |
| C10 | Tụ khối VM | 220 µF 25 V, low-ESR | – | sát U4 |
| C11, C12 | Tụ gốm VM | 10 µF 25 V 0805 | – | mỗi cụm chân VM một tụ |
| C13, C14 | Tụ tách | 100 nF 50 V | – | VM và VCC của U4 |
| R10, R11, C15 | Đo VM | 100 k / 10 k + 100 nF | – | hệ số 1/11; 12 V → 1,09 V |
| R12 | Kéo xuống STBY | 10 k | – | động cơ tắt khi vi điều khiển đang reset |
| R13–R16 | Kéo lên encoder | 10 k lên +3V3 | – | 4 đường |
| R17–R20, C16–C19 | Lọc encoder | 1 k + 1 nF | – | f_c = 1/(2π·1k·1n) ≈ 160 kHz |
| FB1 | Nguồn encoder | ferrite 600 Ω 0805 | – | +3V3 → chân 4 của hai cổng động cơ |
| JP1, JP2 | Địa chỉ | cầu hàn 2 chân, hở | – | 0x30 + (JP2, JP1) |
| LED2, R21 | Báo có VM | LED + 10 k | – | 8,4 V → 0,6 mA |
| J3 | Nguồn | `IRIS:Cong_Nguon_XT30` (đực) | – | |
| J4, J5 | Động cơ | `IRIS:Cong_DongCo` (XH 6 chân) | – | |

### 3.3. Gán chân STM32G030K8T6

| Chân | Tên | Chức năng | Nối tới |
|---|---|---|---|
| 7 | PA0 | ADC1_IN0 | đo VM (R10/R11) |
| 8 | PA1 | GPIO ra | STBY (U4-19) |
| 9, 10 | PA2, PA3 | USART2 TX/RX | 2 điểm thử gỡ lỗi |
| 11 | PA4 | GPIO ra | AIN1 (U4-21) |
| 12 | PA5 | GPIO ra | AIN2 (U4-22) |
| 13 | PA6 | GPIO ra | BIN1 (U4-17) |
| 14 | PA7 | GPIO ra | BIN2 (U4-16) |
| 15 | PB0 | GPIO ra | LED trạng thái |
| 17 | PB2 | GPIO vào, kéo lên nội | JP1 |
| 18 | PA8 | TIM1_CH1 | encoder 1 kênh A |
| 27 | PB3 | TIM1_CH2 | encoder 1 kênh B |
| 28 | PB4 | TIM3_CH1 | encoder 2 kênh A |
| 29 | PB5 | TIM3_CH2 | encoder 2 kênh B |
| 30 | PB6 | I2C1_SCL | bus I2C |
| 31 | PB7 | I2C1_SDA | bus I2C |
| 32 | PB8 | TIM16_CH1 | PWMA (U4-23) |
| 1 | PB9 | TIM17_CH1 | PWMB (U4-15) |
| 26 | PA15 | GPIO vào, kéo lên nội | JP2 |
| 24, 25 | PA13, PA14 | SWD | điểm nạp |

TB6612FNG: AO1 (1, 2) → M+ cổng 1; AO2 (5, 6) → M− cổng 1; BO1 (11, 12) → M+ cổng 2; BO2 (7, 8) → M− cổng 2; VM1–VM3 (24, 13, 14) → VM; PGND (3, 4, 9, 10) và GND (18) → GND; VCC (20) → +3V3.

Lý do chọn timer: chỉ TIM1 và TIM3 của G030 có chế độ đếm encoder, nên hai timer này dành cho encoder và PWM phải lấy từ TIM16, TIM17 (mỗi timer một kênh, đặt cùng tần số 20 kHz).

### 3.4. Tính toán

- **Tổn hao TB6612**: điện trở dẫn tổng hai nhánh khoảng 0,5 Ω. Ở 0,5 A mỗi kênh: 2 × 0,5² × 0,5 = 0,25 W. Ở 1 A mỗi kênh: 1 W, sát giới hạn của vỏ SSOP-24 (khoảng 0,8–1,3 W tuỳ diện tích đồng). Cần đổ đồng rộng cho chân PGND và các chân ra.
- **Kẹt trục**: JGA25-370 có thể kéo 2,2 A, vượt 1,2 A liên tục. IC tự ngắt nhiệt, nhưng firmware phải cắt PWM khi encoder đứng yên quá 0,5 s ở PWM cao. Đây là điểm 11 trong danh sách kiểm chứng của tài liệu hệ thống.
- **Q1**: R_DS khoảng 20 mΩ ở V_GS = −7 V. Ở 4,4 A (hai động cơ kẹt): 0,39 W; ở 1 A: 20 mW.
- **Đo VM**: ADC 12 bit, bước 3,3/4096 × 11 = 8,9 mV.
- **Encoder**: tần số cao nhất khoảng 3,5 kHz (N20, 7 xung/vòng, 30 000 vòng/phút), thấp hơn f_c của bộ lọc 45 lần.

### 3.5. Cảnh báo

- Không đặt TVS trên VM: điện áp tuyệt đối của TB6612 là 15 V, còn TVS cho đường 12 V kẹp ở 17–20 V nên không bảo vệ được. Tụ khối 220 µF hấp thụ năng lượng hãm.
- Chân vào của TB6612 có sẵn điện trở kéo xuống 200 kΩ, không cần thêm ngoài R12.
- Mạch không đo dòng động cơ. Bảo vệ quá tải dựa vào ngắt nhiệt của IC và phát hiện kẹt bằng encoder.
- Thứ tự chân cổng động cơ (M+, M−, GND, 3V3, EncA, EncB) khác với cáp sẵn của động cơ encoder bán trên thị trường; phải làm cáp riêng hoặc bo chuyển.

---

## 4. S2 – dò line 8 mắt (80 × 24)

```
 +5V ─► 4 chuỗi × (2 LED hồng ngoại + R) ─► Q2 AO3400A ◄─ PB0 (phát xung)
 +3V3 ─► 47 k ─► cực C của 8 phototransistor ─► PA0..PA7 (ADC)
 Cổng I2C ×2 ─► khối lõi
```

| Ký hiệu | Linh kiện | Giá trị / mã | LCSC | Ghi chú |
|---|---|---|---|---|
| OP1–OP8 | Mắt phản xạ | ITR8307 (3,4 × 2,7 × 1,5), **mặt dưới** | – | bước 9 mm |
| R30–R33 | Hạn dòng LED | 100 Ω | – | mỗi chuỗi 2 LED nối tiếp |
| R34–R41 | Tải phototransistor | 47 k lên +3V3 | – | chỉnh khi thử |
| Q2, R42, R43 | Đóng cắt LED | AO3400A + 100 Ω cực G + 10 k kéo xuống | – | |

Gán chân: PA0–PA7 (chân 7–14) = ADC1_IN0…IN7 cho mắt 1–8; PB0 (15) = điều khiển LED; PA8 (18) = LED trạng thái; PB6/PB7 = I2C.

Tính toán:
- Dòng LED: (5 − 2 × 1,2 − 0,05) / 100 = 25 mA mỗi chuỗi, 100 mA cho 4 chuỗi khi bật. Phát xung 20 % nên trung bình 20 mA. Nối 2 LED nối tiếp lấy từ 5 V giảm một nửa dòng so với nối từng LED.
- Đo hai lần cho mỗi chu kỳ (LED bật và LED tắt) rồi trừ nhau để loại ánh sáng nền.

Cảnh báo:
- **Khoảng cách đọc.** ITR8307 nhạy nhất ở khoảng 1 mm, trong khi thiết kế cơ khí để mặt mắt cách sàn 5,9 mm. Tín hiệu ở khoảng cách này yếu, chưa tra được đường cong chính xác. Cần thử trên bản mẫu; nếu không đủ thì rút trụ đỡ xuống 8–9 mm hoặc đổi sang mắt có tầm xa hơn (xem Q3 ở mục 9).
- 8 mắt nằm ở mặt dưới: phải đặt lắp hai mặt ở JLCPCB hoặc hàn tay 8 mắt này.
- Tổng dòng 3,3 V của khối tải: 8 × 3,3 V / 47 k = 0,6 mA, không đáng kể.

---

## 5. S3 – IMU (32 × 32)

```
 +3V3 ─► ferrite ─► +3V3_IMU ─► LSM6DS3TR-C ◄═ SPI1 ═► STM32G030 ◄─ I2C ─► cổng I2C ×2
```

| Ký hiệu | Linh kiện | Giá trị / mã | LCSC | Ghi chú |
|---|---|---|---|---|
| U5 | IMU 6 trục | LSM6DS3TR-C, LGA-14 2,5 × 3 | C967633 | Extended |
| FB2, C20, C21 | Nguồn riêng | ferrite 600 Ω + 10 µF + 100 nF | – | VDD (8) và VDDIO (5) |

Nối chân:

| LSM6DS3TR-C | Tín hiệu | STM32G030 |
|---|---|---|
| 13 SCL | SPI1_SCK | PA5 (12) |
| 14 SDA | SPI1_MOSI | PA7 (14) |
| 1 SDO/SA0 | SPI1_MISO | PA6 (13) |
| 12 CS | GPIO | PA4 (11), kéo lên 10 k |
| 4 INT1 | ngắt dữ liệu sẵn sàng | PB0 (15) |
| 9 INT2 | không dùng | để hở |
| – | LED trạng thái | PA8 (18) |
| 2 SDX, 3 SCX | – | nối GND |
| 10, 11 | – | để hở |
| 6, 7 | GND | GND |

Ghi chú:
- Dùng SPI thay vì I2C thứ hai để đọc 1 kHz ổn định và để bus I2C của vi điều khiển chỉ làm tớ.
- CS phải ở mức cao trước khi cấp nguồn xong, nếu không IC vào nhầm chế độ I2C: vì vậy có điện trở kéo lên.
- Layout: IMU ở đúng tâm bo, không đi dây và không đặt via bên dưới, xa lỗ gá (ứng suất khi siết vít làm lệch điểm không).
- Phương án thay thế cùng vỏ LGA-14: ICM-42670-P, BMI270. Sơ đồ chân khác nhau ở vài chân, phải đối chiếu nếu đổi.

---

## 6. C1 – bo chủ (64 × 48)

### 6.1. Sơ đồ khối

```
 USB-C ─┬─ VBUS ─► Q1 AO3401A ─┐
        │                      ├─► +5V_SYS ─┬─► F1 ─► +5V_SERVO ─► 4 cổng servo
 XH 2 chân (từ C2) ─► D1 SS54 ─┘            ├─► F2 ─► +5V ─► 6 D/A, 4 I2C, SPI
        │                                   └─► U2 LDO ─► +3V3 ─► ESP32-S3-WROOM-1
        └─ D+/D− ─► SRV05-4 ─► GPIO20/19
 ESP32-S3: mỗi chân ra cổng ─► 220 Ω (100 Ω với I2C, SPI) ─► SRV05-4 ─► đầu cắm
           nút A, B · còi · LED RGB · nút RESET, BOOT
```

MicroBlocks dựng cho ESP32-S3 với `ARDUINO_USB_CDC_ON_BOOT` (xem `Iris blocks/platformio.ini`), tức là dùng USB gốc của chip. Vì vậy C1 **không cần IC chuyển USB–UART** và không cần mạch tự nạp bằng DTR/RTS.

### 6.2. Linh kiện chính

| Ký hiệu | Linh kiện | Giá trị / mã | LCSC | Ghi chú |
|---|---|---|---|---|
| U1 | Module | ESP32-S3-WROOM-1-N16R8 | C2913202 | Extended |
| U2 | Ổn áp 3,3 V | TLV1117LV33 (SOT-223, 1 A, sụt áp 0,46 V) | – | xem tính toán |
| Q1 | Chọn nguồn USB | AO3401A (P, SOT-23) | – | D = VBUS, S = +5V_SYS, G = lưới 5V_EXT |
| R1 | Kéo xuống cực G của Q1 | 100 k | – | |
| D1 | Chặn dòng ngược về C2 | SS54 (5 A, SMA) | – | |
| F1 | Cầu chì servo | PTC 1,5 A giữ, 1812 | – | |
| F2 | Cầu chì cổng | PTC 1,1 A giữ, 1812 | – | |
| C1 | Tụ khối servo | 220 µF 16 V | – | sau F1 |
| J1 | USB-C | TYPE-C-31-M-12 | – | CC1, CC2 mỗi chân 5k1 xuống GND |
| U3 | ESD USB | SRV05-4, VP = VBUS | – | |
| U4–U9 | ESD cổng | 6 × SRV05-4, VP = +3V3 | – | 22 đường tín hiệu |
| R… | Nối tiếp tín hiệu | 220 Ω × 16, 100 Ω × 6 | – | D/A, servo: 220 Ω; I2C, SPI: 100 Ω |
| R20, R21 | Kéo lên I2C | 2k2 lên +3V3 | – | |
| SW1, SW2 | Nút A, B | nút 6 × 6, 10 k kéo lên + 100 nF | – | GPIO41, GPIO42 |
| SW3 | RESET | TS-1088 | – | EN: 10 k kéo lên + 1 µF |
| SW4 | BOOT | TS-1088 | – | GPIO0 xuống GND |
| BZ1, Q2, D2 | Còi | còi thụ động SMD 8,5 mm + AO3400A + 1N4148W | – | GPIO40; cực G 100 Ω + 10 k kéo xuống |
| LED1 | LED RGB | WS2812B-2020, **cấp +3V3** | – | GPIO48 |
| LED2 | Báo nguồn | LED + 1 k | – | |
| J2 | Nguồn từ C2 | JST XH 2 chân nằm ngang (S2B-XH-A) | – | chưa có trong thư viện IRIS |

### 6.3. Gán chân ESP32-S3-WROOM-1

| Cổng | Chân cổng | GPIO | Chân module |
|---|---|---|---|
| A1 | S1, S2 | 1, 2 | 39, 38 |
| A2 | S1, S2 | 4, 5 | 4, 5 |
| A3 | S1, S2 | 6, 7 | 6, 7 |
| D1 | S1, S2 | 14, 21 | 22, 23 |
| D2 | S1, S2 | 38, 39 | 31, 32 |
| D3 / UART | S1 = TX, S2 = RX | 43, 44 | 37, 36 |
| I2C | SDA, SCL | 8, 9 | 12, 17 |
| SPI | SCK, MOSI, MISO, CS | 12, 11, 13, 10 | 20, 19, 21, 18 |
| Servo 1–4 | PWM | 15, 16, 17, 18 | 8, 9, 10, 11 |
| USB | D−, D+ | 19, 20 | 13, 14 |
| Nút A, B | – | 41, 42 | 34, 35 |
| Còi | – | 40 | 33 |
| LED RGB | – | 48 | 25 |
| Dự phòng | điểm thử | 47 | 24 |
| BOOT | – | 0 | 27 |
| Để hở | – | 3, 45, 46, 35, 36, 37 | 15, 26, 16, 28–30 |
| EN | RESET | – | 3 |

### 6.4. Tính toán

- **Chọn nguồn.** Khi không có C2: cực G của Q1 bị R1 kéo xuống, Q1 dẫn, sụt áp 2 A × 60 mΩ = 0,12 V (0,24 W). Khi có C2: lưới 5V_EXT (5,45 V) đưa cực G lên cao, Q1 khoá, +5V_SYS = 5,45 − 0,4 = 5,05 V; diode thân của Q1 không dẫn vì VBUS không cao hơn +5V_SYS. D1 chặn dòng từ USB chảy ngược vào đầu ra buck của C2.
- **D1**: 0,4 V × 1,5 A = 0,6 W điển hình; 0,45 V × 3 A = 1,35 W ở đỉnh, cần vùng đồng tản nhiệt ở hai chân.
- **U2**: (5,0 − 3,3) × 0,12 A = 0,2 W trung bình; 0,6 W khi phát WiFi liên tục 350 mA. Vỏ SOT-223 với vùng đồng 2 cm² tản khoảng 60 °C/W nên tăng 36 °C ở mức xấu nhất. AP2112K (SOT-23-5, khoảng 200 °C/W) sẽ tăng 120 °C, vì vậy không dùng ở đây.
- **Kéo lên I2C 2k2**: dòng kéo 1,5 mA. Với bus 300 pF (4–5 module và dây), thời gian lên 0,85 × 2k2 × 300 pF = 560 ns: đạt chuẩn 100 kHz (1000 ns), không đạt 400 kHz (300 ns). Thư viện để mặc định 100 kHz; riêng vòng điều khiển xe cân bằng (chuỗi ngắn, khoảng 100 pF, 190 ns) dùng được 400 kHz.
- **Điện trở nối tiếp 220 Ω**: nếu module lỗi đưa 5 V lên chân tín hiệu, dòng qua diode kẹp là (5 − 3,3 − 0,7) / 220 = 4,5 mA, chảy vào lưới +3V3 và được ESP32 tiêu thụ. Thứ tự bắt buộc: đầu cắm → điện trở → (SRV05-4, chân ESP32).
- **Cầu chì**: F1 1,5 A giữ cho 2 servo nhỏ (2 × 0,65 A khi kẹt). F2 1,1 A giữ cho các cổng (tải nặng nhất khoảng 0,6 A). Sụt áp qua PTC khoảng 0,1–0,15 V ở 1 A.

### 6.5. Cảnh báo

- **Anten**: không đổ đồng, không đi dây ở mọi lớp trong vùng anten và 15 mm hai bên; module đặt sát mép phải như tài liệu cơ khí.
- **Chân strapping**: GPIO0 chỉ nối nút BOOT; GPIO3, 45, 46 để hở. GPIO35–37 là bộ nhớ PSRAM của N16R8, không nối ra.
- **GPIO43 phát thông báo khởi động** của ROM lên cổng D3 mỗi lần reset.
- **LED RGB cấp 3,3 V**: nếu cấp 5 V thì ngưỡng mức cao của WS2812B là 3,5 V, cao hơn tín hiệu 3,3 V.
- **Tụ ở chân EN** bắt buộc (10 k + 1 µF) để chip khởi động đúng khi nguồn lên chậm.
- **Tụ tách cho module**: 2 × 10 µF + 100 nF sát chân 2 (3V3).
- **Không đặt tụ lọc trên cổng analog**: các cổng A1–A3 còn dùng làm cổng số tốc độ cao (NeoPixel).
- **Vỏ USB-C** nối GND; chân CC không được nối chung một điện trở.
- **Cổng nguồn 5 V từ C2** cần một loại đầu cắm chịu 3 A. JST PH chỉ 2 A mỗi chân nên chọn XH 2 chân; phải thêm ký hiệu này vào thư viện IRIS.

---

## 7. C2 – nguồn pin 2S (96 × 48)

### 7.1. Sơ đồ khối

```
 USB-C ─► IP2326 (sạc tăng áp 2S, cân bằng cell) ─┬─► B+ ──── cell 1 ── BM ── cell 2 ──── B−
                                                  │                                       │
                                                  │                    HY2120-CB ─► 2 × FET kép 8205A
                                                  ▼                                       │
                                       shunt 10 mΩ ◄─ INA219                            GND
                                                  │
                                 công tắc gạt ─► Q3 AO4435 ─► VBAT ─┬─► XT30 cái
                                                                    └─► TPS563201 ─► 5,45 V ─► XH 2 chân (về C1)
                                                                                    └─► AP2112K ─► +3V3 (INA219)
                                 Cổng I2C: chỉ nối GND, SDA, SCL (chân 5 V để hở)
```

### 7.2. Linh kiện chính

| Ký hiệu | Linh kiện | Giá trị / mã | LCSC | Ghi chú |
|---|---|---|---|---|
| U1 | Sạc | IP2326 (Injoinic), QFN-24 4 × 4 | C2832094 | sạc tăng áp 2S/3S, 500 kHz, có cân bằng cho 2S; đặt 1,0 A (R_ISET 91 k) |
| L1 | Cuộn sạc | 2,2 µH, I_sat ≥ 5 A | – | theo datasheet |
| U2 | Bảo vệ 2 cell | HY2120-CB, SOT-23-6 | C116509 | quá sạc, quá xả, quá dòng |
| Q1, Q2 | FET bảo vệ | 2 × 8205A (N kép, 20 V, 6 A), TSSOP-8, mắc song song | – | phía âm của pin |
| R1 | Shunt | 10 mΩ 1 % 2512 1 W | – | nối Kelvin |
| U3 | Đo dòng, áp | INA219AIDR, SOIC-8 | C138706 | địa chỉ 0x40: A0 = A1 = GND; VS = +3V3 |
| SW1 | Công tắc | công tắc gạt nhỏ | – | chỉ dẫn dòng cực G |
| Q3 | Đóng cắt tải | AO4435 | – | cực G: 100 k lên VBAT_IN, công tắc kéo xuống GND qua 10 k; 100 nF G–S |
| U4 | Buck 5 V | TPS563201DDCR, SOT-23-6 | C116592 | 4,5–17 V, 3 A, 580 kHz; Extended |
| L2 | Cuộn buck | 3,3 µH, I_sat ≥ 4,5 A, có che chắn 6 × 6 | – | |
| C_in | Tụ vào buck | 2 × 10 µF 25 V + 100 nF | – | |
| C_out | Tụ ra buck | 3 × 22 µF 10 V 0805 | – | |
| C_bst | Tụ bootstrap | 100 nF | – | VBST (6) – SW (2) |
| R_fb | Phản hồi | trên 51 k + 10 k, dưới 10 k | – | |
| U5 | Ổn áp 3,3 V | AP2112K-3.3 | – | cho INA219 |
| J1 | USB-C sạc | TYPE-C-31-M-12 | – | CC 5k1 × 2 |
| J2 | Ra động lực | `IRIS:Cong_Nguon_XT30` với chân `Cong_XT30_Cai` | – | |
| J3 | Ra 5 V | XH 2 chân | – | |
| J4 | I2C | `IRIS:Cong_I2C` | – | chân 2 để hở |
| BT1 | Đế pin | đế 2 × 18650 | – | |

### 7.3. Tính toán

- **Buck**: V_out = 0,768 × (1 + 61 k / 10 k) = 5,45 V. Đặt cao hơn 5 V để bù sụt áp của D1 trên C1.
- **Cuộn cảm**: ΔI = V_out × (V_in − V_out) / (V_in × L × f) = 5,45 × 2,95 / (8,4 × 3,3 µH × 580 kHz) = 1,0 A. Đỉnh 3,5 A ở tải 3 A.
- **Nhiệt buck**: hiệu suất khoảng 92 %. Ở 2 A: tổn hao 0,95 W, phần trên IC khoảng 0,6 W, tăng 52 °C (87 °C/W). Ở 3 A: IC khoảng 0,9 W, tăng 80 °C. Kết luận: **2 A liên tục, 3 A chỉ là đỉnh ngắn**.
- **Pin yếu**: chu kỳ làm việc tối đa khoảng 85 %, nên khi pin dưới khoảng 6,5 V thì đầu ra tụt theo (6,0 V → khoảng 5,1 V, còn 4,7 V sau D1). Chấp nhận được; cảnh báo pin yếu bằng INA219.
- **Shunt**: 7,2 A × 10 mΩ = 72 mV, 0,52 W. INA219 đặt dải ±80 mV (PGA /2), bước 10 µV tương ứng 1 mA.
- **Q3**: 7,2² × 0,02 = 1,0 W ở đỉnh; 2 A điển hình: 80 mW. Tụ 100 nF ở cực G làm Q3 mở chậm (cỡ vài mili giây), hạn chế dòng nạp tụ 220 µF của S1.
- **FET bảo vệ**: hai con 8205A song song, điện trở tổng khoảng 20 mΩ. Ngưỡng cắt quá dòng = điện áp phát hiện của HY2120-CB chia cho 20 mΩ; **chưa tra được ngưỡng của bản CB**, phải đọc datasheet để chắc ngưỡng nằm trên 8 A.
- **Dòng sạc**: I = 90000 / R_ISET. Chọn 91 k → 1,0 A thay cho 1,5 A: IC toả khoảng 0,6 W (tăng 36 °C với 60 °C/W) thay vì 1,2 W, và adapter 5 V/2 A nào cũng đủ. Pin 2600 mAh sạc khoảng 3,5 giờ; hẹn giờ đặt 12 h (TIME_SET 120 k).

### 7.4. Cảnh báo

- **IP2326 vẽ theo datasheet V1.2 (hình 5)**: VIN_CHG → L1 2,2 µH → LX (15–17); VIN (13) lọc qua 0,5 Ω + 10 µF; BST (14) 100 nF về LX; VSYS (19, 20) 2 × 22 µF; VOUT (21, 22) 2 × 10 µF, nối VPACK; VBATM (23) về điểm giữa pin qua R_CB 100 Ω (1206) và cầu hàn JP1, có 100 nF lên VOUT và 100 nF xuống GND; VBAT_GND (24) nối GND; NTC 51 k xuống GND; VSET, VIN_OVSET, CON_SEL để hở (8,4 V, quá áp vào 8,75 V, 2 cell); VIN_UVSET 120 k (4,45 V); EN kéo lên VIN qua 10 k; LED qua 330 Ω. D+/D− nối về USB-C: IC xin tối đa 7 V khi pin trên 7,8 V; mọi linh kiện trên VIN_CHG dùng loại 25 V.
- **Đường cân bằng đi vòng qua mạch bảo vệ.** VBATM nối thẳng vào điểm giữa pin trong khi GND của IC nằm sau FET bảo vệ. Khi HY2120 cắt xả mà công tắc vẫn bật, tải có thể tiếp tục rút cell trên qua diode kẹp của chân 23 và R_CB. Dòng này nhỏ (buck đã khoá vì thiếu áp) nhưng phải đo trên bản mẫu; JP1 để cắt đường này nếu cần.
- **Chưa tải được datasheet HY2120-CB và 8205A.** Số chân trong ký hiệu `IRIS:HY2120` (1 OD, 2 OC, 3 CS, 4 VC, 5 VDD, 6 VSS) và `IRIS:FET_Kep_8205` (TSSOP-8: 1, 8 D; 2, 3 S1; 4 G1; 5 G2; 6, 7 S2), cùng mạch quanh U2 (330 Ω + 100 nF ở VDD và VC, 2 k ở CS) ghi theo trí nhớ. **Phải đối chiếu datasheet trước khi layout**, kể cả ngưỡng quá dòng của bản CB (cần trên 8 A với 25 mΩ, tức trên 200 mV).
- SRV05-4 trên cổng I2C của C2 để hở chân VP: nếu nối +3V3 của C2, bus sẽ bị kéo sập qua diode khi C2 tắt mà C1 còn điện.
- **Chân 5 V của cổng I2C trên C2 phải để hở.** Nếu nối vào đường 5 V của C2, nó sẽ đi tắt qua D1 và cầu chì của C1.
- INA219 cấp 3,3 V, không cấp 5 V (ngưỡng mức cao của nó sẽ vượt tín hiệu 3,3 V).
- Shunt đặt giữa pin và cả mạch sạc lẫn tải thì đo được cả dòng sạc (âm) và dòng xả. Dây đo đi từ mép trong của hai pad shunt, thành cặp sát nhau.
- Đường SW của buck và của mạch sạc phải ngắn; tụ vào đặt sát chân VIN–GND.
- Dòng rò khi tắt công tắc: HY2120 khoảng 5 µA cộng dòng chờ của IP2326 (chưa tra). Pin để lâu trong kho cần kiểm tra con số này.
- Yêu cầu vận chuyển và an toàn pin lithium là điểm 10 trong danh sách kiểm chứng của tài liệu hệ thống.

---

## 8. O7 – 16 kênh servo (48 × 64)

```
 XT30 đực ─► Q1 AO4435 chống ngược ─► TPS563201 ─► 5,45 V/3 A ─► 470 µF ─► V+ của 16 cổng servo
 Cổng I2C ─► AP2112K-3.3 ─► PCA9685PW ─► 220 Ω × 16 ─► chân PWM
```

| Ký hiệu | Linh kiện | Giá trị / mã | LCSC | Ghi chú |
|---|---|---|---|---|
| U1 | PWM 16 kênh | PCA9685PW, TSSOP-28 | C2678753 | VDD = +3V3; Extended |
| U2 | Ổn áp | AP2112K-3.3 | – | từ 5 V của cổng I2C |
| U3 | ESD | SRV05-4 | – | trên SDA, SCL |
| U4 | Buck servo | TPS563201DDCR | C116592 | khối giống hệt C2 (`khoi_buck`) |
| Q1 | Chống ngược | AO4435 | – | |
| C13 | Tụ khối servo | 470 µF 16 V | – | cùng 2 × 10 µF |
| JP1 | Địa chỉ | cầu hàn A1 lên +3V3, mặc định hở (R4 10 k kéo xuống) | – | hở: 0x41; hàn: 0x43. A0 = +3V3, A2–A5 = GND |
| R3 | OE | 10 k xuống GND | – | luôn cho phép ra |
| R20–R35 | Nối tiếp | 220 Ω | – | 16 đường PWM |
| J4–J19 | Cổng servo | `IRIS:Cong_Servo` | – | V+ là lưới `+5VP` |

Nối chân PCA9685PW: SDA (27), SCL (26) → bus qua 100 Ω; LED0–LED7 (6–13) và LED8–LED15 (15–22) → 16 cổng servo; OE (23) → R1; EXTCLK (25) → GND; VSS (14) → GND; VDD (28) → +3V3 + 100 nF.

Ghi chú:
- Tài liệu hệ thống ghi 6 V/3 A. Đề xuất hạ xuống **5,45 V**: buck cần chênh áp khoảng 1 V, nên với mục tiêu 6 V thì đầu ra đã tụt khi pin dưới 7 V (phần lớn thời gian xả). Ở 5,45 V, điện áp servo ổn định đến khi pin còn 6,5 V, và khối buck dùng lại nguyên từ C2. Xem Q4 ở mục 9.
- Đầu ra PCA9685 đặt chế độ totem-pole (bit OUTDRV = 1).
- 3 A cho 6 servo của cánh tay robot là mức đỉnh; nếu nhiều servo MG90S kẹt cùng lúc, buck tự giới hạn dòng.

---

## 9. Quyết định thiết kế khác tài liệu hệ thống

Cả 7 đề xuất dưới đây đã được chấp nhận ngày 15/11/2026.

| Mã | Vấn đề | Tài liệu hiện tại | Đề xuất | Lý do |
|---|---|---|---|---|
| Q1 | Nguồn logic của S1 | lấy từ pin | lấy từ 5 V của cổng I2C như S2, S3 | Nếu lấy từ pin, khi tắt C2 mà bus vẫn có điện thì vi điều khiển mất nguồn có thể kéo sập SDA/SCL của cả bus. Ngoài ra AP2112K không chịu được 8,4 V. Lấy từ cổng I2C thì S1 còn báo được “mất nguồn động lực” |
| Q2 | Ổn áp 3,3 V của C1 | chưa ghi | TLV1117LV33 vỏ SOT-223 | AP2112K của bo mẫu quá nóng với ESP32-S3 khi phát WiFi |
| Q3 | Mắt dò line | ITR8307 (theo mô hình cơ khí) | giữ, nhưng thử khoảng cách trên bản mẫu trước khi đặt loạt | Tầm nhạy 1 mm so với khoảng cách lắp 5,9 mm |
| Q4 | Điện áp servo của O7 | 6 V | 5,45 V | Ổn định trên gần hết dải pin, dùng lại khối buck của C2 |
| Q5 | Cổng 5 V giữa C2 và C1 | “2 chân” | JST XH 2 chân, chân 1 GND, chân 2 5 V | Chịu 3 A; không cắm nhầm được với PH và với XH 6 chân |
| Q6 | Chọn nguồn trên C1 | “chống ngược nguồn” | P-FET cho USB + Schottky cho C2, buck của C2 đặt 5,45 V | Adapter USB không mất 0,4 V; USB không đẩy dòng ngược vào C2 |
| Q7 | Mạch sạc C2 | chưa ghi | IP2326 | Rẻ, phổ biến, có sẵn cân bằng 2S; đổi lại datasheet chủ yếu bằng tiếng Trung |

---

## 10. Bo mang cho module đơn giản

Quy tắc chung: đầu cắm theo thư viện IRIS; module cần 3,3 V dùng XC6206P332MR (SOT-23, 200 mA) với 2 tụ 1 µF, riêng I13 dùng AP2112K; mỗi đường tín hiệu đi ra có 1 k nối tiếp nếu là đầu ra của cảm biến.

Mẹo dùng lại nhiều lần: **phân áp 10 k trên, 2 × 10 k nối tiếp dưới** đổi 5 V thành 3,33 V mà chỉ dùng một giá trị điện trở.

| Mã | Khung | Mạch | Giá trị và lưu ý |
|---|---|---|---|
| I1 | S | 2 nút 6 × 6, mỗi nút kéo S1/S2 xuống GND | Mức nghỉ tạo bằng phân áp từ 5 V (10 k trên, 20 k dưới = 3,33 V) nên không phụ thuộc kéo lên nội; 100 nF chống dội |
| I2 | S | Biến trở 10 k giữa +3V3 và GND, con chạy → S1 | 1 k nối tiếp + 100 nF |
| I3 | M | Joystick 2 trục, X → S1, Y → S2 | cấp +3V3; nút nhấn của joystick không nối (cổng chỉ có 2 tín hiệu) |
| I4 | L | PCF8574 + 16 nút ma trận 4 × 4 | VDD = +3V3, A0–A2 = GND (0x20); P0–P3 hàng, P4–P7 cột; không dùng bản PCF8574A |
| I5 | S | LDR GL5528 nối +3V3, 10 k xuống GND, điểm giữa → S1 | sáng thì điện áp cao |
| I6 | S | AHT20 | VDD = +3V3 + 100 nF; không kéo lên trên module |
| I7 | S | Module PIR AM312 | cấp 5 V, đầu ra 3 V → S1 qua 1 k |
| I8 | M | MQ-2 | sợi đốt 5 V (160 mA); điện trở tải chia thành 4k7 trên và 10 k dưới, điểm giữa → S1: tối đa 3,4 V trên lý thuyết |
| I9 | Que | TLC555 dao động khoảng 500 kHz → 10 k → bản cực → 1N4148W → 1 µF ‖ 1 M → S1 | cấp +3V3; f = 1,44 / ((R_A + 2R_B) × C) với R_A = R_B = 1 k, C = 1 nF; bản cực là hai vùng đồng phủ lớp cách điện; chốt giá trị khi thử |
| I10 | M | Lược đồng trần: +3V3 → lược → điểm giữa → 100 k xuống GND | mạ vàng (ENIG) để chống ăn mòn |
| I11 | T | Đế 4 chân cho HC-SR04 | Trig ← S1; Echo 5 V qua phân áp 10 k / 20 k → S2; đầu cắm đứng ở mặt sau (`Cong_PH_4P_Dung`) |
| I12 | S | Mắt thu hồng ngoại 38 kHz (VS1838B) | **cấp +3V3**, không cấp 5 V (đầu ra có kéo lên nội về nguồn); 100 Ω + 10 µF lọc nguồn |
| I13 | L | Đế 8 chân cho module RC522 | AP2112K-3.3; RST nối +3V3 qua 10 k; IRQ để hở |
| I14 | S | APDS-9960 | VDD (8) và LED_A (5) = +3V3; LDR (3) nối LED_K (4); 100 nF + 10 µF; INT (2) để hở |
| O1 | S | 2 LED, mỗi LED một 2N7002 kéo xuống, cấp từ 5 V | đỏ: (5 − 2) / 330 Ω = 9 mA; xanh: (5 − 3) / 220 Ω = 9 mA; cực G 100 k xuống GND |
| O2 | T | 8 × WS2812B + 74AHCT1G125 | bộ đệm cấp 5 V nâng tín hiệu 3,3 V lên 5 V; mỗi LED 100 nF; 2 × 10 µF ở đầu vào; DOUT ra điểm hàn |
| O3 | M | Đế 4 chân cho module OLED 0,96" | cấp +3V3 để điện trở kéo lên trên module không lên 5 V; **thứ tự chân GND/VCC của module khác nhau giữa các nhà bán** |
| O4 | M | S1 → 470 Ω → PC817 → SS8050 → relay 5 V | diode 1N4148W ngược song song cuộn dây; LED báo; cầu đấu 3 chân; nhãn “tối đa 24 V” |
| O5 | S | AO3400A kéo xuống, tải cấp từ 5 V của cổng | cực G 100 Ω + 10 k kéo xuống; SS54 song song tải; đầu ra XH 2 chân |

Sơ đồ của cả 19 bo sinh từ một kịch bản: [bo-mang/ve_so_do.py](bo-mang/ve_so_do.py), mỗi bo một thư mục `bo-mang/<mã>/`. Điểm khác bảng trên hoặc còn phải đối chiếu:

- I3, I7, I11, I13, O3 là đế cắm cho module mua sẵn: thứ tự chân của đế phải đối chiếu với module thực tế.
- I4: ma trận không có diode, nhấn 3 phím cùng lúc có thể ra phím ma.
- I6: AHT20 lấy số chân từ datasheet ASAIR V1.0 (1 NC, 2 VDD, 3 SCL, 4 SDA, 5 GND, 6 NC); chưa có chân linh kiện.
- I9: thêm 1 k nối tiếp trước S1; hai bản cực vẽ tạm là điểm hàn TP1, TP2.
- I12: chân linh kiện đang là của TSOP382 (cùng thứ tự chân với VS1838B).
- O4: tiếp điểm relay đặt tên theo số chân (K_3, K_4); phải đối chiếu datasheet SRD-05VDC để in nhãn NO / NC.
- O5: đầu ra dùng `Conn_01x02` với chân linh kiện XH 2 chân: chân 1 OUT−, chân 2 +5V.

### 10.1. PCB của bo mang

PCB của cả 19 bo dựng bằng [bo-mang/ve_pcb.py](bo-mang/ve_pcb.py) (chạy bằng Python của KiCad), kết quả là `bo-mang/<mã>/<mã>.kicad_pcb`. Chưa xuất Gerber.

- Linh kiện chính (đầu cắm, nút, cảm biến) đặt theo toạ độ trong [bo-mang/bo_tri.py](bo-mang/bo_tri.py), trùng mô hình cơ khí; linh kiện nhỏ do kịch bản tự xếp quanh đó.
- Đi dây 2 lớp trên lưới 0,25 mm, chỉ ngang và dọc: dây 0,4 mm, khe hở 0,2 mm, via 0,6 / 0,3 mm. Mặt dưới đổ đồng GND.
- Không đổ đồng GND dưới bản cực của I9 và dưới vùng anten của module RC522 trên I13.
- I9: hai bản cực là hai mảng đồng 9,5 × 55 mm phủ sơn hàn. I10: lược đồng trần, răng 0,6 mm, khe 0,65 mm.
- Tên linh kiện trên lớp in lụa đã ẩn, trừ đầu cắm, relay và biến trở: bo quá nhỏ.
- DRC: cả 19 bo không còn đường hở. Lỗi còn lại, chấp nhận có lý do: I2 (courtyard của biến trở RK09K trùm lên 2 lỗ gá; thân thật cách lỗ 1,5 mm), I9 (courtyard đầu cắm chạm vành lỗ gá 0,2 mm), I10 (18 cảnh báo đầu dây lơ lửng: là các răng lược). Còn vài cảnh báo in lụa.
- I3 và I13 dùng module mua sẵn rộng hơn khoảng giữa 4 vít (joystick 26 × 34, RC522 40 × 60): module phải đứng trên hàng rào cái, cao hơn đầu vít.
- O3, I7, I11: module (OLED, AM312, HC-SR04) cắm trên hàng rào cái cao 8,5 mm.
- Nút nhấn I1, I4 chọn loại 6 × 6 cao 7 mm để đầu nút nhô khỏi nắp.

Ghi chú cho O4: optocoupler dùng chung nguồn và GND với phần điều khiển nên không phải cách ly an toàn, chỉ giảm nhiễu. Dòng LED của PC817: (3,3 − 1,2) / (220 + 470) = 3 mA.

---

## 11. Lỗi nguyên lý thường gặp – danh sách kiểm trước ERC

- [ ] Mỗi chân nguồn của IC có tụ 100 nF riêng; mỗi ổn áp có tụ vào và ra.
- [ ] Không có điện trở kéo lên I2C ở bất kỳ module nào ngoài C1; không có đường nào kéo lên 5 V.
- [ ] Mọi đầu ra 5 V (Echo của HC-SR04, MQ-2) đi qua phân áp trước khi về cổng.
- [ ] Thứ tự chân đầu cắm lấy từ ký hiệu `IRIS:Cong_*`, không vẽ tay: chân 1 GND, chân 2 5 V.
- [ ] Đầu vào không được để nổi lúc reset: STBY của TB6612, cực G của mọi MOSFET, CS của IMU, EN của ESP32.
- [ ] PA14-BOOT0 của STM32G030 có kéo xuống; có đủ 5 điểm nạp SWD.
- [ ] GPIO0, 3, 45, 46 của ESP32-S3 không nối tải.
- [ ] Hai chân CC của USB-C có hai điện trở 5k1 riêng.
- [ ] Chân 5 V của cổng I2C trên C2 để hở.
- [ ] Mỗi lưới nguồn vào qua đầu cắm có `PWR_FLAG`.
- [ ] Tụ có điện áp định mức tối thiểu gấp 1,5 lần điện áp làm việc (đường VBAT dùng tụ 25 V).
- [ ] Trường `MPN` và `LCSC` khớp với `Value` sau mỗi lần đổi giá trị.

## 12. Việc tiếp theo

1. ~~Xác nhận 7 quyết định ở mục 9~~ (xong). Sơ đồ S1 đã vẽ: [S1-driver-dong-co/S1.kicad_sch](S1-driver-dong-co/S1.kicad_sch), ERC không lỗi.
2. Đối chiếu datasheet HY2120-CB và 8205A với sơ đồ C2 (số chân, mạch quanh IC, ngưỡng quá dòng). IP2326 đã vẽ theo datasheet V1.2.
3. ~~Thêm ký hiệu cổng nguồn 5 V (XH 2 chân) vào thư viện IRIS~~ (xong: `Cong_Nguon_5V`).
4. Sơ đồ đã vẽ đủ 25 bo: S1, S2, S3, C1, C2, O7 và 19 bo mang trong `bo-mang/` (hình ở `docs/hinh-mach/` và `docs/hinh-mach/bo-mang/`).
5. PCB 19 bo mang đã dựng (mục 10.1); vỏ in 3D ở `mechanical/src/vo/` (xem docs/THIET-KE-CO-KHI.md).
6. Việc còn lại: điền mã LCSC, mở từng PCB trong KiCad để soát và chỉnh tay, xuất Gerber; layout PCB cho C1, C2, S1, S2, S3, O7. Riêng C1 đã thu từ 96 × 64 xuống 64 × 48 (bố trí cổng mới ở mục 3.2 của docs/THIET-KE-CO-KHI.md); khi đi dây phải kiểm linh kiện có xếp vừa không, nhiều khả năng cần đặt cả hai mặt.
