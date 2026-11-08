import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import ranking
import ranking_store
import score
from constants import BASE_DIR, BROWSER_RANKING_KEY, ONLINE_RANKING_PATH


class FakeDatabase:
    """Firebase Realtime Database の代わりに、送られたスコアを覚えておく"""

    def __init__(self, entries=None, online=True):
        """entries は {ID: 1件} の辞書、online がFalseなら通信できない"""
        self.entries = dict(entries or {})
        self.online = online
        self.requests = []
        self.last_posts = {}

    def request(self, method, url, body):
        """通信の代わりに (ステータスコード, 本文) を返す"""
        self.requests.append((method, url, body))
        if not self.online:
            return 0, ""
        if method == "PATCH":
            updates = json.loads(body)
            for path, value in updates.items():
                place, key = path.split("/")
                if place == ONLINE_RANKING_PATH:
                    self.entries[key] = value
                else:
                    self.last_posts[key] = value
            return 200, body
        return 200, json.dumps(self.entries)


class FakeStorage:
    """ブラウザの localStorage の代わり"""

    def __init__(self):
        """空の保存場所を作る"""
        self.items = {}

    def getItem(self, key):
        """保存された文字列を返す。ないときはNoneを返す"""
        return self.items.get(key)

    def setItem(self, key, value):
        """文字列を保存する"""
        self.items[key] = value


class TestRankingStore(unittest.TestCase):
    def test_from_online_sorts_top_five(self):
        """オンラインのデータは高い順に上位5件にし、同点は先に登録した順にする"""
        data = {f"k{i}": {"name": f"P{i}", "score": s, "clear": i == 0}
                for i, s in enumerate((100, 600, 300, 300, 500, 200))}
        board = ranking.from_online(data)
        self.assertEqual([d["id"] for d in board], ["k1", "k4", "k2", "k3", "k5"])
        self.assertEqual(ranking.from_online(None), [])

    def test_online_load_and_add(self):
        """オンラインに登録したスコアは読み込みなおしたランキングの順位で返す"""
        db = FakeDatabase({"a": {"name": "OLD", "score": 300, "clear": False}})
        keys = iter(["k001", "k002"])
        store = ranking_store.OnlineStore("https://example.firebaseio.com/", db.request, lambda: next(keys))
        board = store.load()
        self.assertEqual(board[0]["name"], "OLD")
        method, url, _ = db.requests[0]
        self.assertEqual(method, "GET")
        self.assertEqual(url, "https://example.firebaseio.com/scores.json?orderBy=%22score%22&limitToLast=5")

        board, index = store.add(board, "NEW", 500, True)
        self.assertEqual(index, 0)
        self.assertEqual([(d["name"], d["score"], d["clear"]) for d in board],
                         [("NEW", 500, True), ("OLD", 300, False)])
        self.assertFalse(store.error)
        method, url, body = db.requests[1]
        self.assertEqual((method, url), ("PATCH", "https://example.firebaseio.com/.json"))
        self.assertEqual(json.loads(body)["lastPost/NEW"], {".sv": "timestamp"})
        self.assertEqual(db.entries["k001"]["time"], {".sv": "timestamp"})

    def test_new_key_is_ordered_by_time(self):
        """登録する1件のIDは後に作ったものほど後ろに並ぶ"""
        with mock.patch.object(ranking_store.time, "time", return_value=1000.0):
            first = ranking_store.new_key()
        with mock.patch.object(ranking_store.time, "time", return_value=1000.5):
            second = ranking_store.new_key()
        self.assertLess(first, second)

    def test_rules_max_score_matches_game(self):
        """データベースのルールのスコア上限が、ゲームで理論上とれる最大スコアと一致している"""
        rules = json.loads((BASE_DIR / "firebase_rules.json").read_text(encoding="utf-8"))
        rule = rules["rules"][ONLINE_RANKING_PATH]["$id"]["score"][".validate"]
        self.assertIn(f"<= {score.max_score(True)})", rule)
        self.assertIn(f"<= {score.max_score(False)})", rule)
        self.assertIn(f">= {score.clear_bonus(True)} ", rule)

    def test_online_error_keeps_score_on_screen(self):
        """通信できないときは error をTrueにして、画面上のランキングにだけ反映する"""
        store = ranking_store.OnlineStore("https://example.firebaseio.com", FakeDatabase(online=False).request)
        self.assertEqual(store.load(), [])
        self.assertTrue(store.error)
        board, index = store.add([], "NEW", 500, False)
        self.assertEqual((board, index), ([{"name": "NEW", "score": 500, "clear": False}], 0))
        self.assertTrue(store.error)

    def test_browser_store(self):
        """データベースのURLが未設定のWeb版はブラウザに保存して読み込める"""
        storage = FakeStorage()
        store = ranking_store.BrowserStore(storage)
        self.assertEqual(store.load(), [])
        board, index = store.add([], "ABC", 1000, True)
        self.assertEqual(index, 0)
        self.assertIn(BROWSER_RANKING_KEY, storage.items)
        self.assertEqual(ranking_store.BrowserStore(storage).load(), board)

    def test_file_store(self):
        """PC版はファイルに保存して読み込める"""
        with tempfile.TemporaryDirectory() as tmp:
            store = ranking_store.FileStore(Path(tmp) / "ranking.json")
            board, index = store.add([], "ABC", 1000, False)
            self.assertEqual(ranking_store.FileStore(Path(tmp) / "ranking.json").load(), board)

    def test_create_chooses_store(self):
        """PC版はファイル、Web版はURLがあればオンライン、なければブラウザに保存する"""
        with mock.patch.object(ranking_store, "IS_WEB", False):
            self.assertIsInstance(ranking_store.create(), ranking_store.FileStore)
        with mock.patch.object(ranking_store, "IS_WEB", True), \
                mock.patch.object(ranking_store, "web_database_url", return_value="https://example.firebaseio.com"):
            self.assertIsInstance(ranking_store.create(), ranking_store.OnlineStore)


if __name__ == "__main__":
    unittest.main()
