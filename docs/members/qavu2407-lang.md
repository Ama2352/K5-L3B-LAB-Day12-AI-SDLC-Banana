# qavu2407-lang — phản tư cá nhân (≤ 200 từ)

- **Tôi đã làm (kèm link commit):**
  - Lát 2 gather: hái nút, mọc lại, bắt cá, hồi chiêu, báo giỏ đầy ([699162a](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/699162a)), kèm 11 test hộp đen ([1747382](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/1747382)).
  - Lệnh và skill kiểm bàn giao kho gather → quan ([dee3574](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/dee3574)).
  - Một lượt thu nguyên liệu thật, file kho và ma trận truy vết phase 1 ([70e62ee](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/70e62ee), [f8e898f](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/f8e898f), [fc28c66](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/fc28c66)).
  - Hợp đồng file kho, giao diện sim ↔ UI và bảng sự kiện trong `docs/contracts/README.md`.
- **Tôi đã review (kèm link):** chưa review PR nào trong phase 1. Đã gộp thử nhánh lát 3 (`NguyenNgocVinh`) với nhánh của tôi: không xung đột, test xanh.
- **AI sai ở đâu và tôi phát hiện thế nào:** dựng sai fixture test (cá ở d = 0.5 vẫn là mặt nước), lộ ra khi test đỏ. Quên `.gitignore` chặn `*.jsonl` nên thiếu file bằng chứng, lộ ra khi kiểm trên bản checkout sạch.
- **Điều tôi học được:** cho AI đọc đúng PRD trước khi code thì luật ra đúng ngay, chỗ hay sai là dữ liệu test. Bằng chứng phải kiểm trên bản clone sạch, không phải trên máy mình.

## Phase 2 (≤ 200 từ)

- **Tôi đã làm (kèm link commit):**
  - Gather v1.1: cá kèo, kèo nèo N5/N6, 8 đàn đầu ca, cá bơi/đổi hướng/phản xạ mép, sinh cá 360·k, trần 12 ([ac7342e](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/ac7342e), [d922e4e](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/d922e4e)).
  - 20 test hộp đen `tests/test_gather_p2.py` ([4d8f704](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/4d8f704)); `check_handoff` đọc 6 loại từ contract ([aed7a48](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/aed7a48)).
  - Smoke kho tích hợp `docs/proof/phase-2/` ([28cb1f3](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/28cb1f3)); hợp đồng kho v1.1 và 4 giả định trong `clarify.md` ([c7c63ba](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/c7c63ba)).
- **Tôi đã review (kèm link):** gộp thử nhánh của mình với `main` sau PR #4/#5 và nhánh `AnhQuanHANU`: không xung đột code, `check_handoff` khớp; báo Ama2352 test sinh tồn đỏ vì fixture đặt cá ngoài miền bơi v1.1.
- **AI sai ở đâu và tôi phát hiện thế nào:** hợp đồng ghi mode `day` đã có khi chưa có, lộ ra khi chạy thử lệnh. AI còn tự sửa test của người khác, tôi hoàn tác. Bằng chứng smoke cũ không tái lập vì Cá Sấu cắn rơi cá; phát hiện nhờ chạy lại test và `cmp`.
- **Điều tôi học được:** bằng chứng phải chạy lại sau mỗi lần gộp, vì luật của người khác có thể đổi kết quả của mình. Câu "đã có" trong tài liệu cần lệnh chứng minh.

## Phase 3 (≤ 200 từ)

- **Tôi đã làm (kèm link commit, PR #11):** [0cae76e](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/0cae76e), [2c6f35d](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/2c6f35d), [0729ed5](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/0729ed5), [85e8e58](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/85e8e58), [17776ce](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/17776ce), [885c5c4](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/885c5c4), [8a57360](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/8a57360)
  - Kho cá thể v1.2 `{id, kind, fresh}` trong `inventory.py`: đọc/ghi, từ chối kho đếm, id trùng.
  - Gather v1.2: độ tươi trong giỏ (số nguyên 240 đơn vị/điểm), `spoiled` đúng một lần theo id, id I1.., `lost` dạng cá thể.
  - Công tắc `is_v12` theo `contract_version`, `check_handoff` so từng cá thể, 13 test `tests/test_kho_v12.py`, bằng chứng `docs/proof/phase-3/`, CHANGELOG và `docs/contracts/kho-v1.2.md`.
- **Tôi đã review (kèm link):** chạy bàn giao file với quán P3 của TV3 trên `main`: KHỚP. Chạy `day` v1.2 có hàng: vỡ ở `check_evening_fixture`, đã báo TV1. Thử bật preset `1.2`: 23 test cũ đỏ, cần chủ test chuyển.
- **AI sai ở đâu và tôi phát hiện thế nào:** AI ghi `day` v1.2 chạy được dựa trên lượt giỏ rỗng; chạy lại có input mới lộ lỗi. AI lỡ đổi index git khi gộp thử, thấy qua `git status`.
- **Điều tôi học được:** smoke phải có dữ liệu thật đi qua ranh giới; lượt rỗng chứng minh rất ít. Công tắc phiên bản giữ `main` chạy trong lúc chuyển.

## Phase 4 (≤ 200 từ)

- **Tôi đã làm (kèm link commit, PR #12):**
  - `soak_cmd`: `python3 -m chonoi.soak` chạy 10 Ngày một tiến trình bằng bot tất định, kế hoạch D1–D5 lặp, xuất `soak.json` ([8fd7451](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/8fd7451)); bằng chứng 10/10 Ngày ở v1.1 ([d773117](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/d773117)).
  - Adapter nhận contract 1.3 như v1.2 ([a05688e](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/a05688e)); 5 test lát 2 chạy được cả kho đếm và kho cá thể ([13acab4](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/13acab4)).
- **Tôi đã giúp ai:** chia việc Phase 4 cho nhóm kèm bảng test đỏ theo người khi bật v1.2. Soak chỉ ra lỗi `check_evening_fixture` chặn v1.3, đã ghi trong PR #12 cho Sang.
- **AI sai ở đâu và tôi phát hiện thế nào:** bot đầu tiên đo giỏ trước khi bước chạy nên không bao giờ thấy đã hái; lộ ra khi in sự kiện `gather_end` từng Ngày. AI sửa test của QA và test starter khi tôi giao nhầm "phần QA"; tôi dừng lệnh, nói lại phạm vi, AI hoàn tác.
- **Điều tôi học được:** bot soak phải đưa hàng thật qua ranh giới mới bắt được lỗi bàn giao. Sửa file của người khác phải hỏi trước, kể cả khi làm test xanh.
