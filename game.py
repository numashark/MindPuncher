from combat import enemy_attack, release_punch, update_knockback
from constants import FPS, GAME_FRAMES
from effects import Effects
from player import Player
from score import ScoreBoard
from spawner import Spawner

GAME_OVER = "game_over"
CLEAR = "clear"


class Game:
    def __init__(self, rng=None):
        """1プレイ分のゲーム状態を作る"""
        self.player = Player()
        self.enemies = []
        self.score = ScoreBoard()
        self.spawner = Spawner(rng)
        self.effects = Effects(rng)
        self.frame = 0
        self.hitstop = 0
        self.shake = 0
        self.result = None

    def remaining_seconds(self):
        """残り時間を秒で返す"""
        return max(0, -(-(GAME_FRAMES - self.frame) // FPS))

    def survival_seconds(self):
        """ゲームが始まってから生き残った時間を秒で返す"""
        return self.frame // FPS

    def update(self, inputs):
        """入力 inputs をもとにゲームを1フレーム進める"""
        if self.result:
            return
        self.effects.update()
        if self.shake > 0:
            self.shake -= 1
        if self.hitstop > 0:
            self.hitstop -= 1
            return
        self.frame += 1

        player = self.player
        if inputs.left:
            player.turn(-1)
        if inputs.right:
            player.turn(1)
        hold = player.update_charge(inputs.punch_pressed, inputs.punch_held)
        player.update_timers()
        if hold is not None:
            release_punch(self, hold)
        player.update_stamina()

        self.enemies.extend(self.spawner.update(self.frame))
        for enemy in list(self.enemies):
            if enemy.dead:
                continue
            enemy.update_flash()
            if enemy.knocked:
                update_knockback(self, enemy)
            elif enemy.update():
                enemy_attack(self, enemy)
                if player.hp <= 0:
                    self.result = GAME_OVER
                    break
        self.enemies = [e for e in self.enemies if not e.dead]

        if self.result is None and self.frame >= GAME_FRAMES:
            self.result = CLEAR
