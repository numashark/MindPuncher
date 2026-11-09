import sys

import screen_mode


class App:
    def __init__(self):
        """Pyxelを初期化し、タイトル画面から始める"""
        import pyxel

        import ranking_store
        from constants import FPS, FULLSCREEN, SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE
        from text import load_fonts

        quit_key = pyxel.KEY_NONE if screen_mode.IS_WEB else pyxel.KEY_ESCAPE
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title=WINDOW_TITLE, fps=FPS, quit_key=quit_key)
        if FULLSCREEN and not screen_mode.IS_WEB:
            pyxel.fullscreen(True)
        load_fonts()
        self.ranking_store = ranking_store.create()
        self.ranking = self.ranking_store.load()
        self.scene = None
        self.show_title()

    def run(self):
        """ゲームループを開始する"""
        import pyxel
        pyxel.run(self.update, self.draw)

    def update(self):
        """現在の画面を更新する"""
        self.scene.update()

    def draw(self):
        """現在の画面を描画する"""
        self.scene.draw()

    def show_title(self):
        """タイトル画面に移る"""
        from scenes.title import TitleScene
        self.scene = TitleScene(self)

    def show_howto(self):
        """あそびかた画面に移る"""
        from scenes.howto import HowtoScene
        self.scene = HowtoScene(self)

    def show_ranking(self, highlight=-1, reload=False):
        """ランキング画面に移る。highlight は強調表示する順位（0始まり）、reload がTrueならランキングを読み込みなおす"""
        from scenes.ranking_scene import RankingScene
        if reload:
            self.ranking = self.ranking_store.load()
        self.scene = RankingScene(self, highlight)

    def start_play(self):
        """ゲームを開始する"""
        from scenes.play import PlayScene
        self.scene = PlayScene(self)

    def show_result(self, score, max_combo, cleared):
        """スコア確認画面に移る。max_combo はプレイ中の最大コンボ数、cleared はゲームクリアしたかどうか"""
        from scenes.result import ResultScene
        self.ranking = self.ranking_store.load()
        self.scene = ResultScene(self, score, max_combo, cleared)

    def save_score(self, name, score, cleared):
        """スコアをランキングに登録して保存し、登録された順位（0始まり）を返す。cleared はゲームクリアしたかどうか"""
        self.ranking, index = self.ranking_store.add(self.ranking, name, score, cleared)
        return index


def main():
    """画面モードを選ばせてからゲームを起動する"""
    screen_mode.enable_dpi_awareness()
    if not screen_mode.select():
        sys.exit()
    App().run()


if __name__ == "__main__":
    main()
