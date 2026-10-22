import tempfile
import unittest
from pathlib import Path

import ranking


class TestRanking(unittest.TestCase):
    def test_insert_keeps_top_five(self):
        """ランキングは上位5名だけを高い順に残す"""
        board = [{"name": f"P{i}", "score": s} for i, s in enumerate((500, 400, 300, 200, 100))]
        self.assertTrue(ranking.qualifies(board, 150))
        self.assertFalse(ranking.qualifies(board, 100))
        new_board, index = ranking.insert(board, "NEW", 350)
        self.assertEqual(index, 2)
        self.assertEqual([d["score"] for d in new_board], [500, 400, 350, 300, 200])

    def test_empty_name_becomes_player(self):
        """名前が0文字のときはPLAYERになる"""
        self.assertEqual(ranking.entry_name(""), "PLAYER")
        self.assertEqual(ranking.entry_name("ABC"), "ABC")

    def test_save_and_load(self):
        """保存したランキングを読み込める"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sub" / "ranking.json"
            board = [{"name": "ABC123", "score": 1000}]
            ranking.save(path, board)
            self.assertEqual(ranking.load(path), board)
            self.assertEqual(ranking.load(Path(tmp) / "missing.json"), [])


if __name__ == "__main__":
    unittest.main()
