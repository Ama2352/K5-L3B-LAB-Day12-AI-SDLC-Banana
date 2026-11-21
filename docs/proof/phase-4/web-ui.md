# Kiểm giao diện Phase 4

Chrome 157 chạy ở viewport 1280×720 trên Windows. Chạy `python3 -m chonoi.live` với `--mode day --days 1 --seed 42 --scenario docs/proof/phase-4/ui-scenarios/day.json` hoặc `--mode gather --scenario docs/proof/phase-4/ui-scenarios/oxy.json` và `docs/proof/phase-4/ui-scenarios/monster.json` để lặp các ca. Các fixture ở cùng thư mục này chuẩn bị trạng thái để kiểm từng hành vi.

## Vòng ngày và HUD (AC-P2-24)

- Menu có Chơi và Thoát. DayIntro có danh sách nguyên liệu, tự sang gather sau khoảng 4,09 s khi đo từ thao tác bấm Chơi. Lượt riêng dùng phím X để bỏ qua.
- Kiểm Pause trong gather và Shop. Đồng hồ mô phỏng đứng yên. Tiếp tục và Về menu dùng được.
- EveningIntro báo 3 nguyên liệu nhập kho và 2 món có thể nấu. DayResult báo 1 khách được phục vụ, 1 khách bỏ đi, thu 72 nghìn, boa 12 nghìn và uy tín giảm 0,3. Sau khi đóng Shop, Summary hiển thị tổng thu 72 nghìn, uy tín 2,7, điểm và Cá lóc nướng trui bán chạy nhất với 1 suất. [Kết quả ngày](day-result.png)
- Các nút HUD đều có cỡ chữ 18 px và nằm ngoài biển tên cảnh. Kiểm lại chữ chọn món, kiên nhẫn tại bàn, trạng thái bếp, món cầm tay và kho ở ca tối. [HUD gather](gather-hud.png)

## Ba cảnh báo trong chế độ tương phản cao (AC-P4-06)

| Cảnh | Điều kiện kiểm | Kết quả | Ảnh |
|---|---|---|---|
| Thủy quái gần | Út Sen ở `[60, 24]`, M1 ở `[66, 24]` | Hiện chữ “Thủy quái!” và viền cảnh báo | [Ảnh thủy quái](warn-monster.png) |
| Oxy thấp | Út Sen ở `[2, 11]`, còn 85/1.800 tick oxy | Hiện “Oxy sắp hết!” và thanh oxy đổi màu. Tiếp tục tới lúc cạn hiện “Hết hơi!”. | [Ảnh oxy](warn-oxy.png) |
| Khách sắp giận | Khách tại T2 còn 195/3.600 tick kiên nhẫn | Hiện “Khách sắp giận!” và đổi màu thanh kiên nhẫn | [Ảnh ca tối](warn-angry.png) |

## Âm thanh và phụ đề

Đã kiểm ba mức Master 72%, Nhạc 31% và Hiệu ứng 64%. Nhạc phát bằng Web Audio, mỗi kênh có gain riêng. Tải lại trang giữ ba mức âm lượng. Khi tắt âm toàn bộ, hai sự kiện phục vụ và khách bỏ đi vẫn hiển thị phụ đề. [Ảnh phụ đề lúc tắt âm](sfx-subtitle.png)