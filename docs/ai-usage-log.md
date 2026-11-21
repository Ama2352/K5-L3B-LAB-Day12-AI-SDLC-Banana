# Nhật ký dùng AI (theo phase và theo người)

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|
| Phase 1 | AnhQuanHANU | Gemini / Antigravity | Triển khai Lát 4 (Bếp, bưng bê, phục vụ, thanh toán, uy tín, đóng ca) & Viết bộ test `test_tv4_quan.py` | ~15,000 tokens | AI ban đầu gán tick của dish_ready là 360 thay vì 361 theo quy ước ghi event tại k+1 của PRD-0 mục F |
| Phase 1 | qavu2407-lang | Claude Code / Claude Opus 5.5 | Lát 2 gather (hái, mọc lại, bắt cá, hồi chiêu, giỏ đầy), 11 test, lệnh + skill kiểm bàn giao kho, lượt thu thật, hợp đồng kho/sự kiện | Không đo | (1) Dựng fixture test sai: đặt cá ở d = 0.5 (vẫn là mặt nước) và người chơi trong vùng bến; phát hiện khi test đỏ. (2) Quên `.gitignore` bỏ qua `*.jsonl` nên file bằng chứng `gather.jsonl` không được commit; phát hiện khi gộp thử trên bản sạch thì `check_handoff` báo không thấy file. (3) Tự chọn rebase lên `main` khi chưa hỏi; tôi dừng lệnh và chọn chỉ push nhánh. |
| Phase 2 | AnhQuanHANU | Gemini / Antigravity | Triển khai module `ShopSim` (nâng cấp oxygen/hp, kiểm tra funds/max_level, đóng ca shop) & Mở rộng Cháy món (`burn_s`, dish_burnt, auto-reorder) & Bộ test Phase 2 | ~18,000 tokens | Cần chú ý thứ tự xử lý lệnh buy trước cạnh shop_done trong cùng tick và quy tắc mốc burn_s (đúng 1200 tick vẫn bưng được, > 1200 mới cháy) |
