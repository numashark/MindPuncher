import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import ranking
import ranking_store
from constants import BROWSER_RANKING_KEY


class FakeDatabase:
    """Firebase Realtime Database の代わりに、送られたスコアを覚えておく"""

    def __init__(self, entries=None, online=True):
        """entries は {ID: 1件} の辞書、online がFalseなら通信できない"""
        self.entries = dict(entries or {})
        self.online = online
        self.requests = []

    def request(self, method, url, body):
        """通信の代わりに (ステータスコード, 本文) を返す"""
        self.requests.append((method, url, body))
        if not self.online:
            return 0, ""
        if method == "POST":
            key = f"k{len(self.entries):03d}"
            self.entries[key] = json.loads(body)
            return 200, json.dumps({"name": key})
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
        store = ranking_store.OnlineStore("https://example.firebaseio.com/", db.request)
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
                mock.patch.object(ranking_store, "ONLINE_RANKING_URL", "https://example.firebaseio.com"):
            self.assertIsInstance(ranking_store.create(), ranking_store.OnlineStore)


if __name__ == "__main__":
    unittest.main()
