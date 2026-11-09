import pyxel

import controls
import ranking
from constants import (
    CENTER_X, COLOR_ACCENT, COLOR_SUB_TEXT, COLOR_TEXT, CONNECTION_ERROR_TEXT, NAME_MAX_LENGTH, SCALE,
    SCREEN_HEIGHT,
)
from render import draw_stage
from score import clear_bonus
from text import draw_clear_mark, draw_text, text_width


class ResultScene:
    def __init__(self, app, score, max_combo, cleared):
        """スコア確認画面を作る。ゲームクリアしていたらボーナス点を加え、プレイのスコアを記録して順位を求め、
        上位5名に入るなら名前入力を行う。max_combo はプレイ中の最大コンボ数"""
        self.app = app
        self.max_combo = max_combo
        self.cleared = cleared
        self.base_score = score
        self.bonus = clear_bonus(cleared)
        self.score = score + self.bonus
        app.ranking_store.record_play(self.score, cleared)
        self.rank = app.ranking_store.rank(app.ranking, self.score)
        self.rank_error = app.ranking_store.rank_error
        self.entering = ranking.qualifies(app.ranking, self.score)
        self.name = ""

    def update(self):
        """名前入力とランキングへの保存、画面の移動を処理する"""
        if not self.entering:
            if controls.decide_pressed():
                self.app.show_title()
            return
        for ch in controls.typed_chars():
            if len(self.name) < NAME_MAX_LENGTH:
                self.name += ch
        if controls.backspace_pressed():
            self.name = self.name[:-1]
        if controls.confirm_name_pressed():
            index = self.app.save_score(ranking.entry_name(self.name), self.score, self.cleared)
            self.app.show_ranking(index)

    def draw(self):
        """スコアと名前入力欄を描画する"""
        draw_stage()
        draw_text(CENTER_X, SCREEN_HEIGHT * 0.12, "RESULT", COLOR_ACCENT, "l", center=True)
        if self.bonus:
            draw_text(CENTER_X, SCREEN_HEIGHT * 0.21, f"SCORE {self.base_score}", COLOR_TEXT, "m", center=True)
            draw_text(CENTER_X, SCREEN_HEIGHT * 0.275, f"CLEAR BONUS +{self.bonus}", COLOR_ACCENT, "m", center=True)
            total = f"TOTAL {self.score}"
            draw_text(CENTER_X, SCREEN_HEIGHT * 0.34, total, COLOR_TEXT, "m", center=True)
            draw_clear_mark(CENTER_X + text_width(total, "m") // 2, SCREEN_HEIGHT * 0.34, "m")
            combo_y = SCREEN_HEIGHT * 0.405
        else:
            draw_text(CENTER_X, SCREEN_HEIGHT * 0.24, f"SCORE {self.score}", COLOR_TEXT, "m", center=True)
            combo_y = SCREEN_HEIGHT * 0.33
        if self.rank:
            rank = f"RANK {self.rank}"
        elif self.rank_error:
            rank = f"RANK {CONNECTION_ERROR_TEXT}"
        else:
            rank = "ランクがい"
        draw_text(CENTER_X, combo_y, f"MAX COMBO {self.max_combo}   {rank}", COLOR_TEXT, "m", center=True)
        if not self.entering:
            draw_text(CENTER_X, SCREEN_HEIGHT * 0.85, "Enter / Space : タイトルへ", COLOR_SUB_TEXT, center=True)
            return
        draw_text(CENTER_X, SCREEN_HEIGHT * 0.48, "ランクイン！ なまえを いれてください", COLOR_ACCENT, center=True)
        box_w, box_h = int(340 * SCALE), int(50 * SCALE)
        box_y = int(SCREEN_HEIGHT * 0.55)
        pyxel.rect(CENTER_X - box_w // 2, box_y, box_w, box_h, 0)
        pyxel.rectb(CENTER_X - box_w // 2, box_y, box_w, box_h, COLOR_TEXT)
        draw_text(CENTER_X, box_y + int(6 * SCALE), self.name + "_", COLOR_TEXT, "m", center=True)
        draw_text(CENTER_X, SCREEN_HEIGHT * 0.72,
                  f"A~Z / 0~9 : にゅうりょく ({NAME_MAX_LENGTH}もじまで)  BackSpace : けす  Enter : けってい",
                  COLOR_SUB_TEXT, center=True)
