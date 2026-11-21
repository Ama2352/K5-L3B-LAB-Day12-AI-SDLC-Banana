"""Headless day lifecycle and inventory handoff."""

import math
from copy import deepcopy

from .errors import BadInput
from .ids import IdAllocator
from .rng import Streams
from .sim.gather import GatherSim
from .sim.quan import QuanSim


def day_plans(tuning, overrides):
    if not isinstance(overrides, list):
        raise BadInput("day_plan must be a list")
    plans = {plan["day"]: plan for plan in tuning["day_plan"]}
    seen = set()
    for plan in overrides:
        if not isinstance(plan, dict) or set(plan) - {"day", "dishes", "ingredients"}:
            raise BadInput("invalid day plan")
        day, dishes = plan.get("day"), plan.get("dishes")
        if type(day) is not int or day not in plans or day in seen or not isinstance(dishes, dict) or not dishes:
            raise BadInput("invalid or duplicate plan day")
        ingredients = {}
        for dish, servings in dishes.items():
            if dish not in tuning["menu"] or type(servings) is not int or servings <= 0:
                raise BadInput("invalid dish or serving count")
            for kind, amount in tuning["menu"][dish]["recipe"].items():
                ingredients[kind] = ingredients.get(kind, 0) + amount * servings
        if plan.get("ingredients", ingredients) != ingredients:
            raise BadInput("day plan ingredients do not match the recipes")
        plans[day] = {"day": day, "dishes": dishes, "ingredients": ingredients}
        seen.add(day)
    return plans


class DaySession:
    mode = "day"

    def __init__(self, tuning, scenario, seed, days):
        self.tuning = tuning
        self.scenario = scenario
        self.streams = Streams(seed)
        self.days = days
        self.days_completed = 0
        self.tick = self.sim_tick = self.phase_tick = 0
        self.paused = self.done = False
        config = scenario.get("day", {})
        self.plans = day_plans(tuning, config.get("day_plan", []))
        self.money = config.get("money", 0)
        self.earned = config.get("earned", 0)
        self.reputation = config.get("reputation", tuning["quan"]["reputation_initial"])
        self.upgrades = dict(config.get("upgrades", {}))
        self.pending_events = self._start_day()

    @property
    def day(self):
        return min(self.days_completed + 1, self.days)

    def _start_day(self):
        self.phase = "gather"
        self.phase_tick = 0
        self.active_upgrades = self.upgrades.copy()
        self.plan = self.plans[self.day]
        tuning = deepcopy(self.tuning)
        for name, level in self.active_upgrades.items():
            if level:
                tier = tuning["shop"]["upgrades"][name][level - 1]
                key = {"oxygen": "oxygen_max_s", "hp": "hp_max"}[name]
                tuning["gather"][key] = tier[key]
        self.sim = GatherSim(tuning, self.scenario.get("gather", {}), self.streams, IdAllocator())
        return [self._event("day_start"), self._event("day_plan", {
            key: self.plan[key] for key in ("dishes", "ingredients")
        }), self._event("phase_start")]

    def _event(self, name, data=None):
        return {"type": "event", "tick": self.tick, "phase": self.phase, "day": self.day,
                "name": name, "data": {} if data is None else data}

    def _open_quan(self):
        inventory = self.sim.inventory_items()
        fixture = self.scenario.get("quan", {})
        sim = QuanSim(self.tuning, fixture, self.streams, IdAllocator(), inventory=inventory,
                      planned_dishes=self.plan["dishes"])
        available = inventory.copy()
        for customer in sim.customers:
            if customer["dish_id"] not in self.plan["dishes"]:
                raise BadInput("customer dish is outside the day plan")
            for kind, amount in customer["reserved"].items():
                if type(amount) is not int or amount <= 0 or amount > available.get(kind, 0):
                    raise BadInput("customer reservations exceed day inventory")
                available[kind] -= amount
        for dish in [sim.hand and sim.hand["dish_id"], *(stove["dish"] for stove in sim.stoves)]:
            if dish is not None and dish not in self.plan["dishes"]:
                raise BadInput("prepared dish is outside the day plan")
        self.sim = sim
        sim.money, sim.earned, sim.reputation = self.money, self.earned, self.reputation
        self.phase = "quan"
        self.phase_tick = 0

    def _shop_step(self, inp):
        events = []
        if inp.buy is not None:
            name = inp.buy
            tiers = self.tuning["shop"]["upgrades"].get(name)
            level = self.upgrades.get(name, 0)
            reason = None
            if tiers is None:
                reason = "unknown"
            elif level >= len(tiers):
                reason = "max_level"
            elif self.money < tiers[level]["price"]:
                reason = "funds"
            if reason:
                events.append(self._event("buy_failed", {"action": name, "reason": reason}))
            else:
                price = tiers[level]["price"]
                self.money -= price
                self.upgrades[name] = level + 1
                events.append(self._event("bought", {"upgrade": name, "level": level + 1,
                                                     "price": price, "money": self.money}))
        self.shop_ticks -= 1
        if inp.pressed("shop_done") or not self.shop_ticks:
            events.append(self._event("shop_end", {"reason": "done" if inp.pressed("shop_done") else "time"}))
            self.days_completed += 1
            self.done = self.days_completed == self.days
            if not self.done:
                events.extend(self._start_day())
        return events

    def step(self, inp):
        self.tick += 1
        events = []
        if inp.pressed("pause"):
            self.paused = not self.paused
            events.append(self._event("paused" if self.paused else "resumed"))
        if self.paused:
            return events
        self.sim_tick += 1
        self.phase_tick += 1
        if self.phase == "shop":
            return events + self._shop_step(inp)
        events.extend(self._event(name, data) for name, data in self.sim.step(inp))
        if self.phase == "quan":
            self.money, self.earned, self.reputation = self.sim.money, self.sim.earned, self.sim.reputation
        if self.sim.done:
            if self.phase == "gather":
                self._open_quan()
            else:
                self.phase = "shop"
                self.phase_tick = 0
                self.shop_ticks = self.tuning["shop"]["max_ticks"]
            events.append(self._event("phase_start"))
        return events

    def _totals(self):
        return {"money": self.money, "earned": self.earned, "reputation": self.reputation,
                "score": self.earned + self.tuning["score"]["reputation_multiplier"] * math.floor(self.reputation)}

    def snapshot(self):
        payload = ({"stock": self.sim.snapshot()["stock"], "time_left_ticks": self.shop_ticks}
                   if self.phase == "shop"
                   else {**self.sim.snapshot(), "time_left_ticks": self.sim.time_left_ticks})
        return {"type": "snapshot", "tick": self.tick, "sim_tick": self.sim_tick,
                "phase_tick": self.phase_tick, "mode": self.mode, "phase": self.phase, "day": self.day,
                "state": "finished" if self.done else "paused" if self.paused else "playing",
                "day_plan": self.plan, "upgrades": self.upgrades, "active_upgrades": self.active_upgrades,
                **self._totals(), **payload}

    def end_row(self):
        return {"type": "end", "ticks": self.tick, "sim_tick": self.sim_tick, "mode": self.mode,
                "state": "finished" if self.done else "paused" if self.paused else "playing",
                "reason": "days_complete" if self.done else "tick_limit",
                "days_completed": self.days_completed, **self._totals()}
