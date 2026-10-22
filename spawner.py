import random

from constants import (
    ENEMY_HP_WEIGHTS_END, ENEMY_HP_WEIGHTS_START, ENEMY_KIND_WEIGHTS, ENEMY_KINDS,
    ENEMY_SIZE_WEIGHTS, GAME_FRAMES, LARGE, MEDIUM, SMALL, SPAWN_INTERVAL_END,
    SPAWN_INTERVAL_START,
)
from enemy import Enemy


def lerp(start, end, rate):
    """start から end までを rate (0～1) の割合で補間した値を返す"""
    return start + (end - start) * rate


class Spawner:
    def __init__(self, rng=None):
        """敵の出現管理を初期化する。rng には乱数生成器を渡せる"""
        self.rng = rng or random.Random()
        self.timer = SPAWN_INTERVAL_START
        self.count = 0

    def update(self, frame):
        """経過フレーム数に応じて敵を出現させ、新しく出現した敵のリストを返す"""
        self.timer -= 1
        if self.timer > 0:
            return []
        progress = min(1.0, frame / GAME_FRAMES)
        self.timer = int(lerp(SPAWN_INTERVAL_START, SPAWN_INTERVAL_END, progress))
        return [self.create_enemy(progress)]

    def create_enemy(self, progress):
        """進行度 progress (0～1) に応じた体力の敵を1体作る"""
        hp_weights = [lerp(s, e, progress) for s, e in zip(ENEMY_HP_WEIGHTS_START, ENEMY_HP_WEIGHTS_END)]
        hp = self.rng.choices((1, 2, 3), hp_weights)[0]
        kind = self.rng.choices(ENEMY_KINDS, ENEMY_KIND_WEIGHTS)[0]
        size = self.rng.choices((SMALL, MEDIUM, LARGE), ENEMY_SIZE_WEIGHTS)[0]
        side = self.rng.choice((-1, 1))
        self.count += 1
        return Enemy(kind, size, side, hp, self.count)
