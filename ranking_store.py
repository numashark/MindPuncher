import json
import random
import time
from urllib.parse import quote

import ranking
from constants import (
    BROWSER_RANKING_KEY, ONLINE_ADD_RETRIES, ONLINE_COUNT_PATH, ONLINE_LAST_POST_PATH, ONLINE_PLAY_PATH,
    ONLINE_RANKING_PATH, RANKING_SIZE, SCORE_BUCKET_SIZE,
)
from screen_mode import IS_WEB

WEB_FIREBASE_CONFIG = "mindPuncherFirebase"
WEB_APP_CHECK_TOKEN = "mindPuncherAppCheckToken"


class FileStore:
    def __init__(self, path):
        """PC版で使う、ファイルに保存するランキングを作る"""
        self.path = path
        self.error = False
        self.rank_error = False

    def load(self):
        """ランキングを読み込む"""
        return ranking.load(self.path)

    def record_play(self, score, cleared):
        """プレイが終わったときに呼ぶ。この保存先ではプレイごとのスコアは記録しない"""

    def rank(self, board, score):
        """スコアが保存されたランキングの中で何位かを返す。上位5名に入らないときはNoneを返す"""
        return ranking.rank(board, score)

    def add(self, board, name, score, cleared):
        """ランキングに登録して保存し、新しいランキングと登録された順位（0始まり）を返す"""
        new_board, index = ranking.insert(board, name, score, cleared)
        ranking.save(self.path, new_board)
        return new_board, index


class BrowserStore:
    def __init__(self, storage):
        """Web版でデータベースのURLが未設定のときに使う、ブラウザ（localStorage）に保存するランキングを作る"""
        self.storage = storage
        self.error = False
        self.rank_error = False

    def load(self):
        """ランキングを読み込む"""
        text = self.storage.getItem(BROWSER_RANKING_KEY)
        return ranking.from_json(text) if text else []

    def record_play(self, score, cleared):
        """プレイが終わったときに呼ぶ。この保存先ではプレイごとのスコアは記録しない"""

    def rank(self, board, score):
        """スコアが保存されたランキングの中で何位かを返す。上位5名に入らないときはNoneを返す"""
        return ranking.rank(board, score)

    def add(self, board, name, score, cleared):
        """ランキングに登録して保存し、新しいランキングと登録された順位（0始まり）を返す"""
        new_board, index = ranking.insert(board, name, score, cleared)
        self.storage.setItem(BROWSER_RANKING_KEY, ranking.to_json(new_board))
        return new_board, index


class OnlineStore:
    def __init__(self, base_url, request, make_key=None):
        """Web版で使う、全員共通のオンラインのデータベースに保存するランキングを作る。
        request(method, url, body) は通信して (ステータスコード, 本文) を返す関数、make_key は登録する1件のIDを作る関数"""
        self.base_url = base_url.rstrip("/")
        self.root_url = f"{self.base_url}/.json"
        self.url = f"{self.base_url}/{ONLINE_RANKING_PATH}.json"
        self.plays_url = f"{self.base_url}/{ONLINE_PLAY_PATH}.json"
        self.counts_url = f"{self.base_url}/{ONLINE_COUNT_PATH}.json"
        self.request = request
        self.make_key = make_key or new_key
        self.error = False
        self.rank_error = False

    def load(self):
        """上位5件を読み込む。読み込めなかったときは error をTrueにして空のランキングを返す"""
        query = f"?orderBy={quote(json.dumps('score'))}&limitToLast={RANKING_SIZE}"
        status, text = self.request("GET", self.url + query, None)
        try:
            if status != 200:
                raise ValueError(status)
            board = ranking.from_online(json.loads(text))
        except (ValueError, AttributeError):
            self.error = True
            return []
        self.error = False
        return board

    def record_play(self, score, cleared):
        """プレイが終わったときに、名前なしでスコアを記録し、そのスコアの点数帯の件数を1増やす。
        ほかの人の記録と同時になって件数を書き換えられなかったときは、件数を読みなおして記録しなおす。
        記録できたかどうかを返す"""
        key = self.make_key()
        bucket = ranking.score_bucket(score)
        count_path = f"{ONLINE_COUNT_PATH}/{ranking.bucket_key(bucket)}"
        for _ in range(ONLINE_ADD_RETRIES):
            status, text = self.request("GET", f"{self.base_url}/{count_path}.json", None)
            try:
                if status != 200:
                    raise ValueError(status)
                count = int((json.loads(text) or {}).get("n", 0))
            except (ValueError, AttributeError, TypeError):
                return False
            body = json.dumps({
                f"{ONLINE_PLAY_PATH}/{key}": {
                    "score": score, "clear": cleared, "bucket": bucket, "time": {".sv": "timestamp"},
                },
                count_path: {"n": count + 1, "last": key},
            })
            status, _ = self.request("PATCH", self.root_url, body)
            if status == 200:
                return True
        return False

    def rank(self, board, score):
        """スコアがデータベースに記録されている全プレイのスコアの中で何位か（1始まり、同点は同じ順位）を返す。
        点数帯ごとの件数から自分より上の点数帯の件数を求め、同じ点数帯のプレイだけを読み込んで自分より上の件数を足す。
        読み込めなかったときは rank_error をTrueにして、上位5件の board から求める（上位5名に入らないときはNone）"""
        bucket_end = (ranking.score_bucket(score) + 1) * SCORE_BUCKET_SIZE - 1
        query = f"?orderBy={quote(json.dumps('score'))}&startAt={score + 1}&endAt={bucket_end}"
        try:
            status, text = self.request("GET", self.counts_url, None)
            if status != 200:
                raise ValueError(status)
            higher = ranking.count_higher(json.loads(text), score)
            status, text = self.request("GET", self.plays_url + query, None)
            if status != 200:
                raise ValueError(status)
            same = sum(1 for d in (json.loads(text) or {}).values() if int(d["score"]) > score)
        except (ValueError, AttributeError, KeyError, TypeError):
            self.rank_error = True
            return ranking.rank(board, score)
        self.rank_error = False
        return higher + same + 1

    def add(self, board, name, score, cleared):
        """スコアを登録して上位5件を読み込みなおし、新しいランキングと登録された順位（0始まり）を返す。
        保存できなかったときは error をTrueにして、画面上のランキングにだけ反映する"""
        key = self.make_key()
        server_time = {".sv": "timestamp"}
        body = json.dumps({
            f"{ONLINE_RANKING_PATH}/{key}": {"name": name, "score": score, "clear": cleared, "time": server_time},
            f"{ONLINE_LAST_POST_PATH}/{name}": server_time,
        })
        status, _ = self.request("PATCH", self.root_url, body)
        if status != 200:
            self.error = True
            return ranking.insert(board, name, score, cleared)
        new_board = self.load()
        if self.error:
            return ranking.insert(board, name, score, cleared)
        index = next((i for i, d in enumerate(new_board) if d["id"] == key), -1)
        return new_board, index


def new_key():
    """登録する1件のIDを、登録した時刻の順に並ぶ文字列で作る"""
    suffix = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=8))
    return f"{int(time.time() * 1000):013d}{suffix}"


def web_database_url():
    """Web版の起動ページ（docs/firebase_config.js）に設定されたデータベースのURLを返す。未設定なら空文字を返す"""
    import js
    config = getattr(js.window, WEB_FIREBASE_CONFIG, None)
    return str(getattr(config, "databaseURL", "") or "")


def web_request(method, url, body):
    """ブラウザのXMLHttpRequestで通信し、(ステータスコード, 本文) を返す。通信できなかったときは (0, "") を返す。
    App Checkのトークンがあればヘッダーに付ける"""
    import js
    try:
        req = js.XMLHttpRequest.new()
        req.open(method, url, False)
        token = getattr(js.window, WEB_APP_CHECK_TOKEN, None)
        if token:
            req.setRequestHeader("X-Firebase-AppCheck", str(token))
        req.send(body)
        return int(req.status), str(req.responseText)
    except Exception:
        return 0, ""


def create():
    """動いている環境に合わせてランキングの保存先を作る"""
    if not IS_WEB:
        return FileStore(ranking.default_path())
    url = web_database_url()
    if url:
        return OnlineStore(url, web_request)
    import js
    return BrowserStore(js.window.localStorage)
