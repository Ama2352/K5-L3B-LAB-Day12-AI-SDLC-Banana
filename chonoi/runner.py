"""Vòng tick (Contract B, mô hình tick). KHUNG — thường không cần sửa.

Thứ tự ghi: snapshot tick 0 -> với mỗi bước: sự kiện (theo thứ tự xử lý) rồi snapshot (nếu tới lượt
hoặc buổi kết thúc) -> dòng 'end'. Mỗi tick tối đa một snapshot.
"""

import math

from .ids import IdAllocator
from .inputs import InputPlayer
from .inventory import write_inventory
from .jsonl import JsonlWriter
from .rng import Streams
from .sim.quan import QuanSim
from .sim.river import RiverSim


def build_sim(mode, tuning, scenario, seed, inventory):
    streams, ids = Streams(seed), IdAllocator()
    if mode == "river":
        return RiverSim(tuning, scenario, streams, ids)
    return QuanSim(tuning, scenario, streams, ids, inventory=inventory)


def _common(sim, tick, sim_tick, phase_tick, tuning, state):
    mult = tuning["score"]["reputation_multiplier"]
    return {
        "type": "snapshot", "tick": tick, "sim_tick": sim_tick, "mode": sim.mode, "phase": sim.phase,
        "phase_tick": phase_tick, "state": state, "time_left_ticks": sim.time_left_ticks,
        "money": sim.money, "earned": sim.earned, "reputation": sim.reputation,
        "score": sim.earned + mult * math.floor(sim.reputation),
    }


def run(mode, tuning, scenario, seed, frames, ticks, out_path, snapshot_every, inventory=None, inventory_out=None):
    sim = build_sim(mode, tuning, scenario, seed, inventory)
    player = InputPlayer(frames)
    w = JsonlWriter(out_path)
    tick = 0
    try:
        def snap():
            s = _common(sim, tick, tick, tick, tuning, "finished" if sim.done else "playing")
            s.update(sim.snapshot())
            w.write(s)

        snap()  # tick 0: sau khi dựng scenario, trước mọi input
        last_snapped = 0
        while tick < ticks and not sim.done:
            inp = player.advance(tick)  # bước k đọc input có tick == k
            events = sim.step(inp)
            tick += 1  # sự kiện trong bước này mang tick = k + 1
            for name, data in events:
                w.write({"type": "event", "tick": tick, "phase": sim.phase, "name": name, "data": data})
            if tick % snapshot_every == 0 or sim.done:
                snap()
                last_snapped = tick
        if last_snapped != tick:
            snap()
        score = _common(sim, tick, tick, tick, tuning, "")["score"]
        w.write({"type": "end", "ticks": tick, "sim_tick": tick, "mode": sim.mode,
                 "state": "finished" if sim.done else "playing",
                 "reason": sim.reason if sim.done else "tick_limit",
                 "money": sim.money, "earned": sim.earned, "reputation": sim.reputation, "score": score})
    finally:
        w.close()
    # file kho: ghi MỘT lần khi có river_end; chạm --ticks trước đó thì giữ nguyên file đích
    if mode == "river" and sim.done and inventory_out:
        write_inventory(inventory_out, sim.inventory_items())
    return sim
