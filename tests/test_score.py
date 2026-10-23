import unittest

from constants import CLEAR_BONUS
from score import clear_bonus


class TestScore(unittest.TestCase):
    def test_clear_bonus(self):
        """ゲームクリアしたときだけ固定のボーナス点が入る"""
        self.assertEqual(clear_bonus(True), CLEAR_BONUS)
        self.assertEqual(clear_bonus(False), 0)


if __name__ == "__main__":
    unittest.main()
