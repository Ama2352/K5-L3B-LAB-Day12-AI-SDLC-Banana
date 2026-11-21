# Ma trận kiểm chứng Phase 4

Yêu cầu lấy từ TICKET-04 và Test Contract v1.3. Các bằng chứng dưới đây thuộc nội dung ứng dụng của bản bàn giao. Manifest giữ gameplay, kho và JSONL của v1.2.

| AC | Yêu cầu | Kiểm chứng | Kết quả |
|---|---|---|---|
| AC-P4-01 | Manifest v1.3 khai `bench_cmd` và `soak_cmd` | `test_qa_p4.Manifest` và `game.contract.json` | Đạt |
| AC-P4-02 | Soak seed 7, 10 Ngày, 0 crash. Kết quả lặp theo seed khi bỏ thời gian chạy | [Hai lượt soak](../proof/phase-4/soak.txt), [JSON](../proof/phase-4/soak.json) | Đạt |
| AC-P4-03 | Render cảnh lặn seed 42 ở 1280×720, làm nóng 3 s, đo 30 s và xuất đúng năm trường | `test_qa_p4.Bench`, [JSON đo](../proof/phase-4/bench.json), [cảnh đo](../proof/phase-4/bench-scene.png) | Đạt |
| AC-P4-03b | Mốc báo cáo avg ≥ 60 FPS, 1% low ≥ 30 FPS, load ≤ 10 s | Bench ở trên | avg 55.15 FPS (dưới mốc) · 1% low 13.75 FPS (dưới mốc) · tải 1.71 s (đạt) (Chrome 157 headless trên Windows) |
| AC-P4-04 | Mở giao diện từ checkout sạch trong ba lệnh README. Có yêu cầu môi trường, điều khiển, test/headless/bench/soak | `test_qa_p4.ReleaseDocs`, smoke README trên Ubuntu CI, [smoke ZIP](../proof/phase-4/package.txt) | Đạt |
| AC-P4-05 | CHANGELOG theo phase, ghi chú phát hành, credits và giấy phép | [CHANGELOG](../../CHANGELOG.md), [ghi chú phát hành](../release-notes-v1.0.0.md), [CREDITS](../../CREDITS.md), [MIT](../../LICENSE) | Đạt |
| AC-P4-06 | Đủ ba cảnh báo có chữ và kiểm ở chế độ tương phản cao | [Chrome và ảnh](../proof/phase-4/web-ui.md) | Đạt |
| AC-P4-07 | Tag `phase-4` và Release `v1.0.0` cùng commit trên `main`, có ZIP chạy được và notes | [Tag Phase 4](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/tree/phase-4), [Release](https://github.com/Ama2352/K5-L3B-LAB-Day12-AI-SDLC-Banana/releases/tag/v1.0.0) | Bàn giao sau hạn 3:00 của lab |
| AC-P4-08 | Hồi quy P1–P3 còn hiệu lực, gồm hai biên độ tươi (29.999 và 30.008), kho khớp và vòng ngày hoàn tất | [Regression](../proof/phase-4/test-run-qa.txt), [bàn giao kho và một ngày headless](../proof/phase-4/handoff.txt) | 332 đạt, 5 bỏ qua có chủ đích |
| AC-P4-09 | Rà hành động retro P2, ghi lỗi AI đã kiểm và phản tư của mỗi người | [Retro](../retro.md), [đóng góp theo handle](../members/), [nhật ký AI](../ai-usage-log.md), [làm rõ](../clarify.md), [standup](../standup.md) | ✅ Retro mở đầu bằng rà hành động P2, có điều làm tốt, điều cần sửa, hành động tiếp theo và một lỗi AI kèm cách xác minh (giá món 90 → 89, TV4 đối chiếu TICKET-03). Có đủ 6 file `docs/members/<handle>.md` khớp handle trong `TEAM.md`. Mỗi file nêu phần đã làm, hỗ trợ hoặc review, lỗi AI và bài học, kèm link commit. Cả sáu file đều dưới 200 từ, không tính link (đếm lại ngày cập nhật này) |
| Mở rộng | Cháy món (`burn`), phụ đề SFX | `test_qa_ext.Burn` và [phụ đề lúc tắt âm](../proof/phase-4/web-ui.md) | Đạt |
| Sáng tạo | Master, Nhạc và Hiệu ứng có thanh riêng và lưu qua tải lại trang | [Kiểm âm lượng](../proof/phase-4/web-ui.md) | Đạt |

Lệnh hồi quy là `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`. Năm test bảng xếp hạng bỏ qua vì manifest chọn `burn` và phụ đề SFX.
