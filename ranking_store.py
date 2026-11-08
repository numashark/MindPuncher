import json
from urllib.parse import quote

import ranking
from constants import BROWSER_RANKING_KEY, ONLINE_RANKING_PATH, ONLINE_RANKING_URL, RANKING_SIZE
from screen_mode import IS_WEB


class FileStore:
    def __init__(self, path):
        """PC版で使う、ファイルに保存するランキングを作る"""
        self.path = path
        self.error = False

    def load(self):
        """ランキングを読み込む"""
        return ranking.load(self.path)

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

    def add(self, board, name, score, cleared):
        """ランキングに登録して保存し、新しいランキングと登録された順位（0始まり）を返す"""
        new_board, index = ranking.insert(board, name, score, cleared)
        self.storage.setItem(BROWSER_RANKING_KEY, ranking.to_json(new_board))
        return new_board, index


class OnlineStore:
    def __init__(self, base_url, request):
        """Web版で使う、全員共通のオンラインのデータベースに保存するランキングを作る。
        request(method, url, body) は通信して (ステータスコード, 本文) を返す関数"""
        self.url = f"{base_url.rstrip('/')}/{ONLINE_RANKING_PATH}.json"
        self.request = request
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

    def add(self, board, name, score, cleared):
        """スコアを登録して上位5件を読み込みなおし、新しいランキングと登録された順位（0始まり）を返す。
        保存できなかったときは error をTrueにして、画面上のランキングにだけ反映する"""
        body = json.dumps({"name": name, "score": score, "clear": cleared})
        status, text = self.request("POST", self.url, body)
        try:
            if status != 200:
                raise ValueError(status)
            key = str(json.loads(text)["name"])
        except (ValueError, KeyError, TypeError):
            self.error = True
            return ranking.insert(board, name, score, cleared)
        new_board = self.load()
        if self.error:
            return ranking.insert(board, name, score, cleared)
        index = next((i for i, d in enumerate(new_board) if d["id"] == key), -1)
        return new_board, index


def web_request(method, url, body):
    """ブラウザのXMLHttpRequestで通信し、(ステータスコード, 本文) を返す。通信できなかったときは (0, "") を返す"""
    import js
    try:
        req = js.XMLHttpRequest.new()
        req.open(method, url, False)
        req.send(body)
        return int(req.status), str(req.responseText)
    except Exception:
        return 0, ""


def create():
    """動いている環境に合わせてランキングの保存先を作る"""
    if not IS_WEB:
        return FileStore(ranking.default_path())
    if ONLINE_RANKING_URL:
        return OnlineStore(ONLINE_RANKING_URL, web_request)
    import js
    return BrowserStore(js.window.localStorage)
