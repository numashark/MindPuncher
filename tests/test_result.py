import unittest
from unittest import mock

from constants import RESULT_INPUT_LOCK_FRAMES
from scenes.result import ResultScene


class FakeStore:
    """ランキングの保存先の代わりに、呼ばれた処理を記録する"""

    def __init__(self):
        self.calls = []
        self.rank_error = False

    def load(self):
        self.calls.append("load")
        return []

    def record_play(self, score, cleared):
        self.calls.append("record_play")

    def rank(self, board, score):
        self.calls.append("rank")
        return 1


class FakeApp:
    """スコア確認画面から呼ばれるアプリの代わり"""

    def __init__(self):
        self.ranking_store = FakeStore()
        self.ranking = None
        self.show_title = mock.Mock()


class TestResultLoading(unittest.TestCase):
    def test_does_not_load_when_created(self):
        """画面を作った時点では読み込みを行わず、読み込み中になる"""
        app = FakeApp()
        scene = ResultScene(app, 1000, 3, False)
        self.assertTrue(scene.loading)
        self.assertEqual(app.ranking_store.calls, [])

    def test_waits_until_loading_text_is_drawn(self):
        """読み込み中の表示を描画するまでは、更新が呼ばれても読み込みを行わない"""
        app = FakeApp()
        scene = ResultScene(app, 1000, 3, False)
        scene.update()
        scene.update()
        self.assertTrue(scene.loading)
        self.assertEqual(app.ranking_store.calls, [])

    def test_loads_after_loading_text_is_drawn(self):
        """読み込み中の表示を描画した後の更新でランキングの読み込み・プレイの記録・順位の計算を行う"""
        app = FakeApp()
        scene = ResultScene(app, 1000, 3, False)
        scene.loading_drawn = True
        scene.update()
        self.assertFalse(scene.loading)
        self.assertEqual(app.ranking_store.calls, ["load", "record_play", "rank"])
        self.assertEqual(app.ranking, [])
        self.assertEqual(scene.rank, 1)
        self.assertTrue(scene.entering)

    def test_ignores_input_after_loading(self):
        """読み込みが終わってから決められたフレーム数の間は操作を受け付けない"""
        app = FakeApp()
        app.ranking_store.load = lambda: [{"name": "A", "score": 99999, "clear": False}] * 5
        scene = ResultScene(app, 1000, 3, False)
        scene.loading_drawn = True
        scene.update()
        self.assertFalse(scene.entering)
        with mock.patch("controls.decide_pressed", return_value=True):
            for _ in range(RESULT_INPUT_LOCK_FRAMES):
                scene.update()
            app.show_title.assert_not_called()
            scene.update()
        app.show_title.assert_called_once()


if __name__ == "__main__":
    unittest.main()
