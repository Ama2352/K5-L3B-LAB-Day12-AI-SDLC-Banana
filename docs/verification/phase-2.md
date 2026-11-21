# Kiểm chứng Phase 2 · phần TV1

Các kết quả dưới đây được chạy trên workspace nhánh `sang/tv1` sau commit Phase 1 `0d867a1`. Khi tích hợp lên main, QA chạy lại trên SHA bàn giao.

| Mục TICKET-02 | Cách kiểm | Kết quả trên nhánh |
|---|---|---|
| §1.2, §4.5 · Cá Sấu và ngất | Kiểm hòa khoảng cách theo ID, recoil đủ 60 bước, bất tử 90 tick, ngạt xuyên bất tử, rơi hàng LIFO, ngất mở quán cùng tick. | Đạt trong [test TV1](../../tests/test_phase2_tv1.py). |
| §2, §4.2 · Pause, Shop và nâng cấp | Pause ở gather/quan/Shop, giữ nút qua bước resume, mua đúng giá, kiểm cấp mua/cấp đang áp dụng, đóng Shop ở bước cuối. | Đạt trong test TV1. |
| §4.1–4.5 · Day và scenario | Kiểm ngày vượt miền, kế hoạch ghi đè, số tiền đầu kỳ, fixture quán đối chiếu kho khi chuyển pha, M2 xuất hiện từ D3. | Đạt trong test TV1. |
| §5 · Smoke độc lập và nhiều ngày | Kiểm kho hai tiến trình. Chạy day seed 42 hai lần, so SHA-256. Chạy đủ 5 ngày và đọc dòng end. | Kho khớp. 1 ngày 22.200 tick, hai lần có cùng SHA-256. 5 ngày 111.000 tick. [Lệnh và kết quả thực tế](../proof/phase-2/integration.tv1.txt) |

Hồi quy trên nhánh đạt 62/62 test, gồm 9 test TV1 mới. V1.1 nhận mode `day` và nhận nút boolean `attack` dù mở rộng tắt. Vì vậy các test v1.0 từng yêu cầu từ chối hai đầu vào này đã đổi theo §4.1–4.2. Input lạ hoặc sai kiểu vẫn phải thoát mã 2.

TV2 còn tích hợp preset 8 đàn, chuyển động và sinh cá. TV3 còn tích hợp lịch sinh khách trên nền hai bếp/bốn bàn và thực đơn theo ngày. TV5 còn nối HUD/menu, điều khiển trực tiếp và đo FPS. QA cần đo lại trên bản đủ các lát. Thời gian trong log là kết quả máy phát triển.

---

# Ma trận truy vết Phase 2 · QA (TV6)

> Nguồn: TICKET-02 (mục 1–2) và Test Contract v1.1 (mục 4). Test viết từ đề, so nguyên `data` event.
> Lệnh: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`. File QA: `test_qa_p2.py`, `test_qa_spec.py`, `test_qa_quan.py` (hồi quy P1 trên số chuẩn), `test_qa_p1.py`.
> Kết quả: ✅ đạt · ❌ chưa đạt · 🖐 kiểm tay. Cột "Tại tag `phase-2`" là kết quả ở vị trí tag cũ `ff3d6c9` (tag sau đó dời sang `566e121`, xem Ghi chú QA); cột "Sau sửa" là commit QA mới nhất trên nhánh `thaoquyen` (xem [test-run-qa.txt](../proof/phase-2/test-run-qa.txt)).

| AC | Yêu cầu (TICKET-02) | Test | Bản thử `ff3d6c9` | Sau sửa |
|---|---|---|---|---|
| AC-P2-01 | `contract_version` 1.1, hằng số chung (180 s, 4 m/s, oxy 30 s, 3 Máu, giỏ 12, bán kính 2 m, mọc lại 20 s) | `StandardNumbers.test_ac_p2_01_*`, `test_qa_spec.Manifest` | ✅ | ✅ |
| AC-P2-02 | Nút N1–N6 đúng loại/vị trí, hái kèo nèo | `test_ac_p2_02_*` | ✅ | ✅ |
| AC-P2-03 | `fish_yield` 3 loài, `fish_initial` = 8, 10 khóa cá bơi/sinh, đầu ca 8 đàn ở 8 điểm sinh khác nhau, bắt cá kèo yield 2 | `test_ac_p2_03_*` | ✅ | ✅ |
| AC-P2-04 | Số Cá Sấu (loài, M1/M2, bất tử 90, loss 0.5) | `test_ac_p2_04_*` | ✅ | ✅ |
| AC-P2-05 | 2 bếp, 4 bàn đúng vị trí, 6 món đúng công thức/thời gian/giá, `burn_s: null` | `test_ac_p2_05_*` | ✅ | ✅ |
| AC-P2-06 | `day_plan` D1–D5, `ingredients` = tổng công thức × suất | `test_ac_p2_06_*` | ✅ | ✅ |
| AC-P2-07 | Shop: `max_ticks` 600, oxy 200/400 → 45/60 s, Máu 250/500 → 4/5 | `test_ac_p2_07_*` | ✅ | ✅ |
| AC-P2-08 | Cá Sấu tuần tra 1 m/s, quay đầu ở waypoint, phát hiện ≤ 10 m (d ≥ 10) → đuổi 3 m/s, bỏ đuổi khi > 16 m hoặc người chơi lên d < 10, không lên trên d 10 | `test_ac_p2_08_*` (test_qa_p2 + test_qa_spec.CrocDetail) | ✅ | ✅ |
| AC-P2-09 | Hit: −1 Máu, bỏ floor(n/2) LIFO, bất tử 90; trong bất tử không hit/recoil; recoil 60 bước | `test_ac_p2_09_*`, TV1 `test_recoil_tie_break_and_invulnerability` | ✅ | ✅ |
| AC-P2-10 | Ngạt xuyên bất tử, không rơi hàng | `test_ac_p2_10_*` | ✅ | ✅ |
| AC-P2-11 | Ngất do Cá Sấu: `faint` `cause:"monster"`, kho rỗng; cập bến ưu tiên khi còn Máu | `test_ac_p2_11_*` | ✅ | ✅ |
| AC-P2-12 | Khách 120 + 900k, bàn trống id nhỏ nhất, hết bàn bỏ lượt | `test_ac_p2_12_*` | ❌ lát khách TV3 chưa vào main | ✅ |
| AC-P2-13 | Quán độc lập dùng 6 món; trong `day` lọc theo kế hoạch, thiếu → `no_dish` | `test_ac_p2_13_*` | ❌ như trên | ✅ |
| AC-P2-14 | Hai bếp nấu song song; chọn tương tác gần nhất / hòa bếp trước bàn rồi id | `test_ac_p2_14_*`, `test_qa_spec.InteractChoice` | ✅ | ✅ |
| AC-P2-15 | Một Ngày không input = 22.200 tick, ≤ 20 s; kế hoạch D1–D5 qua `--days 5`; snapshot day đủ `day,day_plan,upgrades,active_upgrades`; event có `day` | `test_ac_p2_15_*` | ✅ | ✅ |
| AC-P2-16 | Đổi pha: ngất/cập bến mở quán cùng tick với kho bàn giao | `test_ac_p2_16_*` | ✅ | ✅ |
| AC-P2-17 | Shop: mua trừ money giữ earned/điểm, đủ đúng giá vẫn mua, buy trước shop_done cùng bước, buy sai pha bỏ qua, tự đóng 600 tick | `test_ac_p2_17_*` | ✅ | ✅ |
| AC-P2-18 | Ngày kế: cấp có hiệu lực, Máu/oxy hồi đầy, giỏ mới, kho dư bỏ sau Shop | `test_ac_p2_18_*` | ✅ | ✅ |
| AC-P2-19 | Pause đóng băng đồng hồ/oxy/timer, bỏ qua hành động và buy | `test_ac_p2_19_*`, TV1 `test_pause_*` | ✅ | ✅ |
| AC-P2-20 | Cá bơi 1.5 m/s trong miền/dải độ sâu, đổi hướng ở bước 120, phản xạ mép, `random_fish:false` đứng yên | `test_ac_p2_20_*` | ✅ | ✅ |
| AC-P2-21 | Sinh cá ở 360·k, điểm sinh chuẩn, cách đàn khác > 1 m, id nối tiếp, trần 12 | `test_ac_p2_21_*` | ✅ | ✅ |
| AC-P2-22 | Tất định: `day` một Ngày cùng seed → giống từng byte | `test_ac_p2_22_*`, [smoke-qa.txt](../proof/phase-2/smoke-qa.txt) | ✅ | ✅ |
| AC-P2-23 | Hồi quy P1 trên số chuẩn (gather, quán, contract) | `test_qa_p1`, `test_qa_quan`, `test_qa_spec`, smoke | ❌ 8 test quán (thiếu lát khách) | ✅ |
| AC-P2-24 | Menu, DayIntro/EveningIntro/DayResult/Summary, pause có Tiếp tục/Về menu, HUD sáng/tối, chữ ≥ 18 px, ≥ 30 FPS | 🖐 chơi `python3 -m chonoi.live`, chụp ảnh | 🖐 chưa kiểm | 🖐 chưa kiểm |

Bằng chứng trên commit lịch sử `ff3d6c9`: [test-run-qa-tag-phase-2.txt](../proof/phase-2/test-run-qa-tag-phase-2.txt). Tại tag `phase-2` hiện tại (`566e121`), TV6 chạy lại toàn bộ test của tag: 240/240 OK, [test-run-tag-phase-2-566e121.txt](../proof/phase-2/test-run-tag-phase-2-566e121.txt).

## Ghi chú QA

- Bản tag Phase 2 lúc kiểm (`ff3d6c9`, 11:29) gắn trước khi PR #9 (lát khách TV3) vào main lúc 11:43, nên các AC quán chưa đạt tại tag.
- Khi viết test theo đề, QA phát hiện và sửa (đã ghi lý do trong commit):
  1. `customer_arrived` dùng `customer_id` thay vì `order_id`; `no_dish` có `{table_id}` thay vì `{}` (PRD-0 mục E, `docs/contracts/README.md`). Lỗi có từ `1f10afe`. Test `test_quan_p2.py` của TV3 viết theo code nên không phát hiện; đã đổi kỳ vọng theo đề.
  2. Quán độc lập không kiểm mâu thuẫn fixture (PRD-0 mục D). Đã cho `runner.py` gọi `check_evening_fixture` và bổ sung kiểm khách `eating`. 4 fixture trong `test_tv4_quan.py` thiếu `order_status`, sửa dữ liệu fixture theo đề, giữ nguyên assert.
- Tag `phase-2` trên GitHub hiện trỏ tới `566e121` (đã có giao diện từ PR #8). Smoke live trên commit đó trả HTTP 200 cho `gather`, `quan` và `day`.
- Lượt kiểm AC-P2-24 với giao diện hoàn thiện nằm trong [bằng chứng Phase 4](../proof/phase-4/web-ui.md).
