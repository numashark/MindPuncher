import random
import unittest

from combat import enemy_attack, release_punch, update_knockback
from constants import (
    BIG, BIG_PUNCH_HOLD, BIG_SHOCK_FRAMES, DAMAGE_SHAKE, ENEMY_PARAMS, HURT_FRAMES, FLYER, FLYER_HIGH_ALTITUDE, FLYER_LOW_ALTITUDE, GAME_FRAMES, HITSTOP_FRAMES, KILL_SCORE, LARGE, MAX_HP, MAX_STAMINA,
    MEDIUM, MID, MID_PUNCH_HOLD, MIN_RANGE, NORMAL, PUNCH_COST, SCREEN_WIDTH, SIZE_DAMAGE_BONUS,
    SMALL, WALKER, KNOCK_HIT_HITSTOP_FRAMES,
)
from enemy import Enemy
from game import CLEAR, GAME_OVER, Game
from controls import Inputs

NO_INPUT = Inputs(False, False, False, False)


def make_enemy(size, distance, hp=3, order=1, side=1):
    """プレイヤーから distance 離れた位置に敵を置く"""
    enemy = Enemy(WALKER, size, side, hp, order)
    enemy.set_distance(distance)
    return enemy


def knock_until_stop(game, enemy):
    """吹き飛びが終わるまで吹き飛び処理を繰り返す"""
    for _ in range(200):
        if not enemy.knocked:
            return
        update_knockback(game, enemy)
    raise AssertionError("吹き飛びが終わらない")


class TestCombat(unittest.TestCase):
    def setUp(self):
        """テスト用のゲームを作る"""
        self.game = Game(random.Random(0))
        self.game.player.facing = 1

    def test_normal_punch_hits_oldest_in_min_range(self):
        """通常パンチは最低射程内の敵1体に、先に出現した敵からダメージを与える"""
        newer = make_enemy(SMALL, 0, order=2)
        older = make_enemy(SMALL, 10, order=1)
        far = make_enemy(SMALL, MIN_RANGE + 10, order=0)
        self.game.enemies = [newer, older, far]
        release_punch(self.game, 1)
        self.assertEqual(older.hp, 2)
        self.assertEqual(newer.hp, 3)
        self.assertEqual(far.hp, 3)
        self.assertEqual(self.game.player.stamina, MAX_STAMINA - PUNCH_COST[NORMAL])

    def test_punch_only_hits_facing_side(self):
        """パンチは向いている方向の敵にだけ当たる"""
        behind = make_enemy(SMALL, 0, side=-1)
        self.game.enemies = [behind]
        release_punch(self.game, 1)
        self.assertEqual(behind.hp, 3)

    def test_punch_misses_flying_enemy(self):
        """パンチは飛んでいる敵には当たらず、低空に降りてきた敵には当たる"""
        flyer = Enemy(FLYER, SMALL, 1, 3, 1)
        flyer.set_distance(0)
        flyer.altitude = FLYER_HIGH_ALTITUDE
        self.game.enemies = [flyer]
        release_punch(self.game, BIG_PUNCH_HOLD)
        self.assertEqual(flyer.hp, 3)
        flyer.altitude = FLYER_LOW_ALTITUDE
        release_punch(self.game, 1)
        self.assertEqual(flyer.hp, 2)

    def test_kill_score_combo_and_stamina(self):
        """敵を倒すと体力に応じたスコアとコンボボーナス、大きさに応じたスタミナが入る"""
        game = self.game
        game.player.stamina = 50
        game.enemies = [make_enemy(SMALL, 0, hp=1, order=1)]
        release_punch(game, 1)
        self.assertEqual(game.score.score, KILL_SCORE[1] + 20)
        self.assertEqual(game.player.stamina, 50 - PUNCH_COST[NORMAL] + 1)
        game.enemies = [make_enemy(MEDIUM, 0, hp=1, order=2)]
        release_punch(game, 1)
        self.assertEqual(game.score.score, KILL_SCORE[1] + 20 + KILL_SCORE[1] + 40)

    def test_kill_shows_score_combo_and_heal(self):
        """敵を倒すと獲得スコア、2体目からコンボ数、大パンチではHP回復量が表示される"""
        game = self.game
        game.player.hp = 50
        game.enemies = [make_enemy(SMALL, 0, hp=1, order=1)]
        release_punch(game, 1)
        texts = [t["text"] for t in game.effects.texts]
        self.assertIn(f"+{KILL_SCORE[1] + 20}", texts)
        self.assertNotIn("1 COMBO", texts)
        game.enemies = [make_enemy(LARGE, 0, hp=3, order=2)]
        release_punch(game, BIG_PUNCH_HOLD)
        texts = [t["text"] for t in game.effects.texts]
        self.assertIn(f"+{KILL_SCORE[3] + 40}", texts)
        self.assertIn("2 COMBO", texts)
        self.assertIn("HP+3", texts)

    def test_attack_and_guard_texts(self):
        """攻撃を受けるとダメージ量が表示され、前方ガード時はGUARD!も表示される"""
        game = self.game
        game.player.update_charge(True, True)
        enemy_attack(game, make_enemy(SMALL, 0, side=1))
        texts = [t["text"] for t in game.effects.texts]
        self.assertIn("GUARD!", texts)
        self.assertIn(f"-{-(-ENEMY_PARAMS[WALKER]['damage'] // 2)}", texts)
        self.assertEqual(game.player.hurt, HURT_FRAMES)

    def test_no_stamina_text(self):
        """スタミナが足りずパンチが出ないときは表示で知らせる"""
        self.game.player.stamina = 0
        release_punch(self.game, 1)
        self.assertIn("スタミナ ぶそく!", [t["text"] for t in self.game.effects.texts])

    def test_damage_resets_combo(self):
        """ダメージを受けるとコンボが途切れる"""
        game = self.game
        game.score.combo = 3
        enemy_attack(game, make_enemy(SMALL, 0))
        self.assertEqual(game.score.combo, 0)

    def test_enemy_damage_by_size(self):
        """敵のダメージは大きさが中で+5、大で+10される"""
        base = ENEMY_PARAMS[WALKER]["damage"]
        self.assertEqual(make_enemy(SMALL, 0).damage, base)
        self.assertEqual(make_enemy(MEDIUM, 0).damage, base + 5)
        self.assertEqual(make_enemy(LARGE, 0).damage, base + 10)
        self.assertEqual(SIZE_DAMAGE_BONUS, (0, 5, 10))

    def test_mid_punch_damages_all_and_knocks_one(self):
        """中パンチは射程内の全員に1ダメージ、最低射程内の1体は2ダメージで吹き飛ぶ"""
        target = make_enemy(SMALL, 0, hp=1, order=1)
        other = make_enemy(SMALL, MIN_RANGE + 20, hp=3, order=2)
        self.game.enemies = [target, other]
        release_punch(self.game, MID_PUNCH_HOLD)
        self.assertTrue(target.knocked)
        self.assertFalse(target.dead)
        self.assertEqual(target.hp, -1)
        self.assertEqual(other.hp, 2)

    def test_mid_punch_knocks_nearest_in_mid_range(self):
        """中パンチは通常パンチの射程外でも、中パンチの射程内で最も近い敵1体を吹き飛ばす"""
        near = make_enemy(SMALL, MIN_RANGE + 20, hp=3, order=2)
        far = make_enemy(SMALL, MIN_RANGE + 60, hp=3, order=1)
        self.game.enemies = [far, near]
        release_punch(self.game, MID_PUNCH_HOLD)
        self.assertTrue(near.knocked)
        self.assertEqual(near.hp, 1)
        self.assertFalse(far.knocked)

    def test_knocked_enemy_stops_at_bigger_enemy_and_damages(self):
        """吹き飛んだ小の敵は大きい敵に当たって止まり、当たった敵は1ダメージを受ける"""
        target = make_enemy(SMALL, 0, hp=3, order=1)
        big = make_enemy(LARGE, 200, hp=3, order=2)
        self.game.enemies = [target, big]
        release_punch(self.game, MID_PUNCH_HOLD)
        knock_until_stop(self.game, target)
        self.assertEqual(big.hp, 2)
        self.assertAlmostEqual(target.right(), big.left())
        self.assertEqual(target.hp, 1)
        self.assertFalse(target.dead)

    def test_knocked_enemy_hit_causes_hitstop(self):
        """吹き飛んだ敵がほかの敵に当たるとヒットストップが入り、当たらなければ入らない"""
        target = make_enemy(SMALL, 0, hp=3, order=1)
        big = make_enemy(LARGE, 200, hp=3, order=2)
        self.game.enemies = [target, big]
        release_punch(self.game, MID_PUNCH_HOLD)
        self.game.hitstop = 0
        knock_until_stop(self.game, target)
        self.assertEqual(self.game.hitstop, KNOCK_HIT_HITSTOP_FRAMES[LARGE])

        alone = make_enemy(SMALL, 0, hp=3, order=3)
        self.game.enemies = [alone]
        release_punch(self.game, MID_PUNCH_HOLD)
        self.game.hitstop = 0
        knock_until_stop(self.game, alone)
        self.assertEqual(self.game.hitstop, 0)

    def test_medium_knocked_enemy_reaches_edge(self):
        """吹き飛んだ中の敵は大きさに関わらず画面端まで飛ぶ"""
        target = make_enemy(MEDIUM, 0, hp=3, order=1)
        big = make_enemy(LARGE, 200, hp=3, order=2)
        self.game.enemies = [target, big]
        release_punch(self.game, MID_PUNCH_HOLD)
        knock_until_stop(self.game, target)
        self.assertAlmostEqual(target.right(), SCREEN_WIDTH)
        self.assertEqual(big.hp, 2)

    def test_large_knocked_enemy_kills_small(self):
        """吹き飛んだ大の敵に当たった小の敵は残り体力に関わらず倒れる"""
        target = make_enemy(LARGE, 0, hp=3, order=1)
        small = make_enemy(SMALL, 200, hp=3, order=2)
        self.game.enemies = [target, small]
        release_punch(self.game, MID_PUNCH_HOLD)
        knock_until_stop(self.game, target)
        self.assertTrue(small.dead)
        self.assertAlmostEqual(target.right(), SCREEN_WIDTH)

    def test_knocked_enemy_dies_after_stop(self):
        """体力のなくなった吹き飛び中の敵は吹き飛び終わってから倒れる"""
        target = make_enemy(SMALL, 0, hp=2, order=1)
        self.game.enemies = [target]
        release_punch(self.game, MID_PUNCH_HOLD)
        self.assertFalse(target.dead)
        knock_until_stop(self.game, target)
        self.assertTrue(target.dead)

    def test_big_punch_kill_heals_hp(self):
        """大パンチは範囲内の敵に3ダメージを与え、倒すとスタミナ回復量と同量のHPを回復する"""
        game = self.game
        game.player.hp = 50
        game.enemies = [make_enemy(LARGE, 0, hp=3, order=1), make_enemy(MEDIUM, 100, hp=3, order=2)]
        release_punch(game, BIG_PUNCH_HOLD)
        self.assertTrue(all(e.dead for e in game.enemies))
        self.assertEqual(game.player.hp, 50 + 3 + 2)
        self.assertLessEqual(game.player.hp, MAX_HP)

    def test_big_punch_adds_shock_and_wind(self):
        """大パンチを出すと敵がいなくても射程に衝撃波と風圧が出て、ほかのパンチでは出ない"""
        game = self.game
        release_punch(game, 1)
        release_punch(game, MID_PUNCH_HOLD)
        self.assertEqual(game.effects.shocks, [])
        self.assertEqual(game.effects.winds, [])
        release_punch(game, BIG_PUNCH_HOLD)
        self.assertEqual(len(game.effects.shocks), 1)
        self.assertGreater(len(game.effects.winds), 0)
        for _ in range(BIG_SHOCK_FRAMES):
            game.effects.update()
        self.assertEqual(game.effects.shocks, [])
        self.assertEqual(game.effects.winds, [])

    def test_hitstop_uses_biggest_enemy(self):
        """ヒットストップは当たった中で最も大きい敵の大きさで決まる"""
        game = self.game
        game.enemies = [make_enemy(SMALL, 0, order=1), make_enemy(LARGE, 100, order=2)]
        release_punch(game, BIG_PUNCH_HOLD)
        self.assertEqual(game.hitstop, HITSTOP_FRAMES[BIG][LARGE])

    def test_hitstop_order(self):
        """ヒットストップは通常＜中＜大で、通常パンチは大きさに関わらず一律"""
        for size in (SMALL, MEDIUM, LARGE):
            self.assertLess(HITSTOP_FRAMES[NORMAL][size], HITSTOP_FRAMES[MID][size])
            self.assertLess(HITSTOP_FRAMES[MID][size], HITSTOP_FRAMES[BIG][size])
        self.assertEqual(len(set(HITSTOP_FRAMES[NORMAL])), 1)
        self.assertLess(HITSTOP_FRAMES[MID][SMALL], HITSTOP_FRAMES[MID][LARGE])

    def test_game_over_when_hp_zero(self):
        """HPがなくなるとゲームオーバーになる"""
        game = self.game
        game.spawner.timer = 10 ** 9
        game.player.hp = 1
        enemy = make_enemy(SMALL, 0)
        enemy.windup = 1
        game.enemies = [enemy]
        game.update(NO_INPUT)
        self.assertEqual(game.result, GAME_OVER)

    def test_attack_shakes_screen(self):
        """敵に攻撃されると画面が揺れる"""
        enemy_attack(self.game, make_enemy(SMALL, 0))
        self.assertEqual(self.game.shake, DAMAGE_SHAKE)
        self.game.spawner.timer = 10 ** 9
        self.game.enemies = []
        self.game.update(NO_INPUT)
        self.assertEqual(self.game.shake, DAMAGE_SHAKE - 1)

    def test_damaged_enemy_is_pushed_back(self):
        """ダメージを受けて倒れなかった敵はプレイヤーと反対方向にノックバックし、予備動作が中断される"""
        enemy = make_enemy(SMALL, 0, hp=3)
        enemy.windup = 5
        self.game.enemies = [enemy]
        before = enemy.distance()
        release_punch(self.game, 1)
        self.assertEqual(enemy.windup, 0)
        for _ in range(30):
            enemy.update()
        self.assertGreater(enemy.distance(), before)

    def test_knocked_enemy_passes_flying_enemy(self):
        """吹き飛んだ敵は上空を飛んでいる敵には当たらない"""
        target = make_enemy(SMALL, 0, hp=3, order=1)
        flyer = Enemy(FLYER, LARGE, 1, 3, 2)
        flyer.set_distance(200)
        flyer.altitude = FLYER_HIGH_ALTITUDE
        self.game.enemies = [target, flyer]
        release_punch(self.game, MID_PUNCH_HOLD)
        knock_until_stop(self.game, target)
        self.assertEqual(flyer.hp, 3)
        self.assertAlmostEqual(target.right(), SCREEN_WIDTH)

    def test_clear_after_time_limit(self):
        """HPが残ったまま120秒経つとクリアになる"""
        game = self.game
        game.spawner.timer = 10 ** 9
        self.assertEqual(GAME_FRAMES, 120 * 60)
        for _ in range(GAME_FRAMES):
            game.update(NO_INPUT)
        self.assertEqual(game.result, CLEAR)


if __name__ == "__main__":
    unittest.main()
