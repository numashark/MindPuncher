import random

import pyxel

from constants import (
    CENTER_X, COLOR_GUARD, COLOR_TEXT_SHADOW, COLOR_TRAIL, ENEMY_BODY_COLOR, FLOAT_TEXT_FADE_FRAMES,
    FLOAT_TEXT_FRAMES, FLOAT_TEXT_RISE_SPEED, GROUND_Y,
    GUARD_PARTICLE_COUNT, HIT_EFFECT_RADIUS, HIT_RING_COLOR, KILL_PARTICLE_COUNT, PLAYER_HALF_WIDTH,
    PLAYER_HEIGHT, SCALE,
)
from text import draw_text


def enemy_center_y(enemy):
    """敵の中心のy座標を返す"""
    return GROUND_Y - enemy.altitude - enemy.height / 2


class Effects:
    def __init__(self, rng=None):
        """演出（ヒットエフェクト、粒、浮かぶ文字）の管理を初期化する"""
        self.rng = rng or random.Random()
        self.rings = []
        self.particles = []
        self.texts = []

    def add_ring(self, enemy, kind, life):
        """パンチが当たった敵の位置に、威力とヒットストップに応じた衝撃の輪を出す"""
        radius = HIT_EFFECT_RADIUS[kind] * (1 + 0.25 * enemy.size)
        self.rings.append({"x": enemy.x - enemy.side * enemy.width / 2, "y": enemy_center_y(enemy),
                           "radius": radius, "life": life, "total": life, "color": HIT_RING_COLOR[kind]})

    def add_particle(self, x, y, color, life, vx, vy, gravity=True):
        """粒を1つ出す"""
        self.particles.append({"x": x, "y": y, "vx": vx, "vy": vy, "color": color, "life": life,
                               "gravity": gravity})

    def add_sparks(self, enemy, count):
        """敵のプレイヤー側の面から火花を出す"""
        x = enemy.x - enemy.side * enemy.width / 2
        y = enemy_center_y(enemy)
        for _ in range(count):
            self.add_particle(x, y, self.rng.choice((7, 10)), self.rng.randint(8, 16),
                              enemy.side * self.rng.uniform(0, 5) * SCALE, self.rng.uniform(-4, 2) * SCALE)

    def add_burst(self, enemy):
        """倒した敵の位置から粒を飛び散らせる"""
        colors = (7, 10, 9, ENEMY_BODY_COLOR[enemy.kind])
        for _ in range(KILL_PARTICLE_COUNT):
            self.add_particle(enemy.x, enemy_center_y(enemy), self.rng.choice(colors), self.rng.randint(15, 30),
                              self.rng.uniform(-4, 4) * SCALE, self.rng.uniform(-6, -1) * SCALE)

    def add_guard(self, facing):
        """プレイヤーの前方にガードの粒を出す"""
        x = CENTER_X + facing * (PLAYER_HALF_WIDTH + int(10 * SCALE))
        y = GROUND_Y - PLAYER_HEIGHT // 2
        for _ in range(GUARD_PARTICLE_COUNT):
            self.add_particle(x, y, COLOR_GUARD, 12, facing * self.rng.uniform(1, 4) * SCALE,
                              self.rng.uniform(-4, 1) * SCALE)

    def add_knock_trail(self, enemy):
        """吹き飛んでいる敵の足元に水色の粒を出す"""
        self.add_particle(enemy.x, GROUND_Y - enemy.altitude, COLOR_TRAIL, 10,
                          -enemy.side * self.rng.uniform(0, 2) * SCALE, -self.rng.uniform(1, 3) * SCALE)

    def add_text(self, x, y, text, color):
        """浮かんで消える文字を出す"""
        self.texts.append({"x": x, "y": y, "text": text, "color": color, "life": FLOAT_TEXT_FRAMES})

    def text_alpha(self, t):
        """浮かぶ文字の濃さ（0～1）を返す。最後の数フレームでだんだん薄くなる"""
        return min(1.0, t["life"] / FLOAT_TEXT_FADE_FRAMES)

    def update(self):
        """演出を1フレーム進める"""
        for ring in self.rings:
            ring["life"] -= 1
        self.rings = [r for r in self.rings if r["life"] > 0]
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["gravity"]:
                p["vy"] += 0.3 * SCALE
            p["life"] -= 1
        self.particles = [p for p in self.particles if p["life"] > 0]
        for t in self.texts:
            t["y"] -= FLOAT_TEXT_RISE_SPEED * t["life"] / FLOAT_TEXT_FRAMES
            t["life"] -= 1
        self.texts = [t for t in self.texts if t["life"] > 0]

    def draw(self):
        """演出を描画する"""
        for ring in self.rings:
            progress = 1 - ring["life"] / ring["total"]
            r = int(ring["radius"] * (0.3 + 0.7 * progress))
            pyxel.circb(ring["x"], ring["y"], r, ring["color"])
            if ring["radius"] > 20 * SCALE:
                pyxel.circb(ring["x"], ring["y"], max(1, r - int(4 * SCALE)), 7)
            for i in range(8):
                angle = i * 45 + 22
                r1, r2 = r * 0.6, r * 1.15
                pyxel.line(ring["x"] + pyxel.cos(angle) * r1, ring["y"] + pyxel.sin(angle) * r1,
                           ring["x"] + pyxel.cos(angle) * r2, ring["y"] + pyxel.sin(angle) * r2,
                           ring["color"])
        size = max(1, int(2 * SCALE))
        for p in self.particles:
            pyxel.rect(int(p["x"]), int(p["y"]), size, size, p["color"])
        shadow = max(1, int(SCALE))
        for t in self.texts:
            pyxel.dither(self.text_alpha(t))
            draw_text(t["x"] + shadow, t["y"] + shadow, t["text"], COLOR_TEXT_SHADOW, center=True)
            draw_text(t["x"], t["y"], t["text"], t["color"], center=True)
        pyxel.dither(1.0)
