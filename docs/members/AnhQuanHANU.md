# AnhQuanHANU — phản tư cá nhân (≤ 200 từ)

- **Tôi đã làm (kèm link commit):**
  - Cài đặt toàn bộ Lát 4 của chế độ Mở Quán (`sim/quan`): logic Bếp nấu món, bưng bê, phục vụ tại bàn, tính tiền món và tiền boa (`tip`), cộng điểm uy tín (`reputation`), xử lý khách ăn xong hoặc thanh toán khi đóng ca.
  - Viết bộ unit test chuyên biệt `tests/test_tv4_quan.py` kiểm chứng toàn diện các sự kiện: `cook_started`, `dish_ready`, `dish_picked`, `served`, `paid`, `quan_end`.
  - Thiết kế kịch bản test mẫu `tests/scenarios/test_tv4_bep.json` để TV6 (QA) nghiệm thu độc lập.

- **Tôi đã review (kèm link):**
  - Rà soát giao diện kết nối giữa Lát 3 (Khách) và Lát 4 (Bếp) với TV3, đảm bảo thứ tự ưu tiên interact và cấu trúc dữ liệu khách hàng khớp 100% PRD-0.

- **AI sai ở đâu và tôi phát hiện thế nào:**
  - AI ban đầu tính mốc tick của sự kiện `dish_ready` là tick 360, nhưng theo hợp đồng PRD-0 mục F ("bước k biến trạng thái k thành k+1 và ghi event tại k+1"), tick của event phải là 361. Tôi đã phát hiện qua test runner và điều chỉnh lại kiểm thử cho khớp hoàn toàn quy ước event tick của giảng viên.

- **Điều tôi học được:**
  - Kỹ năng chia nhỏ lát cắt tính năng (slice-based development) để phát triển và kiểm thử độc lập mà không bị nghẽn (block) bởi các thành viên khác trong nhóm.

