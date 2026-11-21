# Ma trận truy vết Phase 1

| AC | Cách kiểm chứng | Bằng chứng (link `docs/proof/phase-1/...`) | Kết quả (đạt / chưa đạt — ghi trung thực) |
|---|---|---|---|
| Hái nút ở mặt nước (gần nhất, hòa theo id, đúng mép bán kính), dưới nước không hái | `tests/test_gather_l2.py::Harvest` | [gather.jsonl](../proof/phase-1/gather.jsonl) tick 151, 801 | đạt |
| Mọc lại: regrow 1200 tick, `node_regrown` rồi hái được ngay | `Harvest.test_moc_lai_roi_hai_duoc_ngay` | test | đạt |
| Giỏ đầy: `hold_full` (action, id, required, free), nút/đàn giữ nguyên, không hồi chiêu | `Harvest.test_gio_day_*`, `Catch.test_gio_thieu_cho_*` | test | đạt |
| Bắt cá dưới nước: yield theo loài, xóa đàn, `fish_caught` | `Catch.test_bat_ca_linh_*` | [gather.jsonl](../proof/phase-1/gather.jsonl) tick 263, 596 | đạt |
| Hồi chiêu 30 tick (đặt ở t, dùng lại từ t+30); không có đàn trong tầm thì không hồi | `Catch.test_hoi_chieu_*`, `Catch.test_khong_co_dan_*` | test | đạt |
| Cập bến → `gather_end` docked, kho ghi một lần, khớp event | `DockAfterGather`, `test_smoke_p1` | [kho.json](../proof/phase-1/kho.json) | đạt |
| Bàn giao kho: quán đọc đúng `stock` | `python3 tools/check_handoff.py docs/proof/phase-1/gather.jsonl docs/proof/phase-1/kho.json` | [handoff.txt](../proof/phase-1/handoff.txt) | đạt (KHỚP 6 món) |
| Tất định: cùng seed + inputs → JSONL và kho giống từng byte | chạy 2 lần + `cmp` | lệnh ở [handoff.txt](../proof/phase-1/handoff.txt) | đạt |

## Đánh giá ngắn
- Yêu cầu nào đạt / chưa đạt:
- Điều cần chỉnh cho phase sau:
