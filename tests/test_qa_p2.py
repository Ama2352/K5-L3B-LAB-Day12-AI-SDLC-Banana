"""Test QA Phase 2 (TV6), kiểu HỘP ĐEN theo TICKET-02 / Test Contract v1.1.

Mỗi test gắn mã AC trong docs/verification/phase-2.md (tên test chứa `ac_p2_xx`).
Bổ sung cho tests/test_phase2_tv1.py (không lặp lại ca TV1 đã có).
Quy ước tick: bước k đọc frame tick = k, ghi event ở tick k + 1.

Chạy: PYTHONPATH=tests:. python3 -m unittest tests.test_qa_p2 -v
"""

import json
import math
import time
import unittest
from collections import Counter

from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json
import v12_adapter as v12  # chuyển fixture/output P1–P2 sang kho cá thể v1.2 (xem tests/v12_adapter.py)

with open("game.contract.json", encoding="utf-8") as _f:
    CONTRACT = json.load(_f)
T = CONTRACT["tuning"]
G, Q = T["gather"], T["quan"]
EXT = set(CONTRACT.get("extensions", []))

# Số chuẩn TICKET-02 (viết tay từ đề, KHÔNG đọc từ contract — để bắt lệch số)
STD_MENU = {
    "ca_loc_nuong_trui": ({"ca_loc": 1}, 6, 60),
    "goi_bong_sung": ({"bong_sung": 2}, 4, 40),
    "lau_ca_linh_dien_dien": ({"ca_linh": 3, "bong_dien_dien": 1}, 10, 120),
    "canh_chua_ca_loc": ({"ca_loc": 1, "bong_dien_dien": 1}, 8, 90),
    "ca_keo_nuong": ({"ca_keo": 2}, 6, 70),
    "lau_mam": ({"ca_linh": 2, "ca_keo": 1, "keo_neo": 1, "bong_dien_dien": 1}, 12, 200),
}
STD_PLAN = {
    1: {"ca_loc_nuong_trui": 3, "goi_bong_sung": 3},
    2: {"ca_loc_nuong_trui": 2, "lau_ca_linh_dien_dien": 2},
    3: {"goi_bong_sung": 2, "canh_chua_ca_loc": 2, "ca_keo_nuong": 2},
    4: {"lau_mam": 1, "ca_loc_nuong_trui": 2, "goi_bong_sung": 1},
    5: {"lau_mam": 1, "lau_ca_linh_dien_dien": 1, "ca_loc_nuong_trui": 1},
}
STD_NODES = {"N1": ("bong_dien_dien", [12, 0]), "N2": ("bong_dien_dien", [28, 0]),
             "N3": ("bong_sung", [44, 0]), "N4": ("bong_sung", [60, 0]),
             "N5": ("keo_neo", [76, 0]), "N6": ("keo_neo", [90, 0])}
FISH_DEPTHS = {"ca_linh": (3, 12), "ca_loc": (8, 20), "ca_keo": (22, 28)}
SPAWN_X = {15, 30, 45, 60, 75, 90}
SPAWN_D = {"ca_linh": {5, 10}, "ca_loc": {10, 16}, "ca_keo": {24, 27}}
DAY_TICKS = 22200


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


def names(rows, tick=None):
    return [r["name"] for r in rows if r["type"] == "event" and (tick is None or r["tick"] == tick)]


def croc(mid="M1", pos=(60, 24), wp=((60, 24), (64, 24)), **kw):
    return {"id": mid, "kind": "ca_sau", "pos": list(pos), "waypoints": [list(p) for p in wp], **kw}


NO_FISH = {"fish": [], "random_fish": False}


# ======================================================== 1. Số chuẩn & manifest v1.1
class StandardNumbers(unittest.TestCase):
    def test_ac_p2_01_contract_version_va_ca_chung(self):
        # TICKET-03 thay contract v1.1 bằng v1.2 (kho cá thể); số chuẩn P2 giữ nguyên
        self.assertIn(CONTRACT["contract_version"], ("1.1", "1.2", "1.3"))  # TICKET-04: v1.3 giữ số chuẩn
        self.assertEqual((G["duration_s"], Q["duration_s"]), (180, 180))
        self.assertEqual((G["swim_speed"], Q["walk_speed"], G["oxygen_max_s"], G["hp_max"]), (4.0, 4.0, 30, 3))
        self.assertEqual((G["hold_capacity"], G["interact_radius"], G["catch_radius"], G["regrow_s"]), (12, 2.0, 2.0, 20))

    def test_ac_p2_02_nut_hai_N1_den_N6(self):
        got = {n["id"]: (n["kind"], n["pos"]) for n in G["nodes"]}
        self.assertEqual(got, STD_NODES)

    def test_ac_p2_03_fish_yield_va_8_dan_dau_ca(self):
        self.assertEqual(G["fish_yield"], {"ca_linh": 3, "ca_loc": 1, "ca_keo": 2})
        self.assertEqual(G["fish_initial"], 8, "TICKET-02 §4.1: fish_initial là số 8")

    def test_ac_p2_03_khoa_ca_boi_va_sinh(self):
        want = {"fish_speed": 1.5, "fish_max": 12, "fish_x": [4, 96],
                "fish_spawn_x": [15, 30, 45, 60, 75, 90]}
        for key in ("fish_speed", "fish_turn_ticks", "fish_max", "fish_spawn_ticks", "fish_spawn_clearance",
                    "fish_x", "fish_depths", "fish_spawn_x", "fish_spawn_depths", "fish_weights"):
            self.assertIn(key, G, f"thiếu khóa {key}")
        for key, val in want.items():
            self.assertEqual(G[key], val, key)
        for key in ("fish_depths", "fish_spawn_depths", "fish_weights"):
            self.assertEqual(set(G[key]), {"ca_linh", "ca_loc", "ca_keo"}, key)

    def test_ac_p2_04_ca_sau_dung_so(self):
        m = G["monsters"]
        self.assertEqual(m["species"]["ca_sau"], {"patrol_speed": 1, "chase_speed": 3, "detect_radius": 10,
                                                  "exit_radius": 16, "depths": [10, 30], "hit_radius": 1.5,
                                                  "recoil_ticks": 60, "recoil_dist": 2})
        self.assertEqual((m["invuln_ticks"], m["loss_ratio"]), (90, 0.5))
        spawns = {s["id"]: (s["pos"], s["waypoints"], s["from_day"]) for s in m["spawns"] if s["kind"] == "ca_sau"}
        self.assertEqual(spawns, {"M1": ([60, 24], [[60, 24], [64, 24]], 1),
                                  "M2": ([85, 18], [[85, 18], [89, 18]], 3)})

    def test_ac_p2_05_quan_2_bep_4_ban_6_mon(self):
        self.assertEqual({s["id"]: s["pos"] for s in Q["stoves"]}, {"B1": [2, 8], "B2": [5, 8]})
        self.assertEqual({t["id"]: t["pos"] for t in Q["tables"]},
                         {"T1": [9, 2], "T2": [13, 2], "T3": [9, 6], "T4": [13, 6]})
        got = {k: (v["recipe"], v["cook_s"], v["price"]) for k, v in T["menu"].items()}
        self.assertEqual(got, STD_MENU)
        if "burn" not in EXT:
            self.assertIsNone(Q["burn_s"], "lõi dùng burn_s: null khi chưa khai mở rộng burn")

    def test_ac_p2_06_day_plan_va_ingredients_bang_tong_cong_thuc(self):
        plans = {p["day"]: p for p in T["day_plan"]}
        self.assertEqual(sorted(plans), [1, 2, 3, 4, 5])
        for day, dishes in STD_PLAN.items():
            with self.subTest(day=day):
                self.assertEqual(plans[day]["dishes"], dishes)
                need = Counter()
                for dish, n in dishes.items():
                    for kind, units in STD_MENU[dish][0].items():
                        need[kind] += units * n
                self.assertEqual(plans[day]["ingredients"], dict(need))

    def test_ac_p2_07_shop_nang_cap(self):
        s = T["shop"]
        self.assertEqual(s["max_ticks"], 600)
        self.assertEqual([(u["level"], u["price"], u["oxygen_max_s"]) for u in s["upgrades"]["oxygen"]],
                         [(1, 200, 45), (2, 400, 60)])
        self.assertEqual([(u["level"], u["price"], u["hp_max"]) for u in s["upgrades"]["hp"]],
                         [(1, 250, 4), (2, 500, 5)])


# ======================================================== 2. Gather chạy với số chuẩn
class GatherStandard(unittest.TestCase):
    def test_ac_p2_03_snapshot_dau_ca_8_dan_6_nut_M1(self):
        with Workdir() as w:
            s = snapshots(run(w, "gather", ticks=0))[0]
            self.assertEqual(len(s["fish"]), 8)
            self.assertEqual(len({tuple(f["pos"]) for f in s["fish"]}), 8, "8 điểm khác nhau")
            for f in s["fish"]:
                self.assertIn(f["pos"][0], SPAWN_X, f)
                self.assertIn(f["pos"][1], SPAWN_D[f["kind"]], f)
            self.assertEqual([n["id"] for n in s["nodes"]], ["N1", "N2", "N3", "N4", "N5", "N6"])
            self.assertEqual([m["id"] for m in s["monsters"]], ["M1"], "gather độc lập dùng bố trí Ngày 1")
            self.assertIn("invuln_ticks", s["player"])

    def test_ac_p2_02_hai_keo_neo(self):
        with Workdir() as w:
            sc = {"gather": {"player": {"pos": [76, 0]}, "monsters": [], **NO_FISH}}
            rows = run(w, "gather", sc, [{"tick": 0, "interact": True}], ticks=1)
            self.assertEqual([e["data"] for e in events(rows, "gather")],
                             [{"node_id": "N5", "kind": "keo_neo", "amount": 1}], "hái N5 tại [76,0]")

    def test_ac_p2_03_bat_ca_keo_yield_2(self):
        with Workdir() as w:
            sc = {"gather": {"player": {"pos": [30, 24]}, "monsters": [],
                             "fish": [{"id": "F1", "kind": "ca_keo", "pos": [31, 24]}], "random_fish": False}}
            rows = run(w, "gather", sc, [{"tick": 0, "catch": True}], ticks=1)
            self.assertEqual(events(rows, "fish_caught")[0]["data"], {"fish_id": "F1", "kind": "ca_keo", "yield": 2})
            self.assertEqual(snapshots(rows)[-1]["hold"], ["ca_keo", "ca_keo"])


# ======================================================== 3. Cá Sấu, Máu, ngất (bổ sung TV1)
class Crocodile(unittest.TestCase):
    def test_ac_p2_08_tuan_tra_1ms_den_waypoint(self):
        with Workdir() as w:
            sc = {"gather": {"player": {"pos": [10, 0]}, "monsters": [croc()], **NO_FISH}}
            rows = run(w, "gather", sc, ticks=60)
            m = snapshots(rows)[-1]["monsters"][0]
            self.assertEqual(m["state"], "patrol")
            self.assertAlmostEqual(m["pos"][0], 61.0, delta=0.1)
            self.assertAlmostEqual(m["pos"][1], 24.0, delta=0.1)

    def test_ac_p2_08_phat_hien_dung_10m_thi_duoi_3ms(self):
        with Workdir() as w:
            sc = {"gather": {"player": {"pos": [50, 24], "oxygen_ticks": 1800}, "monsters": [croc()], **NO_FISH}}
            rows = run(w, "gather", sc, ticks=20)
            m = snapshots(rows)[-1]["monsters"][0]
            self.assertEqual(m["state"], "chase")
            self.assertAlmostEqual(m["pos"][0], 60 - 3 * 20 / 60, delta=0.1)

    def test_ac_p2_08_cach_hon_10m_khong_duoi(self):
        with Workdir() as w:
            sc = {"gather": {"player": {"pos": [49.9, 24]}, "monsters": [croc(wp=((60, 24), (60.5, 24)))], **NO_FISH}}
            rows = run(w, "gather", sc, ticks=1)
            self.assertEqual(snapshots(rows)[-1]["monsters"][0]["state"], "patrol")

    def test_ac_p2_08_nguoi_choi_len_d_duoi_10_thi_bo_duoi(self):
        with Workdir() as w:
            sc = {"gather": {"player": {"pos": [55, 9.5]},
                             "monsters": [croc(state="chase")], **NO_FISH}}
            rows = run(w, "gather", sc, ticks=1)
            self.assertEqual(snapshots(rows)[-1]["monsters"][0]["state"], "patrol")

    def test_ac_p2_09_hit_mat_mau_bo_nua_gio_lifo_bat_tu_90(self):
        hold = ["ca_loc", "bong_sung", "ca_linh", "ca_linh", "keo_neo"]
        with Workdir() as w:
            sc = {"gather": {"player": {"pos": [60, 24]}, "hold": hold, "monsters": [croc()], **NO_FISH}}
            rows = run(w, "gather", sc, ticks=1)
            hit = events(rows, "monster_hit")
            self.assertEqual(len(hit), 1)
            d = hit[0]["data"]
            self.assertEqual((d["monster_id"], d["hp"]), ("M1", 2))
            self.assertEqual(d["lost"], ["keo_neo", "ca_linh"], "floor(5/2)=2, nhặt sau mất trước")
            s = snapshots(rows)[-1]
            self.assertEqual(s["hold"], hold[:3])
            self.assertEqual(s["player"]["invuln_ticks"], G["monsters"]["invuln_ticks"])
            self.assertEqual(s["monsters"][0]["state"], "recoil")

    def test_ac_p2_09_gio_1_mon_khong_mat_gi(self):
        with Workdir() as w:
            sc = {"gather": {"player": {"pos": [60, 24]}, "hold": ["ca_loc"], "monsters": [croc()], **NO_FISH}}
            rows = run(w, "gather", sc, ticks=1)
            self.assertEqual(events(rows, "monster_hit")[0]["data"]["lost"], [])
            self.assertEqual(snapshots(rows)[-1]["hold"], ["ca_loc"])

    def test_ac_p2_09_dang_bat_tu_khong_hit_khong_recoil(self):
        with Workdir() as w:
            sc = {"gather": {"player": {"pos": [60, 24], "invuln_ticks": 5}, "monsters": [croc()], **NO_FISH}}
            rows = run(w, "gather", sc, ticks=3)
            self.assertEqual(events(rows, "monster_hit"), [])
            self.assertNotEqual(snapshots(rows)[-1]["monsters"][0]["state"], "recoil")

    def test_ac_p2_10_ngat_xuyen_bat_tu_khong_roi_hang(self):
        with Workdir() as w:
            hold = ["ca_loc", "bong_sung", "ca_linh", "ca_linh"]
            sc = {"gather": {"player": {"pos": [20, 5], "invuln_ticks": 50, "oxygen_ticks": 0, "zero_oxy_ticks": 59},
                             "hold": hold, "monsters": [], **NO_FISH}}
            rows = run(w, "gather", sc, ticks=1)
            self.assertEqual(names(rows), ["choke"])
            self.assertEqual(events(rows, "choke")[0]["data"], {"hp": 2})
            self.assertEqual(snapshots(rows)[-1]["hold"], hold)

    def test_ac_p2_11_ngat_do_ca_sau_gather_doc_lap(self):
        with Workdir() as w:
            hold = ["ca_loc", "bong_sung", "ca_linh"]
            inv = w.path("inv.json")
            sc = {"gather": {"player": {"pos": [60, 24], "hp": 1}, "hold": hold, "monsters": [croc()], **NO_FISH}}
            rows = run(w, "gather", sc, ticks=5, extra=("--inventory-out", inv))
            self.assertEqual(names(rows), ["monster_hit", "faint", "gather_end"])
            self.assertEqual(events(rows, "monster_hit")[0]["data"]["lost"], ["ca_linh"])
            self.assertEqual(events(rows, "faint")[0]["data"], {"cause": "monster", "lost": ["bong_sung", "ca_loc"], "hp": 0})
            self.assertEqual(rows[-1]["reason"], "fainted")
            with open(inv, encoding="utf-8") as f:
                self.assertEqual(v12.inventory_view(json.load(f)), {"items": {}})

    def test_ac_p2_11_cap_ben_uu_tien_khi_con_mau(self):
        with Workdir() as w:
            sc = {"gather": {"player": {"pos": [2, 0]}, "hold": ["ca_loc"], "monsters": [], **NO_FISH}}
            rows = run(w, "gather", sc, [{"tick": 0, "interact": True, "catch": True}], ticks=3)
            self.assertEqual(events(rows, "gather_end")[0]["data"]["reason"], "docked")


# ======================================================== 4. Quán 2 bếp / 4 bàn
class Restaurant(unittest.TestCase):
    STOCK = {"ca_loc": 9, "bong_sung": 9, "ca_linh": 9, "bong_dien_dien": 9, "ca_keo": 9, "keo_neo": 9}

    def test_ac_p2_12_lich_khach_120_cong_900k_ban_id_nho_nhat(self):
        with Workdir() as w:
            rows = run(w, "quan", {"quan": {"stock": self.STOCK}}, ticks=2900)
            arr = events(rows, "customer_arrived")
            self.assertEqual([(e["tick"], e["data"]["table_id"]) for e in arr],
                             [(120, "T1"), (1020, "T2"), (1920, "T3"), (2820, "T4")])

    def test_ac_p2_12_het_ban_bo_luot(self):
        with Workdir() as w:
            customers = [{"id": f"C{i}", "table_id": f"T{i}", "dish_id": "ca_loc_nuong_trui"} for i in range(1, 5)]
            sc = {"quan": {"stock": {"ca_loc": 4}, "customers": customers}}
            rows = run(w, "quan", sc, ticks=130)
            self.assertEqual(events(rows, "customer_arrived") + events(rows, "no_dish"), [])

    def test_ac_p2_13_quan_doc_lap_dung_mon_moi(self):
        with Workdir() as w:
            rows = run(w, "quan", {"quan": {"stock": {"ca_keo": 2}}}, ticks=120)
            arr = events(rows, "customer_arrived")
            self.assertEqual([e["data"]["dish_id"] for e in arr], ["ca_keo_nuong"])
            self.assertEqual(snapshots(rows)[-1]["customers"][0]["reserved"], {"ca_keo": 2})

    def test_ac_p2_13_day_loc_menu_theo_ke_hoach(self):
        with Workdir() as w:
            sc = {"gather": {"hold": ["ca_keo", "ca_keo"], "time_left_ticks": 1, "monsters": [], **NO_FISH}}
            rows = run(w, "day", sc, ticks=1 + 120)
            self.assertEqual(events(rows, "customer_arrived"), [], "D1 không có ca_keo_nuong")
            self.assertEqual(len(events(rows, "no_dish")), 1)

    def test_ac_p2_14_hai_bep_nau_song_song(self):
        customers = [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui"},
                     {"id": "C2", "table_id": "T2", "dish_id": "goi_bong_sung"}]
        inputs = [{"tick": 0, "interact": True}, {"tick": 1, "interact": False},
                  {"tick": 2, "move": [1, 0]}, {"tick": 47, "move": [0, 0]},
                  {"tick": 60, "interact": True}, {"tick": 61, "interact": False}]
        with Workdir() as w:
            sc = {"quan": {"stock": {"ca_loc": 1, "bong_sung": 2}, "customers": customers,
                           "player": {"pos": [2, 8]}, "random_customers": False}}
            rows = run(w, "quan", sc, inputs, ticks=62)
            cs = events(rows, "cook_started")
            self.assertEqual([(e["data"]["stove_id"], e["data"]["order_id"]) for e in cs], [("B1", "C1"), ("B2", "C2")])
            stoves = {s["id"]: s["state"] for s in snapshots(rows)[-1]["stoves"]}
            self.assertEqual(stoves, {"B1": "cooking", "B2": "cooking"})

    def test_ac_p2_14_chon_tuong_tac_gan_nhat(self):
        customers = [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui"}]
        with Workdir() as w:
            sc = {"quan": {"stock": {"ca_loc": 1}, "customers": customers,
                           "player": {"pos": [4.5, 8]}, "random_customers": False}}
            rows = run(w, "quan", sc, [{"tick": 0, "interact": True}], ticks=1)
            self.assertEqual(events(rows, "cook_started")[0]["data"]["stove_id"], "B2")


# ======================================================== 5. Vòng ngày
class DayLoop(unittest.TestCase):
    def test_ac_p2_15_mot_ngay_khong_input_dung_22200_tick_va_duoi_20s(self):
        with Workdir() as w:
            t0 = time.monotonic()
            rows = run(w, "day", None, ticks=DAY_TICKS + 10, seed=42, every=600)
            elapsed = time.monotonic() - t0
            end = rows[-1]
            self.assertEqual((end["reason"], end["days_completed"], end["ticks"]), ("days_complete", 1, DAY_TICKS))
            self.assertEqual([e["tick"] for e in events(rows, "phase_start")], [0, 10800, 21600])
            self.assertEqual(events(rows, "shop_end")[0]["data"], {"reason": "time"})
            self.assertLessEqual(elapsed, 20, f"một Ngày chạy {elapsed:.1f}s")

    def test_ac_p2_15_ke_hoach_tung_ngay_D1_den_D5(self):
        sc = {"gather": {"time_left_ticks": 1}, "quan": {"time_left_ticks": 1}}
        inputs = []
        for d in range(5):  # mỗi ngày: gather 1 tick + quan 1 tick, rồi đóng shop
            t = d * 3 + 2
            inputs += [{"tick": t, "shop_done": True}, {"tick": t + 1, "shop_done": False}]
        with Workdir() as w:
            rows = run(w, "day", sc, inputs, ticks=20, extra=("--days", "5"))
            plans = events(rows, "day_plan")
            self.assertEqual([e["day"] for e in plans], [1, 2, 3, 4, 5])
            for e in plans:
                self.assertEqual(e["data"]["dishes"], STD_PLAN[e["day"]])
            self.assertEqual((rows[-1]["reason"], rows[-1]["days_completed"]), ("days_complete", 5))

    def test_ac_p2_15_snapshot_day_co_truong_xuyen_ngay(self):
        sc = {"gather": {"time_left_ticks": 1}, "quan": {"time_left_ticks": 1}}
        with Workdir() as w:
            rows = run(w, "day", sc, ticks=4, every=1)
            for s in snapshots(rows):
                for key in ("day", "day_plan", "upgrades", "active_upgrades"):
                    self.assertIn(key, s, (s["phase"], key))
            self.assertEqual([s["phase"] for s in snapshots(rows)], ["gather", "quan", "shop", "shop", "shop"])

    def test_ac_p2_16_ngat_van_mo_quan_kho_rong_cung_tick(self):
        with Workdir() as w:
            sc = {"gather": {"player": {"pos": [60, 24], "hp": 1}, "hold": ["ca_loc", "ca_loc"],
                             "monsters": [croc()], **NO_FISH}}
            rows = run(w, "day", sc, ticks=2, every=1)
            self.assertEqual(names(rows, 1), ["monster_hit", "faint", "gather_end", "phase_start"])
            self.assertEqual(events(rows, "phase_start")[-1]["phase"], "quan")
            s = [s for s in snapshots(rows) if s["tick"] == 1][0]
            self.assertEqual((s["phase"], s["phase_tick"], s["stock"]), ("quan", 0, {}))

    def test_ac_p2_16_cap_ben_ban_giao_kho_vao_quan(self):
        with Workdir() as w:
            sc = {"gather": {"hold": ["ca_loc", "bong_sung", "bong_sung"], **NO_FISH}}
            rows = run(w, "day", sc, [{"tick": 0, "interact": True}], ticks=1)
            self.assertEqual(snapshots(rows)[-1]["stock"], {"bong_sung": 2, "ca_loc": 1})

    def test_ac_p2_17_mua_tru_money_giu_earned_va_diem(self):
        sc = {"day": {"money": 300, "earned": 300, "reputation": 3.0},
              "gather": {"time_left_ticks": 1}, "quan": {"time_left_ticks": 1}}
        with Workdir() as w:
            rows = run(w, "day", sc, [{"tick": 2, "buy": "hp"}], ticks=3, every=1)
            self.assertEqual(events(rows, "bought")[0]["data"], {"upgrade": "hp", "level": 1, "price": 250, "money": 50})
            s = snapshots(rows)[-1]
            self.assertEqual((s["money"], s["earned"], s["score"]), (50, 300, 600))
            self.assertEqual((s["upgrades"], s["active_upgrades"]), ({"hp": 1}, {}), "cấp mua hiện ngay, chưa áp dụng")

    def test_ac_p2_17_shop_tu_dong_sau_600_tick(self):
        sc = {"gather": {"time_left_ticks": 1}, "quan": {"time_left_ticks": 1}}
        with Workdir() as w:
            rows = run(w, "day", sc, ticks=700)
            se = events(rows, "shop_end")
            self.assertEqual([(e["tick"], e["data"]["reason"]) for e in se], [(2 + 600, "time")])

    def test_ac_p2_18_mau_va_oxy_day_lai_moi_ngay_theo_cap(self):
        sc = {"day": {"money": 700, "earned": 700},
              "gather": {"time_left_ticks": 1}, "quan": {"time_left_ticks": 1}}
        inputs = [{"tick": 2, "buy": "hp"}, {"tick": 3, "buy": "oxygen"}, {"tick": 4, "shop_done": True}]
        with Workdir() as w:
            rows = run(w, "day", sc, inputs, ticks=5, extra=("--days", "2"), every=1)
            s = snapshots(rows)[-1]
            self.assertEqual((s["day"], s["phase"]), (2, "gather"))
            self.assertEqual(s["active_upgrades"], {"hp": 1, "oxygen": 1})
            self.assertEqual((s["player"]["hp"], s["player"]["hp_max"]), (4, 4))
            self.assertEqual((s["player"]["oxygen_ticks"], s["player"]["oxygen_max_ticks"]), (2700, 2700))
            self.assertEqual(s["hold"], [], "giỏ làm mới đầu Ngày")


# ======================================================== 6. Pause (bổ sung TV1)
class Pause(unittest.TestCase):
    def test_ac_p2_19_pause_dong_bang_oxy_va_dong_ho(self):
        with Workdir() as w:
            sc = {"gather": {"player": {"pos": [20, 5]}, "monsters": [], **NO_FISH}}
            inputs = [{"tick": 0, "pause": True}, {"tick": 1, "pause": False}]
            rows = run(w, "gather", sc, inputs, ticks=30, every=1)
            s = snapshots(rows)[-1]
            self.assertEqual(s["state"], "paused")
            self.assertEqual(s["sim_tick"], 0)
            self.assertEqual(s["player"]["oxygen_ticks"], 1800)
            self.assertEqual(s["time_left_ticks"], 10800)


# ======================================================== 7. Cá bơi & sinh (chờ TV2)
class FishSwimSpawn(unittest.TestCase):
    def test_ac_p2_20_ca_boi_1_5_ms(self):
        with Workdir() as w:
            sc = {"gather": {"monsters": [], "fish": [{"id": "F1", "kind": "ca_loc", "pos": [50, 14], "heading_deg": 0}]}}
            rows = run(w, "gather", sc, ticks=60)
            f = [f for f in snapshots(rows)[-1]["fish"] if f["id"] == "F1"][0]
            self.assertAlmostEqual(math.dist(f["pos"], [50, 14]), 1.5, delta=0.1)

    def test_ac_p2_20_ca_o_trong_mien_va_dai_do_sau(self):
        with Workdir() as w:
            rows = run(w, "gather", {"gather": {"monsters": []}}, ticks=3000, seed=7, every=50)
            for s in snapshots(rows):
                for f in s["fish"]:
                    lo, hi = FISH_DEPTHS[f["kind"]]
                    self.assertTrue(4 - 0.1 <= f["pos"][0] <= 96 + 0.1, f)
                    self.assertTrue(lo - 0.1 <= f["pos"][1] <= hi + 0.1, f)

    def test_ac_p2_21_sinh_ca_o_phase_tick_360k_toi_da_12(self):
        with Workdir() as w:
            rows = run(w, "gather", {"gather": {"monsters": []}}, ticks=3000, seed=3, every=100)
            sp = events(rows, "fish_spawned")
            self.assertTrue(sp, "không có fish_spawned")
            self.assertTrue(all(e["tick"] % 360 == 0 for e in sp), [e["tick"] for e in sp])
            for e in sp:
                d = e["data"]
                self.assertIn(d["pos"][0], SPAWN_X)
                self.assertIn(d["pos"][1], SPAWN_D[d["kind"]])
            self.assertLessEqual(max(len(s["fish"]) for s in snapshots(rows)), 12)

    def test_ac_p2_22_tat_dinh_day_mot_ngay(self):
        outs = []
        for _ in range(2):
            with Workdir() as w:
                run(w, "day", None, [{"tick": 0, "move": [1, 1]}, {"tick": 300, "move": [-1, -1]}],
                    ticks=DAY_TICKS, seed=42, every=100)
                with open(w.path("o.jsonl"), "rb") as f:
                    outs.append(f.read())
        self.assertEqual(outs[0], outs[1])


if __name__ == "__main__":
    unittest.main()
