"""File kho (Contract G). Hai schema, chọn theo contract_version:

v1.0/v1.1 — kho đếm:     {"items": {kind: số nguyên >= 0}}
v1.2      — kho cá thể:  {"items": [{"id": "I1", "kind": "ca_linh", "fresh": 100}, ...]}

Đọc: từ chối sai schema / kind lạ / số âm / id trùng / fresh ngoài [0, 100] (BadInput -> mã 2).
     v1.2 gặp file kho đếm (hoặc ngược lại) cũng là sai schema.
Ghi: kho đếm bỏ mục bằng 0; kho cá thể sắp theo id. Qua file tạm cùng thư mục rồi thay thế, byte-ổn-định.

Độ tươi bên trong sim là số nguyên `u` = fresh × FRESH_UNIT để so ngưỡng 30 chính xác
(gather trừ 2 đơn vị/tick, quán 1 đơn vị/tick với số chuẩn). Ra ngoài (JSONL, file) mới đổi về fresh.
"""

import json
import math
import os
import tempfile

from .errors import BadInput
from .ids import sort_by_id

# ID cố định theo contract v1.1 (6 nguyên liệu); số liệu đi kèm nằm trong game.contract.json
FISH_KINDS = ("ca_linh", "ca_loc", "ca_keo")
NODE_KINDS = ("bong_dien_dien", "bong_sung", "keo_neo")
KINDS = FISH_KINDS + NODE_KINDS
FRESH_UNIT = 240  # đơn vị nội bộ mỗi điểm tươi


def to_units(fresh) -> int:
    return round(fresh * FRESH_UNIT)


def from_units(u: int) -> float:
    return u / FRESH_UNIT


def item_out(it: dict) -> dict:
    """Cá thể nội bộ {id, kind, u} -> dạng hợp đồng {id, kind, fresh}."""
    return {"id": it["id"], "kind": it["kind"], "fresh": from_units(it["u"])}


def validate_items(items, kinds=KINDS):
    if not isinstance(items, dict):
        raise BadInput("items phải là object")
    out = {}
    for k, v in items.items():
        if k not in kinds:
            raise BadInput(f"nguyên liệu lạ: {k}")
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise BadInput(f"số lượng không hợp lệ cho {k}: {v!r}")
        if v > 0:
            out[k] = v
    return out


def validate_instances(items, kinds=KINDS, name="items") -> list:
    """Mảng cá thể v1.2 -> [{id, kind, fresh}] (dạng hợp đồng) giữ thứ tự gốc. Sai -> BadInput."""
    if not isinstance(items, list):
        raise BadInput(f"{name} phải là mảng cá thể {{id, kind, fresh}} (contract v1.2)")
    out, seen = [], set()
    for it in items:
        if not isinstance(it, dict) or set(it) != {"id", "kind", "fresh"}:
            raise BadInput(f"{name}: mỗi cá thể phải có đúng id, kind, fresh")
        i, k, f = it["id"], it["kind"], it["fresh"]
        if not isinstance(i, str) or not i or i in seen:
            raise BadInput(f"{name}: id phải là chuỗi khác rỗng, duy nhất ({i!r})")
        if k not in kinds:
            raise BadInput(f"{name}: nguyên liệu lạ {k!r}")
        if isinstance(f, bool) or not isinstance(f, (int, float)) or not math.isfinite(f) or not 0 <= f <= 100:
            raise BadInput(f"{name}.{i}: fresh phải hữu hạn trong [0, 100] ({f!r})")
        seen.add(i)
        out.append({"id": i, "kind": k, "fresh": f})
    return out


def read_inventory(path: str, kinds=KINDS, instances=False):
    """instances=True (contract v1.2) trả mảng [{id, kind, fresh}], ngược lại trả object đếm."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được file kho {path}: {e}")
    if not isinstance(data, dict) or set(data.keys()) != {"items"}:
        raise BadInput("file kho chỉ được có khóa gốc 'items'")
    if instances:
        return validate_instances(data["items"], kinds)
    return validate_items(data["items"], kinds)


def hold_to_items(hold: list) -> dict:
    """Khoang (mảng kind theo thứ tự nhặt) -> object đếm, sắp theo id nguyên liệu."""
    counts = {}
    for k in hold:
        counts[k] = counts.get(k, 0) + 1
    return {k: counts[k] for k in sorted(counts)}


def to_counts(items: list) -> dict:
    """Adapter tạm cho bên chưa chuyển sang cá thể: [{kind, ...}] -> object đếm."""
    return hold_to_items([it["kind"] for it in items])


def write_inventory(path: str, items):
    """items: object đếm (v1.1) hoặc mảng cá thể [{id, kind, fresh}] (v1.2), ghi sắp theo id.
    fresh ghi đủ chữ số (repr của float) để đọc lại giữ đúng nhánh ở ngưỡng."""
    if isinstance(items, list):
        items = [{"id": it["id"], "kind": it["kind"], "fresh": it["fresh"]} for it in sort_by_id(items)]
    else:
        items = {k: items[k] for k in sorted(items) if items[k] > 0}
    d = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(prefix=".inv-", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"items": items}, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
