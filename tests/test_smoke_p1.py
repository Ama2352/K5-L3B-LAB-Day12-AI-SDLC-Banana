"""Smoke test Phase 1 (công khai). Các test này PHẢI xanh trên starter; nhóm viết thêm test cho luật của mình.

Chạy: python3 -m unittest discover -s tests -v
"""

import json
import os
import unittest

from chonoi.ids import IdAllocator, id_key, sort_by_id
from chonoi.inputs import InputPlayer, load_frames
from chonoi.errors import BadInput

from helpers import (Workdir, close, events, frames, read_jsonl, run_headless, snapshots, write_json)


class Contract(unittest.TestCase):
    def test_con_01_ticks_zero_and_end_line(self):
        with Workdir() as w:
            for mode in ("river", "quan"):
                code, err = run_headless("--mode", mode, "--seed", "1", "--ticks", "0", "--out", w.path(f"{mode}.jsonl"))
                self.assertEqual(code, 0, err)
                rows = read_jsonl(w.path(f"{mode}.jsonl"))
                self.assertEqual(rows[0]["type"], "snapshot")
                self.assertEqual(rows[0]["tick"], 0)
                self.assertEqual(rows[-1]["type"], "end")
                self.assertEqual(sum(r["type"] == "end" for r in rows), 1)

    def test_con_02_deterministic_bytes(self):
        with Workdir() as w:
            inp = write_json(w.path("in.json"), frames({"tick": 0, "move": [1, 1]}, {"tick": 100, "move": [0, 0]}))
            for i in (1, 2):
                code, err = run_headless("--mode", "river", "--seed", "7", "--ticks", "300", "--inputs", inp,
                                         "--out", w.path(f"o{i}.jsonl"))
                self.assertEqual(code, 0, err)
            with open(w.path("o1.jsonl"), "rb") as a, open(w.path("o2.jsonl"), "rb") as b:
                self.assertEqual(a.read(), b.read())

    def test_con_03_bad_input_exit_2(self):
        with Workdir() as w:
            out = w.path("o.jsonl")
            bad = write_json(w.path("bad.json"), frames({"tick": 5, "move": [0, 1]}, {"tick": 5}))
            self.assertEqual(run_headless("--mode", "river", "--seed", "1", "--ticks", "10", "--inputs", bad, "--out", out)[0], 2)
            self.assertFalse(os.path.exists(out), "lỗi đầu vào phải thoát TRƯỚC khi ghi đầu ra")
            self.assertEqual(run_headless("--mode", "river", "--seed", "1", "--ticks", "-1", "--out", out)[0], 2)
            unk = write_json(w.path("unk.json"), frames({"tick": 0, "jump": True}))
            self.assertEqual(run_headless("--mode", "river", "--seed", "1", "--ticks", "10", "--inputs", unk, "--out", out)[0], 2)


class Movement(unittest.TestCase):
    def test_move_01_speed_and_normalized_diagonal(self):
        """Bỏ 6 tick tăng tốc rồi đo 60 tick: quãng ≈ xuong_speed × 1 s (±0.1), chéo không nhanh hơn."""
        with open("game.contract.json", encoding="utf-8") as f:
            speed = json.load(f)["tuning"]["river"]["xuong_speed"]
        for mv in ([1, 0], [1, 1]):
            with Workdir() as w:
                inp = write_json(w.path("in.json"), frames({"tick": 0, "move": mv}))
                code, err = run_headless("--mode", "river", "--seed", "1", "--ticks", "66", "--inputs", inp,
                                         "--snapshot-every", "1", "--out", w.path("o.jsonl"))
                self.assertEqual(code, 0, err)
                s = {r["tick"]: r for r in snapshots(read_jsonl(w.path("o.jsonl")))}
                a, b = s[6]["player"]["pos"], s[66]["player"]["pos"]
                self.assertTrue(close(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5, speed), (mv, a, b))

    def test_move_03_edge_clamp(self):
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {"river": {"player": {"pos": [118, 20]}}})
            inp = write_json(w.path("in.json"), frames({"tick": 0, "move": [1, 0]}))
            code, err = run_headless("--mode", "river", "--seed", "1", "--ticks", "120", "--scenario", sc,
                                     "--inputs", inp, "--out", w.path("o.jsonl"))
            self.assertEqual(code, 0, err)
            last = snapshots(read_jsonl(w.path("o.jsonl")))[-1]
            self.assertEqual(last["player"]["pos"][0], 120)
            self.assertEqual(last["player"]["floats"], 3)


class Integration(unittest.TestCase):
    def test_inv_01_river_writes_inventory_quan_reads_it(self):
        with Workdir() as w:
            sc = write_json(w.path("sc.json"), {"river": {"hold": ["ca_loc", "bong_sung", "bong_sung"]}})
            inp = write_json(w.path("in.json"), frames({"tick": 0, "interact": True}))
            inv = w.path("inv.json")
            code, err = run_headless("--mode", "river", "--seed", "1", "--ticks", "30", "--scenario", sc,
                                     "--inputs", inp, "--inventory-out", inv, "--out", w.path("r.jsonl"))
            self.assertEqual(code, 0, err)
            with open(inv, encoding="utf-8") as f:
                saved = json.load(f)
            self.assertEqual(saved, {"items": {"bong_sung": 2, "ca_loc": 1}})
            end = events(read_jsonl(w.path("r.jsonl")), "river_end")[0]["data"]
            self.assertEqual(end["reason"], "docked")
            self.assertEqual(end["inventory"], saved)
            code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--inventory", inv,
                                     "--out", w.path("q.jsonl"))
            self.assertEqual(code, 0, err)
            self.assertEqual(snapshots(read_jsonl(w.path("q.jsonl")))[0]["stock"], {"bong_sung": 2, "ca_loc": 1})

    def test_inv_01_not_written_when_tick_limit_first(self):
        with Workdir() as w:
            inv = w.path("inv.json")
            code, _ = run_headless("--mode", "river", "--seed", "1", "--ticks", "5", "--inventory-out", inv,
                                   "--out", w.path("r.jsonl"))
            self.assertEqual(code, 0)
            self.assertFalse(os.path.exists(inv))

    def test_inv_bad_schema_exit_2(self):
        with Workdir() as w:
            for bad in ({"items": {"ca_la_lung": 1}}, {"items": {"ca_loc": -1}}, {"items": {}, "x": 1}):
                p = write_json(w.path("inv.json"), bad)
                self.assertEqual(run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--inventory", p,
                                              "--out", w.path("q.jsonl"))[0], 2, bad)

    def test_inventory_and_scenario_stock_conflict(self):
        with Workdir() as w:
            inv = write_json(w.path("inv.json"), {"items": {}})
            sc = write_json(w.path("sc.json"), {"quan": {"stock": {"ca_loc": 1}}})
            self.assertEqual(run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--inventory", inv,
                                          "--scenario", sc, "--out", w.path("q.jsonl"))[0], 2)


class Units(unittest.TestCase):
    def test_id_sorting(self):
        self.assertEqual([e["id"] for e in sort_by_id([{"id": "F10"}, {"id": "F2"}, {"id": "B1"}])], ["B1", "F2", "F10"])
        self.assertLess(id_key("F2"), id_key("F10"))

    def test_id_allocator_continues_after_max(self):
        a = IdAllocator()
        a.reserve("F3")
        a.reserve("F10")
        self.assertEqual(a.new("F"), "F11")
        self.assertEqual(a.new("F"), "F12")
        self.assertEqual(a.new("S"), "S1")

    def test_input_edges_and_inherit(self):
        with Workdir() as w:
            p = write_json(w.path("i.json"), frames({"tick": 1, "interact": True}, {"tick": 2, "move": [1, 1]}, {"tick": 3, "interact": False}, {"tick": 4, "interact": True}))
            pl = InputPlayer(load_frames(p))
            self.assertFalse(pl.advance(0).pressed("interact"))
            self.assertTrue(pl.advance(1).pressed("interact"))
            s2 = pl.advance(2)
            self.assertFalse(s2.pressed("interact"), "giữ true không lặp lại")
            self.assertAlmostEqual(s2.move[0] ** 2 + s2.move[1] ** 2, 1.0)
            pl.advance(3)
            self.assertTrue(pl.advance(4).pressed("interact"))
            self.assertEqual(pl.advance(5).move, s2.move, "move giữ giá trị cũ khi vắng frame")

    def test_bad_frames_raise(self):
        with Workdir() as w:
            with self.assertRaises(BadInput):
                load_frames(write_json(w.path("i.json"), frames({"tick": 0, "move": [2, 0]})))


if __name__ == "__main__":
    unittest.main()
