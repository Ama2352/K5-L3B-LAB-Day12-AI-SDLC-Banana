"""Chuyển test hồi quy P1/P2 sang Contract v1.2 (TICKET-03: kho đếm → kho cá thể).

Lý do (TICKET-03 mục 3): "chạy lại regression P1–P2 còn hiệu lực. Ghi lý do nếu test cũ bị thay bởi luật mới."
Luật P1/P2 (oxy, Cá Sấu, khách, bếp, boa, vòng ngày...) vẫn còn hiệu lực; chỉ SCHEMA kho đổi. Lớp này:
  - vào: đổi fixture kiểu v1.1 sang cá thể v1.2, fresh 100, id I1.. theo thứ tự:
        gather.hold ["ca_loc", ...]      → [{"id":"I1","kind":"ca_loc","fresh":100}, ...]
        quan.stock  {"ca_loc": 2, ...}   → mảng cá thể (sắp theo kind)
        customers[].reserved {} (đơn không giữ)  → []
  - ra: quy cá thể về dạng v1.1 để so luật cũ:
        hold → mảng kind; stock / inventory.items → object đếm; reserved → đếm theo kind;
        cook_started.items, monster_hit.lost, faint.lost → mảng kind.
Không đổi giá trị nào khác. Chỗ luật THẬT SỰ đổi (giá chốt theo fresh) sửa trực tiếp trong test, có ghi lý do.
Schema v1.2 được kiểm chặt riêng ở tests/test_qa_p3.py (không qua lớp này).
Khi contract còn v1.1 thì lớp này không làm gì.
"""

import copy
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as _f:
    V12 = json.load(_f)["contract_version"] in ("1.2", "1.3")


def _instances(kinds, start=1):
    return [{"id": f"I{start + i}", "kind": k, "fresh": 100} for i, k in enumerate(kinds)]


def _is_count_map(x):
    return isinstance(x, dict) and all(isinstance(v, int) and not isinstance(v, bool) and v >= 0 for v in x.values())


def stock_items(counts, start=1):
    kinds = [k for k in sorted(counts) for _ in range(counts[k])]
    return _instances(kinds, start)


def scenario(sc):
    """Fixture v1.1 → v1.2 (giữ nguyên fixture sai kiểu để test mã 2 vẫn đúng)."""
    if not V12 or not isinstance(sc, dict):
        return sc
    sc = copy.deepcopy(sc)
    g = sc.get("gather")
    if isinstance(g, dict) and isinstance(g.get("hold"), list) and all(isinstance(k, str) for k in g["hold"]):
        g["hold"] = _instances(g["hold"])
    q = sc.get("quan")
    if isinstance(q, dict):
        if _is_count_map(q.get("stock")):
            q["stock"] = stock_items(q["stock"])
        for c in q.get("customers", []) if isinstance(q.get("customers"), list) else []:
            if isinstance(c, dict) and c.get("reserved") == {}:
                c["reserved"] = []
    return sc


def inventory(obj):
    """File kho v1.1 {"items": {kind: n}} → v1.2 (chỉ khi là object đếm hợp lệ)."""
    if V12 and isinstance(obj, dict) and set(obj) == {"items"} and _is_count_map(obj["items"]):
        return {"items": stock_items(obj["items"])}
    return obj


def _kinds(items):
    return [x["kind"] if isinstance(x, dict) else x for x in items]


def _counts(items):
    if not isinstance(items, list):
        return items
    out = {}
    for k in _kinds(items):
        out[k] = out.get(k, 0) + 1
    return {k: out[k] for k in sorted(out)}


def inventory_view(obj):
    if V12 and isinstance(obj, dict) and isinstance(obj.get("items"), list):
        return {**obj, "items": _counts(obj["items"])}
    return obj


def view(rows):
    """Dòng JSONL v1.2 → dạng so sánh v1.1."""
    if not V12:
        return rows
    known = {}
    out = []
    for r in rows:
        r = copy.deepcopy(r)
        if r.get("type") == "snapshot":
            for key in ("hold", "stock"):
                if isinstance(r.get(key), list):
                    known.update({x["id"]: x["kind"] for x in r[key] if isinstance(x, dict)})
            if isinstance(r.get("hold"), list):
                r["hold"] = _kinds(r["hold"])
            if isinstance(r.get("stock"), list):
                r["stock"] = _counts(r["stock"])
            for c in r.get("customers", []) or []:
                if isinstance(c.get("reserved"), list):
                    c["reserved"] = _counts([known.get(i, i) for i in c["reserved"]])
        elif r.get("type") == "event":
            d = r.get("data", {})
            if isinstance(d.get("inventory"), dict):
                d["inventory"] = inventory_view(d["inventory"])
            for key in ("items", "lost"):
                if isinstance(d.get(key), list):
                    d[key] = _kinds(d[key])
        out.append(r)
    return out
