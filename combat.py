from constants import (
    BIG, BIG_DAMAGE, CENTER_X, CHARGER, COLOR_COMBO_TEXT, COLOR_DAMAGE_TEXT, COLOR_GUARD,
    COLOR_HEAL_TEXT, COLOR_SCORE_TEXT, CRUSH_SPARK_COUNT, DAMAGE_SHAKE, ENEMY_PARAMS, GROUND_Y,
    HIT_FLASH_FRAMES, HIT_MAX_ALTITUDE, HIT_SPARK_COUNT, HITSTOP_FRAMES, HURT_FRAMES, KILL_STAMINA,
    KNOCK_FLASH_FRAMES, KNOCK_HIT_HITSTOP_FRAMES, KNOCK_SPARK_COUNT, KNOCK_STOP_SHAKE, KNOCK_STOP_SPARK_COUNT, KNOCKBACK_DAMAGE,
    KNOCKBACK_HIT_DAMAGE, KNOCKBACK_SPEED, LARGE, MEDIUM, MID, MID_DAMAGE, NORMAL, NORMAL_DAMAGE,
    PLAYER_HEIGHT, PUNCH_ANIM_FRAMES, PUNCH_COST, PUNCH_SHAKE, SCALE, SCREEN_WIDTH, SMALL,
)
from enemy import APPROACH
from punch import affordable_kind, punch_range


def player_text_y(offset):
    """プレイヤーの頭上に文字を出すときのy座標を返す"""
    return GROUND_Y - PLAYER_HEIGHT - int(offset * SCALE)


def punch_targets(game, reach, facing):
    """射程 reach 内にいてパンチが当たる敵を、先に出現した順に返す"""
    return sorted(
        (e for e in game.enemies
         if not e.dead and not e.knocked and e.side == facing and e.distance() <= reach
         and e.altitude <= HIT_MAX_ALTITUDE),
        key=lambda e: e.order,
    )


def hit_enemies(kind, targets):
    """パンチの種類 kind で実際にダメージを与える敵を返す"""
    if kind == NORMAL:
        return [e for e in targets if e.in_min_range()][:1]
    return targets


def knockback_target(targets):
    """中パンチの射程内の敵のうち、吹き飛ばす1体（最も近い敵、同じ距離なら先に出現した敵）を返す"""
    if not targets:
        return None
    return min(targets, key=lambda e: (round(e.distance(), 3), e.order))


def release_punch(game, hold):
    """長押ししたフレーム数 hold に応じたパンチを出す"""
    player = game.player
    kind = affordable_kind(hold, player.total_stamina())
    if kind is None:
        game.effects.add_text(CENTER_X, player_text_y(30), "スタミナ ぶそく!", COLOR_DAMAGE_TEXT)
        return
    reach = punch_range(kind, hold)
    player.use_stamina(PUNCH_COST[kind])
    player.punch_anim = PUNCH_ANIM_FRAMES[kind]
    player.last_punch = (kind, reach, player.facing)

    targets = punch_targets(game, reach, player.facing)
    hits = hit_enemies(kind, targets)
    if kind == MID:
        knocked = knockback_target(targets)
        for e in hits:
            if e is knocked:
                start_knockback(game, e)
            else:
                damage(game, e, MID_DAMAGE, MID)
    else:
        for e in hits:
            damage(game, e, NORMAL_DAMAGE if kind == NORMAL else BIG_DAMAGE, kind)

    if kind == BIG:
        game.shake = max(game.shake, PUNCH_SHAKE[BIG])
    if hits:
        biggest = max(hits, key=lambda e: e.size)
        game.hitstop = HITSTOP_FRAMES[kind][biggest.size]
        game.shake = max(game.shake, PUNCH_SHAKE[kind])
        game.effects.add_ring(biggest, kind, game.hitstop + 10)


def damage(game, enemy, amount, method):
    """敵にダメージを与え、体力がなくなったら倒す。method は倒したパンチの種類"""
    if enemy.dead:
        return
    enemy.hp -= amount
    enemy.flash = HIT_FLASH_FRAMES
    game.effects.add_sparks(enemy, HIT_SPARK_COUNT[method])
    if enemy.knocked:
        return
    if enemy.hp <= 0:
        kill(game, enemy, method)
    else:
        enemy.hit_push()


def kill(game, enemy, method):
    """敵を倒し、スタミナ回復とスコア加算を行い、獲得スコア・コンボ・回復量を表示する"""
    if enemy.dead:
        return
    enemy.dead = True
    player = game.player
    gain = KILL_STAMINA[enemy.size]
    player.gain_stamina(gain)
    hp_before = player.hp
    if method == BIG:
        player.heal(gain)
    points = game.score.add_kill(enemy.max_hp)

    top = GROUND_Y - enemy.altitude - enemy.height
    game.effects.add_burst(enemy)
    game.effects.add_text(enemy.x, top - int(10 * SCALE), f"+{points}", COLOR_SCORE_TEXT)
    if game.score.combo >= 2:
        game.effects.add_text(enemy.x, top - int(26 * SCALE), f"{game.score.combo} COMBO", COLOR_COMBO_TEXT)
    if player.hp > hp_before:
        game.effects.add_text(CENTER_X, player_text_y(30), f"HP+{player.hp - hp_before}", COLOR_HEAL_TEXT)


def start_knockback(game, enemy):
    """中パンチで敵を吹き飛ばし始める"""
    enemy.hp -= KNOCKBACK_DAMAGE
    enemy.knocked = True
    enemy.knock_hits = set()
    enemy.windup = 0
    enemy.push = 0
    enemy.flash = KNOCK_FLASH_FRAMES
    game.effects.add_sparks(enemy, KNOCK_SPARK_COUNT)


def update_knockback(game, enemy):
    """吹き飛んでいる敵を動かし、当たった敵へのダメージと止まる判定を行う"""
    old_left, old_right = enemy.left(), enemy.right()
    enemy.x += enemy.side * KNOCKBACK_SPEED
    stop = False
    if enemy.left() <= 0:
        enemy.x = enemy.width / 2
        stop = True
    elif enemy.right() >= SCREEN_WIDTH:
        enemy.x = SCREEN_WIDTH - enemy.width / 2
        stop = True

    swept_left = min(old_left, enemy.left())
    swept_right = max(old_right, enemy.right())
    others = sorted(
        (o for o in game.enemies
         if o is not enemy and not o.dead and not o.knocked and o not in enemy.knock_hits
         and o.side == enemy.side and o.altitude <= HIT_MAX_ALTITUDE
         and swept_left <= o.right() and o.left() <= swept_right),
        key=lambda o: o.distance(),
    )
    for other in others:
        enemy.knock_hits.add(other)
        game.hitstop = max(game.hitstop, KNOCK_HIT_HITSTOP_FRAMES[other.size])
        if enemy.size == LARGE and other.size == SMALL:
            game.effects.add_sparks(other, CRUSH_SPARK_COUNT)
            kill(game, other, MID)
        else:
            damage(game, other, KNOCKBACK_HIT_DAMAGE, MID)
        if other.size > enemy.size and enemy.size != MEDIUM:
            enemy.x = other.x - enemy.side * (other.width / 2 + enemy.width / 2)
            stop = True
            break

    if game.frame % 2 == 0:
        game.effects.add_knock_trail(enemy)
    if stop:
        finish_knockback(game, enemy)


def finish_knockback(game, enemy):
    """吹き飛びを終える。体力がなければ倒し、残っていれば行動を再開させる"""
    enemy.knocked = False
    game.shake = max(game.shake, KNOCK_STOP_SHAKE)
    game.effects.add_sparks(enemy, KNOCK_STOP_SPARK_COUNT)
    if enemy.hp <= 0:
        kill(game, enemy, MID)
    else:
        enemy.attack_timer = ENEMY_PARAMS[enemy.kind]["first_attack_delay"]
        if enemy.kind == CHARGER:
            enemy.state = APPROACH


def enemy_attack(game, enemy):
    """敵の攻撃をプレイヤーに当て、ガード・被ダメージの表示と画面揺れを行う"""
    player = game.player
    if player.is_guarding() and enemy.side == player.facing:
        game.effects.add_text(CENTER_X + player.facing * int(40 * SCALE), player_text_y(0), "GUARD!", COLOR_GUARD)
        game.effects.add_guard(player.facing)
    dealt = player.take_damage(enemy.damage, enemy.side)
    game.score.reset_combo()
    player.hurt = HURT_FRAMES
    game.shake = max(game.shake, DAMAGE_SHAKE)
    game.effects.add_text(CENTER_X, player_text_y(10), f"-{dealt}", COLOR_DAMAGE_TEXT)
