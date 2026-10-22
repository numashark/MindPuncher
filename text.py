import pyxel

from constants import FONT_PATH, FONT_SIZES

_fonts = {}


def load_fonts():
    """フォントを大きさごとに読み込む"""
    for name, size in FONT_SIZES.items():
        _fonts[name] = pyxel.Font(str(FONT_PATH), size)


def text_width(s, size="s"):
    """文字列を描画したときの幅を返す"""
    return _fonts[size].text_width(s)


def draw_text(x, y, s, color, size="s", center=False):
    """文字列を描画する。center がTrueなら x を中央として描画する"""
    if center:
        x -= text_width(s, size) // 2
    pyxel.text(int(x), int(y), s, color, _fonts[size])
