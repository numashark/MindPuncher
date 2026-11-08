import random

from constants import CLEAR_BONUS, COMBO_BONUS, GAME_FRAMES, KILL_SCORE


def clear_bonus(cleared):
    """ゲームクリアしたかどうか cleared から、スコア確認画面で加えるボーナス点を返す"""
    return CLEAR_BONUS if cleared else 0


def max_score(cleared=True):
    """1プレイで理論上とれる最大のスコアを返す（出現する敵をすべて体力3としてダメージを受けずに倒したとき）。
    cleared がTrueならクリアボーナスも加える"""
    from spawner import Spawner
    spawner = Spawner(random.Random(0))
    kills = sum(len(spawner.update(frame)) for frame in range(1, GAME_FRAMES + 1))
    return sum(KILL_SCORE[3] + COMBO_BONUS * n for n in range(1, kills + 1)) + clear_bonus(cleared)


class ScoreBoard:
    def __init__(self):
        """スコアとコンボ数を0にする"""
        self.score = 0
        self.combo = 0

    def add_kill(self, enemy_max_hp):
        """敵を倒したときのスコアとコンボボーナスを加算し、加算した点数を返す"""
        self.combo += 1
        points = KILL_SCORE[enemy_max_hp] + self.combo * COMBO_BONUS
        self.score += points
        return points

    def reset_combo(self):
        """ダメージを受けたときにコンボ数を0に戻す"""
        self.combo = 0
