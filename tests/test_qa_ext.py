"""Test QA mở rộng (TV6) — chỉ chạy khi manifest khai mã trong `extensions`. Hộp đen, viết từ đề.

burn (TICKET-02 mục 3 "Cháy món", v1.1 mục 4.1/4.4/4.5, áp kho cá thể v1.2/v1.3):
  burn_s 20 → 1.200 tick. ready_ticks > 1200 thì bỏ món, nguyên liệu mất, bếp rảnh ngay; thử giữ lại ngay cho đơn:
  đủ → reserved, thiếu → unfulfillable, khách chờ tới hết kiên nhẫn. Đúng 1.200 tick vẫn bưng được.
  Xét món chín/cháy theo id bếp TRƯỚC di chuyển và tương tác. Event dish_burnt {stove_id, order_id, dish_id, order_status}.

Chạy: PYTHONPATH=tests:. python3 -m unittest tests.test_qa_ext -v
"""

import json
import os
import unittest

from helpers import ROOT, Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json

with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as _f:
    CONTRACT = json.load(_f)
EXT = set(CONTRACT.get("extensions") or [])
B1 = [2, 8]
PAY = {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 45}


def run(w, quan, inputs=None, ticks=1):
    args = ["--mode", "quan", "--seed", "1", "--ticks", str(ticks), "--out", w.path("q.jsonl"),
            "--scenario", write_json(w.path("sc.json"), {"quan": quan})]
    if inputs is not None:
        args += ["--inputs", write_json(w.path("in.json"), frames(*inputs))]
    code, err = run_headless(*args)
    if code != 0:
        raise AssertionError(f"headless thoát mã {code}: {err}")
    return read_jsonl(w.path("q.jsonl"))


def fixture(ready_ticks, stock=(), **kw):
    return {"random_customers": False, "player": {"pos": [8, 5]}, "stock": list(stock),
            "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                           "order_status": "assigned", "reserved": []}],
            "stoves": [{"id": "B1", "state": "ready", "dish": PAY, "ready_ticks": ready_ticks}], **kw}


@unittest.skipUnless("burn" in EXT, "chưa khai mở rộng burn")
class Burn(unittest.TestCase):
    def test_ext_burn_manifest(self):
        self.assertEqual(CONTRACT["tuning"]["quan"]["burn_s"], 20)

    def test_ext_burn_dung_1200_tick_van_bung_duoc(self):
        with Workdir() as w:
            rows = run(w, fixture(1199, player={"pos": B1}), [{"tick": 0, "interact": True}])
            self.assertEqual(events(rows, "dish_burnt"), [])
            self.assertEqual(len(events(rows, "dish_picked")), 1, "ready_ticks = 1200 vẫn bưng được")
            self.assertEqual(snapshots(rows)[-1]["hand"], PAY)

    def test_ext_burn_qua_1200_chay_truoc_tuong_tac(self):
        with Workdir() as w:
            rows = run(w, fixture(1200, player={"pos": B1}), [{"tick": 0, "interact": True}])
            e = events(rows, "dish_burnt")
            self.assertEqual(len(e), 1)
            self.assertEqual(e[0]["tick"], 1)
            self.assertEqual(events(rows, "dish_picked"), [], "cháy xét trước tương tác")
            b1 = snapshots(rows)[-1]["stoves"][0]
            self.assertEqual((b1["state"], b1["dish"]), ("idle", None), "bếp rảnh ngay")
            self.assertIsNone(snapshots(rows)[-1]["hand"])

    def test_ext_burn_thieu_nguyen_lieu_unfulfillable_khach_van_cho(self):
        with Workdir() as w:
            rows = run(w, fixture(1200), ticks=3)
            self.assertEqual(events(rows, "dish_burnt")[0]["data"],
                             {"stove_id": "B1", "order_id": "C1", "dish_id": "ca_loc_nuong_trui",
                              "order_status": "unfulfillable"})
            c = snapshots(rows)[-1]["customers"][0]
            self.assertEqual((c["order_status"], c["state"], c["reserved"]), ("unfulfillable", "waiting", []))
            self.assertEqual(events(rows, "customer_left"), [])

    def test_ext_burn_du_nguyen_lieu_giu_lai_tuoi_nhat(self):
        stock = [{"id": "I1", "kind": "ca_loc", "fresh": 60}, {"id": "I2", "kind": "ca_loc", "fresh": 90}]
        with Workdir() as w:
            rows = run(w, fixture(1200, stock), ticks=1)
            self.assertEqual(events(rows, "dish_burnt")[0]["data"]["order_status"], "reserved")
            c = snapshots(rows)[-1]["customers"][0]
            self.assertEqual((c["order_status"], c["reserved"]), ("reserved", ["I2"]))

    def test_ext_burn_hai_bep_xet_theo_id(self):
        pay2 = {"order_id": "C2", "dish_id": "ca_loc_nuong_trui", "base_price": 45}
        q = fixture(1200)
        q["customers"].append({"id": "C2", "table_id": "T2", "dish_id": "ca_loc_nuong_trui",
                               "order_status": "assigned", "reserved": []})
        q["stoves"] = [{"id": "B2", "state": "ready", "dish": pay2, "ready_ticks": 1200},
                       {"id": "B1", "state": "ready", "dish": PAY, "ready_ticks": 1200}]
        with Workdir() as w:
            rows = run(w, q, ticks=1)
            self.assertEqual([e["data"]["stove_id"] for e in events(rows, "dish_burnt")], ["B1", "B2"])


if __name__ == "__main__":
    unittest.main()
