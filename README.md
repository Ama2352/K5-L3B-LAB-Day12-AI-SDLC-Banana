# Day 12 — AI SDLC: Quán Ăn Chợ Nổi

> **Làm theo nhóm 4–6 người** · Dùng AI để xây game 2D qua **4 phase** trong **3 giờ**: Út Sen lặn bắt cá, hái rau trên mặt nước rồi tối mở quán phục vụ khách.
> **Yêu cầu từng phase mở đúng mốc giờ tại lab board:** **[Chợ Nổi Lab](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg)** (cần đăng nhập claude.ai; có trợ giảng AI cho từng phase).

## Bắt buộc (chỉ có thế)

Cách làm việc kỹ thuật là **tự do** (push thẳng, nhánh + PR, pair, có hay không CI…). Cái bắt buộc:

1. **Một repo chung:** trưởng nhóm **fork** repo này, đặt tên `K5-L3B-LAB-Day12-AI-SDLC-<ten-nhom>`, thêm mọi thành viên làm collaborator (*Settings → Collaborators*, quyền Write) và để repo **public** (giảng viên xem được, không cần mời).
2. **Cả nhóm cùng commit** bằng tài khoản GitHub của mình, mỗi người **≥ 3 commit có nội dung** (làm cặp thì ghi `Co-authored-by:`).
3. **Điền [`TEAM.md`](TEAM.md):** danh sách thành viên + thỏa thuận làm việc nhóm; sửa `team_size` trong [`game.contract.json`](game.contract.json). Commit của người không có trong `TEAM.md` không được tính.
4. **Gắn tag** `phase-1` … `phase-4` đúng hạn; chạy được tại từng tag.
5. **Ghi chép tối thiểu:** `docs/verification/phase-n.md`, `docs/clarify.md`, `docs/ai-usage-log.md`, `docs/retro.md`, `docs/members/<handle>.md`.

## Chạy từ clone sạch trên macOS hoặc Linux

Cần Git, Python 3.10 trở lên và trình duyệt có JavaScript. Game dùng thư viện chuẩn Python.

```bash
git clone https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana.git
cd K5-L3B-LAB-Day12-AI-SDLC-Banana
python3 -m chonoi.live --mode day --days 1
```

Mở địa chỉ in trong terminal, mặc định là `http://127.0.0.1:8000/`, rồi chọn **Chơi** trong menu chính. Menu cũng có **Âm thanh** và **Thoát**. Để chơi đủ 5 ngày, đổi `--days 1` thành `--days 5`. Nhấn `Ctrl+C` trong terminal để dừng máy chủ. Xem [ghi chú phát hành](docs/release-notes-v1.0.0.md) và [video demo có thuyết minh](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/releases/download/v1.0.0/Quan_An_Cho_Noi_demo_thuyet_minh.mp4) (2 phút 48 giây, đính kèm Release v1.0.0).

| Phím hoặc nút | Thao tác |
|---|---|
| WASD hoặc phím mũi tên | Bơi và đi bộ |
| E | Cập bến, hái rau hoặc tương tác với bếp và bàn |
| Space | Bắt cá dưới nước |
| P hoặc Esc | Tạm dừng hoặc tiếp tục. Menu tạm dừng có **Tiếp tục**, **Âm thanh**, **Về menu** |
| R | Chơi lại |
| C / H | Bật hoặc tắt tương phản cao / xem thực đơn |
| Âm thanh | Chỉnh Master, Nhạc, Hiệu ứng (SFX) hoặc tắt âm toàn bộ |
| Nút trên màn hình Shop | Mua nâng cấp hoặc đóng Shop để hoàn thành ngày |

Đầu ngày, Má Tư đọc kế hoạch món và nguyên liệu. Màn này tự chuyển sau 4 giây hoặc khi nhấn phím. Sau khi cập bến, xem số lượng nhập kho và món nấu được rồi chọn **Mở quán**. Cuối ca tối, xem khách đã phục vụ, khách bỏ đi, tiền, boa và thay đổi uy tín trước khi đến chợ đêm. Đóng Shop ngày cuối để xem tổng tiền, điểm, uy tín và món bán chạy.

Điểm là `earned + 100 × floor(reputation)`. `earned` gồm tiền món và tiền boa, tính theo nghìn đồng.

### Test, headless và benchmark

Chạy các lệnh sau từ thư mục gốc của repo.

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v                              # toàn bộ test (1 lệnh)
python3 -m chonoi.headless --mode day --days 1 --seed 42 --ticks 22200 --out day.jsonl    # headless_cmd
python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json                          # bench_cmd (có render)
python3 -m chonoi.soak --seed 7 --days 10 --out soak.json                                  # soak_cmd
```

Các lệnh khai trong [game.contract.json](game.contract.json) (Contract v1.3): `run_cmd`, `headless_cmd`, `bench_cmd`, `soak_cmd`.

- **Benchmark** cần thêm Google Chrome hoặc Chromium (tự tìm; hoặc `--browser <đường dẫn>`, biến `CHONOI_BENCH_BROWSER`). Lệnh mở cảnh lặn lõi seed 42 bằng chính giao diện Canvas của game ở 1280×720, Út Sen đứng yên ở bến, làm nóng 3 s rồi đo, ghi `bench.json` gồm `avg_fps, p1_low_fps, frames, measured_s, load_ms`. Thêm `--headed` để xem cửa sổ thật.
- **Soak** chạy 10 Ngày trong một tiến trình bằng bot tất định (kế hoạch D1–D5 lặp ở Ngày 6–10), ghi `soak.json` gồm `days, days_completed, crashes, results, duration_s`.
- Kết quả đo của bản phát hành: [docs/proof/phase-4/](docs/proof/phase-4/).

### Cảnh báo và tương phản cao

HUD hiện chữ kèm biểu tượng cho ba cảnh báo: **Thủy quái!** (kèm viền tím khi thủy quái đuổi hoặc ở gần), **Hết hơi!** (oxy cạn dưới nước, thanh oxy đổi màu dưới 25%) và **😠 Khách sắp giận!** (kiên nhẫn dưới 25%). Nhấn **C** hoặc nút *Tương phản* để bật chế độ tương phản cao; lựa chọn được lưu giữa các lần mở game.

## Sáng tạo của nhóm

Cảnh sông Chín Khúc và nhà bè được vẽ bằng Canvas, với HUD bảng gỗ và âm thanh Web Audio tự tổng hợp. Người chơi có thể chỉnh riêng âm lượng Master, Nhạc và Hiệu ứng. Mức âm lượng và trạng thái tắt âm được lưu trong trình duyệt. Các hiệu ứng này chạy trong giao diện web. Lượt chạy headless tiếp tục kiểm luật và dữ liệu theo Test Contract. [Kiểm giao diện](docs/proof/phase-4/web-ui.md) · [Regression](docs/proof/phase-4/test-run-qa.txt)

## Mở rộng đã chọn của nhóm Banana (Extensions)

1. **Cháy món (`burn`).** Khi món chín nằm trên bếp quá 20 giây (`ready_ticks > 1200`), quán phát `dish_burnt`, giải phóng bếp và thử giữ lại nguyên liệu tươi. Đơn thiếu nguyên liệu chuyển sang `unfulfillable`. [Khai báo mở rộng](game.contract.json) · [Test hộp đen](tests/test_qa_ext.py)
2. **Phụ đề SFX.** Các hiệu ứng âm thanh có chú thích trên màn hình, kể cả khi chọn **Tắt âm** trong **Âm thanh**. [Kiểm thử khi tắt âm](docs/proof/phase-4/web-ui.md)

## Lịch 3 giờ

| Mốc | Phase | Hạn tag |
|---|---|---|
| 0:00 | Phase 1 (PRD-0) | `phase-1` trước 1:00 |
| 1:00 | Phase 2 | `phase-2` trước 1:55 |
| 1:55 | Phase 3 | `phase-3` trước 2:30 |
| 2:30 | Phase 4 | `phase-4` + Release `v1.0.0` trước 3:00 |

Hết giờ mỗi phase thì gắn tag rồi đi tiếp; chỗ chưa xong ghi trung thực trong bằng chứng.

## Đánh giá (100 điểm)

| Hạng mục | Điểm |
|---|---|
| Test tự động ẩn (headless, gồm kiểm tra lại phase trước) | 25 |
| Làm việc nhóm (một repo chung, chia việc, tích hợp, đổi yêu cầu) | 25 |
| Kiểm chứng & bằng chứng | 15 |
| Harness AI (AGENTS.md, skill, nhật ký dùng AI) | 10 |
| Đánh giá & retro | 10 |
| Chất lượng sản phẩm (đúng yêu cầu, mở rộng/sáng tạo) | 10 |
| Demo | 5 |

## Quy định

- Dùng AI thoải mái; **không sao chép repo của nhóm khác**; bằng chứng phải thật.
- Nhân vật, bối cảnh là bản gốc của lab; asset ngoài chỉ dùng CC0/CC-BY/MIT hoặc tự tạo, ghi nguồn trong `CREDITS.md`. Không commit API key, token, `.env`.
