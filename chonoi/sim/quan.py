"""Buổi tối — Mở Quán. KHUNG: đi lại, chặn biên, đồng hồ, kho nạp từ file/scenario.

Phần việc của nhóm:
  - TODO(TV3, lát 3): Khách đến theo lịch, chọn món theo seed trong 3 món đủ nguyên liệu.
  - TIẾN ĐỘ TV4 (AnhQuanHANU - Lát 4, Phần 1): Cơ chế Bếp nấu món, bốc món lên tay.
"""

import math

from ..ids import id_key, sort_by_id
from .ramp import ramp_velocity

TICK = 60.0


class QuanSim:
    mode = "quan"
    phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None):
        t = tuning["quan"]
        self.t = t
        self.menu = tuning["menu"]
        self.rng = streams
        self.ids = ids

        p = scenario.get("player", {})
        self.pos = list(p.get("pos", t["start_pos"]))
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0

        # Kho: --inventory HOẶC scenario.stock
        self.stock = dict(inventory if inventory is not None else scenario.get("stock", {}))

        # Hand: payload món {order_id, dish_id, base_price} hoặc None
        raw_hand = scenario.get("hand")
        if isinstance(raw_hand, dict):
            self.hand = dict(raw_hand)
        elif isinstance(raw_hand, str):
            self.hand = {
                "order_id": "C1",
                "dish_id": raw_hand,
                "base_price": self.menu.get(raw_hand, {}).get("price", 0)
            }
        else:
            self.hand = None

        self.time_left_ticks = scenario.get("time_left_ticks", int(round(t["duration_s"] * 60)))
        self.reputation = float(scenario.get("reputation", t["reputation_initial"]))

        # Bếp (stoves)
        self.stoves = [
            dict(
                s,
                state=s.get("state", "idle"),
                dish=s.get("dish"),
                order_id=s.get("order_id"),
                base_price=s.get("base_price"),
                cook_ticks_left=s.get("cook_ticks_left", 0),
                ready_ticks=s.get("ready_ticks", 0)
            )
            for s in self._merge(t["stoves"], scenario.get("stoves", []))
        ]
        self.tables = self._merge(t["tables"], scenario.get("tables", []))

        # Khách (customers)
        patience_max = int(round(t["patience_s"] * TICK))
        self.customers = []
        for c in scenario.get("customers", []):
            dish_id = c.get("dish_id")
            base_price = c.get("base_price")
            if base_price is None and dish_id and dish_id in self.menu:
                base_price = self.menu[dish_id]["price"]

            cust = {
                "id": c["id"],
                "table_id": c["table_id"],
                "dish_id": dish_id,
                "order_tick": c.get("order_tick", 0),
                "state": c.get("state", "waiting"),
                "patience_ticks_left": c.get("patience_ticks_left", patience_max),
                "eat_ticks_left": c.get("eat_ticks_left", 0),
                "order_status": c.get("order_status", "reserved"),
                "reserved": dict(c.get("reserved", {})),
                "base_price": base_price if base_price is not None else 0,
                "tip": c.get("tip", 0),
            }
            if cust["order_status"] == "reserved" and not cust["reserved"] and dish_id and dish_id in self.menu:
                cust["reserved"] = dict(self.menu[dish_id]["recipe"])
            self.customers.append(cust)
            ids.reserve(c["id"])

        for s in self.stoves:
            if s["dish"] and not s.get("order_id"):
                for c in self.customers:
                    if c.get("dish_id") == s["dish"] and c.get("order_status") in ("assigned", "served"):
                        s["order_id"] = c["id"]
                        s["base_price"] = c.get("base_price", self.menu[s["dish"]]["price"])
                        break

        self.money = 0
        self.earned = 0
        self.shift_earned = 0
        self.done = False
        self.reason = None

    @staticmethod
    def _merge(defaults, updates):
        by_id = {d["id"]: dict(d) for d in defaults}
        for u in updates:
            if u["id"] not in by_id:
                from ..errors import BadInput
                raise BadInput(f"id bếp/bàn không tồn tại: {u['id']}")
            by_id[u["id"]].update(u)
        return sort_by_id(list(by_id.values()))

    def snapshot(self) -> dict:
        occupied = {c["table_id"]: c["id"] for c in self.customers}
        return {
            "player": {"pos": self.pos},
            "stock": {k: self.stock[k] for k in sorted(self.stock) if self.stock[k] > 0},
            "hand": self.hand,
            "stoves": [
                {k: s.get(k) for k in ("id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks")}
                for s in sort_by_id(self.stoves)
            ],
            "tables": [
                {"id": tb["id"], "pos": tb["pos"], "customer_id": occupied.get(tb["id"])}
                for tb in sort_by_id(self.tables)
            ],
            "customers": sort_by_id(self.customers),
        }

    def step(self, inp):
        events = []

        # 1. Đồng hồ, nấu nướng
        self.time_left_ticks = max(0, self.time_left_ticks - 1)

        ready_at_start = {s["id"] for s in self.stoves if s["state"] == "ready"}
        for s in self.stoves:
            if s["id"] in ready_at_start:
                s["ready_ticks"] += 1
            elif s["state"] == "cooking":
                s["cook_ticks_left"] -= 1

        for c in self.customers:
            if c["state"] == "eating":
                c["eat_ticks_left"] = max(0, c["eat_ticks_left"] - 1)
            elif c["state"] == "waiting":
                c["patience_ticks_left"] = max(0, c["patience_ticks_left"] - 1)

        # 2. Bếp nấu xong chuyển ready
        for s in sort_by_id(self.stoves):
            if s["state"] == "cooking" and s["cook_ticks_left"] <= 0:
                s["state"] = "ready"
                s["cook_ticks_left"] = 0
                s["ready_ticks"] = 0
                events.append((
                    "dish_ready",
                    {"stove_id": s["id"], "order_id": s["order_id"], "dish_id": s["dish"]}
                ))

        # 3. Di chuyển
        self._move(inp)

        # 4. Interact tại Bếp
        if inp.pressed("interact"):
            self._handle_interact(events)

        if self.time_left_ticks <= 0:
            self.done = True
            self.reason = "time"
            events.append(("quan_end", {
                "reason": "time", "money": self.money, "earned": self.earned,
                "shift_earned": self.shift_earned, "reputation": self.reputation
            }))

        return events

    def _handle_interact(self, events):
        radius = float(self.t["interact_radius"])
        candidates = []
        for s in sort_by_id(self.stoves):
            d = math.dist(self.pos, s["pos"])
            if d <= radius:
                candidates.append((d, 0, id_key(s["id"]), "stove", s))

        if not candidates:
            return

        candidates.sort(key=lambda item: (item[0], item[1], item[2]))
        best = candidates[0]
        if best[3] == "stove":
            self._interact_stove(best[4], events)

    def _interact_stove(self, stove, events):
        if stove["state"] == "idle":
            reserved_candidates = [
                c for c in self.customers
                if c.get("order_status") == "reserved" and c.get("state") == "waiting"
            ]
            if not reserved_candidates:
                return

            reserved_candidates.sort(key=lambda c: (c.get("order_tick", 0), id_key(c["table_id"])))
            target_cust = reserved_candidates[0]
            dish_id = target_cust["dish_id"]
            if not dish_id or dish_id not in self.menu:
                return

            recipe = self.menu[dish_id]["recipe"]
            for kind, qty in recipe.items():
                self.stock[kind] = self.stock.get(kind, 0) - qty
                if self.stock[kind] <= 0:
                    del self.stock[kind]

            target_cust["reserved"] = {}
            target_cust["order_status"] = "assigned"
            base_price = target_cust.get("base_price", self.menu[dish_id]["price"])

            stove["state"] = "cooking"
            stove["dish"] = dish_id
            stove["order_id"] = target_cust["id"]
            stove["base_price"] = base_price
            stove["cook_ticks_left"] = int(round(self.menu[dish_id]["cook_s"] * TICK))
            stove["ready_ticks"] = 0

            items = []
            for kind in sorted(recipe.keys()):
                items.extend([kind] * recipe[kind])

            events.append((
                "cook_started",
                {
                    "stove_id": stove["id"],
                    "order_id": target_cust["id"],
                    "dish_id": dish_id,
                    "items": items,
                    "base_price": base_price
                }
            ))

        elif stove["state"] == "ready":
            if self.hand is None:
                self.hand = {
                    "order_id": stove["order_id"],
                    "dish_id": stove["dish"],
                    "base_price": stove["base_price"]
                }
                events.append((
                    "dish_picked",
                    {
                        "stove_id": stove["id"],
                        "order_id": stove["order_id"],
                        "dish_id": stove["dish"]
                    }
                ))
                stove["state"] = "idle"
                stove["dish"] = None
                stove["order_id"] = None
                stove["base_price"] = None
                stove["cook_ticks_left"] = 0
                stove["ready_ticks"] = 0

    def _move(self, inp):
        speed = self.t["walk_speed"]
        mx, mz = inp.move
        self.vel = ramp_velocity(self, (mx * speed, mz * speed), int(self.t.get("ramp_max_ticks", 6)))
        b = self.t["bounds"]
        for i, axis in enumerate(("x", "z")):
            self.pos[i] += self.vel[i] / TICK
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i], self.vel[i] = lo, max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i], self.vel[i] = hi, min(0.0, self.vel[i])
