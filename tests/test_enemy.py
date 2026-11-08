import random
import unittest

from constants import (
    CHARGER, CHARGER_DASH_SPEED, ENEMY_PARAMS, FLYER, FLYER_HIGH_ALTITUDE, FLYER_LOW_ALTITUDE, LARGE, MEDIUM, SMALL,
    WALKER,
)
from enemy import AIM, DASH, Enemy
from spawner import Spawner


class TestEnemy(unittest.TestCase):
    def test_bigger_is_slower(self):
        """大きい敵ほど移動速度が遅い"""
        for kind in (WALKER, FLYER, CHARGER):
            speeds = [Enemy(kind, size, 1, 1, 1).speed for size in (SMALL, MEDIUM, LARGE)]
            self.assertGreater(speeds[0], speeds[1])
            self.assertGreater(speeds[1], speeds[2])

    def test_charger_dash_is_fastest(self):
        """突進する敵の突進は他の敵より速い"""
        self.assertGreater(CHARGER_DASH_SPEED, ENEMY_PARAMS[WALKER]["speed"])
        self.assertGreater(CHARGER_DASH_SPEED, ENEMY_PARAMS[FLYER]["speed"])

    def test_enemy_warns_before_attack(self):
        """敵は攻撃射程内に入ってから、点滅する予備動作の後に攻撃する"""
        enemy = Enemy(WALKER, SMALL, -1, 1, 1)
        warned = 0
        for _ in range(2000):
            if enemy.update():
                break
            if enemy.is_warning():
                warned += 1
        else:
            self.fail("攻撃しなかった")
        self.assertEqual(warned, ENEMY_PARAMS[WALKER]["windup"])
        self.assertLessEqual(enemy.distance(), enemy.attack_range + 0.01)

    def test_charger_aims_then_dashes(self):
        """突進する敵は構えて点滅してから突進し、届いたら攻撃する"""
        enemy = Enemy(CHARGER, SMALL, 1, 1, 1)
        states = []
        for _ in range(2000):
            attacked = enemy.update()
            states.append(enemy.state)
            if attacked:
                break
        else:
            self.fail("攻撃しなかった")
        self.assertIn(AIM, states)
        self.assertIn(DASH, states)
        self.assertLessEqual(enemy.distance(), enemy.attack_range + 0.01)

    def test_flyer_rises_and_dives(self):
        """飛行する敵は急上昇と急降下を繰り返す"""
        enemy = Enemy(FLYER, SMALL, 1, 1, 1)
        altitudes = set()
        for _ in range(120):
            enemy.update_altitude()
            altitudes.add(round(enemy.altitude))
        self.assertIn(FLYER_HIGH_ALTITUDE, altitudes)
        self.assertIn(FLYER_LOW_ALTITUDE, altitudes)

    def test_spawner_increases_over_time(self):
        """後半になるほど敵が多く出て、体力の多い敵が出やすい"""
        def run(start, frames):
            spawner = Spawner(random.Random(1))
            enemies = []
            for frame in range(start, start + frames):
                enemies += spawner.update(frame)
            return enemies

        early = run(0, 600)
        late = run(3000, 600)
        self.assertGreater(len(late), len(early))
        self.assertGreater(sum(e.hp for e in late) / len(late), sum(e.hp for e in early) / len(early))


if __name__ == "__main__":
    unittest.main()
