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

Mở địa chỉ in trong terminal, mặc định là `http://127.0.0.1:8000/`. Nhấn `Ctrl+C` để dừng máy chủ.

| Phím hoặc nút | Thao tác |
|---|---|
| WASD hoặc phím mũi tên | Bơi và đi bộ |
| E | Cập bến, hái rau hoặc tương tác với bếp và bàn |
| Space | Bắt cá dưới nước |
| P hoặc Esc | Tạm dừng hoặc tiếp tục |
| R | Chơi lại |
| Nút trên màn hình Shop | Mua nâng cấp hoặc đóng Shop để hoàn thành ngày |

Điểm là `earned + 100 × floor(reputation)`. `earned` gồm tiền món và tiền boa, tính theo nghìn đồng.

### Test, headless và benchmark

Chạy các lệnh sau từ thư mục gốc của repo.

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
python3 -m chonoi.headless --mode day --days 1 --seed 42 --ticks 22200 --out day.jsonl
```

Để benchmark có render, dùng `bench_cmd` trong [game.contract.json](game.contract.json) của bản tích hợp Phase 4. Lệnh dưới lấy cấu hình từ manifest và chạy với seed 42 trong 30 giây để ghi `bench.json`.

```bash
python3 -c 'import json, shlex, subprocess; cmd = json.load(open("game.contract.json", encoding="utf-8")).get("bench_cmd"); assert cmd, "bench_cmd is missing from game.contract.json"; subprocess.run([*shlex.split(cmd), "--seed", "42", "--duration", "30", "--out", "bench.json"], check=True)'
```

## Tự do sáng tạo

Ngoài phần đề yêu cầu, nhóm được **thêm** nhân vật, loài cá/cây, sinh vật, món, bản đồ, cơ chế, câu chuyện, đồ họa, âm nhạc… với ba điều kiện: **không phá phần cố định** (tắt ở headless), ghi mục **"Sáng tạo của nhóm"** trong README của nhóm, và **làm lõi đúng trước**.

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
