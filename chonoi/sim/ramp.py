"""Tăng/giảm tốc tuyến tính: từ lúc ĐỔI input, vận tốc chạm mục tiêu sau tối đa `ramp` tick (PRD-0, ramp_max_ticks).
`ramp = 0` nghĩa là áp ngay trong bước đầu. Dùng chung cho gather và quan."""


def ramp_velocity(sim, target, ramp):
    """Trả vận tốc mới. Lưu trạng thái trên `sim` (_tgt, _ramp_left)."""
    target = tuple(float(c) for c in target)
    if target != sim._tgt:
        sim._tgt = target
        sim._ramp_left = max(0, int(ramp))
    if sim._ramp_left <= 1:
        sim._ramp_left = 0
        return list(target)
    out = [v + (t - v) / sim._ramp_left for v, t in zip(sim.vel, target)]
    sim._ramp_left -= 1
    return out
