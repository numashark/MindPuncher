import unittest

from constants import (
    EXTRA_STAMINA_FRAMES, MAX_HP, MAX_STAMINA, NO_STAMINA_CHARGE_LIMIT, NORMAL, PUNCH_COST,
    STAMINA_REGEN, STAMINA_REGEN_LOW_HP,
)
from player import Player


class TestPlayer(unittest.TestCase):
    def test_initial_values(self):
        """HPとスタミナの初期値は最大値100"""
        player = Player()
        self.assertEqual(player.hp, MAX_HP)
        self.assertEqual(player.stamina, MAX_STAMINA)
        self.assertEqual(MAX_HP, 100)
        self.assertEqual(MAX_STAMINA, 100)

    def test_charge_returns_hold_on_release(self):
        """押してから離すまでのフレーム数が返る"""
        player = Player()
        player.update_charge(True, True)
        for _ in range(29):
            self.assertIsNone(player.update_charge(False, True))
        self.assertEqual(player.update_charge(False, False), 30)
        self.assertFalse(player.charging)

    def test_guard_halves_front_damage_rounded_up(self):
        """チャージ中は前方からのダメージが半減（切り上げ）され、後ろからは半減しない"""
        player = Player()
        player.update_charge(True, True)
        self.assertEqual(player.take_damage(9, player.facing), 5)
        self.assertEqual(player.take_damage(9, -player.facing), 9)
        self.assertEqual(player.hp, MAX_HP - 14)

    def test_no_stamina_charge_limit(self):
        """通常パンチのスタミナが足りないときはチャージが10フレームまでしかできない"""
        self.assertEqual(NO_STAMINA_CHARGE_LIMIT, 10)
        player = Player()
        player.stamina = PUNCH_COST[NORMAL] - 1
        player.update_charge(True, True)
        for _ in range(60):
            player.update_charge(False, True)
        self.assertEqual(player.hold, NO_STAMINA_CHARGE_LIMIT)
        self.assertFalse(player.is_guarding())
        self.assertIsNone(player.preview_punch())

    def test_extra_stamina_expires(self):
        """受けたダメージ分のスタミナが上限を超えて増え、120フレーム後に消える"""
        self.assertEqual(EXTRA_STAMINA_FRAMES, 120)
        player = Player()
        player.take_damage(10, -player.facing)
        self.assertEqual(player.total_stamina(), MAX_STAMINA + 10)
        for _ in range(EXTRA_STAMINA_FRAMES - 1):
            player.update_stamina()
        self.assertEqual(player.extra_total(), 10)
        player.update_stamina()
        self.assertEqual(player.extra_total(), 0)
        self.assertEqual(player.total_stamina(), MAX_STAMINA)

    def test_extra_stamina_timer_resets_on_damage(self):
        """攻撃を受けるたびに消えるまでの時間が戻り、攻撃を受けずに120フレーム経つと全部消える"""
        player = Player()
        player.take_damage(10, -player.facing)
        for _ in range(EXTRA_STAMINA_FRAMES - 10):
            player.update_stamina()
        player.take_damage(5, -player.facing)
        for _ in range(EXTRA_STAMINA_FRAMES - 1):
            player.update_stamina()
        self.assertEqual(player.extra_total(), 15)
        player.update_stamina()
        self.assertEqual(player.extra_total(), 0)

    def test_use_stamina_uses_extra_first(self):
        """上限を超えた分のスタミナから先に使う"""
        player = Player()
        player.take_damage(10, -player.facing)
        player.use_stamina(15)
        self.assertEqual(player.extra_total(), 0)
        self.assertEqual(player.stamina, MAX_STAMINA - 5)

    def test_regen_faster_when_low_hp(self):
        """HPが20を下回るとスタミナの回復速度が上がる"""
        player = Player()
        player.stamina = 0
        player.update_stamina()
        self.assertAlmostEqual(player.stamina, STAMINA_REGEN)
        player.stamina = 0
        player.hp = 19
        player.update_stamina()
        self.assertAlmostEqual(player.stamina, STAMINA_REGEN_LOW_HP)
        self.assertGreater(STAMINA_REGEN_LOW_HP, STAMINA_REGEN)

    def test_no_regen_while_charging(self):
        """チャージ中はスタミナが自然回復しない"""
        player = Player()
        player.stamina = 50
        player.update_charge(True, True)
        for _ in range(30):
            player.update_charge(False, True)
            player.update_stamina()
        self.assertEqual(player.stamina, 50)
        player.update_charge(False, False)
        player.update_stamina()
        self.assertAlmostEqual(player.stamina, 50 + STAMINA_REGEN)

    def test_heal_capped(self):
        """HPは100を超えて回復しない"""
        player = Player()
        player.hp = 99
        player.heal(5)
        self.assertEqual(player.hp, MAX_HP)


if __name__ == "__main__":
    unittest.main()
