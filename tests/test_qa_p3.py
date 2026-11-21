"""Test QA Phase 3 (TV6) — TICKET-03 "Mùa Nước Nổi", Test Contract v1.2 (lõi: độ tươi, kho cá thể).
Viết TỪ ĐỀ, hộp đen qua headless_cmd. Mỗi test gắn mã AC-P3-xx (docs/verification/phase-3.md).
Mở rộng (current, reservations) chỉ chạy khi manifest khai trong `extensions`.

Số chuẩn: gather hao 0.5/s = 0.5/60 mỗi tick; quán hao 0.25/s = 0.25/60 mỗi tick; ươn khi fresh < 30.
Dung sai độ tươi ±0.01 (đề). Ngưỡng/tick event so chính xác.

Chạy: PYTHONPATH=tests:. python3 -m unittest tests.test_qa_p3 -v
"""

import json
import math
import os
import unittest

from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json

with open("game.contract.json", encoding="utf-8") as _f:
    CONTRACT = json.load(_f)
EXT = set(CONTRACT.get("extensions") or [])
G_DECAY = 0.5 / 60
Q_DECAY = 0.25 / 60
NO_FISH = {"fish": [], "random_fish": False, "monsters": []}
B1 = [2, 8]


def it(i, kind, fresh=100):
    return {"id": f"I{i}", "kind": kind, "fresh": fresh}


def run(w, mode, scenario=None, inputs=None, ticks=1, seed=1, extra=(), every=None):
    args = ["--mode", mode, "--seed", str(seed), "--ticks", str(ticks), "--out", w.path("o.jsonl"), *extra]
    if scenario is not None:
        args += ["--scenario", write_json(w.path("sc.json"), scenario)]
    if inputs is not None:
        args += ["--inputs", write_json(w.path("in.json"), frames(*inputs))]
    if every:
        args += ["--snapshot-every", str(every)]
    code, err = run_headless(*args)
    if code != 0:
        raise AssertionError(f"headless thoát mã {code}: {err}")
    return read_jsonl(w.path("o.jsonl"))


def code_of(*args):
    return run_headless(*args)[0]


def press(btn, t):
    return [{"tick": t, btn: True}, {"tick": t + 1, btn: False}]


def ids(items):
    return [x["id"] for x in items]


class Base(unittest.TestCase):
    def assertItems(self, got, want, tol=0.01):
        """So mảng cá thể: id, kind chính xác; fresh ±tol."""
        self.assertTrue(all(isinstance(x, dict) for x in got), f"cần mảng cá thể {{id,kind,fresh}}, nhận {got}")
        self.assertEqual([(x["id"], x["kind"]) for x in got], [(x["id"], x["kind"]) for x in want], got)
        for g, e in zip(got, want):
            self.assertEqual(set(g), {"id", "kind", "fresh"}, g)
            self.assertAlmostEqual(g["fresh"], e["fresh"], delta=tol, msg=g)


# ============================================================ AC-P3-01 Manifest v1.2
class Manifest(Base):
    def test_ac_p3_01_contract_version_1_2_va_freshness(self):
        # TICKET-04: v1.3 giữ gameplay, tuning, kho và JSONL theo v1.2
        self.assertIn(CONTRACT["contract_version"], ("1.2", "1.3"))
        self.assertEqual(CONTRACT["tuning"].get("freshness"),
                         {"initial": 100, "gather_decay_per_s": 0.5, "quan_decay_per_s": 0.25, "spoiled_below": 30})


# ============================================================ AC-P3-02 File kho cá thể (ghi / đọc)
class InventoryFile(Base):
    def dock(self, w, hold, ticks=1):
        inv = w.path("kho.json")
        rows = run(w, "gather", {"gather": {"hold": hold, **NO_FISH}}, [{"tick": 0, "interact": True}],
                   ticks=ticks, seed=42, extra=("--inventory-out", inv))
        with open(inv, encoding="utf-8") as f:
            return rows, json.load(f), inv

    def test_ac_p3_02_smoke_ban_giao_theo_de(self):
        """Mẫu trong đề: fresh 100, interact frame 0 → quán --ticks 0 nhận đúng id/kind/fresh."""
        with Workdir() as w:
            rows, saved, inv = self.dock(w, [it(1, "ca_linh", 100)])
            self.assertEqual(list(saved), ["items"])
            self.assertItems(saved["items"], [it(1, "ca_linh", 100 - G_DECAY)])
            end = events(rows, "gather_end")[0]["data"]
            self.assertEqual(end["reason"], "docked")
            # JSONL làm tròn số; đề v1.2: dung sai quan sát độ tươi ±0.01, id/kind so chính xác
            self.assertEqual(list(end["inventory"]), ["items"], "gather_end.inventory cùng schema")
            self.assertItems(end["inventory"]["items"], saved["items"])
            code, err = run_headless("--mode", "quan", "--seed", "42", "--inventory", inv, "--ticks", "0",
                                     "--out", w.path("q.jsonl"))
            self.assertEqual(code, 0, err)
            self.assertItems(snapshots(read_jsonl(w.path("q.jsonl")))[0]["stock"], saved["items"])

    def test_ac_p3_02_xuat_file_theo_id(self):
        with Workdir() as w:
            _, saved, _ = self.dock(w, [it(2, "ca_loc"), it(1, "bong_sung"), it(10, "ca_linh")])
            self.assertEqual(ids(saved["items"]), ["I1", "I2", "I10"])

    def test_ac_p3_02_kho_rong(self):
        with Workdir() as w:
            _, saved, _ = self.dock(w, [])
            self.assertEqual(saved, {"items": []})

    def test_ac_p3_02_ngat_ghi_kho_rong(self):
        with Workdir() as w:
            inv = w.path("kho.json")
            sc = {"gather": {"player": {"pos": [20, 5], "hp": 1, "oxygen_ticks": 0, "zero_oxy_ticks": 59},
                             "hold": [it(1, "ca_loc")], **NO_FISH}}
            rows = run(w, "gather", sc, ticks=3, extra=("--inventory-out", inv))
            with open(inv, encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"items": []})
            self.assertEqual(events(rows, "gather_end")[0]["data"]["inventory"], {"items": []})

    def test_ac_p3_02_cham_ticks_truoc_gather_end_khong_ghi(self):
        with Workdir() as w:
            inv = w.path("kho.json")
            run(w, "gather", {"gather": {"hold": [it(1, "ca_loc")], **NO_FISH}}, ticks=3, extra=("--inventory-out", inv))
            self.assertFalse(os.path.exists(inv))

    def test_ac_p3_02_quan_tu_choi_kho_sai_ma_2(self):
        bad = [{"items": {"ca_loc": 1}},                                   # kho đếm v1.1
               {"items": [{"id": "I1", "kind": "ca_la", "fresh": 50}]},     # kind lạ
               {"items": [it(1, "ca_loc"), it(1, "ca_linh")]},              # id trùng
               {"items": [it(1, "ca_loc", 100.5)]}, {"items": [it(1, "ca_loc", -0.1)]},
               {"items": [{"id": "", "kind": "ca_loc", "fresh": 50}]},       # id rỗng
               {"items": [{"id": "I1", "kind": "ca_loc"}]},                 # thiếu fresh
               {"items": [{"id": "I1", "kind": "ca_loc", "fresh": "50"}]},   # fresh sai kiểu
               {"items": [dict(it(1, "ca_loc"), extra=1)]},
               {"items": []} | {"x": 1}]
        with Workdir() as w:
            for b in bad:
                p = write_json(w.path("inv.json"), b)
                self.assertEqual(code_of("--mode", "quan", "--seed", "1", "--ticks", "0", "--inventory", p,
                                         "--out", w.path("q.jsonl")), 2, b)
                self.assertFalse(os.path.exists(w.path("q.jsonl")))

    def test_ac_p3_02_quan_nhan_hang_uon_va_khong_ap_tran_gio(self):
        items = [it(i, "ca_loc", 10 if i == 1 else 100) for i in range(1, 15)]
        with Workdir() as w:
            p = write_json(w.path("inv.json"), {"items": items})
            code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--inventory", p,
                                     "--out", w.path("q.jsonl"))
            self.assertEqual(code, 0, err)
            self.assertEqual(snapshots(read_jsonl(w.path("q.jsonl")))[0]["stock"], items)


# ============================================================ AC-P3-03 Id cá thể và LIFO
class ItemIds(Base):
    def test_ac_p3_03_id_moi_noi_tiep_theo_thu_tu_vao_gio(self):
        with Workdir() as w:
            sc = {"gather": {"player": {"pos": [20, 0]}, "hold": [it(1, "ca_loc"), it(2, "bong_sung")],
                             "nodes": [{"id": "N1", "kind": "keo_neo", "pos": [21, 0]}], **NO_FISH}}
            rows = run(w, "gather", sc, press("interact", 0), ticks=1)
            self.assertItems(snapshots(rows)[-1]["hold"],
                             [it(1, "ca_loc", 100 - G_DECAY), it(2, "bong_sung", 100 - G_DECAY), it(3, "keo_neo", 100)])

    def test_ac_p3_03_bat_ca_linh_cap_3_id_lien_tiep(self):
        with Workdir() as w:
            sc = {"gather": {"player": {"pos": [30, 5]}, "hold": [it(4, "ca_loc")], "monsters": [], "random_fish": False,
                             "fish": [{"id": "F1", "kind": "ca_linh", "pos": [31, 5]}]}}
            rows = run(w, "gather", sc, press("catch", 0), ticks=1)
            self.assertEqual(ids(snapshots(rows)[-1]["hold"]), ["I4", "I5", "I6", "I7"])

    def test_ac_p3_03_mat_hang_lifo_va_id_khong_dung_lai(self):
        hold = [it(1, "ca_loc"), it(2, "bong_sung"), it(3, "ca_linh"), it(4, "ca_keo")]
        croc = {"id": "M1", "kind": "ca_sau", "pos": [30, 24], "waypoints": [[30, 24], [34, 24]]}
        with Workdir() as w:
            sc = {"gather": {"player": {"pos": [30, 24]}, "hold": hold, "monsters": [croc], "random_fish": False,
                             "fish": [{"id": "F1", "kind": "ca_loc", "pos": [29, 24]}]}}
            rows = run(w, "gather", sc, press("catch", 1), ticks=2)
            hit = events(rows, "monster_hit")[0]["data"]
            self.assertItems(hit["lost"], [it(4, "ca_keo", 100 - G_DECAY), it(3, "ca_linh", 100 - G_DECAY)])
            self.assertEqual(ids(snapshots(rows)[-1]["hold"]), ["I1", "I2", "I5"], "id mới I5, không dùng lại I3/I4")

    def test_ac_p3_03_ngat_lost_la_ca_the_lifo(self):
        with Workdir() as w:
            sc = {"gather": {"player": {"pos": [20, 5], "hp": 1, "oxygen_ticks": 0, "zero_oxy_ticks": 59},
                             "hold": [it(1, "ca_loc"), it(2, "bong_sung")], **NO_FISH}}
            rows = run(w, "gather", sc, ticks=1)
            f = events(rows, "faint")[0]["data"]
            self.assertItems(f["lost"], [it(2, "bong_sung", 100 - G_DECAY), it(1, "ca_loc", 100 - G_DECAY)])


# ============================================================ AC-P3-04 Hao tươi
class Decay(Base):
    def test_ac_p3_04_gio_giam_0_5_moi_giay(self):
        with Workdir() as w:
            rows = run(w, "gather", {"gather": {"hold": [it(1, "ca_loc")], **NO_FISH}}, ticks=60)
            self.assertItems(snapshots(rows)[-1]["hold"], [it(1, "ca_loc", 99.5)])

    def test_ac_p3_04_hang_moi_100_hao_tu_buoc_sau(self):
        with Workdir() as w:
            sc = {"gather": {"player": {"pos": [20, 0]}, "nodes": [{"id": "N1", "kind": "bong_sung", "pos": [21, 0]}],
                             **NO_FISH}}
            rows = run(w, "gather", sc, press("interact", 0), ticks=2, every=1)
            by = {s["tick"]: s["hold"] for s in snapshots(rows)}
            self.assertItems(by[1], [it(1, "bong_sung", 100)])
            self.assertItems(by[2], [it(1, "bong_sung", 100 - G_DECAY)])

    def test_ac_p3_04_kho_quan_giam_0_25_moi_giay_ke_ca_hang_giu(self):
        with Workdir() as w:
            sc = {"quan": {"random_customers": False, "stock": [it(1, "ca_loc"), it(2, "bong_sung")],
                           "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "reserved": ["I1"]}]}}
            rows = run(w, "quan", sc, ticks=60)
            self.assertItems(snapshots(rows)[-1]["stock"], [it(1, "ca_loc", 99.75), it(2, "bong_sung", 99.75)])

    def test_ac_p3_04_kep_day_0(self):
        with Workdir() as w:
            rows = run(w, "gather", {"gather": {"hold": [it(1, "ca_loc", 0.004)], **NO_FISH}}, ticks=3)
            self.assertEqual(snapshots(rows)[-1]["hold"][0]["fresh"], 0)

    def test_ac_p3_04_pause_dung_hao_tuoi(self):
        with Workdir() as w:
            rows = run(w, "gather", {"gather": {"hold": [it(1, "ca_loc")], **NO_FISH}},
                       [{"tick": 0, "pause": True}], ticks=30)
            self.assertEqual(snapshots(rows)[-1]["hold"][0]["fresh"], 100)

    def test_ac_p3_04_shop_khong_hao_tuoi(self):
        sc = {"gather": {"time_left_ticks": 1, "hold": [it(1, "ca_loc")], **NO_FISH},
              "quan": {"time_left_ticks": 1, "random_customers": False}}
        with Workdir() as w:
            rows = run(w, "day", sc, ticks=100, every=1)
            shop = [s for s in snapshots(rows) if s["phase"] == "shop"]
            self.assertGreater(len(shop), 10)
            self.assertEqual(shop[0]["stock"], shop[-1]["stock"], "hàng thô ở Shop không hao")

    def test_ac_p3_09_day_ban_giao_cung_tick_khong_hao_them(self):
        with Workdir() as w:
            sc = {"gather": {"hold": [it(1, "ca_loc"), it(2, "bong_sung")], **NO_FISH}}
            rows = run(w, "day", sc, [{"tick": 0, "interact": True}], ticks=1, every=1)
            inv = events(rows, "gather_end")[0]["data"]["inventory"]["items"]
            q0 = [s for s in snapshots(rows) if s["phase"] == "quan" and s["phase_tick"] == 0][0]
            self.assertEqual(q0["stock"], inv)


# ============================================================ AC-P3-05 Ươn
class Spoil(Base):
    def test_ac_p3_05_mau_trong_de_fresh_30_uon_buoc_dau(self):
        with Workdir() as w:
            rows = run(w, "gather", {"gather": {"hold": [it(1, "ca_linh", 30)], "random_fish": False, "monsters": []}},
                       ticks=1)
            e = events(rows, "spoiled")
            self.assertEqual([(x["tick"], x["phase"], x["data"]) for x in e],
                             [(1, "gather", {"item_id": "I1", "kind": "ca_linh", "location": "hold"})])

    def test_ac_p3_05_spoiled_dung_mot_lan(self):
        with Workdir() as w:
            rows = run(w, "gather", {"gather": {"hold": [it(1, "ca_linh", 30)], **NO_FISH}}, ticks=50)
            self.assertEqual(len(events(rows, "spoiled")), 1)

    def test_ac_p3_05_chua_qua_nguong_chua_uon(self):
        with Workdir() as w:
            rows = run(w, "gather", {"gather": {"hold": [it(1, "ca_linh", 30.01)], **NO_FISH}}, ticks=2, every=1)
            self.assertEqual([e["tick"] for e in events(rows, "spoiled")], [2], "30.01 → 30.0017 ở tick 1, < 30 ở tick 2")

    # Ca biên sát ngưỡng 30 (không nằm trên lưới 1/240). Đề: "So ngưỡng trước làm tròn", "Tick của event biên phải chính xác".
    # Kỳ vọng tính bằng số học chính xác: gather hao 0.5/60 mỗi tick, quán 0.25/60.
    def _spoil_ticks(self, mode, fresh, ticks=3):
        key, kind = ("hold", "ca_linh") if mode == "gather" else ("stock", "ca_loc")
        sc = {mode: {key: [it(1, kind, fresh)], **({"random_customers": False} if mode == "quan" else NO_FISH)}}
        with Workdir() as w:
            return [e["tick"] for e in events(run(w, mode, sc, ticks=ticks, every=1), "spoiled")]

    def test_ac_p3_05_bien_da_duoi_30_khong_phat_spoiled_gather(self):
        self.assertEqual(self._spoil_ticks("gather", 29.999), [], "29.999 đã < 30 từ đầu: không có bước ≥30 → <30")

    def test_ac_p3_05_bien_da_duoi_30_khong_phat_spoiled_quan(self):
        self.assertEqual(self._spoil_ticks("quan", 29.999), [])

    def test_ac_p3_05_bien_30_001_uon_o_tick_1_gather(self):
        self.assertEqual(self._spoil_ticks("gather", 30.001), [1], "30.001 − 0.00833 = 29.9927 < 30")

    def test_ac_p3_05_bien_30_001_uon_o_tick_1_quan(self):
        self.assertEqual(self._spoil_ticks("quan", 30.001), [1], "30.001 − 0.00417 = 29.9968 < 30")

    def test_ac_p3_05_bien_30_008_uon_o_tick_1_gather(self):
        self.assertEqual(self._spoil_ticks("gather", 30.008), [1], "30.008 − 0.00833 = 29.9997 < 30")

    def test_ac_p3_05_bien_30_004_uon_o_tick_1_quan(self):
        self.assertEqual(self._spoil_ticks("quan", 30.004), [1], "30.004 − 0.00417 = 29.9998 < 30")

    def test_ac_p3_10_chay_dai_ca_the_uon_dung_mot_lan_id_khong_trung(self):
        # Regression chạy cả buổi gather (10800 tick) với kho cá thể v1.2
        with Workdir() as w:
            sc = {"gather": {"hold": [it(1, "ca_linh", 100), it(2, "ca_loc", 50), it(3, "bong_sung", 31)], **NO_FISH}}
            rows = run(w, "gather", sc, ticks=10800, every=2000)
            sp = events(rows, "spoiled")
            self.assertEqual(sorted(e["data"]["item_id"] for e in sp), ["I1", "I2", "I3"], "mỗi cá thể ươn đúng một lần")
            last = snapshots(rows)[-1]["hold"]
            self.assertEqual(len({x["id"] for x in last}), len(last))
            self.assertTrue(all(0 <= x["fresh"] < 30 for x in last), last)

    def test_ac_p3_05_nhieu_ca_the_cung_tick_theo_id(self):
        with Workdir() as w:
            rows = run(w, "gather", {"gather": {"hold": [it(2, "ca_loc", 30), it(1, "bong_sung", 30)], **NO_FISH}}, ticks=1)
            self.assertEqual([e["data"]["item_id"] for e in events(rows, "spoiled")], ["I1", "I2"])

    def test_ac_p3_05_uon_trong_kho_quan(self):
        with Workdir() as w:
            rows = run(w, "quan", {"quan": {"random_customers": False, "stock": [it(1, "ca_loc", 30)]}}, ticks=1)
            self.assertEqual(events(rows, "spoiled")[0]["data"], {"item_id": "I1", "kind": "ca_loc", "location": "stock"})

    def test_ac_p3_05_hang_uon_van_chiem_o_gio(self):
        with Workdir() as w:
            hold = [it(i, "bong_sung", 10) for i in range(1, 13)]
            sc = {"gather": {"player": {"pos": [20, 0]}, "hold": hold,
                             "nodes": [{"id": "N1", "kind": "keo_neo", "pos": [21, 0]}], **NO_FISH}}
            rows = run(w, "gather", sc, press("interact", 0), ticks=1)
            self.assertEqual(len(events(rows, "hold_full")), 1)

    def test_ac_p3_05_hang_uon_khong_dung_nau_khach_no_dish(self):
        with Workdir() as w:
            rows = run(w, "quan", {"quan": {"stock": [it(1, "ca_loc", 20)]}}, ticks=120)
            self.assertEqual(events(rows, "customer_arrived"), [])
            self.assertEqual(len(events(rows, "no_dish")), 1)


# ============================================================ AC-P3-06 Giữ chỗ theo id
class ReserveById(Base):
    def test_ac_p3_06_khach_moi_giu_ca_the_tuoi_nhat(self):
        with Workdir() as w:
            rows = run(w, "quan", {"quan": {"stock": [it(1, "ca_loc", 80), it(2, "ca_loc", 90), it(3, "ca_loc", 20)]}},
                       ticks=120)
            self.assertEqual(snapshots(rows)[-1]["customers"][0]["reserved"], ["I2"])

    def test_ac_p3_06_hoa_tuoi_chon_id_nho(self):
        with Workdir() as w:
            rows = run(w, "quan", {"quan": {"stock": [it(2, "ca_loc", 90), it(1, "ca_loc", 90)]}}, ticks=120)
            self.assertEqual(snapshots(rows)[-1]["customers"][0]["reserved"], ["I1"])

    def test_ac_p3_06_fixture_bo_reserved_tu_cap_tuoi_nhat(self):
        with Workdir() as w:
            sc = {"quan": {"random_customers": False, "stock": [it(1, "ca_loc", 50), it(2, "ca_loc", 70)],
                           "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui"}]}}
            rows = run(w, "quan", sc, ticks=0)
            self.assertEqual(snapshots(rows)[0]["customers"][0]["reserved"], ["I2"])

    def test_ac_p3_06_hang_giu_vua_uon_giu_lai_ca_the_khac(self):
        with Workdir() as w:
            sc = {"quan": {"random_customers": False, "stock": [it(1, "ca_loc", 30), it(2, "ca_loc", 80)],
                           "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "reserved": ["I1"]}]}}
            rows = run(w, "quan", sc, ticks=1)
            self.assertEqual(events(rows, "spoiled")[0]["data"]["item_id"], "I1")
            c = snapshots(rows)[-1]["customers"][0]
            self.assertEqual((c["reserved"], c["order_status"]), (["I2"], "reserved"))

    def test_ac_p3_06_giu_lai_khong_du_thi_unfulfillable_khach_van_cho(self):
        with Workdir() as w:
            sc = {"quan": {"random_customers": False, "stock": [it(1, "ca_loc", 30)],
                           "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "reserved": ["I1"]}]}}
            rows = run(w, "quan", sc, ticks=5)
            c = snapshots(rows)[-1]["customers"][0]
            self.assertEqual((c["reserved"], c["order_status"], c["state"]), ([], "unfulfillable", "waiting"))
            self.assertEqual(events(rows, "customer_left"), [])

    def test_ac_p3_06_nhieu_don_bi_anh_huong_theo_order_tick(self):
        with Workdir() as w:
            stock = [it(1, "ca_loc", 30), it(2, "ca_loc", 30), it(3, "ca_loc", 80)]
            cs = [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "reserved": ["I1"], "order_tick": 50},
                  {"id": "C2", "table_id": "T2", "dish_id": "ca_loc_nuong_trui", "reserved": ["I2"], "order_tick": 10}]
            rows = run(w, "quan", {"quan": {"random_customers": False, "stock": stock, "customers": cs}}, ticks=1)
            got = {c["id"]: (c["reserved"], c["order_status"]) for c in snapshots(rows)[-1]["customers"]}
            self.assertEqual(got, {"C2": (["I3"], "reserved"), "C1": ([], "unfulfillable")})

    def test_ac_p3_06_hang_dang_giu_khong_cho_khach_khac(self):
        with Workdir() as w:
            sc = {"quan": {"stock": [it(1, "ca_loc", 90)],
                           "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "reserved": ["I1"]}]}}
            rows = run(w, "quan", sc, ticks=120)
            self.assertEqual(len(events(rows, "no_dish")), 1)


# ============================================================ AC-P3-07 Giá theo độ tươi
class FreshPrice(Base):
    def cook(self, w, stock, dish, reserved):
        sc = {"quan": {"random_customers": False, "player": {"pos": B1}, "stock": stock,
                       "customers": [{"id": "C1", "table_id": "T1", "dish_id": dish, "reserved": reserved}]}}
        return run(w, "quan", sc, press("interact", 0), ticks=1)

    def test_ac_p3_07_chot_gia_theo_tuoi_tieu_dung_id_giu(self):
        with Workdir() as w:
            rows = self.cook(w, [it(1, "ca_loc", 75.5), it(2, "ca_loc", 100)], "ca_loc_nuong_trui", ["I1"])
            d = events(rows, "cook_started")[0]["data"]
            self.assertEqual(d["base_price"], math.floor(60 * (75.5 - Q_DECAY) / 100))  # 45
            self.assertItems(d["items"], [it(1, "ca_loc", 75.5 - Q_DECAY)])
            self.assertEqual(ids(snapshots(rows)[-1]["stock"]), ["I2"], "tiêu đúng id đang giữ, không lấy I2 tươi hơn")

    def test_ac_p3_07_trung_binh_nhieu_ca_the_va_items_theo_kind_roi_id(self):
        stock = [it(4, "bong_dien_dien", 60), it(3, "ca_linh", 70), it(1, "ca_linh", 90), it(2, "ca_linh", 80)]
        with Workdir() as w:
            rows = self.cook(w, stock, "lau_ca_linh_dien_dien", ["I1", "I2", "I3", "I4"])
            d = events(rows, "cook_started")[0]["data"]
            avg = (90 + 80 + 70 + 60) / 4 - Q_DECAY
            self.assertEqual(d["base_price"], math.floor(120 * avg / 100))  # 89, không phải 90
            self.assertEqual(ids(d["items"]), ["I4", "I1", "I2", "I3"])

    def test_ac_p3_07_boa_tinh_tren_gia_da_chot(self):
        with Workdir() as w:
            pay = {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 45}
            sc = {"quan": {"random_customers": False, "player": {"pos": [9, 2.5]}, "hand": pay,
                           "customers": [{"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                                          "order_status": "assigned", "reserved": []}]}}
            rows = run(w, "quan", sc, press("interact", 0), ticks=601)
            self.assertEqual((events(rows, "served")[0]["data"]["base_price"], events(rows, "served")[0]["data"]["tip"]),
                             (45, 9))
            self.assertEqual(events(rows, "paid")[0]["data"]["amount"], 54)


# ============================================================ AC-P3-08 Scenario v1.2
class ScenarioV12(Base):
    def expect2(self, mode, sc):
        with Workdir() as w:
            p = write_json(w.path("sc.json"), sc)
            self.assertEqual(code_of("--mode", mode, "--seed", "1", "--ticks", "0", "--scenario", p,
                                     "--out", w.path("o.jsonl")), 2, sc)

    def test_ac_p3_08_gather_hold_sai_ma_2(self):
        for hold in (["ca_loc"], [it(1, "ca_loc"), it(1, "ca_linh")], [it(1, "ca_la")], [it(1, "ca_loc", 101)],
                     [{"id": "I1", "kind": "ca_loc"}], [it(i, "ca_loc") for i in range(1, 14)]):
            with self.subTest(hold=hold):
                self.expect2("gather", {"gather": {"hold": hold}})

    def test_ac_p3_08_quan_stock_va_reserved_sai_ma_2(self):
        c = {"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui"}
        for q in ({"stock": {"ca_loc": 1}},
                  {"stock": [it(1, "ca_loc"), it(1, "ca_loc")]},
                  {"stock": [it(1, "ca_loc")], "customers": [dict(c, reserved=["I9"])]},
                  {"stock": [it(1, "ca_loc", 20)], "customers": [dict(c, reserved=["I1"])]},
                  {"stock": [it(1, "bong_sung")], "customers": [dict(c, reserved=["I1"])]},
                  {"stock": [it(1, "ca_loc")], "customers": [dict(c, reserved=["I1"]),
                                                              dict(c, id="C2", table_id="T2", reserved=["I1"])]},
                  {"stock": [it(1, "ca_loc")], "customers": [dict(c, reserved={"ca_loc": 1})]}):
            with self.subTest(q=q):
                self.expect2("quan", {"quan": q})

    def test_ac_p3_08_day_ngay_ke_cap_id_moi_theo_mau(self):
        sc = {"gather": {"time_left_ticks": 1, "hold": [it(1, "ca_loc", 100), it(2, "bong_sung", 50)], **NO_FISH},
              "quan": {"time_left_ticks": 1, "random_customers": False}}
        with Workdir() as w:
            rows = run(w, "day", sc, press("shop_done", 2), ticks=3, every=1, extra=("--days", "2"))
            starts = [s for s in snapshots(rows) if s["phase"] == "gather" and s["phase_tick"] == 0]
            self.assertItems(starts[0]["hold"], [it(1, "ca_loc", 100), it(2, "bong_sung", 50)])
            self.assertItems(starts[1]["hold"], [it(3, "ca_loc", 100), it(4, "bong_sung", 50)])


if __name__ == "__main__":
    unittest.main()
