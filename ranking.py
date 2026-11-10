import json
import sys
from pathlib import Path

from constants import BASE_DIR, DEFAULT_NAME, RANKING_FILE_NAME, RANKING_SIZE, SCORE_BUCKET_SIZE


def default_path():
    """ランキングを保存するファイルのパスを返す。実行ファイルのときは実行ファイルと同じフォルダに保存する"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / RANKING_FILE_NAME
    return BASE_DIR / RANKING_FILE_NAME


def load(path):
    """ランキングを読み込む。読み込めないときは空のランキングを返す"""
    try:
        return from_json(Path(path).read_text(encoding="utf-8"))
    except OSError:
        return []


def from_json(text):
    """JSON文字列からランキングを作る。読み取れないときは空のランキングを返す"""
    try:
        return [normalize(d) for d in json.loads(text)][:RANKING_SIZE]
    except (ValueError, KeyError, TypeError, AttributeError):
        return []


def to_json(ranking):
    """ランキングをJSON文字列にする"""
    return json.dumps(ranking, ensure_ascii=False, indent=2)


def normalize(d):
    """ランキングの1件を名前・スコア・クリアしたかどうかの形にそろえる"""
    return {"name": str(d["name"]), "score": int(d["score"]), "clear": bool(d.get("clear", False))}


def from_online(data):
    """オンラインのデータベースから受け取った {ID: 1件} の辞書を、IDつきのランキングにする。同点は先に登録した順にする"""
    entries = []
    for key, d in (data or {}).items():
        try:
            entries.append({**normalize(d), "id": str(key)})
        except (KeyError, TypeError, ValueError, AttributeError):
            continue
    entries.sort(key=lambda d: (-d["score"], d["id"]))
    return entries[:RANKING_SIZE]


def save(path, ranking):
    """ランキングを保存する"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_json(ranking), encoding="utf-8")


def entry_name(name):
    """登録する名前を返す。0文字のときはPLAYERにする"""
    return name or DEFAULT_NAME


def qualifies(ranking, score):
    """スコアが上位5名に入るかを返す"""
    return len(ranking) < RANKING_SIZE or score > ranking[-1]["score"]


def rank(ranking, score):
    """スコアが上位5件のランキングの中で何位か（1始まり、同点は同じ順位）を返す。上位5名に入らないときはNoneを返す"""
    place = sum(1 for d in ranking if d["score"] > score) + 1
    return place if place <= RANKING_SIZE else None


def score_bucket(score):
    """スコアが入る点数帯の番号を返す"""
    return score // SCORE_BUCKET_SIZE


def bucket_key(bucket):
    """点数帯の番号から、データベースで件数を保存する場所の名前を返す"""
    return f"b{bucket}"


def count_buckets(entries):
    """データベースの {ID: 1件} の辞書（1件にはスコアがあればよい）から、点数帯ごとの件数をデータベースに保存する形
    {場所の名前: {"n": 件数, "last": その点数帯に最後に登録したID}} にして返す。読み取れない1件は数えない"""
    counts = {}
    for key in sorted(entries or {}):
        try:
            name = bucket_key(score_bucket(int(entries[key]["score"])))
        except (KeyError, TypeError, ValueError, AttributeError):
            continue
        counts[name] = {"n": counts.get(name, {"n": 0})["n"] + 1, "last": str(key)}
    return counts


def count_higher(counts, score):
    """点数帯ごとの件数から、スコアの点数帯より上の点数帯にあるスコアの件数の合計を返す"""
    bucket = score_bucket(score)
    total = 0
    for name, d in (counts or {}).items():
        try:
            if int(name[1:]) > bucket:
                total += int(d["n"])
        except (KeyError, TypeError, ValueError):
            continue
    return total


def insert(ranking, name, score, cleared):
    """ランキングに登録し、新しいランキングと登録された順位（0始まり）を返す。cleared はゲームクリアしたかどうか"""
    entry = {"name": name, "score": score, "clear": cleared}
    new_ranking = sorted(ranking + [entry], key=lambda d: -d["score"])[:RANKING_SIZE]
    index = next((i for i, d in enumerate(new_ranking) if d is entry), -1)
    return new_ranking, index
