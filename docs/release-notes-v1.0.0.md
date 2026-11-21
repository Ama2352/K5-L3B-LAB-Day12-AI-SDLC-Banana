# Quán Ăn Chợ Nổi v1.0.0 — nhóm Banana

Bản phát hành cuối của Lab Day 12 (AI SDLC). Contract v1.3. Tag `phase-4` và Release `v1.0.0` cùng trỏ một commit trên `main`.

## Điểm mới
- **Trọn vòng ngày** (5 Ngày): Lặn & Hái → Mở Quán → Shop nâng cấp oxy/Máu, kế hoạch món D1–D5, pause, HUD sáng/tối.
- **Mùa Nước Nổi**: kho cá thể có id và độ tươi; hàng hao tươi, ươn dưới 30; giữ chỗ theo cá thể tươi nhất; giá món theo độ tươi.
- **Cá Sấu Năm Chèo**, đàn cá bơi và sinh theo lịch, 2 bếp / 4 bàn, 6 món.
- **Cảnh báo dễ nhận biết**: Thủy quái!, Hết hơi!, Khách sắp giận! (chữ + biểu tượng) và chế độ tương phản cao (phím C).
- **Mở rộng**: Cháy món (`burn`, khai trong `extensions`) và thiết lập âm lượng Master/Music/SFX lưu giữa các lần mở.
- **Benchmark có render** (`python3 -m chonoi.bench`) và **soak 10 Ngày** (`python3 -m chonoi.soak`).

## Cách chạy (macOS / Linux, Python 3.10+, trình duyệt)
```bash
git clone https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana.git
cd K5-L3B-LAB-Day12-AI-SDLC-Banana
python3 -m chonoi.live --mode day --days 1
```
Mở địa chỉ in ra (mặc định `http://127.0.0.1:8000/`). Bản đóng gói đính kèm (`chonoi-v1.0.0.zip`) giải nén rồi chạy lệnh thứ ba trong thư mục đó.

Test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v` · Headless: `python3 -m chonoi.headless …` · Bench: `python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json` (cần Chrome/Chromium) · Soak: `python3 -m chonoi.soak --seed 7 --days 10 --out soak.json`.

## Số đo của bản phát hành
Xem `docs/proof/phase-4/`: `bench.json` (seed 42, 30 s, 1280×720), `soak.json` (seed 7, 10 Ngày), `test-run-qa.txt`.

## Giới hạn đã biết
- Benchmark cần Google Chrome/Chromium; không có thì mở trình duyệt mặc định và cần giữ cửa sổ ở 1280×720. Trình duyệt thường khóa 60 FPS theo tần số màn hình nên `avg_fps` không vượt quá tần số quét.
- Bot soak không nấu/bưng nên `earned` trong `soak.json` bằng 0; soak kiểm độ bền và tính lặp, không đo kinh tế.
- Đồ họa là hình khối Canvas 2D tự vẽ; âm thanh tổng hợp bằng Web Audio, không dùng tài sản ngoài.
- Chưa làm các mở rộng: dòng nước lũ, khách đặt trước, bảng xếp hạng, phụ đề SFX.

## Tạo bản đóng gói
```bash
git archive --format=zip --prefix=chonoi-v1.0.0/ -o chonoi-v1.0.0.zip phase-4
```
