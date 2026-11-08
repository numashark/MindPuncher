import json
import sys
from pathlib import Path

import ranking
from constants import ONLINE_RANKING_PATH


def make_counts(data):
    """Firebaseのコンソールでエクスポートしたデータベース全体、またはscoresだけのデータから、
    点数帯ごとの件数（scoreCounts にインポートする形）を作る"""
    if isinstance(data, dict) and isinstance(data.get(ONLINE_RANKING_PATH), dict):
        data = data[ONLINE_RANKING_PATH]
    return ranking.count_buckets(data)


def main(argv):
    """エクスポートしたJSONファイルを読み込み、点数帯ごとの件数をJSONファイルに書き出す。
    使い方: python mind_puncher/make_score_counts.py エクスポートしたJSON 書き出すJSON"""
    if len(argv) != 3:
        print("usage: python mind_puncher/make_score_counts.py <exported.json> <scoreCounts.json>")
        return 1
    data = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    counts = make_counts(data)
    Path(argv[2]).write_text(json.dumps(counts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{sum(d['n'] for d in counts.values())} scores -> {len(counts)} buckets")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
