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

## Bảng theo dõi TV1 trước khi đồng bộ main

Tham chiếu theo mục của PRD-0 do Sang cung cấp. Kết quả local ghi riêng. Khi bàn giao, TV6 ghi SHA trên main, chạy lại, dẫn log/ảnh đúng bản rồi chốt đạt hoặc chưa đạt từng dòng.

| Yêu cầu PRD-0 | Người | Cách kiểm và bằng chứng | Trạng thái |
|---|---|---|---|
| A–C · preset, CLI, input | TV6 | Đối chiếu preset v1.0, 60 Hz, seed có dấu, tín hiệu cạnh lên và mã thoát 0/1/2. Kiểm input sai trước khi tạo output. | Chờ kiểm bản bàn giao |
| D · fixture | TV3/4/6 | Dựng đơn đúng/sai cho từng trạng thái. Thử giữ quá tồn, khách trùng bàn, bếp và tay cùng giữ một đơn, timer mâu thuẫn, ID tham chiếu thiếu và trường ngoài v1.0. | Chờ kiểm |
| E · JSONL, điểm và tính tất định | TV6 | Kiểm tick 0, event trước snapshot, snapshot cuối duy nhất, lý do gameplay ưu tiên tick_limit. So hai lượt cùng input/seed từng byte cho cả JSONL và kho. Kiểm điểm = earned + 100 × floor(reputation). | Chờ kiểm |
| F · bơi, biên, oxy và giỏ | TV1 | Test di chuyển trong `test_smoke_p1`; [5 test sinh tồn](../../tests/test_gather_survival.py) kiểm biên mặt nước, nhịp ngạt, hồi oxy và thứ tự mất giỏ. [Kho rỗng khi ngất](../proof/phase-1/handoff-tv1-fainted.txt) | Đạt trên nhánh TV1, chờ kiểm lại trên commit bàn giao |
| F · hái, bắt và cập bến | TV2 | Kiểm mép bán kính, hòa theo ID, nút vừa mọc, cả đàn vượt sức chứa, hồi chiêu, cập bến/hái/bắt ở bước cuối. | Chờ hoàn thiện luật và kiểm |
| F · khách, bàn và kho khả dụng | TV3 | Kiểm lịch khách theo phase_tick, kể cả khi rút ngắn ca. Bàn bận bỏ lượt, bàn trống thiếu món phát no_dish. Kiểm giữ/nhả, thu hồi món của đơn hết hạn và uy tín. | Chờ hoàn thiện luật và kiểm |
| F · bếp, bàn, thu tiền | TV4 | Kiểm một interact, bếp trước bàn khi hòa, bỏ lượt nếu đối tượng gần nhất chưa dùng được. Phục vụ ở tick hết kiên nhẫn/hết ca, chốt boa lúc giao và cộng uy tín lúc thu. | Chờ hoàn thiện luật và kiểm |
| G · smoke hai tiến trình | TV2/6 | Đã chạy hai lệnh mục G với seed 42 trên workspace (HEAD `f0a1906`, có thay đổi local). Cập bến tick 1. Inventory trong gather_end, file kho và stock quán tick 0 đều có 2 bong_sung, 1 ca_loc. Khi chạy trên main, lưu log theo §6.3. | Đạt trên workspace, chờ chạy lại trên commit bàn giao |
| G · các nhánh file kho | TV2/6 | Kiểm ngất ghi rỗng, hết giờ giữ giỏ, tick_limit giữ nguyên file có sẵn, ghi nguyên tử. Kiểm quán độc lập kho rỗng, kho quán vượt trần giỏ vẫn hợp lệ. | Chờ kiểm |
| §2–3, §7 · chơi và HUD | TV5/6 | Chơi cả hai ca, nấu từ kho vừa thu, chụp hai màn hình đủ trường HUD theo kế hoạch. Kiểm góc nhìn và nguồn asset. | Chờ chơi thử trên main |
| §6–7 · tài liệu và bàn giao | TV1/3/5/6 | Từ clone sạch chạy README, kiểm schema + ví dụ kho, roster/quyền Write, nhật ký và bằng chứng ở SHA đã kiểm. Xác nhận tag remote trỏ đúng SHA. | Chờ bàn giao |

### Ghi chú lần kiểm local

Smoke G hiện dùng giỏ dựng sẵn. Ca này chứng minh đường truyền kho. Các lát thu hoạch, sinh tồn, phục vụ và HUD cần bằng chứng riêng. Sau khi chạy trên main, ghi các AC còn thiếu và hành động cho phase sau tại đây.
