# qavu2407-lang — phản tư cá nhân (≤ 200 từ)

- **Tôi đã làm (kèm link commit):**
  - Lát 2 gather: hái nút, mọc lại, bắt cá, hồi chiêu, báo giỏ đầy ([699162a](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/699162a)), kèm 11 test hộp đen ([1747382](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/1747382)).
  - Lệnh và skill kiểm bàn giao kho gather → quan ([dee3574](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/dee3574)).
  - Một lượt thu nguyên liệu thật, file kho và ma trận truy vết phase 1 ([70e62ee](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/70e62ee), [f8e898f](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/f8e898f), [fc28c66](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/commit/fc28c66)).
  - Hợp đồng file kho, giao diện sim ↔ UI và bảng sự kiện trong `docs/contracts/README.md`.
- **Tôi đã review (kèm link):** chưa review PR nào trong phase 1. Đã gộp thử nhánh lát 3 (`NguyenNgocVinh`) với nhánh của tôi: không xung đột, test xanh.
- **AI sai ở đâu và tôi phát hiện thế nào:** dựng sai fixture test (cá ở d = 0.5 vẫn là mặt nước), lộ ra khi test đỏ. Quên `.gitignore` chặn `*.jsonl` nên thiếu file bằng chứng, lộ ra khi kiểm trên bản checkout sạch.
- **Điều tôi học được:** cho AI đọc đúng PRD trước khi code thì luật ra đúng ngay, chỗ hay sai là dữ liệu test. Bằng chứng phải kiểm trên bản clone sạch, không phải trên máy mình.
