# Clarify — câu hỏi và câu trả lời (PO ghi, cả nhóm dùng chung)

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Ai quyết |
|---|---|---|---|---|
| 1 | 2026-11-21 | Khách đến đúng tick nào và được xử lý trước hay sau khách hết kiên nhẫn và thao tác tại bếp? | Đã xác nhận tại F.1–F.5. Tăng phase_tick rồi giảm timer, xử lý bếp và tương tác, xử lý khách theo ID bàn, cuối cùng mới xét lượt đến nếu còn giờ. | PO / giảng viên |
| 2 | 2026-11-21 | Nếu còn nhiều bàn trống hoặc có nhiều món đủ nguyên liệu, chọn bàn và món theo quy tắc nào? | Đã xác nhận tại F.5. Bỏ lượt nếu hết bàn. Lấy bàn trống ID nhỏ nhất và chọn đều theo seed trong các món đủ tồn khả dụng. | PO / giảng viên |
| 3 | 2026-11-21 | Khách giảm kiên nhẫn ở những trạng thái nào? Khi bỏ đi, xử lý phần đã giữ và uy tín ra sao? | Đã xác nhận tại F.3–F.4. Khách vẫn có thể được phục vụ ở tick kiên nhẫn về 0. Khách còn chờ khi đóng ca rời với closing và giữ nguyên uy tín. Khi rời, nhả phần giữ thô và bỏ món của đơn. Nguyên liệu đã tiêu vẫn ghi nhận. | PO / giảng viên |
| 4 | 2026-11-21 | Tên và trường dữ liệu chính xác của các sự kiện khách đến, thiếu món và khách rời là gì? | F.5 xác nhận no_dish và F.4 xác nhận lý do closing. Cần bảng sự kiện để xác nhận tên sự kiện đến/rời và các trường bắt buộc. | PO / giảng viên |
