# Thư viện KiCad dùng chung

Mọi bo của kit lấy đầu cắm và khung bo từ đây, để thứ tự chân và vị trí lỗ gá không thể lệch giữa các bo.

| Tệp | Nội dung |
|---|---|
| `IRIS.kicad_sym` | 7 ký hiệu cổng + 10 ký hiệu khung bo + mắt phản xạ `Mat_ITR8307` + 4 IC dạng hộp (`IP2326`, `HY2120`, `FET_Kep_8205`, `AHT20`) |
| `IRIS.pretty/` | 8 chân đầu cắm + 10 khung bo |
| `tao_thu_vien.py` | Bộ sinh ra hai mục trên |
| `sch.py`, `khoi_chung.py` | Bộ dựng sơ đồ nguyên lý bằng mã và các khối dùng chung (ổn áp, cổng I2C, lõi STM32G030) |
| `kt_sch.py` | Sinh lại sơ đồ một bo, chạy ERC, liệt kê lưới, xuất PDF/SVG vào `docs/hinh-mach/` |

Hai mục đầu là tệp sinh tự động, đừng sửa trong KiCad. Muốn đổi thì sửa bảng trong `tao_thu_vien.py` rồi chạy lại (cần KiCad 10):

```bash
PYTHONUTF8=1 python tao_thu_vien.py
```

Mỗi lần chạy lại, KiCad cấp mã `uuid` mới cho mọi đối tượng, nên `git diff` sẽ có nhiều dòng đổi dù hình học không đổi.

## Cổng

Thứ tự chân theo [THIET-KE-HE-THONG.md](../../docs/THIET-KE-HE-THONG.md) mục 3. Chân 1 luôn là GND, chân 2 luôn là 5 V (trừ cổng động cơ).

| Ký hiệu | Chân 1 → n | Chân linh kiện mặc định | Linh kiện | Màu |
|---|---|---|---|---|
| `Cong_DA` | GND, 5V, S1, S2 | `Cong_PH_4P_Ngang` | JST S4B-PH-K | trắng |
| `Cong_I2C` | GND, 5V, SDA, SCL | `Cong_PH_4P_Ngang` | JST S4B-PH-K | xanh |
| `Cong_SPI` | GND, 5V, SCK, MOSI, MISO, CS | `Cong_PH_6P_Ngang` | JST S6B-PH-K | vàng |
| `Cong_Servo` | GND, 5V, PWM | `Cong_Servo_1x03` | hàng rào 1×3, 2,54 mm | đen |
| `Cong_DongCo` | M+, M-, GND, 3V3, EncA, EncB | `Cong_XH_6P_Ngang` | JST S6B-XH-A | đỏ |
| `Cong_Nguon_XT30` | GND, VBAT | `Cong_XT30_Duc` | XT30UPB-M | – |
| `Cong_Nguon_5V` | GND, 5V | `Cong_XH_2P_Ngang` | JST S2B-XH-A | – |

- `Cong_PH_4P_Dung` (JST B4B-PH-K) là bản cắm đứng, dùng cho I11 có đầu cắm ở mặt sau.
- `Cong_XT30_Cai` (XT30UPB-F) dùng ở bên cấp nguồn (C2); bên nhận (S1) dùng bản đực.
- `IP2326` lấy số chân từ datasheet V1.2; `AHT20` từ datasheet ASAIR V1.0 (chưa có chân linh kiện). `HY2120` và `FET_Kep_8205` ghi số chân theo trí nhớ, **chưa đối chiếu datasheet**.
- `Mat_ITR8307` là mắt phản xạ ITR8307 với chân kiểu *passive*: ký hiệu gốc của KiCad khai cực E là *open emitter*, ERC báo lỗi khi nối xuống GND.
- Mọi chân cổng có kiểu *passive*, vì cùng một ký hiệu dùng cho cả bo chủ lẫn module. Lưới nguồn vì thế cần `PWR_FLAG` để ERC không báo.
- Chân đầu cắm sao nguyên từ thư viện gốc của KiCad 10 (chỉ đổi tên), nên mô hình 3D vẫn trỏ về `${KICAD10_3DMODEL_DIR}`.

## Khung bo

Mỗi cỡ bo là một ký hiệu `Khung_<cỡ>_<rộng>x<cao>` đi kèm chân linh kiện cùng tên. Chân này chứa đường cắt bo (`Edge.Cuts`, góc bo tròn R2, thu vào 0,25 mm mỗi cạnh so với kích thước danh nghĩa trong tên) và các lỗ gá Ø3,2 không mạ. Đặt một ký hiệu khung vào sơ đồ nguyên lý là bo có sẵn đường bao và lỗ gá đúng lưới 8 mm, và chúng không bị xoá khi cập nhật bo từ sơ đồ.

| Khung | Lỗ gá (mm, từ góc dưới trái) | Module |
|---|---|---|
| `Khung_S_24x32` | (4, 12) (20, 12) (4, 28) (20, 28) | I1 I2 I5 I6 I7 I12 I14 O1 O5 |
| `Khung_M_32x48` | (4, 4) (28, 4) (4, 44) (28, 44) | I3 I8 I10 O3 O4 |
| `Khung_L_48x64` | (4, 4) (44, 4) (4, 60) (44, 60) | I4 I13 O7 |
| `Khung_T_64x24` | (4, 4) (60, 4) (4, 20) (60, 20) | I11 O2 |
| `Khung_S3_32x32` | (4, 4) (28, 4) (4, 28) (28, 28) | S3 |
| `Khung_S1_48x48` | (4, 4) (44, 4) (4, 44) (44, 44) | S1 |
| `Khung_S2_80x24` | (4, 4) (76, 4) (4, 20) (76, 20) | S2 |
| `Khung_C2_96x48` | (4, 4) (92, 4) (4, 44) (92, 44) | C2 |
| `Khung_C1_64x48` | (4, 4) (60, 4) (4, 44) (60, 44) | C1 |
| `Khung_Que_24x96` | (4, 92) (20, 92) | I9 |

Quy ước toạ độ:

- Điểm neo của khung là **góc dưới bên trái của bo danh nghĩa** (cách góc đường cắt 0,25 mm), trùng gốc toạ độ trong [THIET-KE-CO-KHI.md](../../docs/THIET-KE-CO-KHI.md) mục 3. Trục Y của KiCad hướng xuống, nên điểm (x, y) trong tài liệu nằm ở (x, −y) so với điểm neo. Nên đặt gốc lưới của KiCad vào điểm neo.
- Quanh mỗi lỗ có vòng cấm bán kính 2,75 mm trên `F.CrtYd` và `B.CrtYd` (trụ đỡ và đầu vít Ø5,5). Thân linh kiện giữ cách tâm lỗ 3 mm.

Cỡ S là ngoại lệ về lỗ gá: hai lỗ phía đầu cắm nằm cách mép dưới 12 mm thay vì 4 mm. Bo rộng 24 mm chỉ còn 10 mm giữa hai trụ đỡ, không đủ cho đầu PH 4 chân rộng 9,9 mm cùng lề hàn.

Vị trí đầu cắm nằm ngang ở mép bo: hàng chân cách mép thật **6,5 mm**, tức 6,75 mm tính từ điểm neo, không xoay khi miệng quay về cạnh dưới. Với đầu 4 chân ở giữa cạnh dưới, chân 1 đặt tại (rộng/2 − 3; 6,75); với đầu 6 chân là (rộng/2 − 5; 6,75).

## Dùng trong một dự án KiCad

Tạo hai tệp sau trong thư mục dự án (ví dụ `hardware/S1-driver-dong-co/`), rồi mở lại dự án.

`sym-lib-table`:

```
(sym_lib_table
  (lib (name "IRIS") (type "KiCad") (uri "${KIPRJMOD}/../common/IRIS.kicad_sym") (options "") (descr "Thư viện chung IRIS-Stem"))
)
```

`fp-lib-table`:

```
(fp_lib_table
  (lib (name "IRIS") (type "KiCad") (uri "${KIPRJMOD}/../common/IRIS.pretty") (options "") (descr "Thư viện chung IRIS-Stem"))
)
```

## Đã kiểm tra

- KiCad 10.0.5 đọc và ghi lại được toàn bộ ký hiệu và chân linh kiện.
- Nạp từng khung bằng `pcbnew`: đường cắt đúng bằng kích thước danh nghĩa trừ 0,5 mm, mọi lỗ gá nằm trên lưới 8 mm.
- Bo thử gồm `Khung_S_24x32` và `Cong_PH_4P_Ngang` ở giữa cạnh dưới: dựng được hình 3D, DRC không báo lỗi nào.

Chưa kiểm tra: chưa bo nào được đặt làm; kích thước chân đầu cắm là của thư viện KiCad, chưa đối chiếu với linh kiện sẽ mua.
