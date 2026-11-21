"""Buổi tối — Mở Quán. KHUNG: đi lại, chặn biên, đồng hồ, kho nạp từ file/scenario.

Nhóm viết tiếp (PRD-0 mục F, Quán):
  TODO(nhóm, lát 4): interact tại bếp/bàn (cook_started, dish_ready, dish_picked, served),
                     ăn xong trả tiền (paid), boa, uy tín, hết ca (quan_end).
"""

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
        # kho: --inventory HOẶC scenario.stock (cả hai -> cli đã báo mã 2)
        self.stock = dict(inventory if inventory is not None else scenario.get("stock", {}))
        self.hand = scenario.get("hand")
        self.time_left_ticks = scenario.get("time_left_ticks", int(round(t["duration_s"] * 60)))
        self.reputation = scenario.get("reputation", t["reputation_initial"])
        self.stoves = [dict(s, state=s.get("state", "idle"), dish=s.get("dish"),
                            cook_ticks_left=s.get("cook_ticks_left", 0), ready_ticks=s.get("ready_ticks", 0))
                       for s in self._merge(t["stoves"], scenario.get("stoves", []))]
        self.tables = self._merge(t["tables"], scenario.get("tables", []))
        self.tick = 0
        self.customer_interval = round(t["customer_interval_s"] * tuning["tick_hz"])
        self.patience_ticks = round(t["patience_s"] * tuning["tick_hz"])
        self.random_customers = scenario.get("random_customers", True)
        self.customers = []
        for customer in scenario.get("customers", []):
            state = customer.get("state", "waiting")
            recipe = self.menu.get(customer.get("dish_id"), {}).get("recipe", {})
            reserved = customer.get("reserved", recipe if state == "waiting" else {})
            self.customers.append(dict(customer, state=state, reserved=dict(reserved),
                                       order_tick=customer.get("order_tick", 0),
                                       patience_ticks_left=customer.get("patience_ticks_left", self.patience_ticks)))
        for e in self.customers:
            ids.reserve(e["id"])
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
            "stoves": [{k: s.get(k) for k in ("id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks")}
                       for s in self.stoves],
            "tables": [{"id": tb["id"], "pos": tb["pos"], "customer_id": occupied.get(tb["id"])} for tb in self.tables],
            "customers": sort_by_id(self.customers),
        }

    def step(self, inp):
        events = []
        self.tick += 1
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        # TODO(nhóm): giảm kiên nhẫn / nấu / ăn; bếp chín -> ready; xử lý khách theo thứ tự PRD-0 mục F.
        self._advance_patience()
        self._move(inp)
        # TODO(nhóm): tối đa MỘT interact, chọn đối tượng theo (khoảng cách, bếp trước bàn, id).
        # Resolve payment in table order alongside waiting departures when TV4 is integrated.
        self._resolve_waiting_departures(events)
        if self.time_left_ticks <= 0:
            self.done = True
            self.reason = "time"
            events.append(("quan_end", {"reason": "time", "money": self.money, "earned": self.earned,
                                        "shift_earned": self.shift_earned, "reputation": self.reputation}))
        else:
            self._arrive(events)
        return events

    def _advance_patience(self):
        for customer in self.customers:
            if customer["state"] == "waiting":
                customer["patience_ticks_left"] = max(0, customer["patience_ticks_left"] - 1)

    def _resolve_waiting_departures(self, events):
        for customer in sorted(self.customers, key=lambda c: id_key(c["table_id"])):
            if customer["state"] != "waiting":
                continue
            if self.time_left_ticks == 0:
                reason = "closing"
            elif customer["patience_ticks_left"] == 0:
                reason = "patience"
                reputation = self.reputation + self.t["left_reputation_delta"]
                self.reputation = min(self.t["reputation_max"],
                                      max(self.t["reputation_min"], reputation))
            else:
                continue

            self.customers.remove(customer)
            self._discard_order_dish(customer.get("order_id", customer["id"]))
            events.append(("customer_left", {"customer_id": customer["id"],
                                             "table_id": customer["table_id"],
                                             "reason": reason}))

    def _discard_order_dish(self, order_id):
        for stove in self.stoves:
            dish = stove["dish"]
            if isinstance(dish, dict) and dish.get("order_id") == order_id:
                stove.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)

        if isinstance(self.hand, dict) and self.hand.get("order_id") == order_id:
            self.hand = None

    def _arrive(self, events):
        first = self.t["first_customer_tick"]
        if (not self.random_customers or self.tick < first
                or (self.tick - first) % self.customer_interval):
            return
        occupied = {customer["table_id"] for customer in self.customers}
        table = next((table for table in self.tables if table["id"] not in occupied), None)
        if table is None:
            return

        available = self.stock.copy()
        for customer in self.customers:
            for item, count in customer["reserved"].items():
                available[item] = available.get(item, 0) - count
        dishes = [
            dish_id for dish_id, dish in sorted(self.menu.items())
            if all(available.get(item, 0) >= count for item, count in dish["recipe"].items())
        ]
        if not dishes:
            events.append(("no_dish", {"table_id": table["id"]}))
            return
        dish_id = self.rng.get("customer_order").choice(dishes)
        customer = {
            "id": self.ids.new("C"),
            "table_id": table["id"],
            "dish_id": dish_id,
            "order_tick": self.tick,
            "state": "waiting",
            "patience_ticks_left": self.patience_ticks,
            "reserved": self.menu[dish_id]["recipe"].copy(),
        }
        self.customers.append(customer)
        events.append(("customer_arrived", {"customer_id": customer["id"],
                                            "table_id": table["id"], "dish_id": dish_id}))

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
