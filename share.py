from urllib.parse import quote, urlencode

from constants import SHARE_GAME_URL, SHARE_INTENT_URL


LOGO_FILL = "fill"
LOGO_OUTLINE = "outline"
LOGO_ACCENT = "accent"

# Xのロゴの太い線（左上から右下）の形。# が黒く塗る部分
X_LOGO_BAND = (
    "######.........",
    ".######........",
    ".######........",
    "..######.......",
    "...######......",
    "...######......",
    "....######.....",
    "....######.....",
    ".....######....",
    "......######...",
    "......######...",
    ".......######..",
    "........######.",
    "........######.",
    ".........######",
)
# Xのロゴの細い線（右上から左下）の形。太い線の縁取りで2つに分かれて見える
X_LOGO_STROKE = (
    ".............##",
    "............##.",
    "...........##..",
    "..........##...",
    ".........##....",
    "........##.....",
    ".......##......",
    "......##.......",
    ".....##........",
    "....##.........",
    "...##..........",
    "..##...........",
    ".##............",
    "##.............",
    "#..............",
)
X_LOGO_SIZE = len(X_LOGO_BAND) + 2


def logo_part_dots(shape):
    """ロゴの線の形 shape から、塗る部分と、その周りの縁取りのドットを {(x, y): 種類} で返す。
    縁取りのうち線の右下側にあるものは水色を混ぜるドットにする。座標は縁取りの分だけ右下にずらす"""
    filled = {(x, y) for y, row in enumerate(shape) for x, ch in enumerate(row) if ch == "#"}
    dots = {}
    for x, y in filled:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                p = (x + dx, y + dy)
                if p in filled or p in dots:
                    continue
                px, py = p
                lower_right = (((px - 1, py) in filled or (px, py - 1) in filled)
                               and (px + 1, py) not in filled and (px, py + 1) not in filled)
                dots[p] = LOGO_ACCENT if lower_right else LOGO_OUTLINE
    for p in filled:
        dots[p] = LOGO_FILL
    return {(x + 1, y + 1): kind for (x, y), kind in dots.items()}


def x_logo_dots():
    """ドット絵のXのロゴのドットを {(x, y): 種類} で返す。細い線の上に太い線を重ねる"""
    dots = logo_part_dots(X_LOGO_STROKE)
    dots.update(logo_part_dots(X_LOGO_BAND))
    return dots


def share_text(score, max_combo, survival_seconds, cleared, rank):
    """Xに投稿する本文を作る。cleared がTrueなら生存時間の代わりにクリアと書き、rank がNoneなら順位の行を省く"""
    survival = "クリア！" if cleared else f"{survival_seconds}秒"
    lines = [
        "#MindPuncher #ゲーム",
        "MindPuncherをプレイ！",
        f"スコア: {score}",
        f"最大コンボ: {max_combo}",
        f"生存時間: {survival}",
    ]
    if rank:
        lines.append(f"順位: {rank}位")
    return "\n".join(lines)


def share_url(text):
    """本文 text とゲームのURLを入れたXの投稿画面のURLを作る"""
    return f"{SHARE_INTENT_URL}?{urlencode({'text': text, 'url': SHARE_GAME_URL}, quote_via=quote)}"


def open_share(url):
    """Web版でXの投稿画面を新しいタブで開く"""
    import js
    js.window.open(url, "_blank")
