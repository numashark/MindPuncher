import unittest

from constants import CLEAR_BONUS
from score import ScoreBoard, clear_bonus


class TestScore(unittest.TestCase):
    def test_clear_bonus(self):
        """ゲームクリアしたときだけ固定のボーナス点が入る"""
        self.assertEqual(clear_bonus(True), CLEAR_BONUS)
        self.assertEqual(clear_bonus(False), 0)

    def test_max_combo(self):
        """コンボが途切れても、プレイ中の最大コンボ数は残る"""
        board = ScoreBoard()
        for _ in range(3):
            board.add_kill(1)
        board.reset_combo()
        board.add_kill(1)
        self.assertEqual(board.combo, 1)
        self.assertEqual(board.max_combo, 3)


if __name__ == "__main__":
    unittest.main()
