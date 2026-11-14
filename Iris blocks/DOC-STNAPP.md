# stnapp

Bản Việt hoá của [MicroBlocks](https://microblocks.fun) — ngôn ngữ lập trình khối cho vi điều khiển 32-bit, dùng để dạy lập trình ESP32 và Raspberry Pi Pico.

- **Nguồn gốc:** https://codeberg.org/MicroBlocks/smallvm
- **Giấy phép:** Mozilla Public License 2.0 (giữ nguyên)
- **Tác giả gốc:** John Maloney, Bernat Romagosa, Jens Mönig

Đây là bản fork. Mọi tệp mã nguồn vẫn giữ nguyên tiêu đề bản quyền và giấy phép MPL-2.0 của tác giả gốc, theo yêu cầu của giấy phép.

## Những gì đã thay đổi so với bản gốc

### 1. Nhập thư viện từ URL GitHub

Bản gốc có sẵn tính năng nhập thư viện từ URL, nhưng **không dùng được với GitHub**:

- Bản desktop native dùng socket TCP thuần ở cổng 80, không có TLS. GitHub bắt buộc HTTPS nên trả về 301 và IDE báo lỗi.
- Link GitHub dạng `blob` trả về trang web HTML của repo, không phải nội dung tệp.

Cùng một lỗ hổng tồn tại ở **cả hai bản IDE**, nên đã sửa ở cả hai nơi.

### Bản JavaScript — [`engine/mb-editor.js`](chromeApp/webapp/engine/mb-editor.js)

Bản này dùng `fetch()` nên HTTPS vốn đã chạy, chỉ thiếu phần chuyển URL GitHub:

- Thêm `static githubFileURL(fullUrl)` đặt ngay cạnh `codebergFileURL` có sẵn, cùng kiểu viết.
- `importLibraryFromUrl` thử lần lượt Codeberg → GitHub → URL nguyên bản.
- `promptLibraryURL` kiểm tra đuôi tệp sau khi bỏ query string/fragment.

### Bản GP (dùng cho Electron/wasm) — [`ide/MicroBlocksScripter.gp`](ide/MicroBlocksScripter.gp)

- Thêm hàm `githubFileURL` (viết theo đúng khuôn mẫu hàm `codebergFileURL` có sẵn): tự chuyển
  `github.com/CHU/REPO/blob/NHANH/DUONG-DAN` thành `raw.githubusercontent.com/CHU/REPO/NHANH/DUONG-DAN`.
  Có bỏ query string và fragment, nên link kèm `?plain=1` hoặc `#L3` vẫn nhận.
- `importLibraryFromUrl` nay giữ nguyên scheme của URL và gọi `httpGetInBrowser` khi chạy trên
  nền tảng Browser (tức bản Electron và bản web), nhờ đó dùng được TLS của trình duyệt.
  Timeout nâng lên 10 giây vì mặc định 1 giây quá ngắn cho GitHub.
- Bản native không có TLS nên vẫn đi đường cũ qua HTTP.

Trong [`ide/MicroBlocksLibraryWidgets.gp`](ide/MicroBlocksLibraryWidgets.gp): ô nhập URL gợi ý
`https://` thay vì `http://`, và phần kiểm tra đuôi `.ubl`/`.ubp` bỏ qua query string/fragment.

**Cách dùng:** trong IDE chọn *Add Library* → biểu tượng đám mây → dán link GitHub. Ví dụ đã kiểm thử:

```
https://github.com/AntonsMindstorms/uRemote/blob/main/library/uremote.ubl
```

Dán link `blob` bình thường cũng được, không cần tự đổi sang `raw`.

### 2. Tiếng Việt

- `translations/vi.po` đã dịch đủ 100% (bản gốc còn 40 chuỗi trống).
- Tiếng Việt là ngôn ngữ mặc định khi mở lần đầu ([`ide/MicroBlocksEditor.gp`](ide/MicroBlocksEditor.gp), hàm `applyUserPreferences`).

**Lưu ý về thuật ngữ:** bản dịch gốc trên Weblate dùng "Báo cáo" cho *Report*. Các chuỗi mới
được dịch theo đúng quy ước đó để nhất quán. Nếu muốn đổi sang "Trả về" (tự nhiên hơn với
người Việt) thì sửa toàn bộ bằng:

```bash
sed -i 's/^msgstr "Báo cáo /msgstr "Trả về /' translations/vi.po
```

### 3. Thương hiệu và giao diện

Tên app là **stnapp**, đổi ở tiêu đề cửa sổ, menu bánh răng, `manifest.json` và
`electron/package.json`. Muốn đổi tên khác:

```bash
grep -rln 'stnapp' ide/ electron/ chromeApp/ | xargs sed -i 's/stnapp/<TÊN MỚI>/g'
```

**Logo** — nguồn là ảnh thật [`img/chikawa.png`](img/chikawa.png). Phần mặt được cắt ra bằng
PIL, bỏ chữ "CHIIKAWA", nền trắng chuyển thành trong suốt:

| Tệp | Dùng ở đâu |
|---|---|
| `img/stnapp-logo.svg` | Thanh trên, màn hình chờ (chữ tối, hợp nền sáng) |
| `img/stnapp-logo-onDark.svg` | Khi cần đặt trên nền tối |
| `img/stnapp-face.png` | Chỉ mặt, 482×482, nền trong suốt |
| `img/stnapp-logo-drawn.svg` | Bản vẽ tay bằng SVG, giữ lại làm phương án dự phòng |

Logo SVG **nhúng ảnh mặt dạng base64** chứ không trỏ tới tệp ngoài, vì SVG nạp qua thẻ `<img>`
bị trình duyệt chặn tham chiếu tài nguyên bên ngoài.

Icon đã xuất từ ảnh thật: `icons/Bunny192.png`, `icons/Bunny512.png`, `favicon.ico` (đa kích
thước) và `electron/MicroBlocks.png`. Muốn tạo lại thì chạy lại script trong lịch sử commit.

> ⚠️ Mascot là **Chiikawa — nhân vật có bản quyền của Nagano**. Đây là logo tạm. Phải thay
> bằng hình tự thiết kế trước khi phát hành ra ngoài trường hoặc dùng thương mại.

**Font** — đặt tại `--font-ui` trong
[`styles/config/_config.css`](chromeApp/webapp/styles/config/_config.css):

```
Nunito, Quicksand, Ubuntu, 'Segoe UI', Arial, sans-serif
```

Nhãn khối lệnh vẽ trên canvas chứ không qua CSS, nên cùng danh sách font đó phải lặp lại ở
`labelFontName` trong [`engine/mb-blocks.js`](chromeApp/webapp/engine/mb-blocks.js) — sửa một
chỗ thì nhớ sửa chỗ kia. Giá trị gốc `'Arial Bold'` không phải tên họ font hợp lệ nên thực tế
vẫn rơi về sans-serif mặc định.

**Nunito đã được nhúng sẵn** tại [`chromeApp/webapp/fonts/`](chromeApp/webapp/fonts) (~88 KB,
giấy phép SIL Open Font License 1.1). Nunito là variable font nên mỗi subset chỉ cần một tệp
cho cả dải đậm 400–700. Chỉ giữ 3 subset latin, latin-ext và vietnamese; bỏ Cyrillic vì không
ngôn ngữ nào trong app cần tới.

Vì nhãn khối vẽ lên canvas rồi **lưu lại thành bitmap**, một nhãn vẽ trước khi font tải xong sẽ
kẹt ở font dự phòng. Nên `purejs.html` chờ `document.fonts.load()` xong mới dựng thế giới
morphic. Nếu font lỗi thì chỉ cảnh báo ra console và rơi về font hệ thống, IDE vẫn chạy.

### Giao diện sáng

Bản gốc dùng chrome tối. stnapp đổi sang sáng cho hợp lứa tuổi học sinh và cho lớp học sáng
đèn / máy chiếu.

Cách làm: thêm **biến ngữ nghĩa** trong `styles/config/_config.css` thay vì sửa rải rác, nên
muốn đổi tông sau này chỉ cần sửa một chỗ:

| Biến | Giá trị | Vai trò |
|---|---|---|
| `--surface-app` | `#EEF1F7` | Nền chung, panel trái |
| `--surface-bar` | `#FFFFFF` | Thanh trên, thanh dưới |
| `--surface-sunken` | `#E3E7F0` | Rãnh thanh cuộn |
| `--border-chrome` | `#C2CAD9` | Đường phân cách |
| `--text-chrome` | `#2D3143` | Chữ chính |
| `--text-chrome-muted` | `#666D8A` | Chữ phụ, nhãn |

**Không đảo ngược cả thang màu.** Menu và cửa sổ popup của bản gốc vốn đã sáng; đảo thang sẽ
biến chúng thành tối. Chỉ phần vỏ (thanh trên, panel trái, thanh dưới, màn hình chờ, lớp phủ)
được chuyển.

Màu nền vùng canvas nằm trong JS chứ không phải CSS — `paneColors()` ở `mb-editor.js`. Đã
chỉnh khớp với `--surface-app` để vùng làm việc là chỗ sáng nhất màn hình.

Nút chạy trước đây màu vàng, trên nền trắng gần như mất hút (tỉ lệ tương phản 1.9:1). Đã đổi
sang xanh lá `#18874A` — vừa đạt 4.6:1, vừa mang nghĩa "chạy" cho trẻ chưa đọc được tooltip.

Độ tương phản đã đo: mọi cặp chữ/nền đều đạt WCAG AA (≥4.5:1).

### Bố cục theo kiểu OhStem App

Tham chiếu: ảnh chụp giao diện trong tài liệu OhStem
(`docs.ohstem.vn/en/latest/_images/xbot_3.6.png`).

**Nút chạy / dừng** — bản gốc để hai icon 24px lẫn giữa các nút khác trên thanh trên. OhStem
đặt hai nút tròn lớn nổi ở góc dưới phải vùng làm việc. Đã chuyển theo:

- `ui/ide.js` không còn thêm `run`/`stop` vào thanh trên, mà dựng vào `[data-ide="run-controls"]`
- Vẫn gọi `Buttons.elementFor()` nên icon, nhãn và mô tả cho tip bar dùng chung một nguồn
- Phải `classList.remove(Buttons[selector].class)`: class của thanh trên ép nút về 24px
- `styles/components/_run-controls.css`: 56×56, tròn, xanh lá / đỏ
- `pointer-events: none` ở khung ngoài, `auto` ở nút — để kéo khối ngang qua vẫn được

**Danh mục khối** — đổi từ pill bo tròn sang khối chữ nhật full-width, CHỮ HOA, như OhStem.
Hiệu ứng chọn trước đây là trượt sang trái (`margin-left`), nay mọi nút đều sát lề nên thay
bằng vạch trắng dọc mép trái cộng tăng sáng.

> **Bẫy chữ hoa tiếng Việt:** "ĐIỀU KHIỂN" có dấu chồng hai tầng nên mực chữ cao 15px ở
> cỡ 14px, trong khi `line-height: 1` chỉ cho 14px — cộng `overflow: hidden` là cụt đầu dấu.
> Đã nâng `line-height` lên 1.45. Nếu sau này đổi cỡ chữ danh mục, phải kiểm lại bằng
> `measureText().actualBoundingBoxAscent`, đừng tin mắt nhìn ở ảnh thu nhỏ.

**Logo** — `.top-bar__logo img` đặt theo chiều cao chứ không theo chiều rộng, kèm
`aspect-ratio: 140 / 44`. Lý do: thanh trên là flex container, nếu để `width: auto` phụ thuộc
`height: 100%` thì flex gặp phụ thuộc vòng và tính ra width 0 (logo biến mất). Còn nếu chỉ đặt
`width` như bản gốc thì logo tỉ lệ 130:57 cao 70px trong thanh 48px, tràn xuống dưới vạch.
Đổi tỉ lệ viewBox của logo thì phải sửa `aspect-ratio` cho khớp.

**Chưa giống OhStem:** danh mục của họ có icon nhỏ bên trái mỗi nhãn (ô tô, ngôi sao, nốt
nhạc…). stnapp chưa có — cần vẽ một bộ icon cho 9 danh mục.

### Hình dạng khối

Chỉnh trong `mb-blocks.js` cho mềm và dễ bấm hơn, hợp trẻ nhỏ:

| Thuộc tính | Gốc | stnapp |
|---|---|---|
| `corner` | 4 | 6 |
| `rounding` | 16 | 18 |
| `minLineHeight` | 20 | 22 |
| `labelPadding` | 2 | 3 |
| `bottomPadding` | 4 | 5 |

Không đụng `edge`, `inset`, `dent` — đó là hình học của khớp nối giữa các khối, đổi vào là sai
chỗ ghép.

### Chưa làm xong

- `chromeApp/webapp/icons/Bunny192.png`, `Bunny512.png`, `favicon.ico` vẫn là hình thỏ của
  MicroBlocks — cần xuất PNG từ logo mới.
- `electron/MicroBlocks.png` (icon app desktop) cũng vậy.

## Chạy web local — không cần build

MicroBlocks có **hai bản IDE** trong cùng repo:

| Tệp | Nền | Cần build? |
|---|---|---|
| `chromeApp/webapp/purejs.html` | JavaScript thuần (`engine/mb-*.js`) | **Không** |
| `chromeApp/webapp/microblocks.html` | GP biên dịch sang WebAssembly | Có, cần emcc |

Bản `purejs.html` có compiler, decompiler, esptool riêng viết bằng JS, và nạp `translations/*.po`
bằng `fetch` lúc chạy. Nghĩa là sửa `.po` hay `.js` chỉ cần tải lại trang.

```bash
# lần đầu sau khi clone (và mỗi khi thêm ví dụ / thư viện / firmware):
bash tools/buildFileList.sh

python3 tools/serve.py 8000
# mở http://localhost:8000/purejs.html
```

Dùng `tools/serve.py`, **không dùng `python3 -m http.server`**: server này gửi
`Cache-Control: no-cache`, nên mọi máy luôn nhận bản `.js`/`.css`/`.po`/bài học mới nhất sau
khi sửa (tệp không đổi thì vẫn chỉ tốn một phản hồi 304).

**Mở thẳng một bài học bằng link** — tham số `#project=` nhận địa chỉ của tệp `.ubp`:

```
http://localhost:8000/purejs.html#project=http://localhost:8000/Examples/stnapp/Buoi%2013%20-%20Linh%20cuu%20hoa%20ti%20hon.ubp
```

Phát link này cho học sinh là mọi máy mở đúng bài, đủ cả khối, không phải tìm trong mục Ví dụ.
Thay `localhost` bằng IP của máy giáo viên để cả phòng mở chung một server.

> **Bắt buộc chạy `tools/buildFileList.sh`.** Bản web không duyệt thư mục được, nó đọc danh
> sách tệp từ `chromeApp/webapp/files.txt`. Upstream gitignore tệp này vì là sản phẩm build,
> nên clone về là **không có** — khi đó hộp thoại "Thêm thư viện" và "Mở → Ví dụ" trống
> trơn, học sinh không thêm được cả thư viện Servo có sẵn.
>
> Firmware cũng vậy: `precompiled/vm_*` bị gitignore. Muốn nút "cập nhật firmware" chạy được
> cho Pico thì tải `vm_pico_w.uf2` từ `https://microblocks.fun/downloads/latest/vm/` vào
> `precompiled/` rồi chạy lại `buildFileList.sh`.

### Quyền cổng serial cho Pico trên Linux

Firmware MicroBlocks trên RP2040 báo USB ID `2e8a:f00a`. Rule udev của PlatformIO chỉ mở quyền
cho `idProduct` bắt đầu bằng `0` hoặc `1`, nên cổng rơi về nhóm `dialout` và trình duyệt
không kết nối được. Mỗi máy Linux trong phòng học cần một lần:

```bash
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="2e8a", ATTRS{idProduct}=="f00a", MODE="0666"' \
  | sudo tee /etc/udev/rules.d/99-stnapp-pico.rules
sudo udevadm control --reload-rules && sudo udevadm trigger --subsystem-match=tty
```

## Dự án mẫu

- [`Examples/stnapp/Buoi 13 - Linh cuu hoa ti hon.ubp`](Examples/stnapp/Buoi%2013%20-%20Linh%20cuu%20hoa%20ti%20hon.ubp)
  — **Buổi 13: Lính cứu hỏa tí hon**, tính năng an toàn cho chuỗi bài "Nhà thông minh của em".
  Servo MG90S quét 0–180°, cảm biến lửa, bơm nước qua relay, board RP2040 Pro Micro (GP2/GP3/GP4).
  Yêu cầu bài học và sơ đồ cắm dây nằm trong phần mô tả dự án. Biến, khối tự tạo và cả tên hàm
  đều tiếng Việt; định nghĩa các khối hiện sẵn trên vùng làm việc để học sinh đọc được.

  Hai thông số chỉnh theo số đo thật: cảm biến lửa bắt ngọn bật lửa **chập chờn** (mỗi đợt
  0,3–1,5 giây), nên mỗi góc nhìn 3 lần, và bơm chỉ tắt khi không thấy lửa liền 1 giây.

> ⚠️ **Cache.** Trình duyệt nào từng mở stnapp qua `python3 -m http.server` (không có
> `Cache-Control`) có thể còn giữ bản cũ: bấm **Ctrl+Shift+R một lần** sau khi chuyển sang
> `tools/serve.py`, từ đó về sau không cần nữa.

Bản gốc ép chuyển sang HTTPS (vì WebSerial cần secure context) nên không chạy được qua HTTP
local. Đã sửa trong [`purejs.html`](chromeApp/webapp/purejs.html): miễn trừ `localhost`,
`127.0.0.1` và `[::1]` — theo chuẩn thì localhost vốn đã là secure context nên WebSerial vẫn
dùng được bình thường.

Đã kiểm thử thực tế trên trình duyệt: IDE lên tiếng Việt, và nhập thư viện từ link GitHub
`blob` thành công (thư viện `uremote` v1.5 hiện đủ khối trong bảng chọn).

## Build bản Electron / WebAssembly

Cần **Node.js** (đã kiểm thử v22), **npm**, và **Emscripten SDK**.

Emscripten là bắt buộc: `chromeApp/emscripten/buildEmcc.sh` copy `ide/*.gp`, `translations/` và
`gp/runtime/` vào hệ thống tệp nhúng rồi biên dịch thành `gp_wasm.data`. Nghĩa là **mọi thay đổi
trong tệp `.gp` hay `.po` chỉ có hiệu lực sau khi build lại bằng emcc** — không có bản wasm
dựng sẵn trong repo.

```bash
# cài Emscripten (một lần)
git clone https://github.com/emscripten-core/emsdk.git ~/emsdk
~/emsdk/emsdk install latest && ~/emsdk/emsdk activate latest
source ~/emsdk/emsdk_env.sh

# build
./build.sh --gp --electron          # build webapp GP rồi chạy app Electron
./build.sh --gp --electron --pack   # đóng gói installer
```

Kiểm tra nhanh cú pháp tệp `.gp` mà không cần emcc (chạy headless, load toàn bộ IDE rồi thoát):

```bash
cd gp && ./gp-linux64bit runtime/lib/* loadIDE.gp updateLocale.gp -- vi
```

Dịch lại tệp ngôn ngữ sau khi thêm chuỗi mới vào mã nguồn:

```bash
./build.sh --locale=vi
```

## Cập nhật từ bản gốc

Remote `upstream` đã được cấu hình sẵn:

```bash
git fetch --unshallow upstream    # lần đầu, vì đây là shallow clone
git fetch upstream
git merge upstream/dev
```

Các tệp dễ bị xung đột khi merge: `ide/MicroBlocksScripter.gp`,
`ide/MicroBlocksLibraryWidgets.gp`, `ide/MicroBlocksEditor.gp`, `translations/vi.po`.

## Phần cứng hỗ trợ

Giữ nguyên VM của bản gốc nên dùng lại được toàn bộ firmware: hơn 40 bo mạch thuộc các họ
ESP32 (classic / S2 / S3 / C3), ESP8266, RP2040, RP2350, nRF51, nRF52, SAMD21.
Xem danh sách đầy đủ trong [`platformio.ini`](platformio.ini).

Chưa hỗ trợ ESP32-C6, C5, H2, P4.
