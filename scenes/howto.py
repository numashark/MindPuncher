import controls
from constants import CENTER_X, COLOR_ACCENT, COLOR_SUB_TEXT, COLOR_TEXT, SCALE, SCREEN_HEIGHT
from render import draw_stage
from text import draw_text

HOWTO_LINES = (
    "ひだりと みぎから くる てきを パンチで たおして スコアを かせごう！ 1プレイ 120びょう",
    "A / D ・ ← / → : ふりむき",
    "Enter / Space : パンチ ながおしで チャージ (おまけに まえからの ダメージが へる)",
    "すぐ はなす : ふつうパンチ めのまえの てき 1たいに よわいダメージ",
    "すこしためて はなす : ちゅうパンチ  とどく てき ぜんいんに ダメージ & (おまけに てき 1たいを ふきとばす)",
    "すごくためて はなす : だいパンチ  ためるほど きょりが のびる いちげきひっさつ (おまけに HPかいふくつき)",
    "とんでいる てきには パンチが あたらない  おりてきた ときを ねらおう",
    "てきの あたまの うえの バーは のこりの たいりょく",
    "ダメージを うけずに たおしつづけると コンボボーナス！こうとくてんを ねらおう",
)


class HowtoScene:
    def __init__(self, app):
        """あそびかた画面を作る"""
        self.app = app

    def update(self):
        """決定キーでタイトルに戻る"""
        if controls.decide_pressed() or controls.backspace_pressed():
            self.app.show_title()

    def draw(self):
        """あそびかたを描画する"""
        draw_stage()
        draw_text(CENTER_X, SCREEN_HEIGHT * 0.08, "あそびかた", COLOR_ACCENT, "m", center=True)
        y = SCREEN_HEIGHT * 0.2
        for line in HOWTO_LINES:
            draw_text(CENTER_X, y, line, COLOR_TEXT, "m", center=True)
            y += int(30 * SCALE)
        draw_text(CENTER_X, SCREEN_HEIGHT * 0.9, "Enter / Space : もどる", COLOR_SUB_TEXT, center=True)
