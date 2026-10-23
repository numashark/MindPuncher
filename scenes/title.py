import pyxel

import controls
from constants import (
    CENTER_X, COLOR_ACCENT, COLOR_RANKING_TITLE, COLOR_SUB_TEXT, COLOR_TEXT, MENU_ITEMS, SCALE,
    SCREEN_HEIGHT,
)
from render import draw_stage
from text import draw_clear_mark, draw_text, text_width


class TitleScene:
    def __init__(self, app):
        """タイトル画面（メインメニュー）を作る"""
        self.app = app
        self.index = 0

    def update(self):
        """メニューの選択と決定を処理する"""
        if controls.up_pressed():
            self.index = (self.index - 1) % len(MENU_ITEMS)
        if controls.down_pressed():
            self.index = (self.index + 1) % len(MENU_ITEMS)
        if controls.decide_pressed():
            if self.index == 0:
                self.app.start_play()
            elif self.index == 1:
                self.app.show_howto()
            else:
                self.app.show_ranking()

    def draw(self):
        """タイトル、メニュー、ランキング、操作説明を描画する"""
        draw_stage()
        draw_text(CENTER_X, SCREEN_HEIGHT * 0.12, "MindPuncher", COLOR_ACCENT, "l", center=True)
        y = SCREEN_HEIGHT * 0.36
        for i, item in enumerate(MENU_ITEMS):
            selected = i == self.index
            draw_text(CENTER_X, y, item, COLOR_ACCENT if selected else COLOR_SUB_TEXT, "m", center=True)
            if selected:
                ax = CENTER_X - int(130 * SCALE)
                pyxel.tri(ax, y + int(6 * SCALE), ax, y + int(26 * SCALE), ax + int(14 * SCALE),
                          y + int(16 * SCALE), COLOR_ACCENT)
            y += int(44 * SCALE)

        y = SCREEN_HEIGHT * 0.62
        draw_text(CENTER_X, y, "- RANKING -", COLOR_RANKING_TITLE, center=True)
        y += int(26 * SCALE)
        if not self.app.ranking:
            draw_text(CENTER_X, y, "まだ きろくが ありません", COLOR_SUB_TEXT, center=True)
        for i, entry in enumerate(self.app.ranking):
            draw_text(CENTER_X - int(130 * SCALE), y, f"{i + 1}. {entry['name']}", COLOR_TEXT)
            score = f"{entry['score']:>7}"
            draw_text(CENTER_X + int(50 * SCALE), y, score, COLOR_TEXT)
            if entry["clear"]:
                draw_clear_mark(CENTER_X + int(50 * SCALE) + text_width(score), y)
            y += int(22 * SCALE)

        draw_text(CENTER_X, SCREEN_HEIGHT * 0.94,
                  "W/S・↑/↓ : せんたく   Enter/Space : けってい   ESC : しゅうりょう",
                  COLOR_SUB_TEXT, center=True)
