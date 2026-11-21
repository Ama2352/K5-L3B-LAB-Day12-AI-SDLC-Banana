# Ma trận truy vết Phase 1

> Nguồn: PRD-0 (mục 2, 7 và Test Contract v1.0 mục A–G). Mã `AC-P1-xx`,
> Test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`. `smoke:` = `tests/test_smoke_p1.py`, `qa:` = `tests/test_qa_p1.py`.
> Kết quả: ✅ đạt · ❌ chưa đạt · ⏳ chưa kiểm. ✅ kèm SHA = TV6 đã chạy đạt trên `main` ở SHA đó (100/100 test, [test-run.txt](../proof/phase-1/test-run.txt)). Khi có tag `phase-1`, TV6 chạy lại ở commit gắn tag và thay SHA.

## Contract & headless (mục A, B, C, D, E)

| AC | Yêu cầu (PRD) | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|---|
| AC-P1-01 | `game.contract.json` đủ khóa preset v1.0, số trong dải hợp lệ; `team`, `team_size` đúng thực tế | `tools/check_team.py` + đọc tay preset | [check-team.txt](../proof/phase-1/check-team.txt) | ⏳ team/team_size ✅ `14c5ccb`; preset v1.0 chưa đọc tay (main đã lên `contract_version` 1.1) |
| AC-P1-02 | Cờ headless đúng mục B; mã thoát 0/1/2; `--ticks 0` chỉ dựng fixture; dòng `end` luôn cuối | smoke: `test_con_01_*`, `test_con_03_*` | [test-run.txt](../proof/phase-1/test-run.txt), [cli-tv6.txt](../proof/phase-1/cli-tv6.txt) | ✅ `14c5ccb` |
| AC-P1-03 | Cùng seed + đầu vào → JSONL và file kho giống từng byte | smoke: `test_con_02_deterministic_bytes`; qa: chạy lại 2 lần cho cả `gather` và `quan` | [test-run.txt](../proof/phase-1/test-run.txt) (`test_qa_p1.OutputFormat` ×2); [handoff-tv6.txt](../proof/phase-1/handoff-tv6.txt): 2 lượt `cmp` giống từng byte | ✅ `14c5ccb` |
| AC-P1-04 | Inputs: nút chỉ tác động ở cạnh lên; frame chỉ cập nhật trường có mặt; trường sai, kiểu sai, tick lặp/giảm → mã 2 | smoke + qa | [test-run.txt](../proof/phase-1/test-run.txt) (`test_input_edges_and_inherit`, `test_bad_frames_raise`, `test_ac_p1_04_*`); [cli-tv6.txt](../proof/phase-1/cli-tv6.txt): tick lặp, kiểu sai → mã 2, không tạo output | ✅ `14c5ccb` |
| AC-P1-05 | Scenario sai (khối sai mode, id trùng, ngoài miền, giỏ quá trần, stock + `--inventory`, giữ chỗ sai…) → mã 2, không ghi output | smoke: `ScenarioModes`, `test_scenario_out_of_domain_exit_2`; qa: thêm các ca còn thiếu | [test-run.txt](../proof/phase-1/test-run.txt) | ⏳ đạt các ca có test (`14c5ccb`); chưa có test riêng cho id trùng, giỏ quá trần, giữ chỗ sai |
| AC-P1-06 | JSONL: snapshot ở tick 0, bội số `--snapshot-every`, tick dừng; đủ trường chung; `score = earned + 100 × floor(reputation)`; tọa độ 3 chữ số; mảng sắp theo id | smoke: `test_gather_snapshot_has_gather_fields`; qa: kiểm score, sắp id | [test-run.txt](../proof/phase-1/test-run.txt) (`test_ac_p1_06_*`, `test_gather_snapshot_has_gather_fields`) | ⏳ snapshot/score/sắp id ✅ `14c5ccb`; chưa có test làm tròn tọa độ 3 chữ số |

## Gather — lát 1: bơi, oxy, Máu, giỏ (TV1)

| AC | Yêu cầu (PRD) | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|---|
| AC-P1-07 | Vận tốc tới `swim_speed × move` trong ≤ 6 tick; chặn mép, triệt vận tốc hướng ra; hướng theo `move` khác 0 gần nhất | smoke: `Movement` | [test-run.txt](../proof/phase-1/test-run.txt) (`Movement`) | ✅ `14c5ccb` |
| AC-P1-08 | Oxy theo d cuối bước: dưới nước −1/tick (kẹp 0), mặt nước (d ≤ 0.5) +6 (kẹp 1800) và reset đếm ngạt; `oxygen_empty` khi từ dương xuống 0 | qa | [test-run.txt](../proof/phase-1/test-run.txt) (`test_qa_p1.Oxygen`) | ✅ `14c5ccb` |
| AC-P1-09 | `dive` / `surface` (data `pos`) chỉ phát khi đổi phía biên mặt nước | qa | [test-run.txt](../proof/phase-1/test-run.txt) (`test_qa_p1.DiveSurface`, `test_dive_at_surface_boundary`) | ✅ `14c5ccb` |
| AC-P1-10 | Ngạt: chạm oxy 0 ở t, ở dưới liên tục → `choke` ở t+59, −1 Máu, đặt lại đếm; nổi lên đúng bước đó thì không ngạt | qa | [test-run.txt](../proof/phase-1/test-run.txt) (`test_qa_p1.Choke`, `test_gather_survival`) | ✅ `14c5ccb` |
| AC-P1-11 | Máu về 0 → bỏ giỏ theo LIFO, `faint` (`cause:"choke"`, `lost`, `hp:0`), `gather_end` `fainted` với kho rỗng, dừng bước | qa | [test-run.txt](../proof/phase-1/test-run.txt) (`test_ac_p1_11_*`, `test_faint_precedes_*`) | ✅ `14c5ccb` |
| AC-P1-12 | Giỏ theo thứ tự nhặt (mới nhất cuối), trần `hold_capacity` = 12 | qa | [test-run.txt](../proof/phase-1/test-run.txt) (`test_ac_p1_12_ac_p1_14_*`, `test_ac_p1_11_*` (thứ tự LIFO)) | ✅ `14c5ccb` |

## Gather — lát 2: hái, bắt cá, cập bến, kho (TV2)

| AC | Yêu cầu (PRD) | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|---|
| AC-P1-13 | `interact` xét bến trước (khoảng cách tới `dock_pos`, tính cả đúng mép) → `gather_end` `docked` | smoke: `test_inv_01_*`; qa: đúng mép bán kính; TV2: `test_gather_l2.py::DockAfterGather` | [kho.json](../proof/phase-1/kho.json); [test-run.txt](../proof/phase-1/test-run.txt) (`test_qa_p1.Dock`, `DockAfterGather`) | ✅ `14c5ccb` |
| AC-P1-14 | Hái chỉ ở mặt nước: nút ready gần nhất trong 2.0 m, hòa theo id; +1, `regrow_ticks` = 1200, phát `gather`; thiếu chỗ → `hold_full`, nút giữ nguyên | qa; TV2: `test_gather_l2.py::Harvest` | [gather.jsonl](../proof/phase-1/gather.jsonl) tick 151, 801; [test-run.txt](../proof/phase-1/test-run.txt) (`test_qa_p1.GatherNode`, `Harvest`) | ✅ `14c5ccb` |
| AC-P1-15 | Nút từ 1 về 0 → `node_regrown` theo id, hái được ngay | qa; TV2: `Harvest.test_moc_lai_roi_hai_duoc_ngay` | [test-run.txt](../proof/phase-1/test-run.txt) (`test_ac_p1_15_*`, `test_moc_lai_roi_hai_duoc_ngay`) | ✅ `14c5ccb` |
| AC-P1-16 | `catch` chỉ khi hết hồi và dưới nước: đàn gần nhất trong 2.0 m, hòa theo id; thêm đủ yield (ca_linh 3, ca_loc 1), xóa đàn, `fish_caught`, hồi 30 tick; thiếu chỗ → `hold_full`, giữ đàn, không hồi chiêu; không có đàn → không event | qa; TV2: `test_gather_l2.py::Catch` | [gather.jsonl](../proof/phase-1/gather.jsonl) tick 263, 596; [test-run.txt](../proof/phase-1/test-run.txt) (`test_qa_p1.Catch`, `Catch`) | ✅ `14c5ccb` |
| AC-P1-17 | Hết giờ → `gather_end` `time` ở mọi độ sâu, giữ giỏ; hái/bắt/cập bến ở bước cuối vẫn tính | smoke: `test_time_ends_gather_and_keeps_hold`; qa: hành động ở bước cuối | [test-run.txt](../proof/phase-1/test-run.txt) (`test_qa_p1.TimeEnd`, `test_time_ends_gather_and_keeps_hold`) | ✅ `14c5ccb` |
| AC-P1-18 | File kho: chỉ khóa `items`, bỏ lượng 0, khớp `gather_end.inventory`; ghi đúng một lần (ngất ghi rỗng); chạm `--ticks` trước thì không ghi; ghi nguyên tử | smoke: `test_inv_01_not_written_when_tick_limit_first`; qa: ngất → `{"items":{}}` | [test-run.txt](../proof/phase-1/test-run.txt); [handoff-tv1-fainted.txt](../proof/phase-1/handoff-tv1-fainted.txt) | ⏳ schema, ngất ghi rỗng, tick_limit không ghi ✅ `14c5ccb`; chưa có test ghi nguyên tử |

## Quán — lát 3: khách, giữ chỗ, kiên nhẫn (TV3)

| AC | Yêu cầu (PRD) | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|---|
| AC-P1-19 | Quán đọc kho: sai schema, kind lạ → mã 2; thiếu kho thì rỗng; tiền, earned đầu lượt = 0; uy tín theo tuning | smoke: `test_inv_bad_schema_exit_2`, `test_inventory_and_scenario_stock_conflict` | [test-run.txt](../proof/phase-1/test-run.txt) (`test_inv_bad_schema_exit_2`, `test_inventory_and_scenario_stock_conflict`, `test_inventory_flags_mode_mismatch_exit_2`) | ✅ `14c5ccb` |
| AC-P1-20 | Khách đến ở `phase_tick` 120 rồi mỗi 900 tick; lấy bàn trống id nhỏ nhất; hết bàn thì bỏ lượt; không món đủ → `no_dish` | qa | `test-run.txt` | ⏳ chưa có test lát 3 (TV3) |
| AC-P1-21 | Chọn đều theo seed trong các món đủ nguyên liệu khả dụng (tồn − giữ); giữ đúng công thức ngay; `customer_arrived`; hai khách tranh phần cuối được xử lý đúng | qa (fixture `random_customers:false`) | `test-run.txt` | ⏳ chưa có test lát 3 (TV3) |
| AC-P1-22 | Kiên nhẫn giảm từ bước sau khi đến; về 0 khi còn giờ → `customer_left` `patience`, uy tín −0.5 (kẹp 0–5), nhả giữ chỗ, bỏ món của đơn | qa | `test-run.txt` | ⏳ chưa có test lát 3 (TV3) |

## Quán — lát 4: bếp, bưng, phục vụ, tiền (TV4)

| AC | Yêu cầu (PRD) | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|---|
| AC-P1-23 | Tối đa một `interact`/bước, chọn theo (khoảng cách, bếp trước bàn, id); đối tượng chọn được nhưng không tương tác được thì bỏ lượt | qa | `test-run.txt` | ⏳ chưa có test chọn interact khi hòa |
| AC-P1-24 | Bếp idle lấy đơn reserved cũ nhất (order_tick, id bàn), tiêu nguyên liệu giữ, `cook_started` (items sắp theo kind, base_price); nấu xong → ready, `dish_ready` | qa | [test-run.txt](../proof/phase-1/test-run.txt) (`test_cook_and_pick_dish_at_stove`) | ✅ `14c5ccb` |
| AC-P1-25 | Bếp ready + tay trống → `dish_picked`, bếp về idle; `carry_limit` 1 | qa | [test-run.txt](../proof/phase-1/test-run.txt) (`test_cook_and_pick_dish_at_stove`) | ⏳ nhặt món ✅ `14c5ccb`; chưa có test `carry_limit` khi tay đang cầm |
| AC-P1-26 | Phục vụ đúng `order_id` → `served`, khách ăn 600 tick; boa = floor(giá × 0.2) nếu tỷ lệ kiên nhẫn ≥ 0.5, ngược lại 0 | qa | [test-run.txt](../proof/phase-1/test-run.txt) (`test_serve_eat_and_payment_with_tip`, `test_serve_at_exact_zero_patience_tick_is_valid`) | ⏳ boa khi ≥ 0.5 ✅ `14c5ccb`; chưa có test boa = 0 khi < 0.5 |
| AC-P1-27 | Ăn xong → `paid` `finished_eating`, rời bàn; boa dương +0.2 uy tín (kẹp) | qa | [test-run.txt](../proof/phase-1/test-run.txt) (`test_serve_eat_and_payment_with_tip`: uy tín 3.0 → 3.2) | ✅ `14c5ccb` |
| AC-P1-28 | Hết ca: khách đang ăn trả `closing`, khách chờ rời `closing` không trừ uy tín; `quan_end` đủ money/earned/shift_earned/reputation | qa | [test-run.txt](../proof/phase-1/test-run.txt) (`test_closing_immediate_payment_*`, `test_serve_at_closing_tick_*`) | ⏳ khách đang ăn trả `closing` ✅ `14c5ccb`; chưa có test khách chờ rời `closing` không trừ uy tín |

## Tích hợp & DoD (mục 7)

| AC | Yêu cầu (PRD) | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|---|
| AC-P1-29 | Smoke hai tiến trình: `dock.json` + `dock-inputs.json` → quán tick 0 có `stock:{"bong_sung":2,"ca_loc":1}` | smoke: `test_inv_01_gather_writes_inventory_quan_reads_it` + chạy tay 2 lệnh mục G; TV2: `tools/check_handoff.py` | [smoke-g-tv6.txt](../proof/phase-1/smoke-g-tv6.txt), [handoff-tv6.txt](../proof/phase-1/handoff-tv6.txt), [handoff.txt](../proof/phase-1/handoff.txt) | ✅ `14c5ccb` |
| AC-P1-30 | Chơi được cả hai buổi; HUD hiện thời gian, oxy, Máu, giỏ (sáng) và kho, món gọi, kiên nhẫn, bếp, tay, tiền, uy tín (tối) | chơi thử `python3 -m chonoi.live`, chụp màn hình | `docs/proof/phase-1/hud-*.png` | ⏳ chưa chơi thử, chưa có ảnh HUD |
| AC-P1-31 | README: chạy từ clone sạch ≤ 3 lệnh, điều khiển, cách tính điểm, lệnh test 1 lệnh | đọc tay README trên clone sạch | Clone sạch ở `14c5ccb`: lệnh test 1 lệnh chạy đạt 100/100 | ❌ README chưa có phím điều khiển (chỉ ở `docs/STARTER.md`) và cách tính điểm |
| AC-P1-32 | TEAM.md đủ người + thỏa thuận; `team_size` khớp; hợp đồng kho có schema + ví dụ ở `docs/contracts/` | `tools/check_team.py`, đọc tay | [check-team.txt](../proof/phase-1/check-team.txt); `docs/contracts/README.md` có schema kho | ✅ `14c5ccb` |
| AC-P1-33 | Ghi chép tối thiểu: `clarify.md`, `ai-usage-log.md`, verification + proof | đọc tay | — | ⏳ `clarify.md` còn trống; `docs/members/100678carwyn.md` (TV6) chưa có |
| AC-P1-34 | Tag `phase-1` trỏ commit bàn giao trên `main`, trước 1:00 | `git show phase-1` | — | ⏳ chưa có tag `phase-1` trên remote |

## Đánh giá ngắn
- Yêu cầu nào đạt / chưa đạt (TV6 kiểm trên `main` ở `14c5ccb`, 2026-11-21): 100/100 test đạt. Đạt 19 AC: 02–04, 07–17, 19, 24, 27, 29, 32. Còn dở 14 AC: 01, 05, 06, 18, 20–23, 25, 26, 28, 30, 33, 34. Chưa đạt 1 AC: 31 (README thiếu phím và cách tính điểm).
- Lát 3 quán (AC-P1-20 đến 22) chưa có test nào. Đây là chỗ trống lớn nhất.
- `main` đã chứa code phase 2 (`contract_version` 1.1, Cá Sấu, chế độ `day`). Tag `phase-1` cần trỏ commit bàn giao phase 1, khi đó TV6 chạy lại và đọc tay preset v1.0.
- Điều cần chỉnh cho phase sau: thêm test lát 3 và các ca biên còn thiếu ở trên; bổ sung README; PO ghi `clarify.md`; mỗi người có file `docs/members/`.

## Bảng theo dõi TV1 trước khi đồng bộ main

Tham chiếu theo mục của PRD-0 do Sang cung cấp. Kết quả local ghi riêng. Khi bàn giao, TV6 ghi SHA trên main, chạy lại, dẫn log/ảnh đúng bản rồi chốt đạt hoặc chưa đạt từng dòng.

| Yêu cầu PRD-0 | Người | Cách kiểm và bằng chứng | Trạng thái |
|---|---|---|---|
| A–C · preset, CLI, input | TV6 | Đối chiếu preset v1.0, 60 Hz, seed có dấu, tín hiệu cạnh lên và mã thoát 0/1/2. Kiểm input sai trước khi tạo output. | Đạt ở `14c5ccb`: mã thoát 0/1/2, seed âm, input sai bị chặn trước khi tạo output ([cli-tv6.txt](../proof/phase-1/cli-tv6.txt)). Preset v1.0 chờ đọc tay ở commit gắn tag |
| D · fixture | TV3/4/6 | Dựng đơn đúng/sai cho từng trạng thái. Thử giữ quá tồn, khách trùng bàn, bếp và tay cùng giữ một đơn, timer mâu thuẫn, ID tham chiếu thiếu và trường ngoài v1.0. | Một phần: có test fixture sai mode và fixture quán sai. Chưa có ca giữ quá tồn, khách trùng bàn, bếp và tay cùng giữ một đơn |
| E · JSONL, điểm và tính tất định | TV6 | Kiểm tick 0, event trước snapshot, snapshot cuối duy nhất, lý do gameplay ưu tiên tick_limit. So hai lượt cùng input/seed từng byte cho cả JSONL và kho. Kiểm điểm = earned + 100 × floor(reputation). | Đạt ở `14c5ccb`: tick 0, snapshot bội số và tick dừng, score, sắp id; gather và quán giống từng byte qua 2 lượt (`test_qa_p1.OutputFormat`) |
| F · bơi, biên, oxy và giỏ | TV1 | Test di chuyển trong `test_smoke_p1`; [5 test sinh tồn](../../tests/test_gather_survival.py) kiểm biên mặt nước, nhịp ngạt, hồi oxy và thứ tự mất giỏ. [Kho rỗng khi ngất](../proof/phase-1/handoff-tv1-fainted.txt) | Đạt trên nhánh TV1, chờ kiểm lại trên commit bàn giao |
| F · hái, bắt và cập bến | TV2 | Kiểm mép bán kính, hòa theo ID, nút vừa mọc, cả đàn vượt sức chứa, hồi chiêu, cập bến/hái/bắt ở bước cuối. | Chờ hoàn thiện luật và kiểm |
| F · khách, bàn và kho khả dụng | TV3 | Kiểm lịch khách theo phase_tick, kể cả khi rút ngắn ca. Bàn bận bỏ lượt, bàn trống thiếu món phát no_dish. Kiểm giữ/nhả, thu hồi món của đơn hết hạn và uy tín. | Chờ hoàn thiện luật và kiểm |
| F · bếp, bàn, thu tiền | TV4 | Kiểm một interact, bếp trước bàn khi hòa, bỏ lượt nếu đối tượng gần nhất chưa dùng được. Phục vụ ở tick hết kiên nhẫn/hết ca, chốt boa lúc giao và cộng uy tín lúc thu. | Chờ hoàn thiện luật và kiểm |
| G · smoke hai tiến trình | TV2/6 | Đã chạy hai lệnh mục G với seed 42 trên workspace (HEAD `f0a1906`, có thay đổi local). Cập bến tick 1. Inventory trong gather_end, file kho và stock quán tick 0 đều có 2 bong_sung, 1 ca_loc. Khi chạy trên main, lưu log theo §6.3. | Đạt trên main `14c5ccb` (seed 42, cập bến tick 1, kho = stock tick 0 = 2 bong_sung, 1 ca_loc): [smoke-g-tv6.txt](../proof/phase-1/smoke-g-tv6.txt) |
| G · các nhánh file kho | TV2/6 | Kiểm ngất ghi rỗng, hết giờ giữ giỏ, tick_limit giữ nguyên file có sẵn, ghi nguyên tử. Kiểm quán độc lập kho rỗng, kho quán vượt trần giỏ vẫn hợp lệ. | Một phần ở `14c5ccb`: ngất ghi rỗng, hết giờ giữ giỏ, tick_limit không ghi, quán đọc kho rỗng đều có test. Chưa có test ghi nguyên tử và kho vượt trần giỏ |
| §2–3, §7 · chơi và HUD | TV5/6 | Chơi cả hai ca, nấu từ kho vừa thu, chụp hai màn hình đủ trường HUD theo kế hoạch. Kiểm góc nhìn và nguồn asset. | Chờ chơi thử trên main |
| §6–7 · tài liệu và bàn giao | TV1/3/5/6 | Từ clone sạch chạy README, kiểm schema + ví dụ kho, roster/quyền Write, nhật ký và bằng chứng ở SHA đã kiểm. Xác nhận tag remote trỏ đúng SHA. | Một phần: clone sạch chạy test đạt, check_team đạt, hợp đồng kho có schema. README thiếu phím và cách tính điểm; chưa có tag |

### Ghi chú lần kiểm local

Smoke G hiện dùng giỏ dựng sẵn. Ca này chứng minh đường truyền kho. Các lát thu hoạch, sinh tồn, phục vụ và HUD cần bằng chứng riêng. Sau khi chạy trên main, ghi các AC còn thiếu và hành động cho phase sau tại đây.

**TV6, `main` `14c5ccb`, 2026-11-21:** 100/100 test đạt. Thu hoạch và sinh tồn đã có bằng chứng riêng (`test_qa_p1`, `test_gather_l2`, `test_gather_survival`), luồng kho thật qua [handoff-tv6.txt](../proof/phase-1/handoff-tv6.txt) khớp 6 món. Còn thiếu: test lát 3 quán, HUD, README, tag. Lưu ý `docs/proof/phase-1/gather.jsonl` được ghi trước khi có phase 2. Lượt mới có thêm trường `monsters` nên không còn giống từng byte, kho thì vẫn giống.
