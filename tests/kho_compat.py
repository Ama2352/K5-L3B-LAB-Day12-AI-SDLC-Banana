"""Chuyển test kho đếm (v1.1) sang chạy được cả kho cá thể (v1.2/v1.3, TICKET-03/04).

Test giữ nguyên ý định (đúng loại, đúng số lượng, đúng thứ tự); chỉ đổi cách dựng fixture và cách so.
Phiên bản đọc từ CHONOI_CONTRACT (nếu đặt) hoặc game.contract.json, giống headless.
"""

import json
import os

with open(os.environ.get("CHONOI_CONTRACT") or "game.contract.json", encoding="utf-8") as _f:
    CONTRACT = json.load(_f)
V12 = CONTRACT["contract_version"] in ("1.2", "1.3")


def hold_fx(kinds):
    """Fixture gather.hold theo schema đang chạy: v1.1 mảng kind, v1.2+ cá thể I1.. tươi 100."""
    if not V12:
        return list(kinds)
    return [{"id": f"I{i}", "kind": k, "fresh": 100} for i, k in enumerate(kinds, 1)]


def kinds_of(items):
    """Giỏ / lost theo thứ tự -> mảng kind."""
    return [it["kind"] if isinstance(it, dict) else it for it in items]


def inv_counts(inv):
    """{"items": ...} (đếm hoặc cá thể) -> {"items": {kind: n}} để so số lượng theo loại."""
    items = inv["items"]
    if isinstance(items, dict):
        return {"items": items}
    out = {}
    for k in kinds_of(items):
        out[k] = out.get(k, 0) + 1
    return {"items": dict(sorted(out.items()))}
