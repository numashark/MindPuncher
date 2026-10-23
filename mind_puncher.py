import sys

import screen_mode


class App:
    def __init__(self):
        """Pyxelを初期化し、タイトル画面から始める"""
        import pyxel

        import ranking
        from constants import FPS, FULLSCREEN, SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE
        from text import load_fonts

        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title=WINDOW_TITLE, fps=FPS, quit_key=pyxel.KEY_ESCAPE)
        if FULLSCREEN:
            pyxel.fullscreen(True)
        load_fonts()
        self.ranking_path = ranking.default_path()
        self.ranking = ranking.load(self.ranking_path)
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

    def show_ranking(self, highlight=-1):
        """ランキング画面に移る。highlight は強調表示する順位（0始まり）"""
        from scenes.ranking_scene import RankingScene
        self.scene = RankingScene(self, highlight)

    def start_play(self):
        """ゲームを開始する"""
        from scenes.play import PlayScene
        self.scene = PlayScene(self)

    def show_result(self, score, cleared):
        """スコア確認画面に移る。cleared はゲームクリアしたかどうか"""
        from scenes.result import ResultScene
        self.scene = ResultScene(self, score, cleared)

    def save_score(self, name, score):
        """スコアをランキングに登録して保存し、登録された順位（0始まり）を返す"""
        import ranking
        self.ranking, index = ranking.insert(self.ranking, name, score)
        ranking.save(self.ranking_path, self.ranking)
        return index


def main():
    """画面モードを選ばせてからゲームを起動する"""
    screen_mode.enable_dpi_awareness()
    if not screen_mode.select():
        sys.exit()
    App().run()


if __name__ == "__main__":
    main()
