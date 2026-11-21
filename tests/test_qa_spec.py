"""Test QA (TV6) — phần còn lại của ĐỀ chưa có test ở test_qa_p1 / test_qa_p2 / test_qa_quan / smoke.
Viết từ PRD-0 (Test Contract v1.0 mục A–G) và TICKET-02 (v1.1 mục 1–4). Hộp đen qua headless_cmd.

Chạy: PYTHONPATH=tests:. python3 -m unittest tests.test_qa_spec -v
"""

import json
import math
import os
import unittest

from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json
import v12_adapter as v12  # chuyển fixture/output P1–P2 sang kho cá thể v1.2 (xem tests/v12_adapter.py)

with open("game.contract.json", encoding="utf-8") as _f:
    CONTRACT = json.load(_f)
T = CONTRACT["tuning"]

NO_FISH = {"fish": [], "random_fish": False, "monsters": []}


def run(w, mode, scenario=None, inputs=None, ticks=1, seed=1, extra=(), every=None):
    args = ["--mode", mode, "--seed", str(seed), "--ticks", str(ticks), "--out", w.path("o.jsonl"), *extra]
    if scenario is not None:
        args += ["--scenario", write_json(w.path("sc.json"), v12.scenario(scenario))]
    if inputs is not None:
        args += ["--inputs", write_json(w.path("in.json"), frames(*inputs))]
    if every:
        args += ["--snapshot-every", str(every)]
    code, err = run_headless(*args)
    if code != 0:
        raise AssertionError(f"headless thoát mã {code}: {err}")
    return v12.view(read_jsonl(w.path("o.jsonl")))


def code_of(w, *args):
    return run_headless(*args)[0]


def press(btn, t):
    return [{"tick": t, btn: True}, {"tick": t + 1, btn: False}]


# ============================================================ A. Manifest (AC-P1-01)
class Manifest(unittest.TestCase):
    def test_ac_p1_01_du_khoa_preset(self):
        for key in ("contract_version", "team", "team_size", "headless_cmd", "run_cmd", "build_cmd", "tuning"):
            self.assertIn(key, CONTRACT, key)
        self.assertTrue(4 <= CONTRACT["team_size"] <= 6)
        self.assertEqual(T["tick_hz"], 60)
        g_keys = ("duration_s", "bounds", "dock_pos", "dock_radius", "start_pos", "start_heading_deg", "swim_speed",
                  "ramp_max_ticks", "surface_depth", "oxygen_max_s", "oxygen_refill_per_tick", "choke_interval_ticks",
                  "hp_max", "hold_capacity", "interact_radius", "node_yield", "regrow_s", "catch_radius",
                  "catch_cooldown_s", "fish_yield", "nodes", "fish_initial", "monsters")
        q_keys = ("duration_s", "bounds", "start_pos", "walk_speed", "ramp_max_ticks", "interact_radius", "stoves",
                  "tables", "first_customer_tick", "customer_interval_s", "patience_s", "eat_s", "burn_s",
                  "carry_limit", "tip_rate", "tip_min_patience_ratio", "tip_reputation", "left_reputation_delta",
                  "reputation_initial", "reputation_min", "reputation_max")
        for k in g_keys:
            self.assertIn(k, T["gather"], f"gather.{k}")
        for k in q_keys:
            self.assertIn(k, T["quan"], f"quan.{k}")
        for k in ("menu", "score", "day_plan", "shop"):
            self.assertIn(k, T, k)
        self.assertEqual(T["score"], {"reputation_multiplier": 100})

    def test_ac_p1_01_gia_tri_quan_chuan(self):
        q = T["quan"]
        self.assertEqual((q["first_customer_tick"], q["customer_interval_s"], q["patience_s"], q["eat_s"]), (120, 15, 60, 10))
        self.assertEqual((q["carry_limit"], q["tip_rate"], q["tip_min_patience_ratio"], q["tip_reputation"]), (1, 0.2, 0.5, 0.2))
        self.assertEqual((q["left_reputation_delta"], q["reputation_initial"], q["reputation_min"], q["reputation_max"]),
                         (-0.5, 3.0, 0, 5))
        self.assertEqual((q["bounds"], q["start_pos"], q["interact_radius"]), ({"x": [0, 16], "z": [0, 10]}, [8, 5], 1.5))
        g = T["gather"]
        self.assertEqual((g["bounds"], g["dock_pos"], g["dock_radius"], g["start_pos"]),
                         ({"x": [0, 100], "d": [0, 30]}, [2, 0], 3, [2, 0]))
        self.assertEqual((g["surface_depth"], g["oxygen_refill_per_tick"], g["choke_interval_ticks"], g["catch_cooldown_s"]),
                         (0.5, 6, 60, 0.5))


# ============================================================ B. CLI và mã thoát (AC-P1-02)
class Cli(unittest.TestCase):
    def test_ac_p1_02_thieu_co_bat_buoc_ma_2(self):
        with Workdir() as w:
            out = w.path("o.jsonl")
            full = ["--mode", "gather", "--seed", "1", "--ticks", "0", "--out", out]
            for i in range(0, len(full), 2):
                args = full[:i] + full[i + 2:]
                self.assertEqual(code_of(w, *args), 2, f"thiếu {full[i]}")
            self.assertFalse(os.path.exists(out))

    def test_ac_p1_02_seed_va_ticks_sai_kieu_ma_2(self):
        with Workdir() as w:
            out = w.path("o.jsonl")
            for seed in ("1.5", "abc", ""):
                self.assertEqual(code_of(w, "--mode", "gather", "--seed", seed, "--ticks", "0", "--out", out), 2, seed)
            for ticks in ("1.5", "x", "-3"):
                self.assertEqual(code_of(w, "--mode", "gather", "--seed", "1", "--ticks", ticks, "--out", out), 2, ticks)
            self.assertEqual(code_of(w, "--mode", "gather", "--seed", "-7", "--ticks", "0", "--out", out), 0,
                             "seed là số nguyên có dấu")

    def test_ac_p1_02_snapshot_every_phai_duong(self):
        with Workdir() as w:
            for n in ("0", "-1", "2.5"):
                self.assertEqual(code_of(w, "--mode", "gather", "--seed", "1", "--ticks", "5", "--out", w.path("o.jsonl"),
                                         "--snapshot-every", n), 2, n)

    def test_ac_p1_02_snapshot_every_mac_dinh_10(self):
        with Workdir() as w:
            rows = run(w, "gather", {"gather": NO_FISH}, ticks=25)
            self.assertEqual([s["tick"] for s in snapshots(rows)], [0, 10, 20, 25])

    def test_ac_p1_02_loi_ghi_dau_ra_ma_1(self):
        with Workdir() as w:
            out = os.path.join(w.path("khong_ton_tai"), "o.jsonl")
            self.assertEqual(code_of(w, "--mode", "gather", "--seed", "1", "--ticks", "1", "--out", out), 1)

    def test_ac_p1_02_ticks_0_chi_dung_fixture(self):
        with Workdir() as w:
            rows = run(w, "gather", None, ticks=0)
            self.assertEqual([r["type"] for r in rows], ["snapshot", "end"])
            self.assertEqual((rows[-1]["reason"], rows[-1]["ticks"], rows[-1]["sim_tick"]), ("tick_limit", 0, 0))

    def test_ac_p1_02_inventory_out_khong_ghi_khi_loi_dau_vao(self):
        with Workdir() as w:
            inv = w.path("inv.json")
            bad = write_json(w.path("sc.json"), {"gather": {"hold": ["ca_la"]}})
            self.assertEqual(code_of(w, "--mode", "gather", "--seed", "1", "--ticks", "1", "--scenario", bad,
                                     "--inventory-out", inv, "--out", w.path("o.jsonl")), 2)
            self.assertFalse(os.path.exists(inv))
            self.assertFalse(os.path.exists(w.path("o.jsonl")))


# ============================================================ C. Inputs (AC-P1-04)
class Inputs(unittest.TestCase):
    def bad(self, *fr):
        with Workdir() as w:
            p = write_json(w.path("in.json"), frames(*fr))
            return code_of(w, "--mode", "gather", "--seed", "1", "--ticks", "5", "--inputs", p, "--out", w.path("o.jsonl"))

    def test_ac_p1_04_move_ngoai_mien_hoac_sai_kieu_ma_2(self):
        for mv in ([1.5, 0], [0, -2], [1], [1, 0, 0], ["a", 0], None, "up"):
            self.assertEqual(self.bad({"tick": 0, "move": mv}), 2, mv)

    def test_ac_p1_04_nut_sai_kieu_ma_2(self):
        for v in ("yes", 1, None):
            self.assertEqual(self.bad({"tick": 0, "interact": v}), 2, v)
            self.assertEqual(self.bad({"tick": 0, "catch": v}), 2, v)

    def test_ac_p1_04_tick_am_giam_lap_ma_2(self):
        self.assertEqual(self.bad({"tick": -1}), 2)
        self.assertEqual(self.bad({"tick": 3}, {"tick": 2}), 2)
        self.assertEqual(self.bad({"tick": 1.5}), 2)

    def test_ac_p1_04_move_dai_hon_1_duoc_chuan_hoa(self):
        with Workdir() as w:
            rows = run(w, "gather", {"gather": {"player": {"pos": [20, 5]}, **NO_FISH}},
                       [{"tick": 0, "move": [1, 1]}], ticks=10)
            v = snapshots(rows)[-1]["player"]["vel"]
            self.assertAlmostEqual(math.hypot(*v), T["gather"]["swim_speed"], delta=0.01)

    def test_ac_p1_04_frame_chi_cap_nhat_truong_co_mat(self):
        with Workdir() as w:
            rows = run(w, "gather", {"gather": {"player": {"pos": [20, 5]}, **NO_FISH}},
                       [{"tick": 0, "move": [1, 0]}, {"tick": 10, "interact": False}], ticks=20)
            self.assertAlmostEqual(snapshots(rows)[-1]["player"]["vel"][0], 4.0, delta=0.01, msg="move giữ nguyên")

    def test_ac_p1_04_nut_dung_kieu_sai_pha_bo_qua(self):
        with Workdir() as w:
            rows = run(w, "quan", {"quan": {"random_customers": False}}, [{"tick": 0, "catch": True}], ticks=2)
            self.assertEqual(events(rows), [])


# ============================================================ D. Scenario sai → mã 2, không ghi output (AC-P1-05)
class ScenarioInvalid(unittest.TestCase):
    def expect2(self, mode, scenario):
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), v12.scenario(scenario))
            out = w.path("o.jsonl")
            code = code_of(w, "--mode", mode, "--seed", "1", "--ticks", "0", "--scenario", sc, "--out", out)
            self.assertEqual(code, 2, scenario)
            self.assertFalse(os.path.exists(out), "phải kiểm trước khi ghi JSONL")

    def test_ac_p1_05_gather_sai(self):
        fish = {"id": "F1", "kind": "ca_loc", "pos": [30, 12]}
        for g in ({"player": {"hp": 0}}, {"player": {"hp": 4}}, {"player": {"oxygen_ticks": 1801}},
                  {"player": {"oxygen_ticks": -1}}, {"player": {"zero_oxy_ticks": 5}},
                  {"player": {"pos": [20, 0], "oxygen_ticks": 0, "zero_oxy_ticks": 5}},
                  {"player": {"zero_oxy_ticks": 60, "oxygen_ticks": 0, "pos": [20, 5]}},
                  {"player": {"catch_cd_ticks": -1}}, {"player": {"bay": 1}},
                  {"hold": ["ca_la"]}, {"time_left_ticks": 0}, {"time_left_ticks": 10801},
                  {"fish": [fish, dict(fish)], "random_fish": False},
                  {"fish": [{"id": "F1", "kind": "ca_map", "pos": [30, 12]}], "random_fish": False},
                  {"fish": [{"id": "F1", "kind": "ca_loc", "pos": [30, 0]}], "random_fish": False},
                  {"nodes": [{"id": "N1", "kind": "rau_muong", "pos": [12, 0]}]},
                  {"nodes": [{"id": "N1", "kind": "bong_sung", "pos": [12, 0], "regrow_ticks": -1}]}):
            with self.subTest(g=g):
                self.expect2("gather", {"gather": g})

    def test_ac_p1_05_quan_sai(self):
        c = {"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui"}
        pay = {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 60}
        assigned = dict(c, order_status="assigned", reserved={})
        for q in ({"stock": {"ca_la": 1}}, {"stock": {"ca_loc": -1}}, {"stock": {"ca_loc": 1.5}},
                  {"stock": {"ca_loc": 2}, "customers": [c, dict(c, id="C2")]},
                  {"stock": {"ca_loc": 2}, "customers": [c, dict(c)]},
                  {"stock": {"ca_loc": 1, "bong_sung": 2}, "customers": [dict(c, reserved={"bong_sung": 2})]},
                  {"stock": {}, "customers": [c]},
                  {"stock": {"ca_loc": 1}, "customers": [dict(c, dish_id="pho_bo")]},
                  {"stoves": [{"id": "B9", "state": "idle"}]},
                  {"stoves": [{"id": "B1", "state": "cooking", "dish": pay, "cook_ticks_left": 0}],
                   "customers": [assigned]},
                  {"customers": [assigned]},
                  {"customers": [assigned], "hand": pay, "stoves": [{"id": "B1", "state": "ready", "dish": pay}]},
                  {"customers": [assigned], "hand": dict(pay, dish_id="goi_bong_sung")},
                  {"customers": [dict(c, state="eating", order_status="served", reserved={}, eat_ticks_left=0,
                                      base_price=60, tip=0)]},
                  {"stock": {"ca_loc": 1},
                   "customers": [dict(c, order_status="unfulfillable", reserved={"ca_loc": 1})]},
                  {"hand": pay}):
            with self.subTest(q=q):
                self.expect2("quan", {"quan": q})


# ============================================================ E. Output JSONL (AC-P1-06)
class Output(unittest.TestCase):
    COMMON = {"type", "tick", "sim_tick", "mode", "phase", "phase_tick", "state", "time_left_ticks", "money",
              "earned", "reputation", "score"}

    def test_ac_p1_06_truong_snapshot_gather(self):
        with Workdir() as w:
            s = snapshots(run(w, "gather", None, ticks=0))[0]
            self.assertLessEqual(self.COMMON, set(s))
            self.assertLessEqual({"player", "hold", "hold_count", "hold_capacity", "nodes", "fish", "monsters"}, set(s))
            self.assertLessEqual({"pos", "vel", "heading_deg", "oxygen_ticks", "hp", "zero_oxy_ticks", "catch_cd_ticks",
                                  "oxygen_max_ticks", "hp_max", "at_surface", "invuln_ticks"}, set(s["player"]))
            self.assertEqual((s["state"], s["phase"], s["phase_tick"], s["sim_tick"]), ("playing", "gather", 0, 0))
            for n in s["nodes"]:
                self.assertLessEqual({"id", "kind", "pos", "regrow_ticks", "ready"}, set(n))

    def test_ac_p1_06_truong_snapshot_quan(self):
        with Workdir() as w:
            s = snapshots(run(w, "quan", None, ticks=0))[0]
            self.assertLessEqual(self.COMMON, set(s))
            self.assertLessEqual({"player", "stock", "hand", "stoves", "tables", "customers"}, set(s))
            self.assertEqual((s["stock"], s["hand"], s["customers"], s["money"], s["earned"]), ({}, None, [], 0, 0))
            self.assertEqual(s["reputation"], 3.0)
            for tb in s["tables"]:
                self.assertIn("customer_id", tb)

    def test_ac_p1_06_dong_end_va_event(self):
        with Workdir() as w:
            rows = run(w, "gather", {"gather": {"player": {"pos": [2, 0]}, **NO_FISH}}, press("interact", 0), ticks=5)
            end = rows[-1]
            self.assertEqual(set(end), {"type", "ticks", "sim_tick", "mode", "state", "reason", "money", "earned",
                                        "reputation", "score"})
            self.assertEqual((end["state"], end["reason"], end["ticks"]), ("finished", "docked", 1))
            for e in events(rows):
                self.assertEqual(set(e), {"type", "tick", "phase", "name", "data"})

    def test_ac_p1_06_event_truoc_snapshot_cung_tick_end_cuoi(self):
        with Workdir() as w:
            rows = run(w, "gather", {"gather": {"player": {"pos": [2, 0]}, **NO_FISH}}, press("interact", 0), ticks=5)
            at1 = [r["type"] for r in rows if r.get("tick") == 1]
            self.assertEqual(at1, ["event", "snapshot"])
            self.assertEqual(rows[-1]["type"], "end")
            ticks = [s["tick"] for s in snapshots(rows)]
            self.assertEqual(len(ticks), len(set(ticks)), "mỗi tick tối đa một snapshot")

    def test_ac_p1_06_toa_do_3_chu_so(self):
        with Workdir() as w:
            rows = run(w, "gather", {"gather": {"player": {"pos": [20, 5]}, "monsters": []}},
                       [{"tick": 0, "move": [0.3, 0.7]}], ticks=37, every=1)
            for s in snapshots(rows):
                for c in s["player"]["pos"] + [c for f in s["fish"] for c in f["pos"]]:
                    self.assertEqual(round(c, 3), c, c)


# ============================================================ F. Quán: chọn interact, rời quán bỏ món, day shift (AC-P1-23, 22, 28)
def cust(cid="C1", table="T1", dish="ca_loc_nuong_trui", **kw):
    return {"id": cid, "table_id": table, "dish_id": dish, **kw}


PAY = {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 60}


class InteractChoice(unittest.TestCase):
    def test_ac_p1_23_hoa_khoang_cach_bep_truoc_ban(self):
        with Workdir() as w:
            sc = {"quan": {"random_customers": False, "player": {"pos": [3, 8]}, "stock": {"ca_loc": 1},
                           "tables": [{"id": "T1", "pos": [4, 8]}], "hand": PAY,
                           "customers": [cust(order_status="assigned", reserved={}), cust("C2", "T2")]}}
            rows = run(w, "quan", sc, press("interact", 0), ticks=1)
            self.assertEqual([e["name"] for e in events(rows)], ["cook_started"])
            self.assertEqual(events(rows, "cook_started")[0]["data"]["order_id"], "C2")

    def test_ac_p1_23_hoa_hai_bep_chon_id_nho_dung_mep(self):
        with Workdir() as w:
            sc = {"quan": {"random_customers": False, "player": {"pos": [3.5, 8]}, "stock": {"ca_loc": 1},
                           "customers": [cust()]}}
            rows = run(w, "quan", sc, press("interact", 0), ticks=1)
            self.assertEqual(events(rows, "cook_started")[0]["data"]["stove_id"], "B1")

    def test_ac_p1_23_doi_tuong_gan_nhat_khong_tuong_tac_duoc_thi_bo_luot(self):
        with Workdir() as w:
            sc = {"quan": {"random_customers": False, "player": {"pos": [2, 8]}, "hand": PAY,
                           "tables": [{"id": "T1", "pos": [3, 8]}],
                           "customers": [cust(order_status="assigned", reserved={})]}}
            rows = run(w, "quan", sc, press("interact", 0), ticks=1)
            self.assertEqual(events(rows), [], "bếp idle không có đơn reserved → bỏ lượt, không phục vụ bàn")

    def test_ac_p1_26_phuc_vu_sai_don_khong_nhan(self):
        with Workdir() as w:
            sc = {"quan": {"random_customers": False, "player": {"pos": [9, 2.5]},
                           "hand": dict(PAY, order_id="C2"),
                           "customers": [cust(order_status="reserved"), cust("C2", "T2", order_status="assigned",
                                                                              reserved={})],
                           "stock": {"ca_loc": 1}}}
            rows = run(w, "quan", sc, press("interact", 0), ticks=1)
            self.assertEqual(events(rows, "served"), [])


class LeaveDropsDish(unittest.TestCase):
    def test_ac_p1_22_khach_roi_bo_mon_tren_tay(self):
        with Workdir() as w:
            sc = {"quan": {"random_customers": False, "hand": PAY,
                           "customers": [cust(order_status="assigned", reserved={}, patience_ticks_left=1)]}}
            rows = run(w, "quan", sc, ticks=1)
            self.assertEqual(events(rows, "customer_left")[0]["data"]["reason"], "patience")
            self.assertIsNone(snapshots(rows)[-1]["hand"])

    def test_ac_p1_22_khach_roi_bo_mon_dang_nau(self):
        with Workdir() as w:
            sc = {"quan": {"random_customers": False,
                           "stoves": [{"id": "B1", "state": "cooking", "dish": PAY, "cook_ticks_left": 100}],
                           "customers": [cust(order_status="assigned", reserved={}, patience_ticks_left=1)]}}
            rows = run(w, "quan", sc, ticks=1)
            b1 = snapshots(rows)[-1]["stoves"][0]
            self.assertEqual((b1["state"], b1["dish"]), ("idle", None))


class DayShift(unittest.TestCase):
    def test_ac_p1_28_shift_earned_chi_tinh_trong_ca(self):
        eating = cust(state="eating", order_status="served", reserved={}, eat_ticks_left=1, base_price=60, tip=0)
        sc = {"day": {"money": 100, "earned": 100}, "gather": {"time_left_ticks": 1, **NO_FISH},
              "quan": {"time_left_ticks": 2, "customers": [eating]}}
        with Workdir() as w:
            rows = run(w, "day", sc, ticks=3)
            self.assertEqual(events(rows, "paid")[0]["data"]["reason"], "finished_eating")
            self.assertEqual(events(rows, "quan_end")[0]["data"],
                             {"reason": "time", "money": 160, "earned": 160, "shift_earned": 60, "reputation": 3.0})


# ============================================================ G. Cá bơi/sinh chi tiết (TICKET-02 §1.1)
class FishDetail(unittest.TestCase):
    def test_ac_p2_20_phan_xa_mep_dao_huong(self):
        with Workdir() as w:
            sc = {"gather": {"monsters": [], "fish": [{"id": "F1", "kind": "ca_loc", "pos": [95.5, 14], "heading_deg": 0}]}}
            rows = run(w, "gather", sc, ticks=60)
            f = [f for f in snapshots(rows)[-1]["fish"] if f["id"] == "F1"][0]
            self.assertAlmostEqual(f["pos"][0], 95.0, delta=0.1, msg="đi 1.5 m: 0.5 tới mép 96, dội lại 1.0")
            self.assertAlmostEqual(f["heading_deg"] % 360, 180, delta=0.5)

    def test_ac_p2_20_doi_huong_o_buoc_120(self):
        changed = 0
        for seed in (1, 2, 3):
            with Workdir() as w:
                sc = {"gather": {"monsters": [], "fish": [{"id": "F1", "kind": "ca_loc", "pos": [50, 14], "heading_deg": 0}]}}
                rows = run(w, "gather", sc, ticks=121, seed=seed, every=1)
                h = {s["tick"]: [f for f in s["fish"] if f["id"] == "F1"][0]["heading_deg"] for s in snapshots(rows)}
                self.assertEqual(h[119], 0, "chưa tới bước 120 thì giữ hướng")
                changed += h[121] != 0
        self.assertGreaterEqual(changed, 2, "đổi hướng theo seed ở bước bơi thứ 120")

    def test_ac_p2_20_random_fish_false_ca_dung_yen_khong_sinh(self):
        with Workdir() as w:
            sc = {"gather": {"monsters": [], "random_fish": False,
                             "fish": [{"id": "F1", "kind": "ca_loc", "pos": [50, 14]}]}}
            rows = run(w, "gather", sc, ticks=800)
            self.assertEqual(events(rows, "fish_spawned"), [])
            self.assertEqual(snapshots(rows)[-1]["fish"][0]["pos"], [50, 14])

    def test_ac_p2_21_ca_moi_id_noi_tiep_va_cach_dan_khac_hon_1m(self):
        with Workdir() as w:
            rows = run(w, "gather", {"gather": {"monsters": []}}, ticks=1080, seed=5, every=360)
            sp = events(rows, "fish_spawned")
            self.assertTrue(sp)
            self.assertEqual(sp[0]["data"]["id"], "F9", "8 đàn đầu ca F1–F8, đàn mới nối hậu tố")
            for e in sp:
                snap = [s for s in snapshots(rows) if s["tick"] == e["tick"]][0]
                me = [f for f in snap["fish"] if f["id"] == e["data"]["id"]][0]
                self.assertEqual(me["pos"], e["data"]["pos"], "đàn mới chưa bơi trong bước sinh")
                for f in snap["fish"]:
                    if f["id"] != me["id"]:
                        self.assertGreater(math.dist(f["pos"], me["pos"]), 1.0 - 0.1)


# ============================================================ H. Cá Sấu chi tiết (TICKET-02 §1.2)
def croc(**kw):
    return {"id": "M1", "kind": "ca_sau", "pos": [60, 24], "waypoints": [[60, 24], [64, 24]], **kw}


class CrocDetail(unittest.TestCase):
    def test_ac_p2_08_den_waypoint_thi_quay_dau(self):
        with Workdir() as w:
            rows = run(w, "gather", {"gather": {"player": {"pos": [10, 0]}, "monsters": [croc()], "fish": [],
                                                "random_fish": False}}, ticks=300)
            m = snapshots(rows)[-1]["monsters"][0]
            self.assertAlmostEqual(m["pos"][0], 63.0, delta=0.1, msg="240 tick tới 64, 60 tick quay lại 1 m")
            self.assertEqual(m["target_idx"], 0)

    def test_ac_p2_08_xa_hon_16m_bo_duoi_trong_16m_van_duoi(self):
        for px, want in ((77, "patrol"), (75, "chase")):
            with Workdir() as w:
                sc = {"gather": {"player": {"pos": [px, 24]}, "monsters": [croc(state="chase")], "fish": [],
                                 "random_fish": False}}
                rows = run(w, "gather", sc, ticks=1)
                self.assertEqual(snapshots(rows)[-1]["monsters"][0]["state"], want, px)

    def test_ac_p2_08_ca_sau_khong_len_tren_d10(self):
        with Workdir() as w:
            sc = {"gather": {"player": {"pos": [60, 10]}, "monsters": [croc(pos=[60, 12], state="chase")],
                             "fish": [], "random_fish": False}}
            rows = run(w, "gather", sc, inputs=[{"tick": 0, "move": [0, -1]}], ticks=30, every=1)
            for s in snapshots(rows):
                for m in s["monsters"]:
                    self.assertGreaterEqual(m["pos"][1], 10 - 1e-9)


# ============================================================ I. Vòng ngày chi tiết (TICKET-02 §2, §4.4, §4.5)
class DayDetail(unittest.TestCase):
    QUICK = {"gather": {"time_left_ticks": 1, **NO_FISH}, "quan": {"time_left_ticks": 1}}

    def test_ac_p2_15_event_day_co_truong_day(self):
        with Workdir() as w:
            rows = run(w, "day", self.QUICK, press("shop_done", 2), ticks=4, extra=("--days", "2"))
            for e in events(rows):
                self.assertIn("day", e, e["name"])
            self.assertEqual(events(rows, "day_plan")[0]["data"]["ingredients"], {"ca_loc": 3, "bong_sung": 6})

    def test_ac_p2_15_snapshot_shop_co_kho_du_va_dong_ho_600(self):
        with Workdir() as w:
            sc = {"gather": {"time_left_ticks": 1, "hold": ["ca_loc", "bong_sung"], **NO_FISH},
                  "quan": {"time_left_ticks": 1, "random_customers": False}}
            rows = run(w, "day", sc, ticks=2, every=1)
            shop = [s for s in snapshots(rows) if s["phase"] == "shop"][0]
            self.assertEqual((shop["phase_tick"], shop["time_left_ticks"]), (0, 600))
            self.assertEqual(shop["stock"], {"bong_sung": 1, "ca_loc": 1})

    def test_ac_p2_18_kho_du_bo_sau_shop(self):
        sc = {"gather": {"hold": ["ca_loc"], **NO_FISH}, "quan": {"time_left_ticks": 1, "random_customers": False}}
        inputs = [{"tick": 0, "interact": True}, {"tick": 1, "interact": False}, {"tick": 2, "shop_done": True},
                  {"tick": 3, "shop_done": False, "interact": True}, {"tick": 4, "interact": False}]
        with Workdir() as w:
            rows = run(w, "day", sc, inputs, ticks=4, every=1, extra=("--days", "2"))
            q2 = [s for s in snapshots(rows) if s["day"] == 2 and s["phase"] == "quan"]
            self.assertTrue(q2, "chưa tới quán ngày 2")
            self.assertEqual(q2[0]["stock"], {"ca_loc": 1}, "kho dư ngày 1 bị bỏ, chỉ còn hàng ngày 2")

    def test_ac_p2_18_mau_oxy_hoi_day_dau_ngay(self):
        sc = {"gather": {"time_left_ticks": 1, "player": {"pos": [60, 24]}, "fish": [], "random_fish": False,
                         "monsters": [croc()]},
              "quan": {"time_left_ticks": 1}}
        with Workdir() as w:
            rows = run(w, "day", sc, press("shop_done", 2), ticks=3, every=1, extra=("--days", "2"))
            self.assertEqual(events(rows, "monster_hit")[0]["data"]["hp"], 2)
            d2 = [s for s in snapshots(rows) if s["day"] == 2 and s["phase"] == "gather" and s["phase_tick"] == 0][0]
            self.assertEqual((d2["player"]["hp"], d2["player"]["oxygen_ticks"]), (3, 1800))

    def test_ac_p2_17_buy_sai_pha_bo_qua(self):
        with Workdir() as w:
            sc = {"day": {"money": 500, "earned": 500}, "gather": NO_FISH}
            rows = run(w, "day", sc, [{"tick": 0, "buy": "hp"}], ticks=2)
            self.assertEqual(events(rows, "bought") + events(rows, "buy_failed"), [])

    def test_ac_p2_17_buy_xu_ly_truoc_shop_done_cung_buoc(self):
        sc = {"day": {"money": 250, "earned": 250}, **self.QUICK}
        with Workdir() as w:
            rows = run(w, "day", sc, [{"tick": 2, "buy": "hp", "shop_done": True}], ticks=3)
            self.assertEqual([e["name"] for e in events(rows) if e["tick"] == 3], ["bought", "shop_end"])

    def test_ac_p2_17_dung_gia_van_mua_duoc(self):
        sc = {"day": {"money": 200, "earned": 200}, **self.QUICK}
        with Workdir() as w:
            rows = run(w, "day", sc, [{"tick": 2, "buy": "oxygen"}], ticks=3)
            self.assertEqual(events(rows, "bought")[0]["data"]["money"], 0)

    def test_ac_p2_19_pause_bo_qua_buy(self):
        sc = {"day": {"money": 500, "earned": 500}, **self.QUICK}
        with Workdir() as w:
            rows = run(w, "day", sc, [{"tick": 2, "pause": True}, {"tick": 3, "buy": "hp"}], ticks=5)
            self.assertEqual(events(rows, "bought"), [])


if __name__ == "__main__":
    unittest.main()
