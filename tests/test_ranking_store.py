import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from urllib.parse import parse_qsl

import ranking
import ranking_store
import score
import make_play_records
from constants import (
    BASE_DIR, BROWSER_RANKING_KEY, ONLINE_ADD_RETRIES, ONLINE_COUNT_PATH, ONLINE_LAST_POST_PATH, ONLINE_PLAY_PATH,
    ONLINE_RANKING_PATH, SCORE_BUCKET_SIZE,
)


class FakeDatabase:
    """Firebase Realtime Database の代わりに、送られたスコアやプレイの記録、点数帯ごとの件数を覚えておく"""

    def __init__(self, entries=None, online=True, plays=None):
        """entries は名前つきのスコア {ID: 1件}、plays はプレイの記録 {ID: 1件} の辞書、online がFalseなら通信できない。
        点数帯ごとの件数は plays から作る"""
        self.entries = dict(entries or {})
        self.plays = dict(plays or {})
        self.counts = ranking.count_buckets(self.plays)
        self.last_posts = {}
        self.nodes = {ONLINE_RANKING_PATH: self.entries, ONLINE_PLAY_PATH: self.plays,
                      ONLINE_COUNT_PATH: self.counts, ONLINE_LAST_POST_PATH: self.last_posts}
        self.online = online
        self.requests = []
        self.conflicts = 0

    def request(self, method, url, body):
        """通信の代わりに (ステータスコード, 本文) を返す。conflicts が残っていれば、書き込みの直前にほかの人の記録で件数が増える"""
        self.requests.append((method, url, body))
        if not self.online:
            return 0, ""
        address, _, query = url.partition("?")
        path = address.split(".com/", 1)[1][:-len(".json")]
        params = {k: json.loads(v) for k, v in parse_qsl(query)}
        if method == "PATCH":
            return self.patch(json.loads(body))
        node, _, key = path.partition("/")
        if key:
            return 200, json.dumps(self.nodes[node].get(key))
        if node == ONLINE_COUNT_PATH:
            return 200, json.dumps(self.counts or None)
        entries = sorted(self.nodes[node].items(), key=lambda kv: kv[1]["score"])
        if "startAt" in params:
            entries = [kv for kv in entries if kv[1]["score"] >= params["startAt"]]
        if "endAt" in params:
            entries = [kv for kv in entries if kv[1]["score"] <= params["endAt"]]
        if "limitToLast" in params:
            entries = entries[-params["limitToLast"]:]
        return 200, json.dumps(dict(entries))

    def patch(self, updates):
        """まとめて書き込む。点数帯の件数が「今の件数+1」でなければ何も書き込まずに失敗する"""
        if self.conflicts:
            self.conflicts -= 1
            for path in updates:
                node, key = path.split("/")
                if node == ONLINE_COUNT_PATH:
                    self.counts.setdefault(key, {"n": 0, "last": "other"})["n"] += 1
        for path, value in updates.items():
            node, key = path.split("/")
            if node == ONLINE_COUNT_PATH and value["n"] != self.counts.get(key, {"n": 0})["n"] + 1:
                return 400, ""
        for path, value in updates.items():
            node, key = path.split("/")
            self.nodes[node][key] = value
        return 200, json.dumps(updates)


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

    def test_online_rank_uses_bucket_counts(self):
        """オンラインの順位は、全プレイの記録の上の点数帯の件数と、同じ点数帯で自分より高いスコアの数から求める（同点は同じ順位）"""
        db = FakeDatabase(plays={f"k{i}": {"score": s, "clear": False, "bucket": s // SCORE_BUCKET_SIZE}
                                 for i, s in enumerate((5500, 5200, 4800, 4100, 3000, 300))})
        store = ranking_store.OnlineStore("https://example.firebaseio.com/", db.request)
        self.assertEqual(store.rank([], 4500), 4)
        method, url, _ = db.requests[-1]
        self.assertEqual(method, "GET")
        self.assertEqual(url, "https://example.firebaseio.com/plays.json?orderBy=%22score%22&startAt=4501&endAt=4999")
        self.assertEqual(db.requests[-2][1], "https://example.firebaseio.com/scoreCounts.json")
        self.assertEqual(store.rank([], 4800), 3)
        self.assertEqual(store.rank([], 6000), 1)
        self.assertEqual(store.rank([], 100), 7)
        self.assertFalse(store.rank_error)

    def test_online_rank_falls_back_to_board(self):
        """通信できなかったときは rank_error をTrueにして、画面上の上位5件から順位を求める"""
        board = [{"name": "A", "score": 500, "clear": False}]
        store = ranking_store.OnlineStore("https://example.firebaseio.com/", FakeDatabase(online=False).request)
        self.assertEqual(store.rank(board, 600), 1)
        self.assertEqual(store.rank(board, 400), 2)
        self.assertTrue(store.rank_error)

    def test_online_record_play_counts_bucket(self):
        """プレイが終わると名前なしでスコアを記録し、その点数帯の件数も1増える。名前つきのスコアは増えない"""
        db = FakeDatabase(plays={"a": {"score": 4200, "clear": False, "bucket": 4}})
        store = ranking_store.OnlineStore("https://example.firebaseio.com/", db.request, lambda: "k001")
        self.assertTrue(store.record_play(4500, False))
        self.assertEqual(db.counts["b4"], {"n": 2, "last": "k001"})
        self.assertEqual(db.plays["k001"], {"score": 4500, "clear": False, "bucket": 4, "time": {".sv": "timestamp"}})
        self.assertEqual(db.entries, {})
        self.assertEqual(store.rank([], 4300), 2)

    def test_online_record_play_retries_when_count_changed(self):
        """ほかの人の記録と同時になって件数を書き換えられなかったときは、件数を読みなおして記録しなおす"""
        db = FakeDatabase()
        db.conflicts = 1
        store = ranking_store.OnlineStore("https://example.firebaseio.com/", db.request, lambda: "k001")
        self.assertTrue(store.record_play(500, False))
        self.assertEqual(db.counts["b0"], {"n": 2, "last": "k001"})

        db = FakeDatabase()
        db.conflicts = ONLINE_ADD_RETRIES
        store = ranking_store.OnlineStore("https://example.firebaseio.com/", db.request, lambda: "k001")
        self.assertFalse(store.record_play(500, False))
        self.assertNotIn("k001", db.plays)
        self.assertFalse(ranking_store.OnlineStore("https://example.firebaseio.com/",
                                                   FakeDatabase(online=False).request).record_play(500, False))

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

    def test_rules_bucket_matches_game(self):
        """データベースのルールの点数帯の幅と保存場所が、ゲームの設定と一致している"""
        rules = json.loads((BASE_DIR / "firebase_rules.json").read_text(encoding="utf-8"))["rules"]
        rule = rules[ONLINE_PLAY_PATH]["$id"]["bucket"][".validate"]
        self.assertIn(f"newData.val() * {SCORE_BUCKET_SIZE} <=", rule)
        self.assertIn(f"(newData.val() + 1) * {SCORE_BUCKET_SIZE}", rule)
        self.assertIn(f"child('{ONLINE_COUNT_PATH}').child('b' + newData.val())", rule)
        self.assertIn(f"child('{ONLINE_PLAY_PATH}')", rules[ONLINE_COUNT_PATH]["$bucket"][".validate"])
        self.assertEqual(rules[ONLINE_PLAY_PATH]["$id"]["score"], rules[ONLINE_RANKING_PATH]["$id"]["score"])
        self.assertIn(ONLINE_LAST_POST_PATH, rules)

    def test_make_play_records_from_export(self):
        """既存のスコアのエクスポート（データベース全体でもscoresだけでも）からプレイの記録と点数帯ごとの件数を作れる"""
        scores = {"k1": {"name": "A", "score": 1500, "clear": False, "time": 111},
                  "k2": {"name": "B", "score": 1999, "clear": False},
                  "k3": {"name": "C", "score": 30000, "clear": True, "time": 333},
                  "bad": {"name": "D"}}
        plays = {"k1": {"score": 1500, "clear": False, "bucket": 1, "time": 111},
                 "k2": {"score": 1999, "clear": False, "bucket": 1, "time": 0},
                 "k3": {"score": 30000, "clear": True, "bucket": 30, "time": 333}}
        self.assertEqual(make_play_records.make_plays(scores), plays)
        self.assertEqual(make_play_records.make_plays({ONLINE_RANKING_PATH: scores, "lastPost": {}}), plays)
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "export.json"
            src.write_text(json.dumps(scores), encoding="utf-8")
            with mock.patch("builtins.print"):
                self.assertEqual(make_play_records.main(["", str(src), str(Path(tmp) / "out")]), 0)
            read = lambda name: json.loads((Path(tmp) / "out" / f"{name}.json").read_text(encoding="utf-8"))
            self.assertEqual(read(ONLINE_PLAY_PATH), plays)
            self.assertEqual(read(ONLINE_COUNT_PATH), {"b1": {"n": 2, "last": "k2"}, "b30": {"n": 1, "last": "k3"}})

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
            store.record_play(1000, False)
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
