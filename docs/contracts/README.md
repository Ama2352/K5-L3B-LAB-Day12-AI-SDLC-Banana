# Hợp đồng tích hợp (PR đầu tiên của nhóm, cần 2 approval độc lập)

Điền trong 15 phút kickoff:
1. **Schema file kho** — khớp mục 13.6 của Test Contract (kho ghi khi `gather_end`) + một file kho mẫu hợp lệ: `inventory.sample.json`.
2. **Giao diện giữa `sim/*` và `client/ui`** — trạng thái nào UI được đọc, lệnh nào UI gửi vào.
3. **Danh sách sự kiện** — tên, `data`, ai phát, ai nghe (gather: `gather`, `node_regrown`, `hold_full`, `fish_caught`, `gather_end`...; quan: theo mục 13.7).

Mọi thay đổi sau PR đầu: PR riêng + ADR trong `docs/adr/`.
