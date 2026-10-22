from constants import (
    BIG, BIG_PUNCH_HOLD, BIG_RANGE, BIG_RANGE_GROWTH, BIG_RANGE_MAX, MID, MID_PUNCH_HOLD,
    MID_RANGE, MIN_RANGE, NORMAL, PUNCH_COST, PUNCH_KINDS,
)


def kind_for_hold(hold):
    """長押ししたフレーム数から、スタミナを考えないときのパンチの種類を返す"""
    if hold >= BIG_PUNCH_HOLD:
        return BIG
    if hold >= MID_PUNCH_HOLD:
        return MID
    return NORMAL


def affordable_kind(hold, stamina):
    """長押ししたフレーム数とスタミナから実際に出るパンチの種類を返す。出せないときはNone"""
    index = PUNCH_KINDS.index(kind_for_hold(hold))
    while index >= 0 and stamina < PUNCH_COST[PUNCH_KINDS[index]]:
        index -= 1
    if index < 0:
        return None
    return PUNCH_KINDS[index]


def punch_range(kind, hold):
    """パンチの種類と長押ししたフレーム数から射程を返す"""
    if kind == BIG:
        return min(BIG_RANGE + max(0, hold - BIG_PUNCH_HOLD) * BIG_RANGE_GROWTH, BIG_RANGE_MAX)
    if kind == MID:
        return MID_RANGE
    return MIN_RANGE
