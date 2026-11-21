# AnhQuanHANU — phản tư cá nhân (≤ 200 từ)

- **Tôi đã làm.** Lát 4 quán: bếp, bưng, phục vụ, tiền boa, uy tín, đóng ca ([cde982c](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/cde982c)). Shop và Cháy món ở phase 2 ([52826ff](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/52826ff)). Tính giá theo độ tươi và kho cá thể ở phase 3. Cảnh báo khách sắp giận ở phase 4 ([1767419](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/1767419)). Test hộp đen: `tests/test_tv4_quan.py` và `tests/test_tv4_phase2.py` đến `phase4.py`.
- **Tôi đã giúp ai.** Đối chiếu giao diện lát khách với TV3 để giữ đúng thứ tự interact. Đọc chéo cảnh báo khách sắp giận với HUD của TV5.
- **AI sai ở đâu.** Phase 1: AI đặt tick `dish_ready` là 360, trong khi PRD-0 mục F ghi event ở k+1 là 361. Phát hiện qua test runner. Phase 3: AI tính giá món trước khi trừ hao tươi một tick, cho 89 thay vì 90. Sửa theo thứ tự tick trong đề.
- **Điều tôi học được.** Thứ tự xử lý trong một tick quyết định kết quả ở ca biên. Khi giá phụ thuộc độ tươi, phải ghi rõ bước nào chạy trước.
