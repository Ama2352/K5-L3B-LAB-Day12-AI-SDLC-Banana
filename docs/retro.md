# Retro nhóm Banana

## Phase 2

- Sáu người phát triển các lát trên nhánh riêng. Kho mẫu và smoke hai tiến trình cho phép người làm quán kiểm thử trước khi hoàn tất tích hợp. [Bằng chứng bàn giao](proof/phase-2/integration.txt)
- Bản QA ban đầu thiếu kiểm tra khách đến nên vẫn xanh khi lát khách chưa tích hợp. Sau khi đối chiếu ma trận AC và chạy trực tiếp quán có kho, QA phát hiện thiếu `customer_arrived` và bổ sung ca kiểm. [Nhật ký AI](ai-usage-log.md) · [Ma trận Phase 2](verification/phase-2.md)
- **Hành động cho Phase 3.** TV2, TV3 và Integrator rà schema kho chung, chạy smoke file và thử vòng ngày có nguyên liệu thật trước khi bàn giao.

## Phase 4

- **Rà hành động Phase 2.** TV2 ghi schema kho cá thể, TV3 xử lý giữ nguyên liệu theo ID và QA chuyển fixture hồi quy. Smoke hai tiến trình kiểm được ID, loại và độ tươi. Thử vòng ngày có hàng phát hiện kiểm fixture đầu ca tối còn đọc kho đếm. Integrator giữ bản sửa kiểm fixture khi giải xung đột PR #13. [Schema v1.2](contracts/kho-v1.2.md) · [Smoke Phase 3](proof/phase-3/handoff.txt) · [c85fd02](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/c85fd02)
- **Điều làm tốt.** Test hộp đen được mở rộng từ gather sang quán, bàn giao kho, vòng ngày và hai biên quanh ngưỡng ươn. Phần benchmark dùng chính giao diện Canvas. Kết quả kiểm bản bàn giao nằm ở [ma trận Phase 4](verification/phase-4.md).
- **Điều cần sửa.** Công việc tích hợp và rà xung đột dồn về cuối. Tag `phase-3` trên GitHub trỏ tới `a0e694f` và được tạo sau hạn Phase 3. Workflow CI có bước kiểm tra PR và `main`. Bằng chứng bàn giao nằm ở các lượt chạy riêng. [Tag Phase 3](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/tree/phase-3) · [Workflow CI](../.github/workflows/ci.yml)
- **Một lỗi AI.** Fixture giá món ban đầu kỳ vọng 90 vì dùng độ tươi ở đầu tick. Khi test trả về 89, TV4 đối chiếu thứ tự trong TICKET-03, xác nhận nguyên liệu hao tươi trước tương tác nấu rồi cập nhật kỳ vọng. [Phản tư TV4](members/AnhQuanHANU.md) · [Test giá món](../tests/test_tv4_phase3.py)
- **Hành động tiếp theo.** Integrator và QA thêm smoke vòng ngày có hàng cùng smoke file kho vào lượt chạy trước khi gộp thay đổi schema. Kiểm riêng commit gắn tag và ghi SHA ngay trong bằng chứng.
- **Rà tài nguyên.** Canvas 2D, CSS và Web Audio tự tạo. Giấy phép MIT ở gốc repo. [CREDITS](../CREDITS.md) · [LICENSE](../LICENSE)

### Bằng chứng đóng góp

Các số dưới đây đếm commit có nội dung ngoài merge tới `7a84eae`. Sau mốc này, TV1 sửa hồi quy ở hai phía ngưỡng ươn tại [577acf1](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/577acf1), nâng số commit ngoài merge của TV1 lên 3. Hai commit xử lý xung đột của TV1 có diff riêng khi chạy `git show --remerge-diff`.

| Thành viên | Commit ở mốc `7a84eae` | Bằng chứng tiêu biểu |
|---|---:|---|
| [TV1 · Ama2352](members/Ama2352.md) | 2 | Sinh tồn [0d867a1](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/0d867a1), vòng ngày [58a4241](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/58a4241), giải xung đột có thay đổi ở [c85fd02](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/c85fd02) và [cf21bc9](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/cf21bc9) |
| [TV2 · qavu2407-lang](members/qavu2407-lang.md) | 30 | Hái/bắt [699162a](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/699162a), test gather [1747382](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/1747382), kiểm kho [dee3574](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/dee3574), soak [8fd7451](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/8fd7451). GitHub liên kết tên tác giả `Anne` trong 5 commit Phase 1 với tài khoản `qavu2407-lang`. |
| [TV3 · cuakicuc4444](members/cuakicuc4444.md) | 6 | Khách [1f10afe](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/1f10afe), kế hoạch ngày [c39bb57](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/c39bb57), biên độ tươi [71ff7f0](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/71ff7f0) |
| [TV4 · AnhQuanHANU](members/AnhQuanHANU.md) | 15 | Bếp [cde982c](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/cde982c), Shop [52826ff](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/52826ff), cảnh báo kiên nhẫn [1767419](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/1767419) |
| [TV5 · NMCcg](members/NMCcg.md) | 4 | HUD [b7ed045](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/b7ed045), giao diện kho cá thể [0701889](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/0701889), sửa UI [152e8db](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/152e8db) |
| [TV6 · 100678carwyn](members/100678carwyn.md) | 16 | QA P1/P2 [e8428b2](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/e8428b2), QA P3 [323c02e](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/323c02e), benchmark và manifest [5301b6c](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/5301b6c), QA P4 [f78e573](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/f78e573) |

TV4 báo tổng khoảng 68.000 token Gemini/Antigravity qua bốn phase. Các số đã đo và mục chưa đo nằm trong [nhật ký AI](ai-usage-log.md).
