from constants import CLEAR_BONUS, COMBO_BONUS, KILL_SCORE


def clear_bonus(cleared):
    """ゲームクリアしたかどうか cleared から、スコア確認画面で加えるボーナス点を返す"""
    return CLEAR_BONUS if cleared else 0


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
