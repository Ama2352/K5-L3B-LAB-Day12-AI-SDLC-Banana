"""Soak headless (TICKET-04 mục 2): N Ngày một tiến trình, kế hoạch lặp sau D5, soak.json tất định."""

import json
import subprocess
import sys
import unittest

from helpers import ROOT, Workdir


def soak(w, days, seed=7, name="soak.json"):
    p = subprocess.run([sys.executable, "-m", "chonoi.soak", "--seed", str(seed), "--days", str(days),
                        "--out", w.path(name)], cwd=ROOT, capture_output=True, text=True)
    if p.returncode == 2:
        return 2, None
    with open(w.path(name), encoding="utf-8") as f:
        return p.returncode, json.load(f)


class Soak(unittest.TestCase):
    def test_6_ngay_qua_ke_hoach_lap_lai_khong_loi(self):
        with Workdir() as w:
            code, r = soak(w, 6)
            self.assertEqual(code, 0, r)
            self.assertEqual(set(r), {"days", "days_completed", "crashes", "results", "duration_s"})
            self.assertEqual((r["days"], r["days_completed"], r["crashes"]), (6, 6, 0))
            self.assertEqual([x["day"] for x in r["results"]], [1, 2, 3, 4, 5, 6])
            self.assertEqual(set(r["results"][0]), {"day", "earned", "reputation", "score"})

    def test_cung_seed_giong_nhau_tru_thoi_gian(self):
        with Workdir() as w:
            a, b = soak(w, 2, name="a.json")[1], soak(w, 2, name="b.json")[1]
            a.pop("duration_s"), b.pop("duration_s")
            self.assertEqual(a, b)

    def test_days_khong_hop_le_ma_2(self):
        with Workdir() as w:
            self.assertEqual(soak(w, 0)[0], 2)


if __name__ == "__main__":
    unittest.main()
