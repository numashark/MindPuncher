import json
import random
import time
from urllib.parse import quote

import ranking
from constants import (
    BROWSER_RANKING_KEY, ONLINE_LAST_POST_PATH, ONLINE_RANK_LIMIT, ONLINE_RANKING_PATH, RANKING_SIZE,
)
from screen_mode import IS_WEB

WEB_FIREBASE_CONFIG = "mindPuncherFirebase"
WEB_APP_CHECK_TOKEN = "mindPuncherAppCheckToken"


class FileStore:
    def __init__(self, path):
        """PC版で使う、ファイルに保存するランキングを作る"""
        self.path = path
        self.error = False

    def load(self):
        """ランキングを読み込む"""
        return ranking.load(self.path)

    def rank(self, board, score):
        """スコアが保存されたランキングの中で何位かと、順位を求めた件数を返す。上位5名に入らないときの順位はNoneにする"""
        return ranking.rank(board, score), RANKING_SIZE

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

    def load(self):
        """ランキングを読み込む"""
        text = self.storage.getItem(BROWSER_RANKING_KEY)
        return ranking.from_json(text) if text else []

    def rank(self, board, score):
        """スコアが保存されたランキングの中で何位かと、順位を求めた件数を返す。上位5名に入らないときの順位はNoneにする"""
        return ranking.rank(board, score), RANKING_SIZE

    def add(self, board, name, score, cleared):
        """ランキングに登録して保存し、新しいランキングと登録された順位（0始まり）を返す"""
        new_board, index = ranking.insert(board, name, score, cleared)
        self.storage.setItem(BROWSER_RANKING_KEY, ranking.to_json(new_board))
        return new_board, index


class OnlineStore:
    def __init__(self, base_url, request, make_key=None):
        """Web版で使う、全員共通のオンラインのデータベースに保存するランキングを作る。
        request(method, url, body) は通信して (ステータスコード, 本文) を返す関数、make_key は登録する1件のIDを作る関数"""
        self.root_url = f"{base_url.rstrip('/')}/.json"
        self.url = f"{base_url.rstrip('/')}/{ONLINE_RANKING_PATH}.json"
        self.request = request
        self.make_key = make_key or new_key
        self.error = False

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

    def rank(self, board, score):
        """スコアがデータベースに保存されている全員のスコアの中で何位か（1始まり、同点は同じ順位）と、順位を求めた件数を返す。
        データベースでスコア順に並べ替えた上位 ONLINE_RANK_LIMIT 件だけを読み込み、それより下の順位はNoneにする。
        読み込めなかったときは上位5件の board から求める"""
        query = f"?orderBy={quote(json.dumps('score'))}&limitToLast={ONLINE_RANK_LIMIT}"
        status, text = self.request("GET", self.url + query, None)
        try:
            if status != 200:
                raise ValueError(status)
            top = [ranking.normalize(d) for d in (json.loads(text) or {}).values()]
        except (ValueError, AttributeError, KeyError, TypeError):
            return ranking.rank(board, score), RANKING_SIZE
        return ranking.rank(top, score, ONLINE_RANK_LIMIT), ONLINE_RANK_LIMIT

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
