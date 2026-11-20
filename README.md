# Day 12 — AI SDLC: Quán Ăn Chợ Nổi (làm theo nhóm)

> **Nhóm 4–6 người** · Áp dụng SDLC cùng AI để xây game **2D** *Quán Ăn Chợ Nổi* qua **4 phase** trong **3 giờ**: Út Sen chèo xuồng đi lấy nguyên liệu buổi sáng, tối mở quán phục vụ khách.
> Yêu cầu từng phase được phát tại **lab board** (đúng mốc giờ). Repo này chỉ chứa **khung kỹ thuật** và **mẫu quy trình** của nhóm.

## Cách vào lab (trưởng nhóm làm, ~5 phút)

1. **Fork** repo này về tài khoản của trưởng nhóm. Đặt tên fork: `Day12-ChoNoi-<ten-nhom>`.
2. **Thêm thành viên:** *Settings → Collaborators → Add people* (quyền **Write**) cho tất cả thành viên **và giảng viên** (handle do giảng viên thông báo).
3. **Bật Actions** cho fork: tab *Actions → I understand my workflows, enable them*.
4. **Bảo vệ `main`:** *Settings → Rules → Rulesets → New ruleset → Import a ruleset* → chọn file [`.github/ruleset-main.json`](.github/ruleset-main.json). Không thêm bypass cho ai (kể cả trưởng nhóm).
5. **Điền danh sách thành viên** trong [`TEAM.md`](TEAM.md) và `team_size` trong [`game.contract.json`](game.contract.json) — làm bằng một PR đầu tiên (xem dưới).

## Danh sách thành viên là điều kiện để commit được nhận

Check `ci / test` chạy [`tools/check_team.py`](tools/check_team.py) trên **mọi PR và mọi commit lên `main`**. Check đỏ (không gộp được) nếu:
- `TEAM.md` chưa có bảng thành viên đủ **4–6 người** với GitHub handle thật, tên và module chính;
- `team_size` trong `game.contract.json` khác số thành viên;
- người mở PR **không có trong danh sách**.

Ghi `Co-authored-by: Tên <email>` trong commit khi làm cặp. Thành viên mới vào nhóm: sửa `TEAM.md` bằng PR.

## 3 lệnh để bắt đầu

```bash
git clone <fork-của-nhóm> && cd <fork-của-nhóm>
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v     # smoke test (phải xanh; nếu dùng starter Python)
python3 -m chonoi.headless --mode river --seed 1 --ticks 600 --out out.jsonl
```

## Công nghệ: tự chọn (starter chỉ là gợi ý, KHÔNG bắt buộc)

Nhóm được dùng **bất kỳ ngôn ngữ/engine nào**. Thứ duy nhất bắt buộc là **Test Contract** (chế độ headless theo tài liệu phase) và `game.contract.json` khai đúng `build_cmd`, `headless_cmd`.

`chonoi/` là một khung **Python 3** (chỉ thư viện chuẩn) giảng viên làm sẵn để tiết kiệm thời gian: đọc tham số, đọc inputs/scenario/kho, kiểm lỗi (mã thoát 2), vòng tick 60 Hz, RNG có seed, cấp/sắp id, ghi JSONL tất định, ghi file kho an toàn. **Luật chơi do nhóm viết** (tìm `TODO(nhóm)`). Dùng hay không tùy nhóm.

| Khung Python đã có | Nhóm viết |
|---|---|
| CLI + kiểm lỗi, mã thoát 0/1/2 | `chonoi/sim/river.py`: hái, chài, xoáy, lật xuồng, hết phao |
| Đọc inputs, cạnh lên, chuẩn hóa vector | `chonoi/sim/quan.py`: khách, giữ chỗ, bếp, bưng, phục vụ, tiền, uy tín |
| Chèo xuồng, chặn mép, cập bến, hết giờ | Nút hái / bầy cá / xoáy mặc định của màn |
| Đọc/ghi file kho, ghi nguyên tử | Kiểm mâu thuẫn scenario mức luật (`scenario.py`) |
| JSONL tất định, làm tròn 3 chữ số, sắp id | Hiển thị / HUD (khung **chưa có cửa sổ**: tự chọn thư viện 2D) |

### Nếu nhóm đổi sang ngôn ngữ khác (một PR, Integrator duyệt)
1. Sửa `build_cmd`, `run_cmd`, `headless_cmd` trong `game.contract.json` cho ngôn ngữ của nhóm.
2. Sửa bước **Build** và **Test** trong `.github/workflows/ci.yml` (cài runtime cần thiết). **Giữ tên job `ci / test`** và giữ bước kiểm danh sách thành viên.
3. **Giữ** `tests/test_smoke_p1.py`: đây là test **hộp đen**, chỉ chạy `headless_cmd` rồi đọc JSONL/file kho, nên dùng nguyên cho mọi ngôn ngữ. **Xóa** `chonoi/` và `tests/test_python_starter_units.py` nếu không dùng; viết unit test bằng ngôn ngữ của nhóm.
4. Vẫn phải qua cùng Test Contract: cùng seed → output giống từng byte.

Lưu ý: `tools/check_team.py` (kiểm danh sách thành viên) là script Python chạy **chỉ trong CI**, không liên quan tới ngôn ngữ của game; giữ nguyên.

## Quy tắc vàng

- Số liệu chỉ nằm trong `game.contract.json`; luật chỉ đọc từ đó.
- Ngẫu nhiên chỉ qua `Streams`; không dùng đồng hồ hệ thống. Cùng seed → output giống từng byte.
- **Không push thẳng `main`.** Mọi thay đổi qua PR (mẫu: `.github/pull_request_template.md`), cần ≥ 1 người khác duyệt và `ci / test` xanh.
- Mỗi PR một việc, có issue, có bằng chứng.

## Tài liệu trong repo

[`TEAM.md`](TEAM.md) (vai + thỏa thuận nhóm) · [`AGENTS.md`](AGENTS.md) · `docs/contracts/` (PR hợp đồng đầu tiên) · `docs/{plan,verification,proof,adr,members}/` · `docs/{clarify,standup,retro,ai-usage-log}.md`.
