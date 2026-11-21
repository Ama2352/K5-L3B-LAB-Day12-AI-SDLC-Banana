# Changelog
## Unreleased

### Breaking change — Contract v1.2: kho cá thể (TICKET-03 "Mùa Nước Nổi")
- File kho đổi từ kho đếm `{"items": {"ca_loc": 1}}` sang mảng cá thể `{"items": [{"id": "I1", "kind": "ca_loc", "fresh": 100}]}`. Khi chạy v1.2, file kho đếm bị từ chối (mã 2). Chi tiết: `docs/contracts/kho-v1.2.md`.
- `gather.hold` trong scenario và snapshot, `lost` trong `monster_hit`/`faint`, `gather_end.data.inventory` dùng cá thể `{id, kind, fresh}`.
- Thêm `tuning.freshness {initial, gather_decay_per_s, quan_decay_per_s, spoiled_below}`, bắt buộc khi `contract_version` là `"1.2"`. Schema kho và độ tươi chỉ bật theo `contract_version`.
- Thêm event `spoiled {item_id, kind, location}`.
- **Cập nhật fixture:** `"hold": ["ca_loc"]` → `"hold": [{"id": "I1", "kind": "ca_loc", "fresh": 100}]`; file kho đếm → mảng cá thể (id duy nhất, fresh trong [0, 100]).
- Biến môi trường `CHONOI_CONTRACT` để chạy thử với contract khác (vd. v1.2) mà không sửa preset gốc.
- **Bật v1.2** ở preset gốc (`contract_version: "1.2"`). Quán: `scenario.quan.stock` là mảng cá thể, `customers[].reserved` là mảng id (kho đếm → mã 2); kho rỗng `[]`; `served`/`paid` dùng giá đã chốt theo fresh trên món.
- **Cập nhật fixture quán:** `"stock": {"ca_loc": 1}` → `"stock": [{"id": "I1", "kind": "ca_loc", "fresh": 100}]`; `"reserved": {"ca_loc": 1}` → `"reserved": ["I1"]` (bỏ trống để tự cấp tươi nhất).
- Test hồi quy P1–P2 chạy trên v1.2 qua `tests/v12_adapter.py`; test đổi vì luật mới ghi trong `docs/verification/phase-3.md`.
