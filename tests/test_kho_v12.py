"""Phase 3 (Contract v1.2): kho cá thể, độ tươi trong giỏ, spoiled, id I1.., file kho, đọc kho theo version.
Hộp đen qua headless với contract v1.2 tạm (CHONOI_CONTRACT); preset ở gốc repo chưa đổi version."""

import json
import os
import subprocess
import unittest

from helpers import ROOT, Workdir, events, frames, headless_cmd, read_jsonl, snapshots, write_json

FRESHNESS = {"initial": 100, "gather_decay_per_s": 0.5, "quan_decay_per_s": 0.25, "spoiled_below": 30}
STEP = 0.5 / 60  # độ tươi mất mỗi tick trong giỏ


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def contract_v12(w, **override):
    with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
        c = json.load(f)
    c["contract_version"] = "1.2"
    c["tuning"]["freshness"] = dict(FRESHNESS)
    c.update(override)
    return write_json(w.path("contract.json"), c)


def run(w, *args, contract=None):
    env = {**os.environ, "CHONOI_CONTRACT": contract or contract_v12(w)}
    p = subprocess.run([*headless_cmd(), *args], cwd=ROOT, capture_output=True, text=True, env=env)
    return p.returncode, p.stderr


def gather(w, scenario, fr=(), ticks=1, inv_out=None, code=0):
    args = ["--mode", "gather", "--seed", "1", "--ticks", str(ticks), "--snapshot-every", "1",
            "--scenario", write_json(w.path("sc.json"), {"gather": scenario}), "--out", w.path("g.jsonl")]
    if fr:
        args += ["--inputs", write_json(w.path("in.json"), frames(*fr))]
    if inv_out:
        args += ["--inventory-out", inv_out]
    rc, err = run(w, *args)
    assert rc == code, err
    return read_jsonl(w.path("g.jsonl")) if rc == 0 else None


I = lambda i, kind, fresh: {"id": i, "kind": kind, "fresh": fresh}
QUIET = {"random_fish": False, "monsters": []}


class Spoil(unittest.TestCase):
    def test_fixture_ticket_fresh_30_uon_o_buoc_dau(self):
        with Workdir() as w:
            rows = gather(w, {"hold": [I("I1", "ca_linh", 30)], **QUIET})
            self.assertEqual([(e["tick"], e["name"], e["data"]) for e in events(rows)],
                             [(1, "spoiled", {"item_id": "I1", "kind": "ca_linh", "location": "hold"})])
            self.assertAlmostEqual(snapshots(rows)[-1]["hold"][0]["fresh"], 30 - STEP, delta=0.001)

    def test_dung_30_sau_buoc_chua_uon_buoc_sau_moi_uon(self):
        with Workdir() as w:
            rows = gather(w, {"hold": [I("I1", "ca_linh", 30 + STEP)], **QUIET}, ticks=2)
            self.assertEqual([(e["tick"], e["name"]) for e in events(rows)], [(2, "spoiled")])

    def test_spoiled_mot_lan_theo_id_va_hang_uon_van_chiem_o(self):
        with Workdir() as w:
            hold = [I("I10", "ca_loc", 30), I("I2", "bong_sung", 30), I("I3", "ca_linh", 20)]
            rows = gather(w, {"hold": hold, **QUIET}, ticks=5)
            self.assertEqual([e["data"]["item_id"] for e in events(rows, "spoiled")], ["I2", "I10"])
            self.assertEqual(snapshots(rows)[-1]["hold_count"], 3)

    def test_kep_day_0(self):
        with Workdir() as w:
            rows = gather(w, {"hold": [I("I1", "ca_linh", 0)], **QUIET}, ticks=3)
            self.assertEqual(snapshots(rows)[-1]["hold"][0]["fresh"], 0)


class NewItems(unittest.TestCase):
    def test_hai_tuoi_100_hao_tu_buoc_sau_id_tiep_tuc(self):
        with Workdir() as w:
            rows = gather(w, {"player": {"pos": [20, 0]}, "hold": [I("I1", "ca_loc", 50)], **QUIET,
                              "nodes": [{"id": "N1", "kind": "bong_sung", "pos": [20, 0]}]},
                          [{"tick": 0, "interact": True}], ticks=2)
            h1, h2 = snapshots(rows)[1]["hold"], snapshots(rows)[2]["hold"]
            self.assertEqual(h1[1], I("I2", "bong_sung", 100))
            self.assertAlmostEqual(h2[1]["fresh"], 100 - STEP, delta=0.001)

    def test_bat_ca_cap_id_theo_thu_tu_vao_gio(self):
        with Workdir() as w:
            rows = gather(w, {"player": {"pos": [20, 5]}, "random_fish": False, "monsters": [],
                              "fish": [{"id": "F1", "kind": "ca_linh", "pos": [20, 5]}]},
                          [{"tick": 0, "catch": True}])
            self.assertEqual([i["id"] for i in snapshots(rows)[-1]["hold"]], ["I1", "I2", "I3"])

    def test_ngat_bo_ca_the_theo_LIFO_kho_rong(self):
        with Workdir() as w:
            inv = w.path("kho.json")
            hold = [I("I1", "ca_loc", 80), I("I2", "bong_sung", 90)]
            rows = gather(w, {"player": {"pos": [20, 5], "hp": 1, "oxygen_ticks": 0, "zero_oxy_ticks": 59},
                              "hold": hold, **QUIET}, inv_out=inv)
            faint = events(rows, "faint")[0]["data"]
            self.assertEqual([i["id"] for i in faint["lost"]], ["I2", "I1"])
            self.assertEqual(events(rows, "gather_end")[0]["data"]["inventory"], {"items": []})
            self.assertEqual(read_json(inv), {"items": []})


class Handoff(unittest.TestCase):
    def test_smoke_ticket_cap_ben_ghi_kho_ca_the_chinh_xac(self):
        with Workdir() as w:
            inv = w.path("kho.json")
            rows = gather(w, {"hold": [I("I1", "ca_linh", 100)], **QUIET}, [{"tick": 0, "interact": True}],
                          inv_out=inv)
            saved = read_json(inv)
            self.assertEqual(saved["items"][0]["id"], "I1")
            self.assertEqual(round(saved["items"][0]["fresh"] * 240), 100 * 240 - 2)  # hao 1 bước, đủ chính xác
            end = events(rows, "gather_end")[0]["data"]
            self.assertEqual(end["reason"], "docked")
            self.assertEqual(end["inventory"]["items"], [I("I1", "ca_linh", round(100 - STEP, 3))])

    def test_file_kho_sap_theo_id(self):
        with Workdir() as w:
            inv = w.path("kho.json")
            hold = [I("I10", "ca_loc", 90), I("I2", "bong_sung", 90)]
            gather(w, {"hold": hold, **QUIET}, [{"tick": 0, "interact": True}], inv_out=inv)
            self.assertEqual([i["id"] for i in read_json(inv)["items"]], ["I2", "I10"])


class ReadInventory(unittest.TestCase):
    def quan_reads(self, w, items):
        p = write_json(w.path("in-kho.json"), {"items": items})
        return run(w, "--mode", "quan", "--seed", "1", "--ticks", "0", "--inventory", p, "--out", w.path("q.jsonl"))[0]

    def test_v12_tu_choi_kho_dem_va_ca_the_sai(self):
        bad = [{"ca_loc": 1}, [I("I1", "ca_loc", 50), I("I1", "ca_linh", 50)], [I("I1", "ca_ro", 50)],
               [I("I1", "ca_loc", 100.5)], [I("I1", "ca_loc", -1)], [I("", "ca_loc", 5)],
               [{"id": "I1", "kind": "ca_loc"}]]
        for items in bad:
            with Workdir() as w:
                self.assertEqual(self.quan_reads(w, items), 2, items)

    def test_v12_scenario_hold_kieu_cu_ma_2(self):
        with Workdir() as w:
            gather(w, {"hold": ["ca_loc"], **QUIET}, code=2)

    def test_co_freshness_nhung_van_1_1_thi_chay_kho_dem(self):
        """Chuyển dần: preset khai sẵn freshness ở 1.1 -> gather vẫn xuất mảng kind / kho đếm như v1.1."""
        with Workdir() as w:
            c = contract_v12(w, contract_version="1.1")
            inv = w.path("kho.json")
            sc = write_json(w.path("sc.json"), {"gather": {"hold": ["ca_loc"], **QUIET}})
            rc, err = run(w, "--mode", "gather", "--seed", "1", "--ticks", "1", "--scenario", sc,
                          "--inputs", write_json(w.path("in.json"), frames({"tick": 0, "interact": True})),
                          "--inventory-out", inv, "--out", w.path("g.jsonl"), contract=c)
            self.assertEqual(rc, 0, err)
            self.assertEqual(read_json(inv), {"items": {"ca_loc": 1}})
            self.assertEqual(snapshots(read_jsonl(w.path("g.jsonl")))[0]["hold"], ["ca_loc"])

    def test_contract_1_2_thieu_freshness_ma_2(self):
        with Workdir() as w:
            c = contract_v12(w)
            data = read_json(c)
            del data["tuning"]["freshness"]
            write_json(c, data)
            self.assertEqual(run(w, "--mode", "gather", "--seed", "1", "--ticks", "0", "--out", w.path("o.jsonl"),
                                 contract=c)[0], 2)


if __name__ == "__main__":
    unittest.main()
