import math

from constants import (
    EXTRA_STAMINA_FRAMES, LOW_HP, MAX_HP, MAX_STAMINA, NO_STAMINA_CHARGE_LIMIT, NORMAL,
    PUNCH_COST, STAMINA_REGEN, STAMINA_REGEN_LOW_HP,
)
from punch import affordable_kind, punch_range


class Player:
    def __init__(self):
        """プレイヤーを初期状態にする"""
        self.hp = MAX_HP
        self.stamina = MAX_STAMINA
        self.extra_stamina = 0
        self.extra_timer = 0
        self.facing = 1
        self.charging = False
        self.hold = 0
        self.punch_anim = 0
        self.last_punch = None
        self.hurt = 0

    def total_stamina(self):
        """上限を超えた分も含めた現在のスタミナを返す"""
        return self.stamina + self.extra_stamina

    def extra_total(self):
        """上限を超えた分のスタミナの合計を返す"""
        return self.extra_stamina

    def can_punch(self):
        """通常パンチを出せるだけのスタミナがあるかを返す"""
        return self.total_stamina() >= PUNCH_COST[NORMAL]

    def is_guarding(self):
        """前方ガード中かを返す"""
        if not self.charging:
            return False
        return self.can_punch() or self.hold < NO_STAMINA_CHARGE_LIMIT

    def turn(self, direction):
        """向きを変える。direction は -1 が左、1 が右"""
        self.facing = direction

    def update_charge(self, pressed, held):
        """パンチキーの状態でチャージを進める。キーを離したらそれまでの長押しフレーム数を返す"""
        if self.charging:
            if held:
                self.hold += 1
                if not self.can_punch():
                    self.hold = min(self.hold, NO_STAMINA_CHARGE_LIMIT)
                return None
            self.charging = False
            hold = self.hold
            self.hold = 0
            return hold
        if pressed:
            self.charging = True
            self.hold = 1
        return None

    def preview_punch(self):
        """今キーを離したときに出るパンチの種類と射程を返す。出せないときはNone"""
        hold = self.hold if self.charging else 0
        kind = affordable_kind(hold, self.total_stamina())
        if kind is None:
            return None
        return kind, punch_range(kind, hold)

    def use_stamina(self, amount):
        """スタミナを消費する。上限を超えた分から先に使う"""
        used = min(self.extra_stamina, amount)
        self.extra_stamina -= used
        self.stamina -= amount - used

    def gain_stamina(self, amount):
        """スタミナを上限まで回復する"""
        self.stamina = min(MAX_STAMINA, self.stamina + amount)

    def heal(self, amount):
        """HPを上限まで回復する"""
        self.hp = min(MAX_HP, self.hp + amount)

    def take_damage(self, damage, side):
        """敵の攻撃を受ける。side は攻撃してきた敵のいる向き。実際に受けたダメージを返す"""
        if self.is_guarding() and side == self.facing:
            damage = math.ceil(damage / 2)
        self.hp = max(0, self.hp - damage)
        self.extra_stamina += damage
        self.extra_timer = EXTRA_STAMINA_FRAMES
        return damage

    def update_stamina(self):
        """チャージしていない間のスタミナ自然回復と、最後に攻撃を受けてから時間が経った上限超えのスタミナの消去を行う"""
        if not self.charging:
            regen = STAMINA_REGEN_LOW_HP if self.hp < LOW_HP else STAMINA_REGEN
            self.gain_stamina(regen)
        if self.extra_timer > 0:
            self.extra_timer -= 1
            if self.extra_timer == 0:
                self.extra_stamina = 0

    def update_timers(self):
        """パンチの演出と被ダメージの点滅の残りフレーム数を減らす"""
        if self.punch_anim > 0:
            self.punch_anim -= 1
        if self.hurt > 0:
            self.hurt -= 1
