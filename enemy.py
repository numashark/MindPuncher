from constants import (
    CENTER_X, CHARGER, CHARGER_AIM_DISTANCE, CHARGER_AIM_FRAMES, CHARGER_DASH_SPEED, ENEMY_HEIGHT,
    ENEMY_PARAMS, ENEMY_WIDTH, FLYER, FLYER_CYCLE_FRAMES, FLYER_HIGH_ALTITUDE, FLYER_LOW_ALTITUDE,
    FLYER_MOVE_FRAMES, HIT_PUSH_DECAY, HIT_PUSH_SPEED, MIN_RANGE, PLAYER_HALF_WIDTH, SCREEN_WIDTH,
    SIZE_DAMAGE_BONUS, SIZE_SPEED_RATE,
)

APPROACH, AIM, DASH, CLOSE = "approach", "aim", "dash", "close"


class Enemy:
    def __init__(self, kind, size, side, hp, order):
        """敵を画面外に作る。side は -1 が左側、1 が右側、order は出現順"""
        self.kind = kind
        self.size = size
        self.side = side
        self.hp = hp
        self.max_hp = hp
        self.order = order
        self.width = ENEMY_WIDTH[size]
        self.height = ENEMY_HEIGHT[size]
        self.x = CENTER_X + side * (SCREEN_WIDTH // 2 + self.width)
        params = ENEMY_PARAMS[kind]
        self.speed = params["speed"] * SIZE_SPEED_RATE[size]
        self.damage = params["damage"] + SIZE_DAMAGE_BONUS[size]
        self.attack_range = params["attack_range"]
        self.attack_interval = params["attack_interval"]
        self.windup_frames = params["windup"]
        self.attack_timer = params["first_attack_delay"]
        self.windup = 0
        self.state = APPROACH if kind == CHARGER else CLOSE
        self.state_timer = 0
        self.push = 0
        self.cycle = FLYER_MOVE_FRAMES
        self.altitude = FLYER_HIGH_ALTITUDE if kind == FLYER else 0
        self.knocked = False
        self.knock_hits = set()
        self.flash = 0
        self.dead = False

    def distance(self):
        """プレイヤーとの距離（お互いの端どうし）を返す"""
        return abs(self.x - CENTER_X) - self.width / 2 - PLAYER_HALF_WIDTH

    def set_distance(self, distance):
        """プレイヤーとの距離が distance になる位置に移動する"""
        self.x = CENTER_X + self.side * (PLAYER_HALF_WIDTH + self.width / 2 + distance)

    def in_min_range(self):
        """パンチの最低射程内にいるかを返す"""
        return self.distance() <= MIN_RANGE

    def left(self):
        """左端のx座標を返す"""
        return self.x - self.width / 2

    def right(self):
        """右端のx座標を返す"""
        return self.x + self.width / 2

    def update_flash(self):
        """被弾時の点滅の残りフレーム数を減らす"""
        if self.flash > 0:
            self.flash -= 1

    def is_warning(self):
        """攻撃の予備動作中（点滅させる状態）かを返す"""
        return self.windup > 0 or self.state == AIM

    def hit_push(self):
        """ダメージを受けてプレイヤーと反対方向にノックバックし始める。予備動作は中断される"""
        self.push = HIT_PUSH_SPEED
        self.windup = 0

    def move_toward(self, speed):
        """プレイヤーに近づく。攻撃射程に入ったら射程の位置で止まり、射程内にいればTrueを返す"""
        if self.distance() > self.attack_range:
            self.x -= self.side * speed
            if self.distance() > self.attack_range:
                return False
            self.set_distance(self.attack_range)
        return True

    def update(self):
        """移動と攻撃のタイミングを進める。このフレームで攻撃するならTrueを返す"""
        if self.kind == FLYER:
            self.update_altitude()
        if self.push > 0:
            self.update_push()
            return False
        if self.state != CLOSE:
            return self.update_charger()
        if self.windup > 0:
            self.windup -= 1
            if self.windup == 0:
                self.attack_timer = self.attack_interval
                return True
            return False
        if not self.move_toward(self.speed):
            return False
        if self.attack_timer > 0:
            self.attack_timer -= 1
            return False
        self.windup = self.windup_frames
        return False

    def update_push(self):
        """ノックバック中の移動を進める"""
        self.x += self.side * self.push
        self.x = max(self.width / 2, min(SCREEN_WIDTH - self.width / 2, self.x))
        self.push *= HIT_PUSH_DECAY
        if self.push < 0.5:
            self.push = 0

    def update_charger(self):
        """突進する敵の、近づく・構える・突進するの流れを進める。突進が届いたらTrueを返す"""
        if self.state == APPROACH:
            self.move_toward(self.speed)
            if self.distance() <= CHARGER_AIM_DISTANCE:
                self.state = AIM
                self.state_timer = CHARGER_AIM_FRAMES
        elif self.state == AIM:
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.state = DASH
        elif self.move_toward(CHARGER_DASH_SPEED * SIZE_SPEED_RATE[self.size]):
            self.state = CLOSE
            self.attack_timer = self.attack_interval
            return True
        return False

    def update_altitude(self):
        """飛行する敵の急上昇と急降下を一定間隔で繰り返す"""
        self.cycle = (self.cycle + 1) % FLYER_CYCLE_FRAMES
        half = FLYER_CYCLE_FRAMES // 2
        if self.cycle < FLYER_MOVE_FRAMES:
            rate = self.cycle / FLYER_MOVE_FRAMES
            self.altitude = FLYER_LOW_ALTITUDE + (FLYER_HIGH_ALTITUDE - FLYER_LOW_ALTITUDE) * rate
        elif self.cycle < half:
            self.altitude = FLYER_HIGH_ALTITUDE
        elif self.cycle < half + FLYER_MOVE_FRAMES:
            rate = (self.cycle - half) / FLYER_MOVE_FRAMES
            self.altitude = FLYER_HIGH_ALTITUDE - (FLYER_HIGH_ALTITUDE - FLYER_LOW_ALTITUDE) * rate
        else:
            self.altitude = FLYER_LOW_ALTITUDE
