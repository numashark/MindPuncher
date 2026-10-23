import json
import sys
from pathlib import Path

from constants import BASE_DIR, DEFAULT_NAME, RANKING_FILE_NAME, RANKING_SIZE


def default_path():
    """ランキングを保存するファイルのパスを返す。実行ファイルのときは実行ファイルと同じフォルダに保存する"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / RANKING_FILE_NAME
    return BASE_DIR / RANKING_FILE_NAME


def load(path):
    """ランキングを読み込む。読み込めないときは空のランキングを返す"""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return [{"name": str(d["name"]), "score": int(d["score"]), "clear": bool(d.get("clear", False))}
                for d in data][:RANKING_SIZE]
    except (OSError, ValueError, KeyError, TypeError):
        return []


def save(path, ranking):
    """ランキングを保存する"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ranking, ensure_ascii=False, indent=2), encoding="utf-8")


def entry_name(name):
    """登録する名前を返す。0文字のときはPLAYERにする"""
    return name or DEFAULT_NAME


def qualifies(ranking, score):
    """スコアが上位5名に入るかを返す"""
    return len(ranking) < RANKING_SIZE or score > ranking[-1]["score"]


def insert(ranking, name, score, cleared):
    """ランキングに登録し、新しいランキングと登録された順位（0始まり）を返す。cleared はゲームクリアしたかどうか"""
    entry = {"name": name, "score": score, "clear": cleared}
    new_ranking = sorted(ranking + [entry], key=lambda d: -d["score"])[:RANKING_SIZE]
    index = next((i for i, d in enumerate(new_ranking) if d is entry), -1)
    return new_ranking, index
