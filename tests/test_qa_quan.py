"""Test QA Quán (TV6), HỘP ĐEN, phủ đủ AC-P1-19..28 (lát 3 khách + lát 4 bếp/tiền) theo PRD-0 mục E/F/G,
chạy với số chuẩn TICKET-02 (2 bếp, 4 bàn). So NGUYÊN `data` của event theo bảng mục E.

Chạy: PYTHONPATH=tests:. python3 -m unittest tests.test_qa_quan -v
"""

import unittest

from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json

PATIENCE = 3600   # 60 s
EAT = 600         # 10 s
COOK = {"ca_loc_nuong_trui": 360, "goi_bong_sung": 240}
PRICE = {"ca_loc_nuong_trui": 60, "goi_bong_sung": 40}
B1, T1 = [2, 8], [9, 2]


def run_quan(w, quan, inputs=None, ticks=1, seed=1, every=None):
    args = ["--mode", "quan", "--seed", str(seed), "--ticks", str(ticks), "--out", w.path("q.jsonl"),
            "--scenario", write_json(w.path("sc.json"), {"quan": quan})]
    if inputs is not None:
        args += ["--inputs", write_json(w.path("in.json"), frames(*inputs))]
    if every:
        args += ["--snapshot-every", str(every)]
    code, err = run_headless(*args)
    if code != 0:
        raise AssertionError(f"headless thoát mã {code}: {err}")
    return read_jsonl(w.path("q.jsonl"))


def press(t):
    return [{"tick": t, "interact": True}, {"tick": t + 1, "interact": False}]


def cust(cid="C1", table="T1", dish="ca_loc_nuong_trui", **kw):
    return {"id": cid, "table_id": table, "dish_id": dish, **kw}


def payload(cid="C1", dish="ca_loc_nuong_trui"):
    return {"order_id": cid, "dish_id": dish, "base_price": PRICE[dish]}


def one(tc, rows, name):
    ev = events(rows, name)
    tc.assertEqual(len(ev), 1, f"cần đúng 1 event {name}, có {len(ev)}")
    return ev[0]


# ------------------------------------------------------------- Lát 3: khách, giữ chỗ, kiên nhẫn (TV3)
class Arrival(unittest.TestCase):
    def test_ac_p1_20_khach_dau_tien_tick_120_data_dung_de(self):
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"ca_loc": 1}}, ticks=120)
            e = one(self, rows, "customer_arrived")
            self.assertEqual(e["tick"], 120)
            self.assertEqual(set(e["data"]), {"order_id", "table_id", "dish_id"}, "PRD-0 mục E: order_id,table_id,dish_id")
            self.assertEqual((e["data"]["table_id"], e["data"]["dish_id"]), ("T1", "ca_loc_nuong_trui"))
            c = snapshots(rows)[-1]["customers"][0]
            self.assertEqual(c["id"], e["data"]["order_id"], "order_id bằng id khách")
            self.assertEqual((c["state"], c["order_status"], c["order_tick"], c["patience_ticks_left"]),
                             ("waiting", "reserved", 120, PATIENCE))
            self.assertEqual(c["reserved"], {"ca_loc": 1})

    def test_ac_p1_20_chua_toi_tick_120_khong_co_khach(self):
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"ca_loc": 1}}, ticks=119)
            self.assertEqual(events(rows, "customer_arrived") + events(rows, "no_dish"), [])

    def test_ac_p1_20_no_dish_data_rong(self):
        with Workdir() as w:
            rows = run_quan(w, {"stock": {}}, ticks=120)
            e = one(self, rows, "no_dish")
            self.assertEqual((e["tick"], e["data"]), (120, {}), "PRD-0 mục E: no_dish data {}")

    def test_ac_p1_20_random_customers_false_khong_sinh_khach(self):
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"ca_loc": 5}, "random_customers": False}, ticks=1100)
            self.assertEqual(events(rows, "customer_arrived") + events(rows, "no_dish"), [])

    def test_ac_p1_21_giu_cho_tru_khoi_kho_kha_dung(self):
        """Hai khách tranh phần cuối: C1 đã giữ 1 cá lóc duy nhất → khách mới không gọi được cá lóc."""
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"ca_loc": 1}, "customers": [cust()]}, ticks=120)
            self.assertEqual(events(rows, "customer_arrived"), [])
            self.assertEqual(one(self, rows, "no_dish")["data"], {})

    def test_ac_p1_21_chon_mon_trong_cac_mon_du_nguyen_lieu(self):
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"ca_loc": 1, "bong_sung": 1}}, ticks=120)
            self.assertEqual(one(self, rows, "customer_arrived")["data"]["dish_id"], "ca_loc_nuong_trui",
                             "gỏi cần 2 bông súng, chỉ có 1")

    def test_ac_p1_21_chon_deu_theo_seed(self):
        seen = set()
        for seed in range(1, 21):
            with Workdir() as w:
                rows = run_quan(w, {"stock": {"ca_loc": 1, "bong_sung": 2}}, ticks=120, seed=seed)
                seen.add(one(self, rows, "customer_arrived")["data"]["dish_id"])
        self.assertEqual(seen, {"ca_loc_nuong_trui", "goi_bong_sung"}, "20 seed phải ra cả hai món đủ nguyên liệu")

    def test_ac_p1_21_cung_seed_cung_mon(self):
        picks = []
        for _ in range(2):
            with Workdir() as w:
                rows = run_quan(w, {"stock": {"ca_loc": 1, "bong_sung": 2}}, ticks=120, seed=11)
                picks.append(one(self, rows, "customer_arrived")["data"]["dish_id"])
        self.assertEqual(picks[0], picks[1])

    def test_ac_p1_22_het_kien_nhan_roi_quan_tru_uy_tin(self):
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"ca_loc": 1}, "random_customers": False,
                                "customers": [cust(patience_ticks_left=1)]}, ticks=3)
            e = one(self, rows, "customer_left")
            self.assertEqual(e["tick"], 1)
            self.assertEqual(e["data"], {"order_id": "C1", "table_id": "T1", "reason": "patience", "reputation": 2.5})
            s = snapshots(rows)[-1]
            self.assertEqual((s["customers"], s["reputation"]), ([], 2.5))
            self.assertIsNone(s["tables"][0]["customer_id"])

    def test_ac_p1_22_khach_roi_nha_giu_cho_cho_khach_sau(self):
        with Workdir() as w:
            sc = {"stock": {"ca_loc": 1}, "customers": [cust(patience_ticks_left=50)]}
            rows = run_quan(w, sc, ticks=120)
            self.assertEqual(one(self, rows, "customer_left")["data"]["reason"], "patience")
            self.assertEqual(one(self, rows, "customer_arrived")["data"]["dish_id"], "ca_loc_nuong_trui",
                             "cá lóc được nhả sau khi C1 rời")

    def test_ac_p1_22_uy_tin_kep_toi_thieu_0(self):
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"ca_loc": 1}, "random_customers": False, "reputation": 0.2,
                                "customers": [cust(patience_ticks_left=1)]}, ticks=1)
            self.assertEqual(one(self, rows, "customer_left")["data"]["reputation"], 0)


# ------------------------------------------------------------- Lát 4: bếp, bưng, phục vụ, tiền (TV4)
class Kitchen(unittest.TestCase):
    def test_ac_p1_24_bep_idle_bat_dau_nau_dung_data(self):
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"ca_loc": 1}, "random_customers": False, "customers": [cust()],
                                "player": {"pos": B1}}, press(0), ticks=2)
            e = one(self, rows, "cook_started")
            self.assertEqual(e["tick"], 1)
            self.assertEqual(e["data"], {"stove_id": "B1", "order_id": "C1", "dish_id": "ca_loc_nuong_trui",
                                         "items": ["ca_loc"], "base_price": 60})
            s = snapshots(rows)[-1]
            self.assertEqual(s["stock"], {}, "tiêu đúng nguyên liệu đã giữ")
            self.assertEqual(s["customers"][0]["order_status"], "assigned")
            self.assertEqual(s["stoves"][0]["state"], "cooking")

    def test_ac_p1_24_lay_don_reserved_cu_nhat(self):
        with Workdir() as w:
            cs = [cust("C1", "T1", order_tick=50), cust("C2", "T2", "goi_bong_sung", order_tick=10)]
            rows = run_quan(w, {"stock": {"ca_loc": 1, "bong_sung": 2}, "random_customers": False, "customers": cs,
                                "player": {"pos": B1}}, press(0), ticks=1)
            self.assertEqual(one(self, rows, "cook_started")["data"]["order_id"], "C2")

    def test_ac_p1_24_items_sap_theo_kind(self):
        with Workdir() as w:
            cs = [cust(dish="lau_ca_linh_dien_dien")]
            rows = run_quan(w, {"stock": {"ca_linh": 3, "bong_dien_dien": 1}, "random_customers": False,
                                "customers": cs, "player": {"pos": B1}}, press(0), ticks=1)
            self.assertEqual(one(self, rows, "cook_started")["data"]["items"],
                             ["bong_dien_dien", "ca_linh", "ca_linh", "ca_linh"])

    def test_ac_p1_24_nau_xong_dung_cook_s(self):
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"ca_loc": 1}, "random_customers": False, "customers": [cust()],
                                "player": {"pos": B1}}, press(0), ticks=400)
            start = one(self, rows, "cook_started")["tick"]
            ready = one(self, rows, "dish_ready")
            self.assertEqual(ready["tick"] - start, COOK["ca_loc_nuong_trui"])
            self.assertEqual(ready["data"], {"stove_id": "B1", "order_id": "C1", "dish_id": "ca_loc_nuong_trui"})

    def test_ac_p1_25_bung_mon_tu_bep_ready(self):
        with Workdir() as w:
            sc = {"random_customers": False, "player": {"pos": B1},
                  "customers": [cust(order_status="assigned", reserved={})],
                  "stoves": [{"id": "B1", "state": "ready", "dish": payload()}]}
            rows = run_quan(w, sc, press(0), ticks=1)
            self.assertEqual(one(self, rows, "dish_picked")["data"],
                             {"stove_id": "B1", "order_id": "C1", "dish_id": "ca_loc_nuong_trui"})
            s = snapshots(rows)[-1]
            self.assertEqual(s["hand"], payload())
            self.assertEqual(s["stoves"][0]["state"], "idle")

    def test_ac_p1_25_tay_day_khong_bung_them(self):
        with Workdir() as w:
            cs = [cust(order_status="assigned", reserved={}),
                  cust("C2", "T2", order_status="assigned", reserved={})]
            sc = {"random_customers": False, "player": {"pos": B1}, "customers": cs, "hand": payload("C2"),
                  "stoves": [{"id": "B1", "state": "ready", "dish": payload()}]}
            rows = run_quan(w, sc, press(0), ticks=1)
            self.assertEqual(events(rows, "dish_picked"), [])
            self.assertEqual(snapshots(rows)[-1]["hand"], payload("C2"))

    def test_ac_p1_26_phuc_vu_con_nhieu_kien_nhan_co_boa(self):
        with Workdir() as w:
            sc = {"random_customers": False, "player": {"pos": [9, 2.5]}, "hand": payload(),
                  "customers": [cust(order_status="assigned", reserved={})]}
            rows = run_quan(w, sc, press(0), ticks=1)
            e = one(self, rows, "served")
            self.assertEqual(e["data"], {"order_id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                                         "patience_ticks_left": PATIENCE - 1, "base_price": 60, "tip": 12})
            s = snapshots(rows)[-1]
            self.assertIsNone(s["hand"])
            c = s["customers"][0]
            self.assertEqual((c["state"], c["order_status"], c["eat_ticks_left"]), ("eating", "served", EAT))

    def test_ac_p1_26_kien_nhan_duoi_50_phan_tram_boa_0(self):
        with Workdir() as w:
            sc = {"random_customers": False, "player": {"pos": [9, 2.5]}, "hand": payload(),
                  "customers": [cust(order_status="assigned", reserved={}, patience_ticks_left=1000)]}
            rows = run_quan(w, sc, press(0), ticks=1)
            self.assertEqual(one(self, rows, "served")["data"]["tip"], 0)

    def test_ac_p1_26_dung_moc_50_phan_tram_van_boa(self):
        with Workdir() as w:
            sc = {"random_customers": False, "player": {"pos": [9, 2.5]}, "hand": payload(),
                  "customers": [cust(order_status="assigned", reserved={}, patience_ticks_left=PATIENCE // 2 + 1)]}
            rows = run_quan(w, sc, press(0), ticks=1)
            self.assertEqual(one(self, rows, "served")["data"]["tip"], 12, "còn 1800/3600 sau bước 1 = 50%")

    def test_ac_p1_27_an_xong_tra_tien_cong_uy_tin(self):
        with Workdir() as w:
            sc = {"random_customers": False,
                  "customers": [cust(state="eating", order_status="served", reserved={}, eat_ticks_left=1,
                                     base_price=60, tip=12)]}
            rows = run_quan(w, sc, ticks=2)
            e = one(self, rows, "paid")
            self.assertEqual(e["tick"], 1)
            self.assertEqual(e["data"], {"order_id": "C1", "table_id": "T1", "base_price": 60, "tip": 12,
                                         "amount": 72, "reason": "finished_eating"})
            s = snapshots(rows)[-1]
            self.assertEqual((s["money"], s["earned"], s["customers"]), (72, 72, []))
            self.assertAlmostEqual(s["reputation"], 3.2, delta=0.01)
            self.assertEqual(s["score"], 72 + 300)

    def test_ac_p1_27_uy_tin_kep_toi_da_5(self):
        with Workdir() as w:
            sc = {"random_customers": False, "reputation": 5,
                  "customers": [cust(state="eating", order_status="served", reserved={}, eat_ticks_left=1,
                                     base_price=60, tip=12)]}
            rows = run_quan(w, sc, ticks=1)
            self.assertEqual(snapshots(rows)[-1]["reputation"], 5)

    def test_ac_p1_28_dong_ca(self):
        with Workdir() as w:
            cs = [cust("C1", "T1", state="eating", order_status="served", reserved={}, eat_ticks_left=300,
                       base_price=60, tip=0),
                  cust("C2", "T2", "goi_bong_sung")]
            sc = {"random_customers": False, "time_left_ticks": 1, "stock": {"bong_sung": 2}, "customers": cs}
            rows = run_quan(w, sc, ticks=5)
            self.assertEqual(one(self, rows, "paid")["data"],
                             {"order_id": "C1", "table_id": "T1", "base_price": 60, "tip": 0, "amount": 60,
                              "reason": "closing"})
            self.assertEqual(one(self, rows, "customer_left")["data"],
                             {"order_id": "C2", "table_id": "T2", "reason": "closing", "reputation": 3.0})
            end = one(self, rows, "quan_end")
            self.assertEqual(end["data"], {"reason": "time", "money": 60, "earned": 60, "shift_earned": 60,
                                           "reputation": 3.0})
            self.assertEqual([r["name"] for r in events(rows)][-1], "quan_end", "dọn xong mới phát quan_end")
            self.assertEqual((rows[-1]["reason"], rows[-1]["score"]), ("time", 360))


# ------------------------------------------------------------- Trọn vòng: khách tự đến → nấu → bưng → phục vụ → trả tiền
class FullFlow(unittest.TestCase):
    def test_ac_p1_29_tron_vong_quan_co_khach_va_nhan_tien(self):
        """Người chơi đứng ở B1; khách đến tick 120; nấu; bưng; đi tới T1; phục vụ; ăn xong trả tiền."""
        to_t1 = [7 / 9.2195, -6 / 9.2195]  # hướng B1 → T1
        inputs = (press(125) + press(500)
                  + [{"tick": 510, "move": to_t1}, {"tick": 648, "move": [0, 0]}] + press(670))
        with Workdir() as w:
            rows = run_quan(w, {"stock": {"ca_loc": 1}, "player": {"pos": B1}}, inputs, ticks=1400, every=100)
            got = [r["name"] for r in events(rows)]
            for name in ("customer_arrived", "cook_started", "dish_ready", "dish_picked", "served", "paid"):
                self.assertIn(name, got, f"thiếu {name} trong vòng chơi: {got}")
            self.assertEqual(one(self, rows, "paid")["data"]["reason"], "finished_eating")
            self.assertEqual(snapshots(rows)[-1]["money"], 72)


if __name__ == "__main__":
    unittest.main()
