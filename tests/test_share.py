import unittest
from urllib.parse import parse_qs, urlparse

from share import share_text, share_url


class TestShareText(unittest.TestCase):
    def test_game_over_text(self):
        """ゲームオーバーのときはスコア、最大コンボ、生存時間、順位を書く"""
        self.assertEqual(
            share_text(12345, 23, 87, False, 5),
            "MindPuncherをプレイ！\nスコア: 12345\n最大コンボ: 23\n生存時間: 87秒\n順位: 5位",
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


if __name__ == "__main__":
    unittest.main()
