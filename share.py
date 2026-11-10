from urllib.parse import quote, urlencode

from constants import SHARE_GAME_URL, SHARE_INTENT_URL


def share_text(score, max_combo, survival_seconds, cleared, rank):
    """Xに投稿する本文を作る。cleared がTrueなら生存時間の代わりにクリアと書き、rank がNoneなら順位の行を省く"""
    survival = "クリア！" if cleared else f"{survival_seconds}秒"
    lines = [
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
