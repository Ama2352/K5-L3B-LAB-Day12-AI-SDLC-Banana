# Ma trận truy vết Phase 3 · QA (TV6)

> Nguồn: TICKET-03 "Mùa Nước Nổi", Test Contract v1.2 (lõi: kho cá thể, độ tươi). Test viết từ đề, hộp đen.
> Lệnh: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`. Test P3: `tests/test_qa_p3.py` (39 test).
> Kết quả: ✅ đạt · ❌ chưa đạt · 🖐 kiểm tay. Bằng chứng: [test-run-qa.txt](../proof/phase-3/test-run-qa.txt) (306/306 OK), [smoke-qa.txt](../proof/phase-3/smoke-qa.txt).
> Khi gắn tag `phase-3`: chạy lại lệnh trên đúng commit tag và thay dòng đầu `test-run-qa.txt`.

| AC | Yêu cầu (TICKET-03) | Test | Kết quả |
|---|---|---|---|
| AC-P3-01 | `contract_version: "1.2"`, `freshness {100, 0.5, 0.25, 30}` | `Manifest` | ✅ |
| AC-P3-02 | File kho cá thể `{items:[{id,kind,fresh}]}`: smoke bàn giao theo đề, xuất theo id, kho rỗng `[]`, ngất ghi rỗng, chạm `--ticks` không ghi, `gather_end.inventory` cùng schema; quán từ chối kho đếm / kind lạ / id trùng / fresh ngoài miền / id rỗng / thiếu-thừa khóa (mã 2); nhận hàng ươn, không áp trần giỏ | `InventoryFile` (7), smoke mục 2–3 | ✅ |
| AC-P3-03 | Id I1.. theo thứ tự vào giỏ, tăng tiếp, không dùng lại; `lost` (monster_hit/faint) là cá thể theo LIFO | `ItemIds` (4) | ✅ |
| AC-P3-04 | Giỏ −0.5/s, kho quán −0.25/s kể cả hàng giữ; hàng mới 100 hao từ bước sau; kẹp 0; pause dừng hao; Shop không hao | `Decay` (6) | ✅ |
| AC-P3-05 | `spoiled` đúng mẫu đề (fresh 30 → tick 1), đúng một lần, ngưỡng chính xác (30.01 → tick 2), nhiều cá thể theo id, `location` hold/stock; hàng ươn chiếm ô, không nấu | `Spoil` (7), smoke mục 1 | ✅ |
| AC-P3-06 | Giữ chỗ theo id: tươi nhất rồi id nhỏ; fixture bỏ `reserved` tự cấp; hàng giữ vừa ươn → nhả và giữ lại một lần; không đủ → `unfulfillable`, khách vẫn chờ; nhiều đơn theo `order_tick` rồi id bàn; hàng đang giữ không cho đơn khác | `ReserveById` (7) | ✅ |
| AC-P3-07 | Nấu tiêu đúng id giữ, `base_price = floor(giá × TB fresh / 100)`, `items` cá thể theo kind rồi id; boa trên giá đã chốt | `FreshPrice` (3) | ✅ |
| AC-P3-08 | Scenario v1.2: `hold`/`stock` mảng cá thể, `reserved` mảng id; sai/mâu thuẫn → mã 2; `day` Ngày kế cấp id mới theo mẫu | `ScenarioV12` (3) | ✅ |
| AC-P3-09 | `day`: bàn giao cùng tick chuyển pha, không hao thêm | `Decay.test_ac_p3_09_*`, smoke mục 4 | ✅ |
| AC-P3-10 | Regression P1–P2 còn hiệu lực với v1.2 | toàn bộ `tests/` (306) | ✅ — xem "Test đổi vì luật mới" |
| AC-P3-11 | HUD đọc được độ tươi / nhận ra hàng ươn | 🖐 chơi `python3 -m chonoi.live`, chụp ảnh | 🖐 chưa kiểm |
| AC-P3-12 | `CHANGELOG.md` ghi breaking change, schema mới, cách cập nhật fixture | đọc tay | ✅ |
| Mở rộng | current / reservations | chưa khai `extensions` | — không làm |

## Sửa để đạt đề (TV6, theo yêu cầu nhóm)

Chạy thử v1.2 (`CHONOI_CONTRACT`) trên `main` `beeb36c`: gather/kho (TV2) đạt; quán thiếu 3 chỗ. Đã sửa:

1. `chonoi/scenario.py`: `quan.stock` ở v1.2 kiểm bằng `validate_instances` (mảng cá thể), kho đếm → mã 2; `customers[].reserved` phải là mảng id. Trước đó luôn kiểm theo kho đếm v1.1 nên chặn mọi fixture quán v1.2.
2. `chonoi/sim/quan.py`: quán không khai kho thì kho rỗng là `[]` ở v1.2 (trước là `{}` → chạy nhánh kho đếm).
3. `chonoi/sim/quan.py`: `served`/`paid` dùng giá đã chốt trên món (`hand.base_price`), boa tính trên giá này. Trước đó lấy giá niêm yết của khách (60 thay vì 45).
4. `game.contract.json`: `contract_version` `"1.1"` → `"1.2"`.

## Test đổi vì luật mới (TICKET-03 mục 3)

- `tests/v12_adapter.py` (mới): chuyển fixture P1–P2 kiểu v1.1 sang cá thể (fresh 100, id I1..) và quy output cá thể về dạng v1.1 để so **luật cũ**. Không đổi giá trị nào khác. Dùng trong `test_qa_p1/p2/spec/quan`, `test_smoke_p1`, `test_phase2_tv1`, `test_gather_survival`, `test_tv4_quan`. Schema v1.2 kiểm chặt riêng ở `test_qa_p3.py`.
- Giá món chốt theo fresh: `test_qa_quan` (cook 60 → 59, trọn vòng 72 → 70), `test_tv4_quan` (cook 60 → 59). Lý do: fresh 100 hao 1 tick ở quán còn 99.9958 → floor(60 × 0.999958) = 59.
- `test_qa_p2.test_ac_p2_01`: `contract_version` nhận 1.1 hoặc 1.2 (TICKET-03 thay phiên bản; số chuẩn P2 giữ nguyên). AC-P3-01 kiểm chặt `"1.2"`.
- `test_python_starter_units.test_session_steps_gather_and_dock`: `hold` dạng cá thể khi v1.2.
- `test_qa_p3.test_ac_p3_02_smoke_*`: so fresh trong JSONL với file theo dung sai ±0.01 (JSONL làm tròn 3 chữ số; đề cho dung sai quan sát ±0.01).
