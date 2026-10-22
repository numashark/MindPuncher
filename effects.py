import random

import pyxel

from constants import (
    BIG, BIG_SHOCK_FRAMES, BIG_SHOCK_WAVES, BIG_WIND_COUNT, BIG_WIND_FRAMES, BIG_WIND_SPEED, CENTER_X,
    COLOR_GUARD, COLOR_TEXT_SHADOW, COLOR_TRAIL, COLOR_WIND, ENEMY_BODY_COLOR, ENEMY_HEIGHT,
    FLOAT_TEXT_FADE_FRAMES, FLOAT_TEXT_FRAMES, FLOAT_TEXT_RISE_SPEED, GROUND_Y,
    GUARD_PARTICLE_COUNT, HIT_EFFECT_RADIUS, HIT_RING_COLOR, KILL_PARTICLE_COUNT, LARGE, PLAYER_HALF_WIDTH,
    PLAYER_HEIGHT, PUNCH_COLOR, SCALE,
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
        self.shocks = []
        self.winds = []

    def add_big_punch(self, facing, reach):
        """大パンチの射程に、走り抜ける衝撃波と風圧の筋を出す"""
        x1 = CENTER_X + facing * PLAYER_HALF_WIDTH
        x2 = CENTER_X + facing * (PLAYER_HALF_WIDTH + reach)
        top = GROUND_Y - ENEMY_HEIGHT[LARGE] - int(14 * SCALE)
        self.shocks.append({"x1": x1, "x2": x2, "top": top, "life": BIG_SHOCK_FRAMES})
        for _ in range(BIG_WIND_COUNT):
            self.winds.append({
                "x": x1 + (x2 - x1) * self.rng.uniform(0, 0.4), "y": self.rng.uniform(top, GROUND_Y - 2 * SCALE),
                "x2": x2, "vx": facing * BIG_WIND_SPEED * self.rng.uniform(0.7, 1.3),
                "length": self.rng.uniform(20, 50) * SCALE, "color": self.rng.choice(COLOR_WIND),
                "life": self.rng.randint(BIG_WIND_FRAMES // 2, BIG_WIND_FRAMES),
            })

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
        for s in self.shocks:
            s["life"] -= 1
        self.shocks = [s for s in self.shocks if s["life"] > 0]
        for w in self.winds:
            w["x"] += w["vx"]
            w["life"] -= 1
        self.winds = [w for w in self.winds if w["life"] > 0 and (w["x2"] - w["x"]) * w["vx"] > 0]

    def draw_big_punch(self):
        """大パンチの衝撃波と風圧の筋を描画する"""
        for s in self.shocks:
            progress = 1 - s["life"] / BIG_SHOCK_FRAMES
            left, right = min(s["x1"], s["x2"]), max(s["x1"], s["x2"])
            height = GROUND_Y - s["top"]
            pyxel.dither(0.35 * (1 - progress) ** 2)
            pyxel.rect(left, s["top"], right - left, height, 7)
            pyxel.dither(1.0)
            for i in range(BIG_SHOCK_WAVES):
                p = progress * 1.6 - i * 0.2
                if not 0 <= p <= 1:
                    continue
                x = s["x1"] + (s["x2"] - s["x1"]) * p
                w = int((10 + 20 * p) * SCALE)
                pyxel.ellib(x - w // 2, s["top"], w, height, PUNCH_COLOR[BIG] if i == 0 else 7)
        for w in self.winds:
            pyxel.dither(min(1.0, w["life"] / (BIG_WIND_FRAMES / 2)))
            tail = w["x"] - (w["length"] if w["vx"] > 0 else -w["length"])
            pyxel.line(tail, w["y"], w["x"], w["y"], w["color"])
        pyxel.dither(1.0)

    def draw(self):
        """演出を描画する"""
        self.draw_big_punch()
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
