import json
from pathlib import Path

import pyxel

from constants import DEFAULT_NAME, RANKING_FILE_NAME, RANKING_SIZE, USER_DATA_APP, USER_DATA_VENDOR


def default_path():
    """ランキングを保存するファイルのパスを返す"""
    return Path(pyxel.user_data_dir(USER_DATA_VENDOR, USER_DATA_APP)) / RANKING_FILE_NAME


def load(path):
    """ランキングを読み込む。読み込めないときは空のランキングを返す"""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return [{"name": str(d["name"]), "score": int(d["score"])} for d in data][:RANKING_SIZE]
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


def insert(ranking, name, score):
    """ランキングに登録し、新しいランキングと登録された順位（0始まり）を返す"""
    entry = {"name": name, "score": score}
    new_ranking = sorted(ranking + [entry], key=lambda d: -d["score"])[:RANKING_SIZE]
    index = next((i for i, d in enumerate(new_ranking) if d is entry), -1)
    return new_ranking, index
