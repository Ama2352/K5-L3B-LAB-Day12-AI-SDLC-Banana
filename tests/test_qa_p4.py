"""Test QA Phase 4 (TV6) — TICKET-04 "Phát hành v1.0.0", Test Contract v1.3.
Viết TỪ ĐỀ, hộp đen qua lệnh khai trong game.contract.json (bench_cmd, soak_cmd, headless_cmd, run_cmd).
Mỗi test gắn mã AC-P4-xx (docs/verification/phase-4.md).

Phần không tự động hóa được (kiểm tay, ghi ở phase-4.md): chơi thử 3 cảnh báo ở chế độ tương phản cao,
clone sạch chạy ≤ 3 lệnh, GitHub Release v1.0.0 + bản đóng gói, retro, phản tư cá nhân.
Mốc FPS (avg ≥ 60, 1% low ≥ 30, load ≤ 10 s) chỉ để BÁO CÁO, không assert (đề: "dùng để báo cáo").

Chạy: PYTHONPATH=tests:. python3 -m unittest tests.test_qa_p4 -v
"""

import json
import math
import os
import shlex
import subprocess
import unittest

from helpers import ROOT, Workdir, events, read_jsonl, run_headless

with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as _f:
    CONTRACT = json.load(_f)
EXT = set(CONTRACT.get("extensions") or [])
BENCH_FIELDS = {"avg_fps", "p1_low_fps", "frames", "measured_s", "load_ms"}
SOAK_FIELDS = {"days", "days_completed", "crashes", "results", "duration_s"}


def run_cmd_key(key, *args, timeout=600):
    """Chạy `<CONTRACT[key]> <args>` từ gốc repo; trả (mã thoát, stdout+stderr)."""
    cmd = CONTRACT.get(key)
    if not isinstance(cmd, str) or not cmd.strip():
        raise AssertionError(f"game.contract.json thiếu {key}")
    p = subprocess.run([*shlex.split(cmd), *map(str, args)], cwd=ROOT, capture_output=True, text=True,
                       timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ============================================================ AC-P4-01 Manifest v1.3
class Manifest(unittest.TestCase):
    def test_ac_p4_01_contract_version_1_3(self):
        self.assertEqual(CONTRACT["contract_version"], "1.3")

    def test_ac_p4_01_khai_bench_cmd_va_soak_cmd_o_goc(self):
        for key in ("bench_cmd", "soak_cmd", "headless_cmd", "run_cmd", "build_cmd"):
            with self.subTest(key=key):
                self.assertIsInstance(CONTRACT.get(key), str, key)
                self.assertTrue(CONTRACT[key].strip(), key)

    def test_ac_p4_01_gameplay_tuning_kho_theo_v1_2(self):
        self.assertEqual(CONTRACT["tuning"].get("freshness"),
                         {"initial": 100, "gather_decay_per_s": 0.5, "quan_decay_per_s": 0.25, "spoiled_below": 30})
        with Workdir() as w:
            p = os.path.join(w.path("old.json"))
            with open(p, "w", encoding="utf-8") as f:
                json.dump({"items": {"ca_loc": 1}}, f)
            code, _ = run_headless("--mode", "quan", "--seed", "1", "--inventory", p, "--ticks", "0",
                                   "--out", w.path("q.jsonl"))
            self.assertEqual(code, 2, "v1.3 giữ kho cá thể v1.2: kho đếm → mã 2")


# ============================================================ AC-P4-02 Soak headless
class Soak(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w = Workdir().__enter__()
        cls.out = [cls.w.path("soak1.json"), cls.w.path("soak2.json")]
        try:
            cls.codes = [run_cmd_key("soak_cmd", "--seed", 7, "--days", 10, "--out", o) for o in cls.out]
            cls.err = None
        except AssertionError as e:  # chưa khai soak_cmd → báo FAIL rõ ràng ở từng test
            cls.err = str(e)

    def setUp(self):
        if self.err:
            self.fail(self.err)

    @classmethod
    def tearDownClass(cls):
        cls.w.__exit__()

    def test_ac_p4_02_chay_dat_va_dung_cau_truc(self):
        code, log = self.codes[0]
        self.assertEqual(code, 0, log)
        s = load(self.out[0])
        self.assertEqual(set(s), SOAK_FIELDS)
        self.assertEqual((s["days"], s["days_completed"], s["crashes"]), (10, 10, 0), "đạt khi days_completed = days, crashes = 0")
        self.assertIsInstance(s["duration_s"], (int, float))

    def test_ac_p4_02_results_moi_ngay_luc_shop_dong(self):
        s = load(self.out[0])
        self.assertEqual([r["day"] for r in s["results"]], list(range(1, 11)))
        prev = 0
        for r in s["results"]:
            self.assertEqual(set(r), {"day", "earned", "reputation", "score"}, r)
            self.assertEqual(r["score"], r["earned"] + 100 * math.floor(r["reputation"]), r)
            self.assertGreaterEqual(r["earned"], prev, "earned là tổng thu, tiếp tục xuyên Ngày")
            self.assertTrue(0 <= r["reputation"] <= 5, r)
            prev = r["earned"]

    def test_ac_p4_02_tat_dinh_bo_qua_thoi_gian_thuc(self):
        a, b = (load(p) for p in self.out)
        for s in (a, b):
            s.pop("duration_s")
        self.assertEqual(a, b, "cùng seed → các trường gameplay giống nhau")


# ============================================================ AC-P4-03 Benchmark có render
class Bench(unittest.TestCase):
    """Chạy ngắn (--duration 3) để kiểm cấu trúc; số đo 30 s thật lưu ở docs/proof/phase-4/bench.json."""

    @classmethod
    def setUpClass(cls):
        cls.w = Workdir().__enter__()
        cls.path = cls.w.path("bench.json")
        try:
            cls.code, cls.log = run_cmd_key("bench_cmd", "--seed", 42, "--duration", 3, "--out", cls.path, timeout=300)
            cls.err = None
        except AssertionError as e:  # chưa khai bench_cmd → báo FAIL rõ ràng ở từng test
            cls.err = str(e)

    def setUp(self):
        if self.err:
            self.fail(self.err)

    @classmethod
    def tearDownClass(cls):
        cls.w.__exit__()

    def test_ac_p4_03_tao_bench_json_dung_5_truong(self):
        self.assertEqual(self.code, 0, self.log)
        b = load(self.path)
        self.assertEqual(set(b), BENCH_FIELDS)
        for k in BENCH_FIELDS:
            self.assertIsInstance(b[k], (int, float), k)
            self.assertFalse(isinstance(b[k], bool), k)

    def test_ac_p4_03_cong_thuc_va_mien_gia_tri(self):
        b = load(self.path)
        self.assertGreaterEqual(b["frames"], 1)
        self.assertGreater(b["measured_s"], 0)
        self.assertAlmostEqual(b["measured_s"], 3, delta=1.0, msg="số giây đo thực tế sau làm nóng")
        self.assertAlmostEqual(b["avg_fps"], b["frames"] / b["measured_s"], delta=max(0.5, 0.01 * b["avg_fps"]),
                               msg="avg_fps = frames / measured_s")
        self.assertGreater(b["p1_low_fps"], 0)
        self.assertLessEqual(b["p1_low_fps"], b["avg_fps"] + 1e-6, "1% low không vượt trung bình")
        self.assertGreaterEqual(b["load_ms"], 0)


# ============================================================ AC-P4-04 Tài liệu phát hành (kiểm tĩnh)
class ReleaseDocs(unittest.TestCase):
    def read(self, name):
        p = os.path.join(ROOT, name)
        self.assertTrue(os.path.exists(p), f"thiếu {name}")
        with open(p, encoding="utf-8") as f:
            return f.read()

    def test_ac_p4_04_readme_ghi_lenh_chay_test_headless_bench_soak_dieu_khien(self):
        r = self.read("README.md")
        for key in ("run_cmd", "headless_cmd", "bench_cmd", "soak_cmd"):
            with self.subTest(key=key):
                self.assertTrue(CONTRACT.get(key), f"game.contract.json thiếu {key}")
                self.assertIn(CONTRACT[key].split(" --")[0], r, f"README chưa ghi lệnh {key}")
        self.assertIn("unittest", r, "README chưa ghi lệnh test")
        self.assertTrue(any(k in r for k in ("WASD", "phím", "Phím")), "README chưa ghi điều khiển")

    def test_ac_p4_04_changelog_theo_tung_phase(self):
        c = self.read("CHANGELOG.md")
        for v in ("1.1", "1.2", "1.3"):
            self.assertIn(v, c, f"CHANGELOG thiếu mục v{v}")

    def test_ac_p4_04_co_credits_va_license(self):
        self.read("CREDITS.md")
        self.assertTrue(any(os.path.exists(os.path.join(ROOT, n)) for n in ("LICENSE", "LICENSE.md", "LICENSE.txt")),
                        "thiếu LICENSE")

    def test_ac_p4_04_ghi_chep_bat_buoc(self):
        for name in ("docs/verification/phase-4.md", "docs/retro.md", "docs/clarify.md", "docs/ai-usage-log.md"):
            with self.subTest(name=name):
                self.assertTrue(self.read(name).strip())


# ============================================================ AC-P4-05 Mở rộng leaderboard (chỉ khi khai)
@unittest.skipUnless("leaderboard" in EXT, "nhóm chưa khai mở rộng leaderboard")
class Leaderboard(unittest.TestCase):
    def day5(self, w, store, name, extra=()):
        return run_headless("--mode", "day", "--seed", "42", "--days", "5", "--ticks", "200000",
                            "--out", w.path("d.jsonl"), "--leaderboard", store, "--player-name", name, *extra)

    def export(self, store, out):
        return run_cmd_key("run_cmd", "--export-leaderboard", out, "--leaderboard", store)

    def test_ac_p4_05_ghi_dung_mot_muc_khi_du_5_ngay(self):
        with Workdir() as w:
            store = w.path("lb.json")
            code, err = self.day5(w, store, "Út Sen")
            self.assertEqual(code, 0, err)
            self.assertEqual(read_jsonl(w.path("d.jsonl"))[-1]["reason"], "days_complete")
            code, log = self.export(store, w.path("out.json"))
            self.assertEqual(code, 0, log)
            e = load(w.path("out.json"))["entries"]
            self.assertEqual(len(e), 1)
            self.assertEqual(set(e[0]), {"name", "score", "days_completed", "seed"})
            self.assertEqual((e[0]["name"], e[0]["days_completed"], e[0]["seed"]), ("Út Sen", 5, 42))

    def test_ac_p4_05_thieu_mot_co_hoac_sai_mode_ma_2(self):
        with Workdir() as w:
            store = w.path("lb.json")
            self.assertEqual(run_headless("--mode", "day", "--seed", "1", "--ticks", "0", "--out", w.path("a.jsonl"),
                                          "--leaderboard", store)[0], 2)
            self.assertEqual(run_headless("--mode", "day", "--seed", "1", "--ticks", "0", "--out", w.path("a.jsonl"),
                                          "--player-name", "A")[0], 2)
            self.assertEqual(run_headless("--mode", "gather", "--seed", "1", "--ticks", "0", "--out", w.path("a.jsonl"),
                                          "--leaderboard", store, "--player-name", "A")[0], 2)

    def test_ac_p4_05_khong_ghi_khi_co_scenario_hoac_chua_du_ngay(self):
        with Workdir() as w:
            store = w.path("lb.json")
            sc = w.path("sc.json")
            with open(sc, "w", encoding="utf-8") as f:
                json.dump({"day": {}}, f)
            self.day5(w, store, "A", ("--scenario", sc))
            run_headless("--mode", "day", "--seed", "1", "--days", "1", "--ticks", "30000", "--out", w.path("b.jsonl"),
                         "--leaderboard", store, "--player-name", "B")
            if os.path.exists(store):
                self.export(store, w.path("out.json"))
                self.assertEqual(load(w.path("out.json"))["entries"], [])

    def test_ac_p4_05_khong_doi_jsonl(self):
        with Workdir() as w:
            self.day5(w, w.path("lb.json"), "A")
            with open(w.path("d.jsonl"), "rb") as f:
                with_lb = f.read()
            run_headless("--mode", "day", "--seed", "42", "--days", "5", "--ticks", "200000", "--out", w.path("d.jsonl"))
            with open(w.path("d.jsonl"), "rb") as f:
                self.assertEqual(with_lb, f.read())

    def test_ac_p4_05_sap_diem_giam_hoa_thi_muc_truoc_dung_truoc(self):
        with Workdir() as w:
            store = w.path("lb.json")
            for name in ("A", "B"):  # cùng seed → cùng điểm → hòa: A ghi trước đứng trước
                self.day5(w, store, name)
            self.export(store, w.path("out.json"))
            e = load(w.path("out.json"))["entries"]
            self.assertEqual([x["name"] for x in e], ["A", "B"])
            self.assertEqual(e, sorted(e, key=lambda x: -x["score"]))


if __name__ == "__main__":
    unittest.main()
