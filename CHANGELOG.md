# Changelog

Ghi theo từng phase (tag `phase-1` … `phase-4`). Phiên bản Test Contract ghi trong ngoặc.

## [1.0.0] — Phase 4: Phát hành (Contract v1.3, TICKET-04)
- `contract_version: "1.3"`; gameplay, tuning, kho cá thể và JSONL giữ như v1.2.
- Thêm `bench_cmd` = `python3 -m chonoi.bench`: benchmark có render cảnh lặn lõi (seed, độ tươi, cá bơi, Cá Sấu, Út Sen đứng yên ở bến) bằng giao diện Canvas của game ở 1280×720, làm nóng 3 s, ghi `bench.json {avg_fps, p1_low_fps, frames, measured_s, load_ms}`. Giao diện chỉ bật bộ đo khi URL có `?bench=1`.
- Thêm `soak_cmd` = `python3 -m chonoi.soak`: 10 Ngày trong một tiến trình bằng bot tất định, ghi `soak.json {days, days_completed, crashes, results, duration_s}`.
- Khai mở rộng `extensions: ["burn"]`, `quan.burn_s: 20` (Cháy món). Trình kiểm contract chỉ nhận `burn_s` khác `null` khi khai `burn`.
- Cảnh báo bằng chữ + biểu tượng (Thủy quái!, Hết hơi!, Khách sắp giận!) và chế độ tương phản cao (phím C).
- Thêm `LICENSE` (MIT), README ghi đủ lệnh chạy/test/headless/bench/soak, release notes `docs/release-notes-v1.0.0.md`.
- Test: `tests/test_qa_p4.py` (manifest v1.3, soak, bench, tài liệu phát hành, leaderboard nếu khai), `tests/test_qa_ext.py` (burn).

## Phase 3 — Mùa Nước Nổi (Contract v1.2, TICKET-03)

### Breaking change — kho cá thể
- File kho đổi từ kho đếm `{"items": {"ca_loc": 1}}` sang mảng cá thể `{"items": [{"id": "I1", "kind": "ca_loc", "fresh": 100}]}`. Khi chạy v1.2, file kho đếm bị từ chối (mã 2). Chi tiết: `docs/contracts/kho-v1.2.md`.
- `gather.hold` trong scenario và snapshot, `lost` trong `monster_hit`/`faint`, `gather_end.data.inventory` dùng cá thể `{id, kind, fresh}`.
- Thêm `tuning.freshness {initial, gather_decay_per_s, quan_decay_per_s, spoiled_below}`, bắt buộc khi `contract_version` là `"1.2"`. Schema kho và độ tươi chỉ bật theo `contract_version`.
- Thêm event `spoiled {item_id, kind, location}`.
- **Cập nhật fixture:** `"hold": ["ca_loc"]` → `"hold": [{"id": "I1", "kind": "ca_loc", "fresh": 100}]`; file kho đếm → mảng cá thể (id duy nhất, fresh trong [0, 100]).
- Biến môi trường `CHONOI_CONTRACT` để chạy thử với contract khác (vd. v1.2) mà không sửa preset gốc.
- **Bật v1.2** ở preset gốc (`contract_version: "1.2"`). Quán: `scenario.quan.stock` là mảng cá thể, `customers[].reserved` là mảng id (kho đếm → mã 2); kho rỗng `[]`; `served`/`paid` dùng giá đã chốt theo fresh trên món.
- **Cập nhật fixture quán:** `"stock": {"ca_loc": 1}` → `"stock": [{"id": "I1", "kind": "ca_loc", "fresh": 100}]`; `"reserved": {"ca_loc": 1}` → `"reserved": ["I1"]` (bỏ trống để tự cấp tươi nhất).
- Test hồi quy P1–P2 chạy trên v1.2 qua `tests/v12_adapter.py`; test đổi vì luật mới ghi trong `docs/verification/phase-3.md`.

## Phase 2 — Một ngày ở chợ nổi (Contract v1.1, TICKET-02)
- Số chuẩn: 8 đàn cá bơi 1.5 m/s, đổi hướng/phản xạ mép, sinh theo lịch 360·k (trần 12); nút N1–N6 (thêm kèo nèo); cá kèo yield 2.
- Cá Sấu Năm Chèo (M1, M2 từ Ngày 3): tuần tra, đuổi, chạm mất Máu và nửa giỏ LIFO, bất tử 90 tick, recoil 60 bước; ngất do thủy quái.
- Quán 2 bếp / 4 bàn, 6 món (thêm canh chua cá lóc, cá kèo nướng, lẩu mắm); kế hoạch ngày D1–D5.
- Mode `day` (`--days 1..5`): gather → quán → Shop (nâng cấp oxy/Máu, hiệu lực từ Ngày kế), pause, `days_completed`.
- Sửa theo PRD-0: data `customer_arrived` dùng `order_id`, `no_dish` là `{}`; quán độc lập kiểm mâu thuẫn fixture (mã 2).

## Phase 1 — PRD-0 (Contract v1.0)
- Buổi sáng `gather`: bơi/ramp/chặn mép, oxy và ngạt, Máu, ngất, hái nút, bắt cá, giỏ LIFO 12 ô, cập bến, file kho.
- Buổi tối `quan`: khách theo lịch, giữ chỗ nguyên liệu, kiên nhẫn, nấu → bưng → phục vụ, boa, uy tín, đóng ca.
- Hợp đồng kho `{"items": {kind: n}}`, smoke hai tiến trình `gather --inventory-out` → `quan --inventory`.
