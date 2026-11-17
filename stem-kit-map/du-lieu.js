/* Dữ liệu bản đồ kit: loại module, module, cấp độ, dự án. Sửa nội dung kit ở tệp này; giao diện ở ban-do.js và ban-do.css. */
const TYPES = {core:'Trung tâm', smart:'Module thông minh tự thiết kế', in:'Đầu vào', out:'Đầu ra', mech:'Cơ khí'};
const M = {
  C1:{n:'Bo chủ ESP32-S3', t:'core', port:'Máy tính qua USB-C hoặc Bluetooth', d:'Bộ não của kit, chạy chương trình MicroBlocks. Có sẵn 2 nút bấm, còi, LED RGB, WiFi và Bluetooth; 6 cổng D/A, 2 bus I2C (thường và tốc độ cao), cổng SPI và 2 cổng servo.'},
  C2:{n:'Nguồn pin 2S', t:'core', port:'5 V vào bo chủ, 7,4 V sang module động lực, I2C để đọc pin', d:'Hai cell 18650 có mạch bảo vệ. Cấp 5 V cho bo chủ và 7,4 V cho động cơ; đo được phần trăm pin và dòng tiêu thụ.'},
  S1:{n:'Driver động cơ encoder', t:'smart', port:'I2C; nguồn 7,4 V từ C2; 2 cổng động cơ 6 chân', d:'Bo chủ chỉ gửi vận tốc hoặc vị trí mong muốn, module tự điều khiển 2 động cơ cho đúng. Học sinh không phải tự đọc encoder.'},
  S2:{n:'Dò line 8 mắt', t:'smart', port:'I2C, nối chuỗi', d:'Tám mắt đọc vạch, tự hiệu chuẩn đen trắng. Trả về vị trí vạch từ -100 đến 100 và báo ngã tư, mất vạch.'},
  S3:{n:'IMU trả góc', t:'smart', port:'I2C, nối chuỗi', d:'Trả về góc nghiêng và góc xoay đã lọc sẵn, kèm cờ báo rung và va chạm.'},
  I1:{n:'Nút bấm đôi', t:'in', port:'Cổng D/A', d:'Hai nút bấm trên một module.'},
  I2:{n:'Biến trở xoay', t:'in', port:'Cổng A (analog)', d:'Núm xoay cho giá trị thay đổi liên tục, dùng để chỉnh mức.'},
  I3:{n:'Joystick 2 trục', t:'in', port:'Cổng A (analog)', d:'Cần gạt hai chiều để điều khiển bằng tay.'},
  I4:{n:'Bàn phím 4x4', t:'in', port:'I2C', d:'Mười sáu phím để nhập số và mật khẩu.'},
  I5:{n:'Cảm biến ánh sáng', t:'in', port:'Cổng A (analog)', d:'Đo độ sáng môi trường để biết trời sáng hay tối.'},
  I6:{n:'Nhiệt ẩm AHT20', t:'in', port:'I2C', d:'Đo nhiệt độ và độ ẩm không khí.'},
  I7:{n:'Chuyển động PIR', t:'in', port:'Cổng D/A', d:'Phát hiện có người di chuyển trong phòng.'},
  I8:{n:'Khí gas MQ-2', t:'in', port:'Cổng A (analog)', d:'Phát hiện khí gas và khói.'},
  I9:{n:'Độ ẩm đất', t:'in', port:'Cổng A (analog)', d:'Cắm vào chậu cây để biết đất khô hay ướt.'},
  I10:{n:'Cảm biến mưa', t:'in', port:'Cổng A (analog)', d:'Phát hiện nước mưa rơi trên bề mặt.'},
  I11:{n:'Siêu âm đo khoảng cách', t:'in', port:'Cổng D/A (2 tín hiệu)', d:'Đo khoảng cách tới vật cản bằng sóng siêu âm.'},
  I12:{n:'Thu hồng ngoại', t:'in', port:'Cổng D/A', d:'Nhận lệnh từ điều khiển từ xa đi kèm.'},
  I13:{n:'RFID RC522', t:'in', port:'Cổng SPI', d:'Đọc thẻ từ để nhận dạng người hoặc vị trí.'},
  I14:{n:'Cảm biến màu', t:'in', port:'I2C', d:'Nhận biết màu của vật đặt trước cảm biến.'},
  O1:{n:'LED đôi', t:'out', port:'Cổng D/A', d:'Hai đèn LED trên một module.'},
  O2:{n:'Thanh NeoPixel 8 LED', t:'out', port:'Cổng D/A', d:'Tám đèn đổi màu tùy ý, làm đèn báo và hiệu ứng.'},
  O3:{n:'Màn hình OLED', t:'out', port:'I2C', d:'Màn hình nhỏ hiện chữ, số và đồ thị.'},
  O4:{n:'Relay', t:'out', port:'Cổng D/A', d:'Công tắc điện tử đóng cắt tải điện áp thấp như đèn 12 V.'},
  O5:{n:'MOSFET + quạt/bơm', t:'out', port:'Cổng D/A (PWM)', d:'Điều khiển tốc độ quạt hoặc bơm nước mini.'},
  O6:{n:'Servo', t:'out', port:'Cổng servo, hoặc qua O7', d:'Động cơ quay tới góc chỉ định, làm cửa, tay gạt, khớp tay robot.'},
  O7:{n:'Bộ điều khiển 16 servo', t:'out', port:'I2C; nguồn từ C2', d:'Điều khiển nhiều servo cùng lúc với nguồn riêng, dùng cho cánh tay robot.'},
  K1:{n:'Cụm truyền động', t:'mech', port:'Cắm vào cổng động cơ của S1', d:'Hai động cơ encoder kèm gá và bánh xe; có bản N20 và bản JGA25-370.'},
  K2:{n:'Khung xe đa năng', t:'mech', port:'Bắt vít theo lưới 8 mm', d:'Lắp ngang thành xe dò line, lắp đứng thành xe cân bằng.'},
  K3:{n:'Mô hình nhà', t:'mech', port:'Bắt vít theo lưới 8 mm', d:'Nhà cắt laser có sẵn lỗ gá module.'},
  K4:{n:'Phụ kiện', t:'mech', port:'Tùy dự án', d:'Sa bàn vạch, thẻ RFID, khung cánh tay robot, băng tải mini.'}
};
const LV = [
  {n:'Làm quen', age:'12–13 tuổi', s:'8 buổi'},
  {n:'Nhà thông minh', age:'12–15 tuổi', s:'10 buổi'},
  {n:'Robot di động', age:'13–16 tuổi', s:'12 buổi'},
  {n:'IoT', age:'14–17 tuổi', s:'8 buổi'},
  {n:'Nâng cao', age:'16–18 tuổi', s:'10 buổi'}
];
const ATT = {S1:'+ 2 động cơ encoder', O7:'+ 4 servo'};
const PHONE = 'MQTT tới bảng điều khiển trên điện thoại';
const P = [
  {id:1, lv:0, n:'Đèn giao thông', pw:'usb', d:'Ba đèn đỏ, vàng, xanh đổi theo chu kỳ; bấm nút để người đi bộ xin qua đường.', stem:'mạch điện, lệnh tuần tự, thời gian', c:{A1:'I1', D1:'O1', D2:'O2'}},
  {id:2, lv:0, n:'Đàn điện tử', pw:'usb', d:'Mỗi nút là một nốt nhạc, xoay biến trở để đổi cao độ; còi trên bo chủ phát âm.', stem:'tần số âm thanh, biến, vòng lặp', c:{A1:'I2', D1:'I1'}, on:['Còi']},
  {id:3, lv:0, n:'Đo phản xạ', pw:'usb', d:'Đèn sáng ngẫu nhiên, bấm nút thật nhanh; màn hình hiện thời gian phản xạ và kỷ lục.', stem:'đo thời gian, số ngẫu nhiên, trung bình cộng', c:{D1:'I1', D2:'O2', I2C:['O3']}},
  {id:4, lv:0, n:'Nhiệt ẩm kế', pw:'usb', d:'Đo nhiệt độ, độ ẩm trong phòng và hiện lên màn hình; đổi màu đèn khi quá nóng.', stem:'cảm biến, đơn vị đo, hiển thị', c:{I2C:['O3','I6']}, on:['LED RGB']},
  {id:5, lv:1, n:'Đèn tự động', pw:'adp', d:'Đèn chỉ bật khi trời tối và có người trong phòng, tự tắt khi không còn ai.', stem:'ngưỡng, logic VÀ/HOẶC, tiết kiệm điện', c:{A1:'I5', A2:'I7', D1:'O4', D2:'O1'}, k:['K3']},
  {id:6, lv:1, n:'Cửa thông minh', pw:'adp', d:'Mở cửa bằng thẻ từ hoặc mật khẩu; nhập sai ba lần thì báo động.', stem:'nhận dạng, mật khẩu, danh sách', c:{I2C:['O3','I4'], SPI:'I13', SV:['O6']}, on:['Còi'], k:['K3']},
  {id:7, lv:1, n:'Báo cháy, rò gas', pw:'adp', d:'Phát hiện khí gas hoặc nhiệt độ tăng bất thường, hú còi, nháy đèn và bật quạt hút.', stem:'nồng độ khí, cảnh báo, an toàn', c:{A1:'I8', D1:'O2', D2:'O5', I2C:['I6']}, on:['Còi'], k:['K3']},
  {id:8, lv:1, n:'Quạt theo nhiệt độ', pw:'adp', d:'Quạt quay nhanh dần khi phòng nóng lên; xoay biến trở để đặt nhiệt độ mong muốn.', stem:'PWM, điều khiển tỉ lệ, đồ thị', c:{A1:'I2', D1:'O5', I2C:['O3','I6']}, k:['K3']},
  {id:9, lv:1, n:'Giàn phơi tự động', pw:'adp', d:'Trời mưa hoặc tối thì giàn phơi tự thu vào, nắng lên thì đưa ra.', stem:'máy trạng thái, cơ cấu truyền động', c:{A1:'I10', A2:'I5', SV:['O6']}, k:['K3']},
  {id:10, lv:1, n:'Nhà thông minh IoT', pw:'adp', d:'Ghép các dự án 5–9 thành một ngôi nhà hoàn chỉnh, xem và điều khiển từ điện thoại.', stem:'WiFi, MQTT, tích hợp hệ thống', c:{A1:'I5', A2:'I8', A3:'I10', D1:'O4', D2:'O5', D3:'I7', I2C:['O3','I6','I4'], SPI:'I13', SV:['O6','O6']}, on:['Còi','LED RGB'], wifi:PHONE, k:['K3']},
  {id:11, lv:2, n:'Xe điều khiển từ xa', pw:'bat', d:'Xe hai bánh chạy tiến, lùi, rẽ theo điều khiển hồng ngoại.', stem:'vận tốc, chuyển động vi sai', c:{D1:'I12', I2C:['S1']}, k:['K1','K2']},
  {id:12, lv:2, n:'Xe tránh vật cản', pw:'bat', d:'Xe tự chạy, quay cảm biến siêu âm sang hai bên để chọn hướng còn trống.', stem:'vận tốc âm thanh, đo khoảng cách', c:{D1:'I11', I2C:['S1'], SV:['O6']}, k:['K1','K2']},
  {id:13, lv:2, n:'Xe dò line cơ bản', pw:'bat', d:'Xe bám theo vạch đen trên sa bàn bằng luật rẽ trái, rẽ phải đơn giản.', stem:'phản xạ ánh sáng, điều khiển bật–tắt', c:{I2C:['S1','S2']}, k:['K1','K2','K4']},
  {id:14, lv:2, n:'Xe dò line PID', pw:'bat', d:'Xe bám vạch mượt và nhanh nhờ PID; chỉnh Kp, Ki, Kd và xem kết quả trên màn hình.', stem:'sai số, P–I–D, thực nghiệm chỉnh tham số', c:{I2C:['S1','S2','O3']}, k:['K1','K2','K4']},
  {id:15, lv:2, n:'Xe vẽ hình', pw:'bat', d:'Xe chạy theo hình vuông, tam giác, ngôi sao bằng lệnh đi thẳng và quay góc chính xác.', stem:'chu vi, góc, quãng đường = vận tốc × thời gian', c:{I2C:['S1','S3']}, k:['K1','K2']},
  {id:16, lv:2, n:'Xe giao hàng', pw:'bat', d:'Xe theo vạch tới đúng trạm nhờ thẻ RFID, dừng giao hàng và báo trạng thái về máy chủ.', stem:'ngã tư, bản đồ, nhận dạng trạm, truyền tin', c:{I2C:['S1','S2'], SPI:'I13'}, wifi:'MQTT báo trạng thái giao hàng', k:['K1','K2','K4']},
  {id:17, lv:3, n:'Trạm thời tiết online', pw:'adp', d:'Đo nhiệt độ, độ ẩm, ánh sáng, mưa và gửi lên mạng để vẽ đồ thị theo ngày.', stem:'thu thập dữ liệu, đồ thị, thống kê', c:{A1:'I5', A2:'I10', I2C:['O3','I6']}, wifi:PHONE},
  {id:18, lv:3, n:'Vườn thông minh', pw:'adp', d:'Đất khô thì tự bơm nước; theo dõi và tưới từ xa bằng điện thoại.', stem:'độ ẩm đất, tưới tự động, điều khiển từ xa', c:{A1:'I9', D1:'O5', D2:'O4', I2C:['O3','I6']}, wifi:PHONE},
  {id:19, lv:3, n:'Giám sát năng lượng', pw:'bat', d:'Đo điện áp, dòng và công suất của pin; ước tính thời gian chạy còn lại.', stem:'điện áp, dòng điện, công suất, dung lượng pin', c:{I2C:['O3']}, wifi:PHONE},
  {id:20, lv:3, n:'Điểm danh RFID', pw:'adp', d:'Quẹt thẻ để điểm danh; tên và giờ đến được gửi lên máy chủ của lớp.', stem:'cơ sở dữ liệu, giao tiếp máy chủ', c:{D1:'O2', I2C:['O3'], SPI:'I13'}, wifi:'Gửi dữ liệu lên máy chủ của lớp'},
  {id:21, lv:4, n:'Xe cân bằng 2 bánh', pw:'bat', d:'Xe đứng thăng bằng trên hai bánh như con lắc ngược, tự giữ khi bị đẩy nhẹ.', stem:'con lắc ngược, trọng tâm, PID lồng nhau', c:{I2C:['S1','S3']}, k:['K1','K2']},
  {id:22, lv:4, n:'Xe cân bằng qua điện thoại', pw:'bat', d:'Xe cân bằng chạy tiến, lùi, rẽ theo điện thoại; chỉnh tham số PID từ xa.', stem:'chỉnh tham số từ xa, đo đạc và so sánh', c:{I2C:['S1','S3']}, wifi:'Điều khiển và chỉnh PID từ điện thoại', k:['K1','K2']},
  {id:23, lv:4, n:'Cánh tay robot', pw:'bat', d:'Cánh tay bốn khớp gắp vật bằng joystick; ghi lại rồi tự lặp lại chuỗi động tác.', stem:'động học, góc khớp, ghi và phát lại chuyển động', c:{A1:'I3', I2C:['O7']}, extra:['O6'], k:['K4']},
  {id:24, lv:4, n:'Băng tải phân loại màu', pw:'bat', d:'Băng tải đưa vật qua cảm biến màu, tay gạt servo đẩy vật vào đúng ô.', stem:'ánh sáng và màu sắc, tự động hóa dây chuyền', c:{I2C:['S1','I14','O3'], SV:['O6']}, att:{S1:'+ động cơ băng tải'}, k:['K4']},
  {id:25, lv:4, n:'Dự án mở', pw:'usb', open:true, d:'Học sinh tự chọn vấn đề, tự chọn module và làm sản phẩm dự thi khoa học kỹ thuật.', stem:'quy trình thiết kế kỹ thuật', c:{}}
];
const PW = {usb:'Cáp USB từ máy tính', adp:'Adapter USB-C 5 V / 2 A'};
const DA = ['A1','A2','A3','D1','D2','D3'];
