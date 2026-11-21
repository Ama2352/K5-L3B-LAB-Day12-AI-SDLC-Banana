"""Kiểm bàn giao kho gather -> quan (Contract G; v1.2 kho cá thể). Chỉ thư viện chuẩn, chạy hộp đen qua headless_cmd.

Dùng: python3 tools/check_handoff.py <gather.jsonl> <kho.json>
  1. kho.json đúng schema theo contract_version:
       v1.1 {"items": {kind: int > 0}} · v1.2 {"items": [{id, kind, fresh}]} (id duy nhất, fresh ∈ [0, 100])
  2. kho.json == data.inventory của gather_end (đúng một gather_end) trong gather.jsonl
  3. quan --inventory kho.json --ticks 0: snapshot tick 0 có stock == items
v1.2 so từng cá thể: id, kind chính xác; fresh trong JSONL đã làm tròn 3 chữ số nên so với round(fresh file, 3).
Contract đọc từ game.contract.json, hoặc CHONOI_CONTRACT nếu đặt. In bảng; mã 0 khi khớp hết, 1 khi lệch.
"""

import json
import math
import os
import shlex
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_contract():
    path = os.environ.get("CHONOI_CONTRACT") or os.path.join(ROOT, "game.contract.json")
    with open(path, encoding="utf-8") as f:
        c = json.load(f)
    t = c["tuning"]
    # loại nguyên liệu lấy từ dữ liệu: cá (fish_yield), nút hái, công thức món
    kinds = set(t["gather"]["fish_yield"]) | {n["kind"] for n in t["gather"]["nodes"]}
    kinds |= {k for d in t["menu"].values() for k in d["recipe"]}
    return shlex.split(c["headless_cmd"]), tuple(sorted(kinds)), c.get("contract_version") in ("1.2", "1.3")


def schema_ok(items, kinds, v12):
    if not v12:
        return isinstance(items, dict) and all(k in kinds and type(v) is int and v > 0 for k, v in items.items())
    return (isinstance(items, list)
            and all(isinstance(i, dict) and set(i) == {"id", "kind", "fresh"} and isinstance(i["id"], str) and i["id"]
                    and i["kind"] in kinds and type(i["fresh"]) in (int, float) and math.isfinite(i["fresh"])
                    and 0 <= i["fresh"] <= 100 for i in items)
            and len({i["id"] for i in items}) == len(items))


def quan_stock(cmd, inv_path, errs):
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "quan.jsonl")
        p = subprocess.run([*cmd, "--mode", "quan", "--seed", "1", "--ticks", "0",
                            "--inventory", os.path.abspath(inv_path), "--out", out],
                           cwd=ROOT, capture_output=True, text=True)
        if p.returncode != 0:
            errs.append(f"quan đọc kho lỗi (mã {p.returncode}): {p.stderr.strip()}")
            return None
        with open(out, encoding="utf-8") as f:
            return json.loads(f.readline())["stock"]


def report_counts(items, end_inv, stock, kinds, errs):
    print(f"{'kind':<16}{'kho.json':>10}{'gather_end':>12}{'quan.stock':>12}")
    for k in kinds:
        a = items.get(k, 0)
        b = "?" if end_inv is None else end_inv.get(k, 0)
        c = "?" if stock is None else stock.get(k, 0)
        mark = "" if a == b == c else "  <-- LỆCH"
        print(f"{k:<16}{a:>10}{b:>12}{c:>12}{mark}")
        if mark:
            errs.append(f"lệch {k}: kho={a} gather_end={b} quan={c}")
    print(f"tổng: {sum(items.values())} món")


def report_instances(items, end_inv, stock, errs):
    def by_id(arr):
        return {i["id"]: i for i in arr} if isinstance(arr, list) else None

    a, b, c = by_id(items), by_id(end_inv), by_id(stock)
    if stock is not None and c is None:
        errs.append(f"quan.stock chưa là mảng cá thể: {stock}")
    ids = sorted(set(a) | set(b or {}) | set(c or {}), key=lambda i: (len(i), i))
    print(f"{'id':<6}{'kind':<16}{'fresh (kho.json)':>20}{'gather_end':>12}{'quan.stock':>12}")
    for i in ids:
        x = a.get(i)
        want = (x["kind"], round(x["fresh"], 3)) if x else None
        got = [(d[i]["kind"], d[i]["fresh"]) if d is not None and i in d else None for d in (b, c)]
        mark = "" if all(g == want for g, d in zip(got, (b, c)) if d is not None) else "  <-- LỆCH"
        cells = ["?" if d is None else ("-" if g is None else g[1]) for g, d in zip(got, (b, c))]
        print(f"{i:<6}{(x or {}).get('kind', '-'):<16}{(x['fresh'] if x else '-'):>20}{cells[0]:>12}{cells[1]:>12}{mark}")
        if mark:
            errs.append(f"lệch {i}: kho={want} gather_end={got[0]} quan={got[1]}")
    print(f"tổng: {len(items)} cá thể, ươn (< 30): {sum(1 for x in items if x['fresh'] < 30)}")


def main(gather_jsonl, inv_path):
    errs = []
    cmd, kinds, v12 = load_contract()
    with open(inv_path, encoding="utf-8") as f:
        inv = json.load(f)
    items = inv.get("items") if isinstance(inv, dict) and set(inv) == {"items"} else None
    if not schema_ok(items, kinds, v12):
        errs.append(f"schema kho sai cho contract {'1.2' if v12 else '1.1'}: {inv}")
        items = [] if v12 else {}

    with open(gather_jsonl, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    ends = [r for r in rows if r["type"] == "event" and r["name"] == "gather_end"]
    end_inv = ends[0]["data"]["inventory"]["items"] if len(ends) == 1 else None
    if end_inv is None:
        errs.append(f"cần đúng 1 gather_end, thấy {len(ends)}")
    stock = quan_stock(cmd, inv_path, errs)

    print(f"contract {'1.2 (kho cá thể)' if v12 else '1.1 (kho đếm)'} · gather_end reason: "
          f"{ends[0]['data']['reason'] if ends else '-'}")
    if v12:
        report_instances(items, end_inv, stock, errs)
    else:
        report_counts(items, end_inv, stock, kinds, errs)
    for e in errs:
        print("LỖI:", e, file=sys.stderr)
    print("KẾT QUẢ:", "KHỚP" if not errs else "LỆCH")
    return 0 if not errs else 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(*sys.argv[1:]))
