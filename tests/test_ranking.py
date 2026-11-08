import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import ranking
from constants import BASE_DIR


class TestRanking(unittest.TestCase):
    def test_insert_keeps_top_five(self):
        """ランキングは上位5名だけを高い順に残す"""
        board = [{"name": f"P{i}", "score": s, "clear": False} for i, s in enumerate((500, 400, 300, 200, 100))]
        self.assertTrue(ranking.qualifies(board, 150))
        self.assertFalse(ranking.qualifies(board, 100))
        new_board, index = ranking.insert(board, "NEW", 350, True)
        self.assertEqual(index, 2)
        self.assertEqual([d["score"] for d in new_board], [500, 400, 350, 300, 200])
        self.assertTrue(new_board[index]["clear"])

    def test_empty_name_becomes_player(self):
        """名前が0文字のときはPLAYERになる"""
        self.assertEqual(ranking.entry_name(""), "PLAYER")
        self.assertEqual(ranking.entry_name("ABC"), "ABC")

    def test_save_and_load(self):
        """保存したランキングを読み込める"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sub" / "ranking.json"
            board = [{"name": "ABC123", "score": 1000, "clear": True}, {"name": "DEF", "score": 500, "clear": False}]
            ranking.save(path, board)
            self.assertEqual(ranking.load(path), board)
            self.assertEqual(ranking.load(Path(tmp) / "missing.json"), [])

    def test_load_old_ranking_without_clear(self):
        """クリアしたかどうかが保存されていない以前のランキングはクリアしていない扱いで読み込む"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ranking.json"
            ranking.save(path, [{"name": "OLD", "score": 300}])
            self.assertEqual(ranking.load(path), [{"name": "OLD", "score": 300, "clear": False}])

    def test_default_path_is_game_dir(self):
        """スクリプトで実行したときはゲームのフォルダに保存する"""
        self.assertEqual(ranking.default_path(), BASE_DIR / "ranking.json")

    def test_default_path_is_executable_dir(self):
        """実行ファイルで実行したときは実行ファイルと同じフォルダに保存する"""
        with tempfile.TemporaryDirectory() as tmp:
            exe = Path(tmp).resolve() / "mind_puncher.exe"
            with mock.patch.object(sys, "frozen", True, create=True), mock.patch.object(sys, "executable", str(exe)):
                self.assertEqual(ranking.default_path(), exe.parent / "ranking.json")


if __name__ == "__main__":
    unittest.main()
