"""Test cửa sổ chơi trực tiếp (chonoi.live). Chỉ dành cho starter Python: nhóm đổi ngôn ngữ thì xóa file này."""

import json
import time
import unittest
import urllib.error
import urllib.request

from chonoi.contract import load_contract
from chonoi.live import LiveGame, LiveServer


def _get(url):
    with urllib.request.urlopen(url, timeout=5) as r:
        return r.status, r.read()


def _post(url, obj):
    req = urllib.request.Request(url, data=json.dumps(obj).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status
    except urllib.error.HTTPError as e:
        e.close()
        return e.code


class LiveServerTest(unittest.TestCase):
    def test_state_input_and_clean_stop(self):
        tuning = load_contract()["tuning"]
        server = LiveServer(LiveGame("gather", tuning, {}, 1), port=0)  # cổng ngẫu nhiên
        server.start()
        try:
            base = f"http://127.0.0.1:{server.port}"
            code, body = _get(base + "/state")
            self.assertEqual(code, 200)
            st = json.loads(body)
            self.assertIn("tick", st)
            self.assertEqual(st["mode"], "gather")
            self.assertEqual(st["player"]["pos"], [2, 0])
            self.assertEqual(_post(base + "/input", {"move": [1, 0], "interact": False, "catch": False}), 200)
            self.assertEqual(_post(base + "/input", {"move": [5, 0]}), 400)
            code, html = _get(base + "/")
            self.assertEqual(code, 200)
            self.assertIn(b"<canvas", html)
            deadline = time.time() + 3
            while time.time() < deadline:
                st2 = json.loads(_get(base + "/state")[1])
                if st2["tick"] > st["tick"] + 3 and st2["player"]["pos"][0] > st["player"]["pos"][0]:
                    break
                time.sleep(0.05)
            self.assertGreater(st2["tick"], st["tick"], "mô phỏng phải chạy nền")
            self.assertGreater(st2["player"]["pos"][0], st["player"]["pos"][0], "input phải tác động tới sim")
        finally:
            server.stop()
        self.assertFalse(server.game._thread.is_alive())
        self.assertFalse(server._thread.is_alive())


    def test_day_screens_freeze_ticks_and_drop_input_before_shop(self):
        tuning = load_contract()["tuning"]
        scenario = {
            "gather": {"time_left_ticks": 1},
            "quan": {"time_left_ticks": 1},
        }
        game = LiveGame("day", tuning, scenario, 42, guided=True)

        def state():
            return json.loads(game.state_json())

        game._tick_once()
        self.assertEqual((state()["screen"], state()["sim_tick"]), ("menu", 0))
        game.present("play")
        game._tick_once()
        self.assertEqual((state()["screen"], state()["sim_tick"]), ("day_intro", 0))
        game.present("continue")
        game._tick_once()

        self.assertEqual((state()["screen"], state()["phase"]), ("evening_intro", "quan"))
        self.assertEqual(state()["evening"], {"stock": {}, "dishes": []})
        game._tick_once()
        self.assertEqual(state()["sim_tick"], 1)
        game.present("continue")
        game._tick_once()

        self.assertEqual((state()["screen"], state()["phase"]), ("day_result", "shop"))
        game.set_input({"shop_done": True})
        game._tick_once()
        self.assertEqual(state()["sim_tick"], 2)
        game.present("continue")
        game._tick_once()
        self.assertEqual((state()["screen"], state()["phase"]), ("playing", "shop"))

        game.set_input({"shop_done": True})
        game._tick_once()
        self.assertEqual((state()["screen"], state()["days_completed"]), ("summary", 1))
        self.assertEqual(state()["reason"], "days_complete")


if __name__ == "__main__":
    unittest.main()
