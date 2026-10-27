import pyxel

from constants import (
    BIG, CENTER_X, CHARGE_GAUGE_HEIGHT, CHARGE_GAUGE_WIDTH,
    COLOR_BACKGROUND, COLOR_BIG_GLOVE_BLINK, COLOR_CHARGE_EMPTY, COLOR_ENEMY_OUTLINE,
    COLOR_ENEMY_WINDUP, COLOR_GLOVE, COLOR_GROUND, COLOR_GROUND_LINE, COLOR_GUARD, COLOR_GUARD_FRAME,
    COLOR_HIT_FLASH, COLOR_HURT, COLOR_KNOCKBACK_OUTLINE, COLOR_PLAYER, COLOR_PLAYER_SKIN, COLOR_STAMINA_BAR,
    COLOR_TEXT, COLOR_TRAIL, ENEMY_BODY_COLOR, ENEMY_HP_BAR_COLOR, ENEMY_HP_BAR_GAP, ENEMY_HP_BAR_HEIGHT, FLYER,
    GLOVE_BLINK_FRAMES, GROUND_Y, MAX_STAMINA, MID, NORMAL, PUNCH_COST, PLAYER_HALF_WIDTH, PLAYER_HEIGHT,
    PUNCH_ANIM_FRAMES, PUNCH_COLOR, SCALE, SCREEN_HEIGHT, SCREEN_WIDTH, STAR_COUNT, WALKER,
    WINDUP_BLINK_FRAMES,
)


def draw_stage():
    """夜空の背景と地面を描画する"""
    pyxel.cls(COLOR_BACKGROUND)
    for i in range(STAR_COUNT):
        x = (i * 197 + 31) % SCREEN_WIDTH
        y = (i * 83 + 17) % (GROUND_Y - int(80 * SCALE))
        pyxel.pset(x, y, 7 if i % 3 else 13)
    margin = int(20 * SCALE)
    pyxel.rect(-margin, GROUND_Y, SCREEN_WIDTH + margin * 2, SCREEN_HEIGHT - GROUND_Y + margin, COLOR_GROUND)
    pyxel.rect(-margin, GROUND_Y, SCREEN_WIDTH + margin * 2, int(4 * SCALE), COLOR_GROUND_LINE)


def draw_enemies(enemies):
    """敵を、大きい敵ほど奥になるように描画する"""
    for enemy in sorted(enemies, key=lambda e: (-e.size, e.order)):
        draw_enemy(enemy)


def draw_enemy(enemy):
    """敵を1体描画する。吹き飛び中はアウトラインを水色にし、予備動作中は点滅させる"""
    x0 = int(enemy.left())
    y0 = int(GROUND_Y - enemy.altitude - enemy.height)
    w, h = enemy.width, enemy.height
    outline = COLOR_KNOCKBACK_OUTLINE if enemy.knocked else COLOR_ENEMY_OUTLINE
    body = ENEMY_BODY_COLOR[enemy.kind]
    if enemy.flash > 0 and enemy.flash % 4 < 2:
        body = COLOR_HIT_FLASH
    elif enemy.is_warning() and pyxel.frame_count % WINDUP_BLINK_FRAMES < WINDUP_BLINK_FRAMES // 2:
        body = COLOR_ENEMY_WINDUP
    thickness = max(2, int(3 * SCALE))
    face = -enemy.side
    if enemy.kind == FLYER:
        wing_y = y0 + h // 3
        for sx in (-1, 1):
            bx = x0 + w // 2 + sx * w // 2
            pyxel.tri(bx, wing_y, bx + sx * int(w * 0.7), wing_y - int(10 * SCALE),
                      bx + sx * int(w * 0.5), wing_y + int(10 * SCALE), body)
    pyxel.rect(x0, y0, w, h, outline)
    pyxel.rect(x0 + thickness, y0 + thickness, w - thickness * 2, h - thickness * 2, body)
    eye_x = x0 + w // 2 + face * w // 5
    eye_y = y0 + h // 3
    r = max(2, int(w * 0.09))
    pyxel.circ(eye_x, eye_y, r + 1, 7)
    pyxel.circ(eye_x + face * r // 2, eye_y, max(1, r // 2), 0)
    if enemy.kind == WALKER and enemy.windup > 0:
        arm_x = x0 + w // 2 + face * w // 2
        pyxel.rect(arm_x - int(4 * SCALE), y0 - int(6 * SCALE), int(8 * SCALE), int(14 * SCALE), body)
    draw_enemy_hp_bar(enemy, x0, y0)


def draw_enemy_hp_bar(enemy, x0, y0):
    """敵の頭上に、残り体力を3マスのHPバーで表示する。色は多い順に緑→黄→赤"""
    hp = max(0, min(3, enemy.hp))
    bar_y = y0 - ENEMY_HP_BAR_GAP - ENEMY_HP_BAR_HEIGHT
    pyxel.rect(x0, bar_y, enemy.width, ENEMY_HP_BAR_HEIGHT, 0)
    if hp > 0:
        pyxel.rect(x0, bar_y, enemy.width * hp // 3, ENEMY_HP_BAR_HEIGHT, ENEMY_HP_BAR_COLOR[hp])
    for i in (1, 2):
        mark_x = x0 + enemy.width * i // 3
        pyxel.line(mark_x, bar_y, mark_x, bar_y + ENEMY_HP_BAR_HEIGHT - 1, 0)


def draw_player(player):
    """プレイヤー、パンチの軌跡、ガード、チャージゲージを描画する"""
    f = player.facing
    x0 = CENTER_X - PLAYER_HALF_WIDTH
    y0 = GROUND_Y - PLAYER_HEIGHT
    body = COLOR_HURT if player.hurt > 0 and player.hurt % 4 < 2 else COLOR_PLAYER
    pyxel.rect(x0, y0 + int(24 * SCALE), PLAYER_HALF_WIDTH * 2, PLAYER_HEIGHT - int(24 * SCALE), body)
    pyxel.circ(CENTER_X, y0 + int(12 * SCALE), int(13 * SCALE), COLOR_PLAYER_SKIN)
    pyxel.circ(CENTER_X + f * int(6 * SCALE), y0 + int(10 * SCALE), max(1, int(2 * SCALE)), 0)

    arm_y = y0 + int(36 * SCALE)
    if player.punch_anim > 0:
        reach = int(PLAYER_HALF_WIDTH + 34 * SCALE)
        start = int(PLAYER_HALF_WIDTH - 6 * SCALE)
        n = 5
        for i in range(n):
            tx = CENTER_X + f * (start + (reach - start) * i / n)
            pyxel.circb(tx, arm_y, max(1, int(9 * SCALE * (0.4 + 0.6 * i / n))), COLOR_TRAIL)
        for dy in (-int(6 * SCALE), 0, int(6 * SCALE)):
            pyxel.line(CENTER_X + f * start, arm_y + dy, CENTER_X + f * reach, arm_y + dy, COLOR_TRAIL)
    elif player.charging:
        reach = int(PLAYER_HALF_WIDTH - 6 * SCALE)
    else:
        reach = int(PLAYER_HALF_WIDTH + 10 * SCALE)

    glove = COLOR_GLOVE
    if player.charging:
        preview = player.preview_punch()
        kind = preview[0] if preview else None
        glove = PUNCH_COLOR[kind] if kind else COLOR_CHARGE_EMPTY
        if kind == BIG and pyxel.frame_count % GLOVE_BLINK_FRAMES < GLOVE_BLINK_FRAMES // 2:
            glove = COLOR_BIG_GLOVE_BLINK
        draw_charge_gauge(player, y0, kind)
    glove_x = CENTER_X + f * reach
    pyxel.line(CENTER_X, arm_y, glove_x, arm_y, COLOR_PLAYER_SKIN)
    pyxel.circ(glove_x, arm_y, int(9 * SCALE), glove)

    if player.is_guarding():
        guard_x = CENTER_X + f * (PLAYER_HALF_WIDTH + int(10 * SCALE))
        pyxel.rect(guard_x - int(2 * SCALE), y0 + int(10 * SCALE), int(4 * SCALE),
                   PLAYER_HEIGHT - int(10 * SCALE), COLOR_GUARD)
        pyxel.rectb(guard_x - int(4 * SCALE), y0 + int(6 * SCALE), int(8 * SCALE),
                    PLAYER_HEIGHT - int(4 * SCALE), COLOR_GUARD_FRAME)


def draw_punch_wave(player):
    """中パンチと大パンチを出した直後に、射程いっぱいに広がる衝撃波を描画する"""
    if player.punch_anim <= 0 or not player.last_punch:
        return
    kind, reach, facing = player.last_punch
    if kind == NORMAL:
        return
    color = PUNCH_COLOR[kind]
    x1 = CENTER_X + facing * PLAYER_HALF_WIDTH
    x2 = CENTER_X + facing * (PLAYER_HALF_WIDTH + reach)
    h = int((40 if kind == MID else 70) * SCALE)
    progress = 1 - player.punch_anim / PUNCH_ANIM_FRAMES[kind]
    wave_x = x1 + (x2 - x1) * min(1.0, progress * 1.5)
    pyxel.line(wave_x, GROUND_Y - h, wave_x, GROUND_Y, color)
    pyxel.rectb(min(x1, x2), GROUND_Y - h // 2 - int(4 * SCALE), abs(x2 - x1), int(8 * SCALE), color)


def draw_charge_gauge(player, player_top, kind):
    """プレイヤーの頭上に現在のスタミナを表示し、今離すと出るパンチで減る分をパンチの色で点滅させる"""
    gx = CENTER_X - CHARGE_GAUGE_WIDTH // 2
    gy = player_top - int(26 * SCALE)
    total = player.total_stamina()
    scale = max(MAX_STAMINA, total)
    cost = PUNCH_COST[kind] if kind else 0
    remain_w = int(CHARGE_GAUGE_WIDTH * (total - cost) / scale)
    total_w = int(CHARGE_GAUGE_WIDTH * total / scale)
    pyxel.rect(gx, gy, CHARGE_GAUGE_WIDTH, CHARGE_GAUGE_HEIGHT, 0)
    pyxel.rect(gx, gy, remain_w, CHARGE_GAUGE_HEIGHT, COLOR_STAMINA_BAR)
    if kind:
        cost_color = PUNCH_COLOR[kind]
        if pyxel.frame_count % GLOVE_BLINK_FRAMES < GLOVE_BLINK_FRAMES // 2:
            cost_color = COLOR_CHARGE_EMPTY
        pyxel.rect(gx + remain_w, gy, total_w - remain_w, CHARGE_GAUGE_HEIGHT, cost_color)
        pyxel.line(gx + remain_w, gy, gx + remain_w, gy + CHARGE_GAUGE_HEIGHT - 1, 0)
    pyxel.rectb(gx, gy, CHARGE_GAUGE_WIDTH, CHARGE_GAUGE_HEIGHT, COLOR_TEXT)
