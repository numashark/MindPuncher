import controls
from constants import CENTER_X, COLOR_ACCENT, COLOR_SUB_TEXT, COLOR_TEXT, SCALE, SCREEN_HEIGHT
from render import draw_stage
from text import draw_text


class RankingScene:
    def __init__(self, app, highlight=-1):
        """ランキング画面を作る。highlight は強調表示する順位（0始まり）"""
        self.app = app
        self.highlight = highlight

    def update(self):
        """決定キーでタイトルに戻る"""
        if controls.decide_pressed() or controls.backspace_pressed():
            self.app.show_title()

    def draw(self):
        """ランキングを描画する"""
        draw_stage()
        draw_text(CENTER_X, SCREEN_HEIGHT * 0.1, "RANKING", COLOR_ACCENT, "l", center=True)
        y = SCREEN_HEIGHT * 0.32
        for i, entry in enumerate(self.app.ranking):
            color = COLOR_ACCENT if i == self.highlight else COLOR_TEXT
            draw_text(CENTER_X - int(200 * SCALE), y, f"{i + 1}. {entry['name']}", color, "m")
            draw_text(CENTER_X + int(70 * SCALE), y, f"{entry['score']:>7}", color, "m")
            y += int(44 * SCALE)
        draw_text(CENTER_X, SCREEN_HEIGHT * 0.9, "Enter / Space : もどる", COLOR_SUB_TEXT, center=True)
