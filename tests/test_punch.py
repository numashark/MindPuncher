import unittest

from constants import BIG, BIG_RANGE, BIG_RANGE_GROWTH, MID, MID_RANGE, MID_RANGE_MAX, MIN_RANGE, NORMAL, PUNCH_COST
from punch import affordable_kind, kind_for_hold, punch_range


class TestPunch(unittest.TestCase):
    def test_kind_for_hold(self):
        """15フレーム未満は通常、15～59は中、60以上は大パンチになる"""
        self.assertEqual(kind_for_hold(1), NORMAL)
        self.assertEqual(kind_for_hold(14), NORMAL)
        self.assertEqual(kind_for_hold(15), MID)
        self.assertEqual(kind_for_hold(59), MID)
        self.assertEqual(kind_for_hold(60), BIG)

    def test_affordable_kind_downgrades(self):
        """スタミナが足りないときは出せる中で最も長押しが必要なパンチになる"""
        self.assertEqual(affordable_kind(60, PUNCH_COST[BIG]), BIG)
        self.assertEqual(affordable_kind(60, PUNCH_COST[BIG] - 1), MID)
        self.assertEqual(affordable_kind(60, PUNCH_COST[MID] - 1), NORMAL)
        self.assertIsNone(affordable_kind(60, PUNCH_COST[NORMAL] - 1))

    def test_range_order(self):
        """射程は通常＜中＜大で、大パンチは長押しした分だけ伸びる"""
        self.assertEqual(punch_range(NORMAL, 1), MIN_RANGE)
        self.assertEqual(punch_range(MID, 15), MID_RANGE)
        self.assertEqual(punch_range(BIG, 60), BIG_RANGE)
        self.assertEqual(punch_range(BIG, 62), BIG_RANGE + 2 * BIG_RANGE_GROWTH)
        self.assertLess(MIN_RANGE, MID_RANGE)
        self.assertLess(MID_RANGE_MAX, BIG_RANGE)

    def test_mid_range_grows(self):
        """中パンチは長押しした分だけ初期射程から最大射程まで伸びる"""
        self.assertLess(MID_RANGE, punch_range(MID, 30))
        self.assertLess(punch_range(MID, 30), punch_range(MID, 45))
        self.assertLess(punch_range(MID, 45), MID_RANGE_MAX)
        self.assertEqual(punch_range(MID, 59), MID_RANGE_MAX)
        self.assertEqual(punch_range(MID, 90), MID_RANGE_MAX)

    def test_cost_order(self):
        """スタミナ消費量は通常＜中＜大"""
        self.assertLess(PUNCH_COST[NORMAL], PUNCH_COST[MID])
        self.assertLess(PUNCH_COST[MID], PUNCH_COST[BIG])


if __name__ == "__main__":
    unittest.main()
