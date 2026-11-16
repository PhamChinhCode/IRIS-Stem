# Bản đồ kit STEM – hướng dẫn cập nhật mô hình 3D

Trang [index.html](index.html) hiện 25 dự án và 26 module của bộ kit: sơ đồ nối, mô hình 3D, sơ đồ nguyên lý và mạch in. Mở trang bằng cách bấm đúp `index.html`; không cần máy chủ, nhưng máy phải có mạng để tải thư viện vẽ 3D (three.js) và phông chữ.

## Trong thư mục này có gì

| Mục | Nội dung | Ai sửa |
|---|---|---|
| `index.html` | Trang web. Dữ liệu dự án và module nằm trong phần `<script>` của tệp | sửa tay khi đổi nội dung |
| `nguon-3d/` | Tệp 3D bạn tự chỉnh sửa rồi thả vào (`.step`, `.stp`, `.stl`) | **bạn** |
| `update_3d.py` | Chuyển tệp 3D thành dữ liệu cho trang, xuất hình sơ đồ và PCB từ KiCad, chép tài liệu PDF | chạy, không cần sửa |
| `mo-hinh/` | Dữ liệu 3D của trang, mỗi mô hình một tệp `.js` | máy sinh, đừng sửa tay |
| `hinh/` | Hình sơ đồ nguyên lý và mạch in của từng module | máy xuất từ KiCad, đừng sửa tay |
| `tai-lieu/` | Tài liệu PDF của từng module | máy chép, đừng sửa tay |

Trình duyệt không cho trang mở thẳng tệp STEP hay STL khi chạy từ ổ đĩa, nên mọi tệp 3D phải qua `update_3d.py` một lần.

## Cách làm thường ngày: lưu STEP ngay trong thư mục thiết kế

`update_3d.py` tự dò hai chỗ sau, nên bạn không phải chép tệp đi đâu cả:

| Loại | Lưu ở đâu | Tên tệp | Ví dụ |
|---|---|---|---|
| Module (mạch + vỏ đã ghép) | bất kỳ đâu trong `hardware/` | đúng mã module | `hardware/C1-bo-chu/C1.step`, `hardware/bo-mang/I1/I1.step` |
| Mô hình lắp ráp của một dự án | bất kỳ đâu trong `projects/` | `Project` + số dự án | `projects/cap-3-robot/Project11.step` |

Sau khi lưu hoặc sửa tệp, chạy một lần trong thư mục `stem-kit-map`:

```bash
python update_3d.py
```

rồi tải lại trang. Lệnh in ra tệp nguồn đã dùng cho từng mô hình, ví dụ `C1: ... (từ hardware/C1-bo-chu/C1.step)`.

Lưu ý:

- Tên tệp không phân biệt hoa thường; `Project11`, `project_11`, `Project-11` đều được. Đuôi `.step`, `.stp` hoặc `.stl`.
- Tệp phải là **cả cụm đã ghép trong một tệp**. Trang không tự ghép mạch với vỏ.
- Dự án có `Project<số>.step` thì hiện mô hình đó; dự án chưa có thì vẫn hiện mô hình chung của nhóm (bảng ở bước 2 bên dưới).
- Tệp của bạn thắng mô hình dựng từ mã trong `mechanical/STEP/`. Xoá tệp rồi chạy lại lệnh thì trang quay về mô hình dựng từ mã.
- Đừng để hai tệp cùng mã ở hai nơi trong `hardware/` (ví dụ `C1.step` và `backup/C1.step`): lệnh chỉ lấy một tệp và không báo trùng.
- Thư mục `nguon-3d/` vẫn dùng được cho tệp thả tay và thắng mọi nguồn khác; phần dưới đây mô tả cách đó.

## Đưa tệp 3D đã chỉnh sửa vào trang

### Bước 1. Xuất tệp từ phần mềm CAD

- Định dạng: **STEP** (`.step`, `.stp`) hoặc **STL**. Nên dùng STEP: giữ được màu từng khối. STL không có màu, cả mô hình hiện một màu xanh.
- Đơn vị milimét.
- Trục Z hướng lên, mặt đáy mô hình nằm trên mặt phẳng XY. Trang tự căn giữa và tự thu phóng, nên vị trí gốc toạ độ không quan trọng.
- Với cụm lắp nhiều chi tiết: xuất **một tệp STEP** chứa cả cụm.

### Bước 2. Đặt tên tệp cho đúng

Trang nhận ra mô hình qua **tên tệp** (không tính đuôi). Thả tệp vào `nguon-3d/` với một trong các tên sau:

| Muốn thay mô hình của | Tên tệp | Ví dụ |
|---|---|---|
| Một module (tab Module) | mã module | `I1.step`, `O3.step`, `C1.step` |
| Một nhóm dự án (tab Dự án) | tên nhóm, xem bảng dưới | `xe_do_line.step` |
| Riêng một dự án | `du_an_` + số dự án | `du_an_15.step` |

Tên nhóm dự án:

| Tên tệp | Dự án dùng mô hình này |
|---|---|
| `ban_thuc_hanh` | 1–4, 17, 19, 20 |
| `nha_thong_minh` | 5–10 |
| `xe_do_line` | 11–16 |
| `vuon_thong_minh` | 18 |
| `xe_can_bang` | 21, 22 |
| `canh_tay_robot` | 23 |
| `bang_tai` | 24 |

Quy tắc ưu tiên:

- Thứ tự ưu tiên: `nguon-3d/` → `projects/` và `hardware/` → mô hình dựng từ mã CAD trong `mechanical/STEP/`.
- Mô hình `du_an_<số>` thắng mô hình của nhóm. Ví dụ có `du_an_15.step` thì dự án 15 hiện mô hình đó, các dự án 11–14 và 16 vẫn hiện `xe_do_line`.
- Module chưa có tệp 3D nào thì tab Module không hiện khung 3D cho module đó.

### Bước 3. Chạy lệnh cập nhật

Mở Git Bash (hoặc PowerShell) trong thư mục `stem-kit-map`:

```bash
python update_3d.py
```

Lệnh chỉ chuyển các tệp mới hoặc vừa sửa và in ra từng mô hình đã chuyển, ví dụ:

```
xe_do_line: 36925 đỉnh, 36616 tam giác, 0.59 MB  (từ nguon-3d/xe_do_line.step)
33 mô hình trong mo-hinh/; 44 hình trong hinh/ (0 vừa xuất từ KiCad); 2 tài liệu PDF trong tai-lieu/ (0 mới)
```

Dòng `(từ nguon-3d/...)` cho biết trang đang dùng tệp của bạn chứ không phải tệp dựng từ mã.

Các cách chạy khác:

```bash
python update_3d.py --tat-ca
```

chuyển lại toàn bộ, dùng khi nghi dữ liệu cũ;

```bash
python update_3d.py xe_do_line I1
```

chỉ chuyển các mô hình nêu tên.

### Bước 4. Xem kết quả

Tải lại trang (`Ctrl + F5`). Dòng «Kích thước bao» ở tab Module lấy từ chính tệp 3D, nên là cách nhanh để biết trang đã nhận tệp mới chưa.

### Quay về mô hình gốc

Xoá tệp của bạn khỏi `nguon-3d/` rồi chạy lại `python update_3d.py`. Trang trở về mô hình dựng từ mã CAD; nếu không còn nguồn nào, mô hình được gỡ khỏi trang.

## Khi mô hình gốc trong mã CAD thay đổi

Nếu sửa mã trong `mechanical/src/` (không phải sửa tay tệp STEP), dựng lại rồi cập nhật trang:

```bash
cd ../mechanical/src
```

```bash
export PYTHONPATH="$PWD" PYTHONUTF8=1
```

```bash
for f in du_an/*.py; do python "$f"; done
```

```bash
python xuat_module.py
```

```bash
cd ../../stem-kit-map && python update_3d.py
```

`xuat_module.py` xuất mô hình từng module (bo kèm đế và nắp) ra `mechanical/STEP/module/`.

Lưu ý: tệp STEP trong `mechanical/STEP/` bị **ghi đè** mỗi lần dựng lại từ mã. Tệp bạn sửa tay luôn phải để trong `nguon-3d/`, đừng sửa thẳng trong `mechanical/STEP/`.

## Hình sơ đồ nguyên lý và mạch in

Hình lấy thẳng từ tệp KiCad trong thư mục của module, bạn không phải xuất tay:

| Hình trên trang | Tệp nguồn | Ví dụ |
|---|---|---|
| Sơ đồ nguyên lý | `<mã>.kicad_sch` | `hardware/bo-mang/I1/I1.kicad_sch` |
| Mạch in, mặt trên | `<mã>.kicad_pcb` | `hardware/bo-mang/I1/I1.kicad_pcb` |

Sửa mạch trong KiCad, **lưu lại**, rồi chạy `python update_3d.py`. Lệnh gọi `kicad-cli` xuất lại những hình có tệp KiCad mới hơn và in ra dòng `hình I1-so-do: từ hardware/bo-mang/I1/I1.kicad_sch`. Kết quả nằm ở `hinh/<mã>-so-do.svg` và `hinh/<mã>-pcb.svg`. Module chưa có tệp KiCad nào thì trang tự ẩn ô đó.

- Muốn xuất lại toàn bộ hình: `python update_3d.py --tat-ca` (chuyển lại cả mô hình 3D nên chậm hơn).
- Lệnh cần KiCad cài ở `C:\Program Files\KiCad\10.0`. Cài chỗ khác thì đặt biến môi trường `KICAD_DIR` trỏ tới thư mục đó. Không thấy KiCad thì lệnh in cảnh báo và giữ nguyên hình cũ.
- Thư mục `docs/hinh-mach/` không còn được trang dùng tới.

## Tài liệu PDF của module

Tài liệu của mỗi module lấy từ chính thư mục KiCad của module đó. Tệp phải đặt tên đúng **mã module**, ví dụ:

| Module | Tệp tài liệu |
|---|---|
| I1 | `hardware/bo-mang/I1/I1.pdf` |
| C1 | `hardware/C1-bo-chu/C1.pdf` |

Trong KiCad: mở sơ đồ, chọn `File → Plot`, định dạng PDF, lưu vào thư mục của module (tên mặc định đã là `<mã>.pdf`). Sau đó chạy `python update_3d.py`: lệnh chép tệp sang `tai-lieu/<mã>.pdf` và tab Module hiện dòng «Tài liệu» với liên kết mở PDF. Tệp tên khác mã module (như `I1-Edge_Cuts.pdf`) bị bỏ qua. Xoá tệp PDF nguồn rồi chạy lại lệnh thì liên kết cũng biến mất.

## Sự cố thường gặp

| Hiện tượng | Nguyên nhân và cách xử lý |
|---|---|
| Lệnh báo `No module named 'build123d'` | Chưa cài thư viện đọc STEP: `python -m pip install "cadgen[snapshot]==0.5.1"`. Tệp STL thì không cần thư viện này |
| Lệnh báo `LỖI <tên>: tệp không có khối đặc nào` | Tệp STEP chỉ chứa mặt hoặc đường. Xuất lại dạng khối đặc (solid) |
| Trang vẫn hiện mô hình cũ | Tải lại bằng `Ctrl + F5`; kiểm tra tên tệp đúng bảng ở bước 2; xem dòng in ra có `(từ nguon-3d/...)` không |
| Mô hình nằm nghiêng hoặc lộn ngược | Tệp xuất với trục Y hướng lên. Xuất lại với Z hướng lên |
| Mô hình một màu | Tệp là STL, hoặc STEP xuất không kèm màu. Bật tuỳ chọn xuất màu trong phần mềm CAD |
| Khung 3D hiện «Sơ đồ khối» thay vì mô hình | Chưa có tệp cho mô hình đó trong `mo-hinh/`, hoặc đang chọn nút «Sơ đồ khối» |
| Trang nặng, xoay giật | Mô hình quá chi tiết. Giản lược trước khi xuất (bỏ ren, bo góc nhỏ); nên giữ dưới 150 000 tam giác mỗi mô hình |

## Đưa trang lên mạng

Chép cả thư mục `stem-kit-map` (trừ `nguon-3d/` và `update_3d.py` nếu muốn gọn) lên máy chủ tĩnh bất kỳ. Trang chỉ cần `index.html`, `mo-hinh/`, `hinh/` và `tai-lieu/`.
