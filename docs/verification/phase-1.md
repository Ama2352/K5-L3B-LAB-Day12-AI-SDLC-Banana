# Ma trận truy vết Phase 1

> Nguồn: PRD-0 (mục 2, 7 và Test Contract v1.0 mục A–G). Mã `AC-P1-xx`,
> Test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`. `smoke:` = `tests/test_smoke_p1.py`, `qa:` = `tests/test_qa_p1.py`.
> Kết quả: ✅ đạt · ❌ chưa đạt · ⏳ chưa kiểm. ✅ kèm SHA = TV6 đã chạy đạt trên `main` ở SHA đó (100/100 test, [test-run.txt](../proof/phase-1/test-run.txt)). Khi có tag `phase-1`, TV6 chạy lại ở commit gắn tag và thay SHA.

## Contract & headless (mục A, B, C, D, E)

| AC | Yêu cầu (PRD) | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|---|
| AC-P1-01 | `game.contract.json` đủ khóa preset, số trong dải hợp lệ; `team`, `team_size` đúng thực tế | `test_qa_spec.Manifest` (đủ khóa, giá trị chuẩn quán/gather), `test_qa_p2.StandardNumbers`, `tools/check_team.py` | [test-run-qa.txt](../proof/phase-2/test-run-qa.txt) | ✅ (số chuẩn v1.1 ở main hiện tại) |
| AC-P1-02 | Cờ headless đúng mục B; mã thoát 0/1/2; `--ticks 0` chỉ dựng fixture; dòng `end` luôn cuối | `test_qa_spec.Cli` (thiếu cờ, seed/ticks sai kiểu, `--snapshot-every`, lỗi ghi → mã 1, `--ticks 0`, không ghi kho khi lỗi), smoke `test_con_01/03` | [test-run-qa.txt](../proof/phase-2/test-run-qa.txt) | ✅ |
| AC-P1-03 | Cùng seed + đầu vào → JSONL và file kho giống từng byte | smoke: `test_con_02_deterministic_bytes`; qa: chạy lại 2 lần cho cả `gather` và `quan` | [test-run.txt](../proof/phase-1/test-run.txt) (`test_qa_p1.OutputFormat` ×2); [handoff-tv6.txt](../proof/phase-1/handoff-tv6.txt): 2 lượt `cmp` giống từng byte | ✅ `14c5ccb` |
| AC-P1-04 | Inputs: nút chỉ tác động ở cạnh lên; frame chỉ cập nhật trường có mặt; move chuẩn hóa; trường sai, kiểu sai, tick lặp/giảm → mã 2; nút sai pha bỏ qua | `test_qa_spec.Inputs`, `test_qa_p1.GatherNode.test_ac_p1_04_*`, smoke `test_con_03_*` | [test-run-qa.txt](../proof/phase-2/test-run-qa.txt) | ✅ |
| AC-P1-05 | Scenario sai → mã 2, không ghi output (gather: Máu/oxy/đếm ngạt ngoài miền, id trùng, kind lạ, cá trên mặt nước, regrow âm, time_left ngoài miền; quán: kind lạ, kho âm, khách trùng bàn/id, giữ khác công thức hoặc quá kho, món lạ, bếp/bàn lạ, bếp cooking timer 0, đơn assigned thiếu món, bếp và tay cùng đơn, món không khớp đơn, eating sai, unfulfillable còn giữ, món không có khách) | `test_qa_spec.ScenarioInvalid`, smoke `ScenarioModes` | [test-run-qa.txt](../proof/phase-2/test-run-qa.txt) | ✅ `e3acdb9`+: quán độc lập trước đó **không** kiểm mâu thuẫn fixture, đã sửa (xem Cập nhật sau tag) |
| AC-P1-06 | JSONL: snapshot tick 0, bội số `--snapshot-every` (mặc định 10), tick dừng; đủ trường chung/gather/quán; dòng end đủ trường; event trước snapshot, end cuối; tọa độ 3 chữ số; `score`; sắp id | `test_qa_spec.Output`, `test_qa_p1.OutputFormat` | [test-run-qa.txt](../proof/phase-2/test-run-qa.txt) | ✅ |

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
| AC-P1-20 | Khách đến ở `phase_tick` 120 rồi mỗi 900 tick; lấy bàn trống id nhỏ nhất; hết bàn thì bỏ lượt; không món đủ → `no_dish` | `test_qa_quan.Arrival` (tick 120, data `customer_arrived`/`no_dish` theo mục E), `test_qa_p2.Restaurant` (120+900k, bàn id nhỏ nhất, hết bàn) | [test-run-qa.txt](../proof/phase-2/test-run-qa.txt), [smoke-qa.txt](../proof/phase-2/smoke-qa.txt) | ❌ tại tag `phase-1` (`0d867a1`: quán chưa có khách); ✅ `e3acdb9`. Data event sửa theo đề ở `e3acdb9` |
| AC-P1-21 | Chọn đều theo seed trong các món đủ nguyên liệu khả dụng (tồn − giữ); giữ đúng công thức ngay; `customer_arrived`; hai khách tranh phần cuối được xử lý đúng | `test_qa_quan.Arrival` (`giu_cho_tru_khoi_kho`, `chon_deu_theo_seed`, `cung_seed_cung_mon`, `chon_mon_du_nguyen_lieu`) | [test-run-qa.txt](../proof/phase-2/test-run-qa.txt) | ❌ tại tag `phase-1` (`0d867a1`: quán chưa có khách); ✅ `e3acdb9` |
| AC-P1-22 | Kiên nhẫn giảm từ bước sau khi đến; về 0 khi còn giờ → `customer_left` `patience`, uy tín −0.5 (kẹp 0–5), nhả giữ chỗ, bỏ món của đơn | `test_qa_quan.Arrival` (`het_kien_nhan_roi_quan`, `nha_giu_cho`, `uy_tin_kep_0`) | [test-run-qa.txt](../proof/phase-2/test-run-qa.txt) | ❌ tại tag `phase-1` (`0d867a1`: quán chưa có khách); ✅ `e3acdb9` |

## Quán — lát 4: bếp, bưng, phục vụ, tiền (TV4)

| AC | Yêu cầu (PRD) | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|---|
| AC-P1-23 | Tối đa một `interact`/bước, chọn theo (khoảng cách, bếp trước bàn, id); đối tượng chọn được nhưng không tương tác được thì bỏ lượt | `test_qa_spec.InteractChoice` (hòa bếp/bàn, hòa hai bếp đúng mép, bỏ lượt, phục vụ sai đơn), `test_qa_p2.test_ac_p2_14_chon_tuong_tac_gan_nhat` | [test-run-qa.txt](../proof/phase-2/test-run-qa.txt) | ✅ |
| AC-P1-24 | Bếp idle lấy đơn reserved cũ nhất (order_tick, id bàn), tiêu nguyên liệu giữ, `cook_started` (items sắp theo kind, base_price); nấu xong → ready, `dish_ready` | `test_qa_quan.Kitchen` (data đủ, đơn cũ nhất, items theo kind, đúng `cook_s`) | [test-run-qa.txt](../proof/phase-2/test-run-qa.txt) | ✅ `e3acdb9` |
| AC-P1-25 | Bếp ready + tay trống → `dish_picked`, bếp về idle; `carry_limit` 1 | `test_qa_quan.Kitchen` (`bung_mon_tu_bep_ready`, `tay_day_khong_bung_them`) | [test-run-qa.txt](../proof/phase-2/test-run-qa.txt) | ✅ `e3acdb9` |
| AC-P1-26 | Phục vụ đúng `order_id` → `served`, khách ăn 600 tick; boa = floor(giá × 0.2) nếu tỷ lệ kiên nhẫn ≥ 0.5, ngược lại 0 | `test_qa_quan.Kitchen` (boa 12, boa 0 khi < 50%, đúng mốc 50%) | [test-run-qa.txt](../proof/phase-2/test-run-qa.txt) | ✅ `e3acdb9` |
| AC-P1-27 | Ăn xong → `paid` `finished_eating`, rời bàn; boa dương +0.2 uy tín (kẹp) | `test_qa_quan.Kitchen` (`an_xong_tra_tien`, `uy_tin_kep_toi_da_5`) | [test-run-qa.txt](../proof/phase-2/test-run-qa.txt) | ✅ `e3acdb9` |
| AC-P1-28 | Hết ca: khách đang ăn trả `closing`, khách chờ rời `closing` không trừ uy tín; `quan_end` đủ money/earned/shift_earned/reputation | `test_qa_quan.Kitchen.test_ac_p1_28_dong_ca` | [test-run-qa.txt](../proof/phase-2/test-run-qa.txt) | ✅ `e3acdb9` |

## Tích hợp & DoD (mục 7)

| AC | Yêu cầu (PRD) | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|---|
| AC-P1-29 | Smoke hai tiến trình: `dock.json` + `dock-inputs.json` → quán tick 0 có `stock:{"bong_sung":2,"ca_loc":1}` | smoke: `test_inv_01_gather_writes_inventory_quan_reads_it` + chạy tay 2 lệnh mục G; TV2: `tools/check_handoff.py` | [smoke-g-tv6.txt](../proof/phase-1/smoke-g-tv6.txt), [handoff-tv6.txt](../proof/phase-1/handoff-tv6.txt), [handoff.txt](../proof/phase-1/handoff.txt) | ✅ `14c5ccb` |
| AC-P1-30 | Chơi được cả hai buổi; HUD hiện thời gian, oxy, Máu, giỏ (sáng) và kho, món gọi, kiên nhẫn, bếp, tay, tiền, uy tín (tối) | chơi thử `python3 -m chonoi.live`, chụp màn hình | `docs/proof/phase-1/hud-*.png` | ⏳ chưa chơi thử, chưa có ảnh HUD |
| AC-P1-31 | README: chạy từ clone sạch ≤ 3 lệnh, điều khiển, cách tính điểm, lệnh test 1 lệnh | đọc tay README trên clone sạch | Clone sạch ở `14c5ccb`: lệnh test 1 lệnh chạy đạt 100/100 | ❌ README chưa có phím điều khiển (chỉ ở `docs/STARTER.md`) và cách tính điểm |
| AC-P1-32 | TEAM.md đủ người + thỏa thuận; `team_size` khớp; hợp đồng kho có schema + ví dụ ở `docs/contracts/` | `tools/check_team.py`, đọc tay | [check-team.txt](../proof/phase-1/check-team.txt); `docs/contracts/README.md` có schema kho | ✅ `14c5ccb` |
| AC-P1-33 | Ghi chép tối thiểu: `clarify.md`, `ai-usage-log.md`, verification + proof | đọc tay | — | ⏳ `clarify.md` còn trống; `docs/members/100678carwyn.md` (TV6) chưa có |
| AC-P1-34 | Tag `phase-1` trỏ commit bàn giao trên `main`, trước 1:00 | `git ls-remote --tags origin` | tag `phase-1` → `0d867a1` | ⚠️ có tag, nhưng tại commit đó lát 3 (khách) chưa vào `main` → AC-P1-20..22 chưa đạt tại tag. Xem mục "Cập nhật sau tag" |

## Đánh giá ngắn
- Yêu cầu nào đạt / chưa đạt (TV6 kiểm trên `main` ở `14c5ccb`, 2026-11-21): 100/100 test đạt. Đạt 19 AC: 02–04, 07–17, 19, 24, 27, 29, 32. Còn dở 14 AC: 01, 05, 06, 18, 20–23, 25, 26, 28, 30, 33, 34. Chưa đạt 1 AC: 31 (README thiếu phím và cách tính điểm).
- Lát 3 quán (AC-P1-20 đến 22) chưa có test nào. Đây là chỗ trống lớn nhất.
- `main` đã chứa code phase 2 (`contract_version` 1.1, Cá Sấu, chế độ `day`). Tag `phase-1` cần trỏ commit bàn giao phase 1, khi đó TV6 chạy lại và đọc tay preset v1.0.
- Điều cần chỉnh cho phase sau: thêm test lát 3 và các ca biên còn thiếu ở trên; bổ sung README; PO ghi `clarify.md`; mỗi người có file `docs/members/`.

## Cập nhật sau tag (TV6, 2026-11-21 12:35)

- Tại tag `phase-1` (`0d867a1`) quán **chưa có khách**: luật khách (lát 3, TV3) chưa vào `main`. Chạy quán có kho 200 tick → 0 `customer_arrived`. Bộ test lúc đó (100/100, [test-run.txt](../proof/phase-1/test-run.txt)) không có test nào cho lát 3 nên không phát hiện.
- Lát 3 vào `main` ở PR #9 (`8d9fb80`, 11:43). Khi QA viết test so nguyên data theo PRD-0 mục E thì phát hiện code lệch đề: `customer_arrived` dùng `customer_id` (đề: `order_id`), `no_dish` có `{table_id}` (đề: `{}`). Lỗi có từ commit `1f10afe` (10:12). Đã sửa code và test `test_quan_p2.py` theo đề ở `e3acdb9`.
- Không dời tag `phase-1`: mọi commit trên `main` có khách đều đã là contract v1.1. Phần khách được chấm lại ở các tag sau (test ẩn có kiểm lại phase trước).
- Rà độ phủ theo đề, viết thêm `tests/test_qa_spec.py` (CLI, inputs, scenario sai, output, chọn interact, cá/Cá Sấu/vòng ngày chi tiết). Phát hiện quán độc lập không kiểm mâu thuẫn fixture (PRD-0 mục D): đã cho `runner.py` gọi `check_evening_fixture` với đủ thực đơn và bổ sung kiểm khách `eating`. 4 fixture trong `tests/test_tv4_quan.py` thiếu `order_status` (đơn có món trên tay phải `assigned`, khách `eating` phải `served`) nên sửa dữ liệu fixture, giữ nguyên assert.
- Kết quả hiện tại: toàn bộ test đạt, xem [test-run-qa.txt](../proof/phase-2/test-run-qa.txt).

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
