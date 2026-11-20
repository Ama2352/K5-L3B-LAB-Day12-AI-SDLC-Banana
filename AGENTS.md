# AGENTS.md — hướng dẫn chung cho mọi agent AI của nhóm

> Cập nhật file này qua các phase (lịch sử git phải cho thấy điều đó). Ngắn gọn, có lệnh chạy thật.

## Lệnh
- Test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`
- Headless: `python3 -m chonoi.headless --mode river|quan --seed 1 --ticks 600 --out out.jsonl`

## Cấu trúc & quy ước
- Khung do giảng viên cấp: `chonoi/{cli-headless,inputs,scenario,rng,ids,jsonl,inventory,runner}.py`. Hạn chế sửa; nếu phải sửa thì qua PR riêng có ADR.
- Luật chơi của nhóm: `chonoi/sim/river.py`, `chonoi/sim/quan.py` (tìm `TODO(nhóm)`).
- **Số liệu chỉ đọc từ `game.contract.json` / dữ liệu**, không hard-code trong luật.
- Mọi số ngẫu nhiên đi qua `Streams` (`chonoi/rng.py`); không dùng `random` toàn cục, không dùng đồng hồ hệ thống.
- Sắp danh sách thực thể bằng `ids.sort_by_id`; cấp id bằng `IdAllocator`.

## Cấm
- Không sửa `docs/contracts/`, `game.contract.json` (khóa contract) hoặc schema kho mà không qua PR có 2 approval.
- Không đẩy thẳng lên `main`; không tắt/vượt CI.
- Không bịa yêu cầu: chỗ mơ hồ thì ghi `docs/clarify.md` và hỏi PO.
- Không sửa test cho xanh khi luật sai; phải sửa luật hoặc ghi lý do đổi test trong PR.

## Quy tắc làm việc với agent
- Một agent / một nhánh / một issue. Cho agent đọc PRD/ticket đúng phase và `docs/contracts/` trước.
- Agent làm xong phải chạy test và dán kết quả vào PR; người đọc lại diff trước khi mở PR.

## Skills / hooks của nhóm
- (Ghi tên và khi nào dùng; tối thiểu 2 skill/hook/command nhóm tự viết, đặt ở `.agents/skills/` hoặc tương đương.)
