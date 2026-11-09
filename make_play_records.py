import json
import sys
from pathlib import Path

import ranking
from constants import ONLINE_COUNT_PATH, ONLINE_PLAY_PATH, ONLINE_RANKING_PATH


def make_plays(data):
    """Firebaseのコンソールでエクスポートしたデータベース全体、またはscoresだけのデータから、
    既存のスコアをプレイの記録（plays にインポートする形）にして返す。読み取れない1件は入れない"""
    if isinstance(data, dict) and isinstance(data.get(ONLINE_RANKING_PATH), dict):
        data = data[ONLINE_RANKING_PATH]
    plays = {}
    for key, d in (data or {}).items():
        try:
            entry = ranking.normalize(d)
            played_at = d.get("time", 0)
        except (KeyError, TypeError, ValueError, AttributeError):
            continue
        plays[str(key)] = {
            "score": entry["score"], "clear": entry["clear"], "bucket": ranking.score_bucket(entry["score"]),
            "time": played_at if isinstance(played_at, int) else 0,
        }
    return plays


def main(argv):
    """エクスポートしたJSONファイルを読み込み、プレイの記録と点数帯ごとの件数をフォルダにJSONファイルで書き出す。
    使い方: python mind_puncher/make_play_records.py エクスポートしたJSON 書き出すフォルダ"""
    if len(argv) != 3:
        print("usage: python mind_puncher/make_play_records.py <exported.json> <output_dir>")
        return 1
    plays = make_plays(json.loads(Path(argv[1]).read_text(encoding="utf-8")))
    counts = ranking.count_buckets(plays)
    out = Path(argv[2])
    out.mkdir(parents=True, exist_ok=True)
    for name, data in ((ONLINE_PLAY_PATH, plays), (ONLINE_COUNT_PATH, counts)):
        (out / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(plays)} plays -> {len(counts)} buckets")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
