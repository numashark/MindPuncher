import pyxel

import controls
from constants import (
    CENTER_X, COLOR_ACCENT, COLOR_SUB_TEXT, COLOR_TEXT, SCALE, SCREEN_HEIGHT, SCREEN_WIDTH,
)
from render import draw_stage
from text import draw_text

HOWTO_PAGES = (
    ("あそびかた", (
        "てきを パンチでたおして 2ふんかん いきのころう！",
        "たおして スコアを かせごう！",
    )),
    ("そうさせつめい", (
        "Enter / Spaceで パンチ!",
        "ながおしで チャージ (おまけに まえからの ダメージが へる)",
    )),
    ("パンチのしゅるい", (
        "すぐ はなす : めのまえの てき 1たいに ふつうの パンチ",
        "すこしためて はなす : とどく てき ぜんいんに ちゅうパンチ",
        "(おまけに てき 1たいを ふきとばす)",
        "すごくためて はなす : ためるほど きょりが のびる だいパンチ",
        "(おまけに HPかいふく)",
    )),
    ("ヒント", (
        "とんでいる てきには パンチが あたらない  おりてきた ときを ねらおう",
        "あかい てきは とつげきしてくる! きをつけよう",
        "おおきい てき ほど こうげきが つよいから ちゅうい!",
        "ちゅうパンチで おおきい てきを ふきとばしてみよう",
        "だいパンチで たくさん てきを まきこんでみよう",
    )),
)
# ページ切り替えの矢印の、画面端からの距離と大きさ
HOWTO_ARROW_MARGIN = int(20 * SCALE)
HOWTO_ARROW_SIZE = int(20 * SCALE)


class HowtoScene:
    def __init__(self, app):
        """あそびかた画面を作る"""
        self.app = app
        self.page = 0

    def update(self):
        """左右キーでページを切り替え、決定キーでタイトルに戻る"""
        if controls.left_pressed():
            self.page = max(self.page - 1, 0)
        if controls.right_pressed():
            self.page = min(self.page + 1, len(HOWTO_PAGES) - 1)
        if controls.decide_pressed() or controls.backspace_pressed():
            self.app.show_title()

    def draw(self):
        """いまのページのあそびかたと、ページ切り替えの矢印を描画する"""
        draw_stage()
        title, lines = HOWTO_PAGES[self.page]
        draw_text(CENTER_X, SCREEN_HEIGHT * 0.08, title, COLOR_ACCENT, "m", center=True)
        y = SCREEN_HEIGHT * 0.22
        for line in lines:
            draw_text(CENTER_X, y, line, COLOR_TEXT, "howto", center=True)
            y += int(44 * SCALE)

        mid_y = SCREEN_HEIGHT // 2
        half = HOWTO_ARROW_SIZE // 2
        if self.page > 0:
            x = HOWTO_ARROW_MARGIN
            pyxel.tri(x, mid_y, x + half, mid_y - HOWTO_ARROW_SIZE, x + half, mid_y + HOWTO_ARROW_SIZE,
                      COLOR_ACCENT)
        if self.page < len(HOWTO_PAGES) - 1:
            x = SCREEN_WIDTH - HOWTO_ARROW_MARGIN
            pyxel.tri(x, mid_y, x - half, mid_y - HOWTO_ARROW_SIZE, x - half, mid_y + HOWTO_ARROW_SIZE,
                      COLOR_ACCENT)

        draw_text(CENTER_X, SCREEN_HEIGHT * 0.82, f"{self.page + 1} / {len(HOWTO_PAGES)}",
                  COLOR_SUB_TEXT, center=True)
        draw_text(CENTER_X, SCREEN_HEIGHT * 0.9, "A/D・←/→ : ページ   Enter / Space : もどる",
                  COLOR_SUB_TEXT, center=True)
