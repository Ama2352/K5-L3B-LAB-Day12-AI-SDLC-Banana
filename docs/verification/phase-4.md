# Ma trận truy vết Phase 4 · QA (TV6)

> Nguồn: TICKET-04 "Phát hành v1.0.0", Test Contract v1.3. Test: `tests/test_qa_p4.py` (17 test; 5 test leaderboard chỉ chạy khi khai mở rộng), `tests/test_qa_ext.py` (burn, 6 test).
> Lệnh: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`. Kết quả: ✅ đạt · ❌ chưa đạt · 🖐 kiểm tay · — không làm.
> Bằng chứng đo trên working tree trước commit (contract 1.3): [test-run-qa.txt](../proof/phase-4/test-run-qa.txt) 330 test, OK (5 skip). **Chạy lại toàn bộ lệnh và bench 30 s trên commit gắn tag `phase-4` / Release v1.0.0 rồi thay dòng đầu các file bằng chứng.**

| AC | Yêu cầu (TICKET-04) | Cách kiểm | Bằng chứng | Kết quả |
|---|---|---|---|---|
| AC-P4-01 | `contract_version: "1.3"`, `bench_cmd`, `soak_cmd` ở gốc; gameplay/tuning/kho/JSONL theo v1.2 | `test_qa_p4.Manifest` | `game.contract.json` | ✅ |
| AC-P4-02 | Soak `--seed 7 --days 10`: đúng 5 trường, `days_completed = days = 10`, `crashes = 0`, `results` theo Ngày, `score` đúng công thức, tất định (bỏ `duration_s`) | `test_qa_p4.Soak` | [soak.json](../proof/phase-4/soak.json) | ✅ |
| AC-P4-03 | Bench `--seed 42 --duration 30`: đúng 5 trường, `avg_fps = frames / measured_s`, `p1_low_fps` 1% khung chậm nhất, `load_ms` | `test_qa_p4.Bench` (3 s) + chạy 30 s | [bench.json](../proof/phase-4/bench.json), [bench-scene.png](../proof/phase-4/bench-scene.png) (khung 1280×720 của cảnh đo) | ✅ |
| AC-P4-03b | Báo cáo mốc: avg ≥ 60, 1% low ≥ 30, load ≤ 10 s | đọc `bench.json` 30 s | `{"avg_fps":60.002,"p1_low_fps":59.524,"frames":1801,"measured_s":30.016,"load_ms":1471.4}` | ✅ đạt cả 3 mốc (Chrome headless, khóa 60 Hz) |
| AC-P4-04 | README: ≤ 3 lệnh từ clone sạch, môi trường, điều khiển, lệnh test/headless/bench/soak | `test_qa_p4.ReleaseDocs` + chạy bản sạch (chỉ file theo git) | lệnh 3 README mở máy chủ, `/state` trả `day/gather`; test trong bản sạch OK | ✅ |
| AC-P4-05 | `CHANGELOG.md` theo từng phase; `CREDITS.md`, `LICENSE` | `test_qa_p4.ReleaseDocs` | `CHANGELOG.md`, `LICENSE` (MIT), `CREDITS.md` | ✅ |
| AC-P4-06 | Cảnh báo chữ/biểu tượng: thủy quái gần, oxy sắp hết, khách sắp giận; chế độ tương phản cao; chơi thử cả 3 ở chế độ đó | 🖐 `python3 -m chonoi.live --mode day --days 1`, nhấn C | `docs/proof/phase-4/warn-*.png` (cần chụp) | 🖐 đã có trong giao diện (TV5): `Thủy quái!` + viền tím, `Hết hơi!`, `😠 Khách sắp giận!`, nút/phím C; **chưa chụp ảnh chơi thử** |
| AC-P4-07 | GitHub Release v1.0.0 + bản đóng gói + release notes; tag `phase-4` và Release cùng commit trên `main` | 🖐 trang Release | [release-notes-v1.0.0.md](../release-notes-v1.0.0.md), `git archive` trong đó | 🖐 chờ merge + gắn tag + tạo Release |
| AC-P4-08 | Regression P1–P3 còn hiệu lực ở v1.3 | toàn bộ `tests/` | [test-run-qa.txt](../proof/phase-4/test-run-qa.txt) | ✅ |
| AC-P4-09 | Retro rà hành động P2, một lỗi AI và cách xác minh; `docs/members/<handle>.md` đủ người | 🖐 đọc tay | `docs/retro.md`, `docs/members/` | 🖐 mỗi người tự viết |
| Mở rộng burn | Cháy món: đúng 1.200 tick vẫn bưng, quá thì cháy trước tương tác, giữ lại tươi nhất / `unfulfillable`, theo id bếp | `test_qa_ext.Burn` (6) | `extensions: ["burn"]`, `burn_s: 20` | ✅ |
| Mở rộng audio | Âm lượng Master/Music/SFX lưu giữa các lần mở (không có mã contract) | 🖐 chỉnh, tải lại trang | ảnh chụp | 🖐 |
| Mở rộng khác | leaderboard, phụ đề SFX | `test_qa_p4.Leaderboard` (tự bật khi khai) | — | — không làm |

## Thay đổi Phase 4 (TV6, theo yêu cầu nhóm)
- `chonoi/bench.py` (mới) + bộ đo trong `chonoi/web/index.html` (chỉ bật khi `?bench=1`).
- `game.contract.json`: `1.3`, `bench_cmd`, `soak_cmd` (soak của TV2), `extensions: ["burn"]`, `burn_s: 20`.
- `chonoi/contract.py`: nhận `burn_s` hữu hạn khi khai `burn` (trước luôn bắt `null` theo Phase 1).
- README, `CHANGELOG.md` theo phase, `LICENSE`, `docs/release-notes-v1.0.0.md`; `test_qa_p2/p3` chấp nhận `1.3` (TICKET-04: v1.3 giữ gameplay v1.2).
