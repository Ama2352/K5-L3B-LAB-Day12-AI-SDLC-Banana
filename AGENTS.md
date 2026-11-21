# AGENTS.md — hướng dẫn chung cho mọi agent AI của nhóm

> Cập nhật file này qua các phase (lịch sử git phải cho thấy điều đó). Ngắn gọn, có lệnh chạy thật.

## Lệnh
- Test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`
- Smoke vòng ngày P2: `python3 -m chonoi.headless --mode day --days 1 --seed 42 --ticks 22200 --out day.jsonl`. Dòng cuối cần có `days_completed: 1` và `reason: "days_complete"`.
- Tích hợp TV1 theo TICKET-02: `runner.Session` dùng chung cho live và headless, quản lý pause, ba đồng hồ và đổi pha. `scenario` kiểm trạng thái đầu ngày; đơn món được đối chiếu với kho thực lúc mở quán. `inputs` xử lý cạnh nút và lệnh mua theo frame. Đây là các thay đổi ở khung để hỗ trợ contract v1.1.
- Headless: `python3 -m chonoi.headless --mode gather|quan --seed 1 --ticks 600 --out out.jsonl`
- Chơi thử trên trình duyệt: `python3 -m chonoi.live --mode day --days 1` (mở địa chỉ in ra, chọn Chơi; WASD, E, Space, Esc)

## Cấu trúc & quy ước
- (Starter Python là TÙY CHỌN; nhóm có thể dùng ngôn ngữ khác nếu giữ Test Contract.) Khung do giảng viên cấp: `chonoi/{headless,inputs,scenario,contract,rng,ids,jsonl,inventory,runner,live}.py` và `chonoi/web/`. Hạn chế sửa; nếu phải sửa thì báo cả nhóm và ghi lại lý do.
- Luật chơi của nhóm: `chonoi/sim/gather.py`, `chonoi/sim/quan.py` (tìm `TODO(nhóm)`).
- **Số liệu chỉ đọc từ `game.contract.json` / dữ liệu**, không hard-code trong luật.
- Mọi số ngẫu nhiên đi qua `Streams` (`chonoi/rng.py`); không dùng `random` toàn cục, không dùng đồng hồ hệ thống.
- Sắp danh sách thực thể bằng `ids.sort_by_id`; cấp id bằng `IdAllocator`.

## Nên tránh
- Không sửa `docs/contracts/`, `game.contract.json` (khóa contract) hoặc schema kho khi chưa báo cả nhóm (đổi hợp đồng ảnh hưởng mọi module).
- Không làm hỏng nhánh chính: trước khi đẩy, chạy test.
- Không bịa yêu cầu: chỗ mơ hồ thì ghi `docs/clarify.md` và hỏi PO.
- Không sửa test cho xanh khi luật sai; phải sửa luật hoặc ghi lý do đổi test trong commit.

## Quy tắc làm việc với agent
- Mỗi agent một việc rõ ràng (một lát). Cho agent đọc PRD/ticket đúng phase và hợp đồng kho trước.
- Agent làm xong phải chạy test và ghi kết quả vào mô tả commit hoặc `docs/proof/`; người đọc lại thay đổi trước khi đẩy.
- Sáng tạo thêm được khuyến khích nhưng phải tắt ở headless (xem README, mục "Tự do sáng tạo").

## Skills / hooks của nhóm
- `check-handoff` (`.agents/skills/check-handoff/SKILL.md`): kiểm file kho gather → quan. Lệnh: `python3 tools/check_handoff.py <gather.jsonl> <kho.json>` (0 khớp / 1 lệch). Chạy trước khi gửi kho cho quán/QA và trước khi gắn tag. Phase 2: đọc 6 loại nguyên liệu từ `game.contract.json`; bằng chứng smoke kho ở `docs/proof/phase-2/integration.txt`. Phase 3: tự chọn schema theo `contract_version` (v1.2 so từng cá thể id/kind/fresh); chạy thử v1.2 bằng `CHONOI_CONTRACT=docs/proof/phase-3/contract-v1.2.json`.
- Lệnh QA soak (TV2): `python3 -m chonoi.soak --seed 7 --days 10 --out soak.json`. Trước phát hành, kiểm `days_completed: 10`, `crashes: 0` và kết quả hai lần chạy khớp khi bỏ `duration_s`. Sau đó chạy benchmark render 30 giây theo README.
