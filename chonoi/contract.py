"""Đọc game.contract.json và kiểm dải hợp lệ của tuning P1 (xem PRD-0, Test Contract A)."""

import json
import os

from .errors import BadInput

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game.contract.json")


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _between(name, v, lo, hi):
    if not _num(v) or not (lo <= v <= hi):
        raise BadInput(f"tuning.{name} phải trong [{lo}, {hi}], đang là {v!r}")


def load_contract(path=DEFAULT_PATH) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            c = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được {path}: {e}")
    validate_tuning(c.get("tuning"))
    return c


def validate_tuning(t):
    if not isinstance(t, dict):
        raise BadInput("thiếu khối tuning")
    r, q, menu = t.get("river"), t.get("quan"), t.get("menu")
    if not isinstance(r, dict) or not isinstance(q, dict) or not isinstance(menu, dict):
        raise BadInput("tuning phải có river, quan, menu")
    # TODO(nhóm): bổ sung kiểm các khóa còn lại theo dải trong PRD-0 nếu muốn chặt hơn.
    _between("river.duration_s", r.get("duration_s"), 60, 600)
    _between("quan.duration_s", q.get("duration_s"), 60, 600)
    _between("river.hold_capacity", r.get("hold_capacity"), 4, 30)
    _between("quan.patience_s", q.get("patience_s"), 20, 180)
    _between("river.xuong_speed", r.get("xuong_speed"), 1, 10)
    _between("quan.walk_speed", q.get("walk_speed"), 1, 10)
    _between("river.vortex_pull_radius", r.get("vortex_pull_radius"), 2, 15)
    _between("river.vortex_eject_radius", r.get("vortex_eject_radius"), 2, 20)
    _between("river.fish_initial", r.get("fish_initial"), 1, 12)
    w = r.get("fish_weights", {})
    if not w or abs(sum(w.values()) - 1) > 1e-9:
        raise BadInput("river.fish_weights phải có tổng = 1")
    if not (q.get("tip_rate", 0) > 0 and q.get("left_reputation_delta", 0) < 0):
        raise BadInput("tip_rate phải > 0 và left_reputation_delta phải < 0")
    if q.get("burn_s") is not None:
        raise BadInput("burn_s phải là null ở Phase 1")
    for dish_id, d in menu.items():
        if not (d.get("price", 0) > 0 and d.get("cook_s", 0) > 0):
            raise BadInput(f"menu.{dish_id}: price và cook_s phải > 0")
