"""Buổi sáng — Đi Ghe. KHUNG: chèo xuồng, chặn mép, đồng hồ, cập bến, xuất kho.

Đã làm sẵn để smoke test chạy được: di chuyển + tăng/giảm tốc, chặn mép nước, hết giờ, cập bến.
Nhóm viết tiếp (đúng thứ tự trong PRD-0 mục F, River):
  TODO(nhóm, lát 1): hái nút (gather, hold_full, node_regrown), khoang và LIFO.
  TODO(nhóm, lát 2): quăng chài (net_cast, fish_caught, overflow), xoáy và lật xuồng (capsize),
                     hết phao -> river_end(capsized).
"""

import math

from ..inventory import hold_to_items

TICK = 60.0


class RiverSim:
    mode = "river"
    phase = "river"

    def __init__(self, tuning, scenario, streams, ids):
        t = tuning["river"]
        self.t = t
        self.rng = streams
        self.ids = ids
        p = scenario.get("player", {})
        self.pos = list(p.get("pos", t["start_pos"]))
        self.vel = list(p.get("vel", [0.0, 0.0]))
        self.heading = float(p.get("heading_deg", t["start_heading_deg"]))
        self.floats = p.get("floats", t["floats"])
        self.invuln_ticks = p.get("invuln_ticks", 0)
        self.net_cd_ticks = p.get("net_cd_ticks", 0)
        self.hold = list(scenario.get("hold", []))  # thứ tự nhặt, cuối mảng là mới nhất
        self.time_left_ticks = scenario.get("time_left_ticks", t["duration_s"] * 60)
        # TODO(nhóm): nút hái mặc định của màn (id N1, N2, …), bầy cá và xoáy mặc định theo PRD-0.
        self.nodes = [dict(n, regrow_ticks=n.get("regrow_ticks", 0)) for n in scenario.get("nodes", [])]
        self.fish = [dict(f, heading_deg=f.get("heading_deg", 0)) for f in scenario.get("fish", [])]
        self.vortices = [dict(v) for v in scenario.get("vortices", [])]
        for coll in (self.nodes, self.fish, self.vortices):
            for e in coll:
                ids.reserve(e["id"])
        self.money = 0
        self.earned = 0
        self.reputation = tuning["quan"]["reputation_initial"]
        self.done = False
        self.reason = None

    # --- giao diện cho runner -------------------------------------------------
    def inventory_items(self) -> dict:
        return hold_to_items(self.hold)

    def snapshot(self) -> dict:
        return {
            "player": {"pos": self.pos, "vel": self.vel, "heading_deg": self.heading,
                       "floats": self.floats, "invuln_ticks": self.invuln_ticks,
                       "net_cd_ticks": self.net_cd_ticks},
            "hold": self.hold, "hold_count": len(self.hold),
            "hold_capacity": self.t["hold_capacity"],
            "nodes": [{"id": n["id"], "pos": n["pos"], "kind": n["kind"],
                       "ready": n["regrow_ticks"] == 0, "regrow_ticks": n["regrow_ticks"]} for n in self._sorted(self.nodes)],
            "fish": [{"id": f["id"], "pos": f["pos"], "kind": f["kind"], "heading_deg": f["heading_deg"]}
                     for f in self._sorted(self.fish)],
            "vortices": [{"id": v["id"], "pos": v["pos"]} for v in self._sorted(self.vortices)],
        }

    @staticmethod
    def _sorted(coll):
        from ..ids import sort_by_id
        return sort_by_id(coll)

    # --- một bước ---------------------------------------------------------------
    def step(self, inp):
        events = []
        # 1. giảm bộ đếm
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        self.invuln_ticks = max(0, self.invuln_ticks - 1)
        self.net_cd_ticks = max(0, self.net_cd_ticks - 1)
        for n in self.nodes:
            if n["regrow_ticks"] > 0:
                n["regrow_ticks"] -= 1
                if n["regrow_ticks"] == 0:
                    events.append(("node_regrown", {"node_id": n["id"]}))
        # 2. chèo + chặn mép
        self._move(inp)
        # TODO(nhóm): lực hút xoáy tại vị trí đầu bước; xét lật tại vị trí mới (capsize, LIFO, đẩy ra, bất tử).
        # 3. interact: bến trước, rồi hái
        if inp.pressed("interact"):
            if self._in_dock():
                self._finish("docked", events)
                return events
            # TODO(nhóm): hái nút sẵn sàng gần nhất (gather / hold_full).
        # 4. TODO(nhóm): quăng chài (net_cast, fish_caught, overflow).
        # 5. hết giờ
        if self.time_left_ticks <= 0:
            self._finish("time", events)
        return events

    def _in_dock(self) -> bool:
        d = math.dist(self.pos, self.t["dock_pos"])
        return d <= self.t["dock_radius"]

    def _finish(self, reason, events):
        self.done = True
        self.reason = reason
        events.append(("river_end", {"reason": reason, "inventory": {"items": self.inventory_items()}}))

    def _move(self, inp):
        speed = self.t["xuong_speed"]
        ramp = max(1, self.t["ramp_max_ticks"])
        mx, mz = inp.move
        target = (mx * speed, mz * speed)
        step = speed / ramp
        for i in (0, 1):
            diff = target[i] - self.vel[i]
            self.vel[i] += max(-step, min(step, diff))
        if (mx, mz) != (0.0, 0.0):
            self.heading = math.degrees(math.atan2(mz, mx)) % 360
        b = self.t["bounds"]
        for i, axis in enumerate(("x", "z")):
            self.pos[i] += self.vel[i] / TICK
            lo, hi = b[axis]
            if self.pos[i] < lo:
                self.pos[i] = lo
                self.vel[i] = max(0.0, self.vel[i])
            elif self.pos[i] > hi:
                self.pos[i] = hi
                self.vel[i] = min(0.0, self.vel[i])
