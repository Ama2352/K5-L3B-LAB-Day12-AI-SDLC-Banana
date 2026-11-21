# NMCcg — phản tư cá nhân (TV5 · Nguyễn Mạnh Cường)

- **Tôi đã làm.** Thiết kế giao diện gather, quan và HUD bảng gỗ miền Tây trong `chonoi/web/index.html` gồm đồng hồ, oxy, Máu, giỏ cá thể, kho khả dụng, trạng thái bếp, món gọi và kiên nhẫn. Bổ sung cảnh báo, tương phản cao, âm thanh Web Audio và thực đơn (H). Cập nhật README và CREDITS. [b7ed045](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/b7ed045) · [0701889](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/0701889) · [152e8db](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/152e8db)
- **Tôi đã review.** Rà cấu trúc snapshot/events của gather và quán cùng TV2, TV4 để giao diện đọc đúng dữ liệu bàn giao.
- **AI sai ở đâu và tôi phát hiện thế nào.** AI từng đặt JavaScript bên trong thẻ `<style>` và bỏ sót `hold[]` dạng `{id, kind, fresh}`. Tôi phát hiện khi đọc lại mã và đối chiếu schema mới.
- **Điều tôi học được.** Tách hiển thị chỉ đọc snapshot/events khỏi mô phỏng giúp phát triển song song và giữ tính tất định của test.
