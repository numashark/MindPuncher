import unittest
from urllib.parse import parse_qs, urlparse

from share import LOGO_ACCENT, LOGO_FILL, LOGO_OUTLINE, X_LOGO_SIZE, share_text, share_url, x_logo_dots


class TestShareText(unittest.TestCase):
    def test_game_over_text(self):
        """ゲームオーバーのときはハッシュタグ、スコア、最大コンボ、生存時間、順位を書く"""
        self.assertEqual(
            share_text(12345, 23, 87, False, 5),
            "#MindPuncher #ゲーム\nMindPuncherをプレイ！\nスコア: 12345\n最大コンボ: 23\n生存時間: 87秒\n順位: 5位",
        )

    def test_clear_text(self):
        """クリアしたときは生存時間の代わりにクリアと書く"""
        self.assertIn("生存時間: クリア！", share_text(30000, 40, 120, True, 1))

    def test_no_rank(self):
        """順位がわからないときは順位の行を省く"""
        self.assertNotIn("順位", share_text(100, 1, 10, False, None))


class TestShareUrl(unittest.TestCase):
    def test_url_has_text_and_game_url(self):
        """投稿画面のURLに本文とゲームのURLが入る"""
        url = urlparse(share_url("スコア: 1\n順位: 2位"))
        self.assertEqual(f"{url.scheme}://{url.netloc}{url.path}", "https://x.com/intent/tweet")
        query = parse_qs(url.query)
        self.assertEqual(query["text"], ["スコア: 1\n順位: 2位"])
        self.assertEqual(query["url"], ["https://numashark.github.io/MindPuncher/"])
        self.assertNotIn("+", url.query)


class TestXLogo(unittest.TestCase):
    def test_dots_inside_logo(self):
        """ロゴのドットはすべてロゴの大きさの中に収まる"""
        for x, y in x_logo_dots():
            self.assertTrue(0 <= x < X_LOGO_SIZE and 0 <= y < X_LOGO_SIZE)

    def test_fill_is_surrounded_by_outline(self):
        """黒く塗る部分の上下左右は、塗る部分か縁取り（白または水色）で囲まれている"""
        dots = x_logo_dots()
        for (x, y), kind in dots.items():
            if kind != LOGO_FILL:
                continue
            for p in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                self.assertIn(dots.get(p), (LOGO_FILL, LOGO_OUTLINE, LOGO_ACCENT))

    def test_accent_is_a_little(self):
        """水色のドットは縁取りに少しだけ混ぜる"""
        kinds = list(x_logo_dots().values())
        self.assertGreater(kinds.count(LOGO_ACCENT), 0)
        self.assertLess(kinds.count(LOGO_ACCENT), kinds.count(LOGO_OUTLINE) // 2)


if __name__ == "__main__":
    unittest.main()
