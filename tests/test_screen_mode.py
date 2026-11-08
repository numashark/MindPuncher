import sys
import types
import unittest
from unittest import mock

import screen_mode


class TestScreenMode(unittest.TestCase):
    def setUp(self):
        """テスト前の画面モードを覚えておく"""
        self.saved = screen_mode.fullscreen

    def tearDown(self):
        """テスト後に画面モードを元に戻す"""
        screen_mode.fullscreen = self.saved

    def select_on_web(self, window):
        """ブラウザの window を差し替えて、Web版として画面モードを選ぶ"""
        fake_js = types.SimpleNamespace(window=window)
        with mock.patch.object(screen_mode, "IS_WEB", True), mock.patch.dict(sys.modules, {"js": fake_js}):
            return screen_mode.select()

    def test_web_uses_fullscreen_chosen_on_page(self):
        """Web版は起動ページでフルスクリーンが選ばれていればフルスクリーンになる"""
        window = types.SimpleNamespace(**{screen_mode.WEB_FULLSCREEN_FLAG: True})
        self.assertTrue(self.select_on_web(window))
        self.assertTrue(screen_mode.fullscreen)

    def test_web_defaults_to_window(self):
        """Web版で起動ページの選択がないときはウィンドウモードになる"""
        self.assertTrue(self.select_on_web(types.SimpleNamespace()))
        self.assertFalse(screen_mode.fullscreen)

    def test_desktop_uses_dialog(self):
        """PC版はダイアログの選択を使い、閉じられたら起動しない"""
        with mock.patch.object(screen_mode, "IS_WEB", False):
            with mock.patch.object(screen_mode, "select_by_dialog", return_value=True):
                self.assertTrue(screen_mode.select())
                self.assertTrue(screen_mode.fullscreen)
            with mock.patch.object(screen_mode, "select_by_dialog", return_value=None):
                self.assertFalse(screen_mode.select())


if __name__ == "__main__":
    unittest.main()
