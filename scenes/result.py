import pyxel

import controls
import ranking
from constants import (
    CENTER_X, COLOR_ACCENT, COLOR_SUB_TEXT, COLOR_TEXT, NAME_MAX_LENGTH, SCALE, SCREEN_HEIGHT,
)
from render import draw_stage
from text import draw_text


class ResultScene:
    def __init__(self, app, score):
        """スコア確認画面を作る。上位5名に入るなら名前入力を行う"""
        self.app = app
        self.score = score
        self.entering = ranking.qualifies(app.ranking, score)
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
            index = self.app.save_score(ranking.entry_name(self.name), self.score)
            self.app.show_ranking(index)

    def draw(self):
        """スコアと名前入力欄を描画する"""
        draw_stage()
        draw_text(CENTER_X, SCREEN_HEIGHT * 0.12, "RESULT", COLOR_ACCENT, "l", center=True)
        draw_text(CENTER_X, SCREEN_HEIGHT * 0.32, f"SCORE {self.score}", COLOR_TEXT, "m", center=True)
        if not self.entering:
            draw_text(CENTER_X, SCREEN_HEIGHT * 0.85, "Enter / Space : タイトルへ", COLOR_SUB_TEXT, center=True)
            return
        draw_text(CENTER_X, SCREEN_HEIGHT * 0.46, "ランクイン！ なまえを いれてください", COLOR_ACCENT, center=True)
        box_w, box_h = int(300 * SCALE), int(36 * SCALE)
        box_y = int(SCREEN_HEIGHT * 0.53)
        pyxel.rect(CENTER_X - box_w // 2, box_y, box_w, box_h, 0)
        pyxel.rectb(CENTER_X - box_w // 2, box_y, box_w, box_h, COLOR_TEXT)
        draw_text(CENTER_X, box_y + int(6 * SCALE), self.name + "_", COLOR_TEXT, "m", center=True)
        draw_text(CENTER_X, SCREEN_HEIGHT * 0.7,
                  f"A~Z / 0~9 : にゅうりょく ({NAME_MAX_LENGTH}もじまで)  BackSpace : けす  Enter : けってい",
                  COLOR_SUB_TEXT, center=True)
