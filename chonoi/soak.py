"""Soak headless (TICKET-04 mục 2): chạy N Ngày trong MỘT tiến trình bằng bot tất định.

Dùng: python3 -m chonoi.soak --seed 7 --days 10 --out soak.json
  - Mỗi Ngày đi qua gather -> quan -> shop (Session mode day, cùng lớp sim với headless).
  - Kế hoạch D1–D5 lặp ở Ngày 6–10. Tiền, earned, uy tín, cấp nâng cấp, số Ngày và id cá thể
    chạy liên tục vì cả lượt dùng một Session (một IdAllocator, một Streams).
  - Bot: gather bơi tới nút hái gần bến nhất, hái một lần, về bến và cập bến (giỏ có hàng thật để thử
    bàn giao kho); quán đứng yên; shop bấm shop_done.
    ponytail: bot không nấu/bưng nên earned = 0; muốn soak cả luồng tiền thì thêm bot quán.
  - soak.json: days, days_completed, crashes, results[{day, earned, reputation, score}] lúc Shop đóng,
    duration_s (đồng hồ thật, chỉ để báo cáo; các trường còn lại tất định theo seed).
Mã thoát: 0 khi days_completed == days và crashes == 0; 1 nếu không; 2 khi cờ/dữ liệu sai.
"""

import argparse
import json
import math
import sys
import time

from .contract import load_contract
from .errors import BadInput
from .inputs import InputState
from .runner import Session

DAY_TICK_LIMIT = 22_200  # một Ngày không pause dài tối đa 22.200 tick (TICKET-02)


class Bot:
    """Sinh InputState tất định từ trạng thái sim hiện tại (chỉ đọc, không đổi sim)."""

    def __init__(self, tuning):
        self.dock = tuning["gather"]["dock_pos"]
        self._held = False  # để tạo cạnh lên: bấm 1 tick, nhả 1 tick
        self._target = ...  # id nút định hái trong Ngày; ... = chưa chọn, None = xong / không có nút

    def new_day(self):
        self._target = ...  # chọn lại ở tick gather đầu tiên

    def _press(self, name, move=(0.0, 0.0)):
        if self._held:
            self._held = False
            return InputState(move, set(), set())
        self._held = True
        return InputState(move, {name}, {name})

    def _go(self, pos, target):
        dx, dd = target[0] - pos[0], target[1] - pos[1]
        n = math.hypot(dx, dd)
        return (dx / n, dd / n) if n > 1e-9 else (0.0, 0.0)

    def act(self, sim):
        if sim.phase == "shop":
            return self._press("shop_done")
        if sim.phase != "gather":
            return InputState((0.0, 0.0), set(), set())
        pos = sim.pos
        if self._target is ...:  # đầu Ngày: nút sẵn sàng gần bến nhất (hòa theo id)
            ready = [n for n in sim.nodes if n["regrow_ticks"] == 0]
            self._target = min(ready, key=lambda n: (math.dist(self.dock, n["pos"]), n["id"]))["id"] if ready else None
        node = next((n for n in sim.nodes if n["id"] == self._target), None)
        if node is not None and node["regrow_ticks"] == 0 and len(sim.hold) < sim.t["hold_capacity"]:
            if math.dist(pos, node["pos"]) <= 1.0:
                return self._press("interact")
            return InputState(self._go(pos, node["pos"]), set(), set())
        self._target = None  # đã hái (nút đang mọc lại) hoặc giỏ đầy: về bến
        if math.dist(pos, self.dock) <= 1.0:
            return self._press("interact")
        return InputState(self._go(pos, self.dock), set(), set())


def soak(seed, days):
    tuning = load_contract()["tuning"]
    plans_per_cycle = len(tuning["day_plan"])
    sess = Session("day", tuning, {}, seed, days=min(days, plans_per_cycle))
    sess.days = days
    # Kế hoạch D1–D5 lặp ở Ngày 6..N (Session chỉ dựng sẵn D1–D5)
    sess.plans = {d: sess.plans[(d - 1) % plans_per_cycle + 1] for d in range(1, days + 1)}
    bot, results, crashes = Bot(tuning), [], 0
    limit = days * DAY_TICK_LIMIT + 10
    try:
        while not sess.done and sess.tick < limit:
            phase = sess.sim.phase
            rows = sess.step(bot.act(sess.sim))
            for r in rows:
                if r["name"] == "shop_end":
                    s = sess.snapshot()
                    results.append({"day": r["day"], "earned": s["earned"], "reputation": s["reputation"],
                                    "score": s["score"]})
                    bot.new_day()
            if phase != sess.sim.phase and sess.sim.phase == "gather":
                bot.new_day()
    except Exception as e:  # soak đếm sự cố thay vì dừng im lặng
        crashes += 1
        sys.stderr.write(f"soak: lỗi ở tick {sess.tick}, Ngày {getattr(sess, 'day', '?')}: {e!r}\n")
    return {"days": days, "days_completed": sess.days_completed, "crashes": crashes, "results": results}


def main(argv=None):
    p = argparse.ArgumentParser(prog="chonoi.soak")
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--days", type=int, required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    if a.days < 1:
        sys.stderr.write("đầu vào sai: --days phải >= 1\n")
        return 2
    start = time.perf_counter()
    try:
        report = soak(a.seed, a.days)
    except BadInput as e:
        sys.stderr.write(f"đầu vào sai: {e}\n")
        return 2
    report["duration_s"] = round(time.perf_counter() - start, 3)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    ok = report["days_completed"] == report["days"] and report["crashes"] == 0
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
