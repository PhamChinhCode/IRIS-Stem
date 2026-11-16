# Mô hình cơ khí IRIS-Stem

Mô hình CAD tham số viết bằng Python (build123d qua `cadgen`). Tài liệu thiết kế: [docs/THIET-KE-CO-KHI.md](../../docs/THIET-KE-CO-KHI.md).

## Dựng mô hình

Cài một lần: `python -m pip install "cadgen[snapshot]==0.5.1"`.

Chạy từ thư mục `mechanical/src`, trong Git Bash:

```bash
export PYTHONPATH="$PWD" PYTHONUTF8=1
```

```bash
python du_an/xe_do_line.py
```

Chạy một cụm dự án sẽ tự dựng các chi tiết con còn cũ. Dựng lại toàn bộ:

```bash
for f in chi_tiet/*.py du_an/*.py mach/*.py; do python "$f"; done
```

Hai lưu ý trên Windows:

- `PYTHONUTF8=1` là bắt buộc vì mã có chú thích tiếng Việt. Nếu đã lỡ chạy khi chưa đặt biến này, phải tắt các tiến trình `python -m cadgen.daemon` rồi chạy lại.
- Mỗi tệp chỉ chứa một mô hình. Hai mô hình trong một tệp làm `cadgen` 0.5.1 lỗi khi mã nguồn và Python nằm trên hai ổ đĩa khác nhau.

Kết quả: `../STEP/` (xem và lắp ráp), `../STL/` (in 3D). Ảnh xem nhanh: `cadgen step snapshot ../STEP/du_an/xe_do_line.step ../tmp/xe.png`.

## Danh mục

| Thư mục | Nội dung |
|---|---|
| `lib/chuan.py` | Chuẩn lưới 8 mm, hàm dựng tấm lưới, lớp `Tam` kiểm tra lỗ gá trùng lưới |
| `lib/kt.py` | Kích thước và toạ độ lỗ gá dùng chung giữa chi tiết và cụm lắp |
| `lib/mach.py` | Khối bao của mọi bo mạch: kích thước, lỗ gá, đầu cắm |
| `lib/mua_san.py` | Linh kiện mua sẵn: servo, N20, JGA25, bánh, mắt trâu, quạt, bơm |
| `lib/xe.py` | Khung xe K2 dùng chung cho xe dò line và xe cân bằng |
| `chi_tiet/` | 28 chi tiết in 3D / cắt laser, mỗi tệp một chi tiết → `STEP/chi_tiet/`, `STL/` |
| `lib/vo.py`, `vo/` | Vỏ bo mang: 19 đế + 17 nắp, mỗi tệp một chi tiết (sinh bằng `tao_tep_vo.py`) → `STEP/vo/`, `STL/vo/` |
| `mach/vo_module.py` | Mọi bo mang kèm vỏ bày trên một mặt phẳng → `STEP/mach/vo_module.step` |
| `mach/bo_module.py` | Toàn bộ bo mạch bày trên một mặt phẳng → `STEP/mach/bo_module.step` |
| `du_an/` | 7 cụm lắp dự án → `STEP/du_an/` |

| Cụm dự án | Dự án |
|---|---|
| `du_an/ban_thuc_hanh.py` | 1–4, 17, 19, 20 |
| `du_an/nha_thong_minh.py` | 5–10 |
| `du_an/xe_do_line.py` | 11–16 |
| `du_an/vuon_thong_minh.py` | 18 |
| `du_an/xe_can_bang.py` | 21–22 |
| `du_an/canh_tay_robot.py` | 23 |
| `du_an/bang_tai.py` | 24 |

Đổi vị trí một module: sửa toạ độ (u, v) trong tệp cụm dự án. Nếu lỗ gá không trùng lưới, lệnh dựng dừng và báo lỗ nào lệch.

## Đưa mô hình vào bản đồ kit

Sau khi dựng lại các cụm dự án, xuất mô hình từng module rồi cập nhật trang:

```bash
python xuat_module.py
```

```bash
cd ../../stem-kit-map && python update_3d.py
```

Chi tiết, kể cả cách đưa tệp STEP/STL tự chỉnh sửa vào trang: [stem-kit-map/HUONG-DAN.md](../../stem-kit-map/HUONG-DAN.md).
