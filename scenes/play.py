import random

import pyxel

import controls
from constants import CENTER_X, COLOR_ACCENT, COLOR_DANGER, FINISH_TEXT_FRAMES, SCALE, SCREEN_HEIGHT
from game import CLEAR, Game
from hud import draw_danger_border, draw_hud, draw_range, draw_retry_hint
from render import draw_enemies, draw_player, draw_punch_wave, draw_stage
from text import draw_text


class PlayScene:
    def __init__(self, app):
        """ゲーム画面を作り、1プレイを開始する"""
        self.app = app
        self.game = Game()
        self.finish_timer = 0

    def update(self):
        """ゲームを進め、終了したらテキスト表示の後にスコア確認画面へ移る。Rキーで最初からやり直す"""
        if controls.retry_pressed():
            self.app.start_play()
            return
        if self.game.result is None:
            self.game.update(controls.read_play_inputs())
            return
        self.finish_timer += 1
        if self.finish_timer >= FINISH_TEXT_FRAMES:
            self.app.show_result(self.game.score.score, self.game.result == CLEAR)

    def draw(self):
        """ゲーム画面を描画する"""
        game = self.game
        shake = int(game.shake * SCALE) if game.result is None else 0
        if shake > 0:
            pyxel.camera(random.randint(-shake, shake), random.randint(-shake, shake))
        draw_stage()
        draw_enemies(game.enemies)
        if game.result is None:
            draw_range(game)
        draw_punch_wave(game.player)
        draw_player(game.player)
        game.effects.draw()
        pyxel.camera()
        draw_hud(game)
        draw_retry_hint()
        draw_danger_border(game.player, game.frame)
        if game.result == CLEAR:
            draw_text(CENTER_X, SCREEN_HEIGHT * 0.38, "CLEAR!", COLOR_ACCENT, "l", center=True)
        elif game.result is not None:
            draw_text(CENTER_X, SCREEN_HEIGHT * 0.38, "GAME OVER", COLOR_DANGER, "l", center=True)
