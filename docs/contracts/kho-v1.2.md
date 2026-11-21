# Hợp đồng kho cá thể (Contract v1.2, TICKET-03)

**Breaking change** so với v1.1: kho đếm `{"items": {kind: n}}` → kho cá thể. Bên đọc chọn schema theo `contract_version`.

```json
{"items":[{"id":"I1","kind":"ca_linh","fresh":100},{"id":"I2","kind":"ca_loc","fresh":97.5}]}
```

- Gốc chỉ có `items`, là mảng `{id, kind, fresh}`. Kho rỗng `{"items":[]}`. Mẫu: [`inventory.v1.2.sample.json`](inventory.v1.2.sample.json).
- `id` chuỗi khác rỗng, duy nhất; `kind` thuộc 6 nguyên liệu; `fresh` hữu hạn trong [0, 100]. Sai, id trùng, hoặc **file kho đếm khi chạy v1.2** → mã 2.
- Id cấp `I1, I2, …` theo thứ tự vào giỏ, tăng liên tục qua pha và Ngày (không cấp lại id đã dùng/bỏ). LIFO theo thứ tự vào giỏ.
- File ghi sắp theo id, `fresh` đủ chữ số (repr float) để đọc lại giữ đúng nhánh ở ngưỡng 30. Ghi một lần khi `gather_end`, nguyên tử; ngất ghi `{"items":[]}`. `gather_end.data.inventory` cùng schema (JSONL làm tròn 3 chữ số).
- Kho quán nhận nguyên id, kind, fresh, kể cả hàng ươn. Sức chứa giỏ chỉ áp lên giỏ.

## Độ tươi

| | Giỏ (gather) | Kho quán |
|---|---|---|
| Hao | 0.5/s | 0.25/s, kể cả hàng đang giữ chỗ |
| Bắt đầu | hàng mới `fresh = 100`, hao từ bước sau | nhận nguyên giá trị lúc bàn giao, hao từ bước sau |
| Ươn | `fresh < 30`: vẫn chiếm ô, không nấu được; phát `spoiled {item_id, kind, location}` đúng một lần khi đi từ ≥ 30 xuống < 30, nhiều cá thể thì theo id |

**Giao diện giữa module:** file kho, `gather_end`, `read_inventory(..., instances=True)` và kho truyền cho `QuanSim` trong `day` đều là dạng hợp đồng `{id, kind, fresh}` (fresh là số thực).

**Biểu diễn nội bộ của gather:** `u = round(fresh × 240)` là số nguyên, trừ 2 đơn vị/tick, ươn khi `u < 30 × 240`; file ghi `u/240` đủ chữ số. **Bên đọc nên làm tròn về cùng lưới** (`round(fresh × 240)` hoặc `Fraction(round(fresh × 240), 240)`) trước khi hao tươi, vì `u/240` dạng float có thể nhỏ hơn giá trị đúng một chút (vd. `30.004166666666666`) và làm hàng ươn sớm 1 tick. Hàm có sẵn: `chonoi/inventory.py` `to_units`, `from_units`, `item_out`, `validate_instances`, `to_counts`; `chonoi/contract.py` `is_v12(tuning)`, `decay_units_per_tick(tuning, "gather"|"quan")`.

## Công tắc chuyển phiên bản

- Bật theo `contract_version`: `is_v12(tuning)` (`load_contract` chép version vào `tuning`). `tuning.freshness` bắt buộc ở 1.2; khai sẵn ở 1.1 được (preset hiện có) nhưng chưa dùng.
- `gather` hỗ trợ cả hai: v1.1 xuất mảng kind / kho đếm như cũ; v1.2 xuất cá thể, hao tươi, `spoiled`.
- Chạy thử v1.2 khi preset gốc còn 1.1: `CHONOI_CONTRACT=docs/proof/phase-3/contract-v1.2.json python3 -m chonoi.headless …`.

## Thứ tự tích hợp

1. Adapter kho + gather v1.2 (TV2) — xong, test `tests/test_kho_v12.py`. Trên main 8d9fb80 (có quán P3 của TV3): 145/145 test xanh, `check_handoff` v1.2 KHỚP. `day` v1.2 chỉ chạy khi giỏ rỗng; có hàng thì vỡ ở `check_evening_fixture` (bước 2, xem `docs/proof/phase-3/handoff.txt` mục 4).
2. Quán v1.2 (TV3/TV4): `QuanSim` nhận `stock` mảng cá thể, hao 1 đơn vị/tick, giữ chỗ theo id, giá theo tươi; `scenario.quan.stock` và `customers[].reserved` dạng cá thể. `day.py` (TV1): `check_evening_fixture` nhận mảng cá thể.
3. HUD (TV5) đọc `hold[].fresh`, `stock[].fresh`.
4. Integrator (TV1) đổi `contract_version` thành `"1.2"` và thêm `tuning.freshness` ở preset gốc khi 1–3 xong; chạy `tools/check_handoff.py` + regression.
