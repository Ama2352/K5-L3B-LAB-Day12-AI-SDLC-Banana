# Nhật ký dùng AI (theo phase và theo người)

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|
| Phase 1 | AnhQuanHANU | Gemini / Antigravity | Triển khai Lát 4 (Bếp, bưng bê, phục vụ, thanh toán, uy tín, đóng ca) & Viết bộ test `test_tv4_quan.py` | ~15,000 tokens | AI ban đầu gán tick của dish_ready là 360 thay vì 361 theo quy ước ghi event tại k+1 của PRD-0 mục F |
| Phase 1 | NguyenNgocVinh | OpenAI Codex | Triển khai lát 3 trong `quan.py` và đối chiếu PRD-0 mục F. Khách đến theo lịch, chọn món đủ nguyên liệu, giữ phần cho đơn và rời khi hết kiên nhẫn. | Chưa đo | Bản đầu xử lý khách rời trước lượt tương tác. Sau khi đọc mục F, chuyển xử lý khách rời xuống sau tương tác để vẫn phục vụ được đúng tick kiên nhẫn về 0. Ghi các điểm đã xác nhận và câu hỏi về sự kiện vào `docs/clarify.md`. |
| Phase 1 | NguyenNgocVinh | OpenAI Codex | Gộp phần khách TV3 với bếp TV4, kiểm thử ba ca với bàn T1 và rà bàn giao kho TV2 bằng `check-handoff`. | Chưa đo | Ca hai khách tranh suất cuối dùng hai bàn, nên thay bằng các ca đúng preset Phase 1: T1 bận bỏ lượt, T1 trống thiếu món phát `no_dish`, đơn hợp lệ giữ đúng công thức. Cả ba ca đều đạt. Sau khi lấy code TV2, 46/46 test qua và kho xuất khớp `quan.stock` ở tick 0. |
| Phase 2 | NguyenNgocVinh | OpenAI Codex | Cập nhật dữ liệu quán, bổ sung lọc món theo kế hoạch ngày, kiểm thử bàn giao nguyên liệu mới. | Chưa đo | Rà theo Ticket-02 để giữ đúng quy tắc số suất chỉ là mục tiêu thu gom. Chạy 50/50 test, gồm 4 ca mới cho TV3. |
