# Quán Ăn Chợ Nổi v1.0.0 — nhóm Banana

Bản phát hành của Lab Day 12 (AI SDLC) dùng Test Contract v1.3.

## Điểm mới

- Lặn & Hái → Mở Quán → Shop nâng cấp oxy/Máu trong tối đa 5 ngày. Menu chính có **Chơi**, **Âm thanh** và **Thoát**. Đầu ngày xem kế hoạch của Má Tư, đầu ca tối xem tổng nhập kho và món nấu được. Sau ca tối xem kết quả ngày, sau ngày cuối xem bảng tổng kết.
- Kho cá thể có ID và độ tươi. Hàng ươn dưới 30, quán giữ nguyên liệu tươi nhất và chốt giá theo độ tươi lúc nấu.
- Cá Sấu Năm Chèo và đàn cá di chuyển. Quán có 2 bếp, 4 bàn và 6 món.
- Cảnh báo thủy quái, cạn oxy và khách sắp giận có chữ kèm biểu tượng. Nhấn **C** để bật tương phản cao.
- Hai mở rộng của lab gồm **Cháy món** và **Phụ đề SFX**. Phụ đề hiện cả khi tắt âm. Âm lượng Master, Nhạc và Hiệu ứng lưu giữa các phiên.

## Cách chạy

Cần Python 3.10 trở lên và trình duyệt có JavaScript trên macOS hoặc Linux. Giải nén `chonoi-v1.0.0.zip` từ mục Assets của Release rồi chạy lệnh thứ ba trong thư mục đã giải nén. Nếu dùng Git, chạy đủ ba lệnh sau.

```bash
git clone --branch v1.0.0 https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana.git
cd K5-L3B-LAB-Day12-AI-SDLC-Banana
python3 -m chonoi.live --mode day --days 1
```

Mở địa chỉ in trong terminal, mặc định là `http://127.0.0.1:8000/`. Để chơi đủ 5 ngày, đổi thành `--days 5`. Xem [điều khiển](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/blob/v1.0.0/README.md#chạy-từ-clone-sạch-trên-macos-hoặc-linux).

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
python3 -m chonoi.headless --mode day --days 1 --seed 42 --ticks 22200 --out day.jsonl
python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json
python3 -m chonoi.soak --seed 7 --days 10 --out soak.json
```

## Video demo

[Quan_An_Cho_Noi_demo_thuyet_minh.mp4](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/releases/download/v1.0.0/Quan_An_Cho_Noi_demo_thuyet_minh.mp4) (2 phút 48 giây, có thuyết minh), nằm trong mục Assets của Release v1.0.0.

## Kiểm chứng

- Cảnh lặn lõi 1280×720, seed 42, làm nóng 3 giây rồi đo trong 30 giây. [Kết quả benchmark](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/blob/v1.0.0/docs/proof/phase-4/bench.json)
- Soak 10 ngày qua đủ ba ca trong một tiến trình. [Kết quả soak](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/blob/v1.0.0/docs/proof/phase-4/soak.json)
- Chơi thử ba cảnh báo ở chế độ tương phản cao, các màn chuyển pha và phụ đề khi tắt âm. [Kiểm giao diện](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/blob/v1.0.0/docs/proof/phase-4/web-ui.md)
- Regression P1–P3 và kiểm phát hành. [Ma trận Phase 4](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/blob/v1.0.0/docs/verification/phase-4.md)

## Giới hạn đã biết

- Benchmark tự tìm Chrome/Chromium. Nếu dùng trình duyệt mặc định, cần giữ khu vực vẽ ở 1280×720. FPS phụ thuộc trình duyệt, màn hình và tải máy.
- Bot soak di chuyển qua đủ các pha và bàn giao hàng thật. Kịch bản bot hiện bỏ qua nấu và phục vụ nên tổng thu trong kết quả soak bằng 0.
- Nút **Thoát** dừng lượt và mở màn rời game. Đóng tab trình duyệt để rời trang.
- Các mở rộng còn lại gồm dòng nước lũ, khách đặt trước và bảng xếp hạng.

## Tạo bản đóng gói

```bash
git archive --format=zip --prefix=chonoi-v1.0.0/ -o chonoi-v1.0.0.zip v1.0.0
```
