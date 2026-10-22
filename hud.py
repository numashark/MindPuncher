import pyxel

from combat import hit_enemies, punch_targets
from constants import (
    CENTER_X, COLOR_COMBO_TEXT, COLOR_DANGER, COLOR_EXTRA_STAMINA, COLOR_HP_BAR, COLOR_SCORE_TEXT,
    COLOR_STAMINA_BAR, COLOR_STAMINA_TICK, COLOR_TEXT, DANGER_BLINK_FRAMES, DANGER_BORDER_WIDTH,
    ENEMY_HEIGHT, ENEMY_HP_BAR_GAP, ENEMY_HP_BAR_HEIGHT, GROUND_Y, LARGE, LOW_HP, MAX_HP, MAX_STAMINA,
    PLAYER_HALF_WIDTH, PUNCH_COLOR, PUNCH_COST, PUNCH_KINDS, PUNCH_LABEL,
    RANGE_DITHER, SCALE, SCREEN_HEIGHT, SCREEN_WIDTH, TIME_WARNING_SECONDS,
)
from text import draw_text

BAR_MARGIN = int(10 * SCALE)
BAR_Y = BAR_MARGIN + int(20 * SCALE)
BAR_WIDTH = int(220 * SCALE)
BAR_HEIGHT = int(14 * SCALE)
LABEL_WIDTH = int(36 * SCALE)


def draw_range(game):
    """今のスタミナとチャージ状態で出せるパンチの最大射程を敵に重ねて表示し、当たる敵に印を付ける"""
    player = game.player
    preview = player.preview_punch()
    if preview is None:
        return
    kind, reach = preview
    f = player.facing
    color = PUNCH_COLOR[kind]
    x1 = CENTER_X + f * PLAYER_HALF_WIDTH
    x2 = CENTER_X + f * (PLAYER_HALF_WIDTH + reach)
    left, right = int(min(x1, x2)), int(max(x1, x2))
    top = GROUND_Y - ENEMY_HEIGHT[LARGE] - int(14 * SCALE)
    pyxel.dither(RANGE_DITHER if player.charging else RANGE_DITHER / 2)
    pyxel.rect(left, top, right - left, GROUND_Y - top, color)
    pyxel.dither(1.0)
    if player.charging:
        pyxel.line(left, top, right, top, color)
        pyxel.line(x2, top, x2, GROUND_Y, color)
        draw_text(x2 - f * int(20 * SCALE), top - int(16 * SCALE), PUNCH_LABEL[kind], color, center=True)
    for e in hit_enemies(kind, punch_targets(game, reach, f)):
        ty = int(GROUND_Y - e.altitude - e.height) - ENEMY_HP_BAR_GAP - ENEMY_HP_BAR_HEIGHT - int(4 * SCALE)
        pyxel.tri(e.x - int(5 * SCALE), ty - int(6 * SCALE), e.x + int(5 * SCALE), ty - int(6 * SCALE),
                  e.x, ty, color)


def draw_hud(game):
    """HPバー、スタミナバー、残り時間、スコア、コンボを描画する"""
    player = game.player
    m = BAR_MARGIN
    y = BAR_Y

    draw_text(m, y, "HP", COLOR_HP_BAR)
    bx = m + LABEL_WIDTH
    pyxel.rect(bx, y, BAR_WIDTH, BAR_HEIGHT, 0)
    pyxel.rect(bx, y, int(BAR_WIDTH * player.hp / MAX_HP), BAR_HEIGHT, COLOR_HP_BAR)
    pyxel.rectb(bx, y, BAR_WIDTH, BAR_HEIGHT, COLOR_TEXT)
    draw_text(bx, y + BAR_HEIGHT + int(4 * SCALE), f"{int(player.hp)}/{MAX_HP}", COLOR_TEXT)

    bx = SCREEN_WIDTH - m - BAR_WIDTH
    draw_text(bx - LABEL_WIDTH, y, "STA", COLOR_STAMINA_BAR)
    base = min(player.stamina, MAX_STAMINA)
    extra = min(player.extra_total(), MAX_STAMINA)
    extra_start = min(base, MAX_STAMINA - extra)
    pyxel.rect(bx, y, BAR_WIDTH, BAR_HEIGHT, 0)
    pyxel.rect(bx, y, int(BAR_WIDTH * base / MAX_STAMINA), BAR_HEIGHT, COLOR_STAMINA_BAR)
    if extra > 0:
        pyxel.rect(bx + int(BAR_WIDTH * extra_start / MAX_STAMINA), y, int(BAR_WIDTH * extra / MAX_STAMINA),
                   BAR_HEIGHT, COLOR_EXTRA_STAMINA)
    pyxel.rectb(bx, y, BAR_WIDTH, BAR_HEIGHT, COLOR_TEXT)
    total = player.total_stamina()
    for kind in PUNCH_KINDS:
        tick_x = bx + int(BAR_WIDTH * PUNCH_COST[kind] / MAX_STAMINA)
        pyxel.line(tick_x, y - int(3 * SCALE), tick_x, y + BAR_HEIGHT + int(3 * SCALE), COLOR_STAMINA_TICK)
        label_color = PUNCH_COLOR[kind] if total >= PUNCH_COST[kind] else COLOR_STAMINA_TICK
        draw_text(tick_x, y - int(17 * SCALE), PUNCH_LABEL[kind], label_color, center=True)

    remain = game.remaining_seconds()
    time_color = COLOR_DANGER if remain <= TIME_WARNING_SECONDS else COLOR_TEXT
    draw_text(CENTER_X, m, f"TIME {remain}", time_color, "m", center=True)
    draw_text(CENTER_X, m + int(30 * SCALE), f"SCORE {game.score.score}", COLOR_SCORE_TEXT, center=True)
    if game.score.combo >= 2:
        draw_text(CENTER_X, m + int(48 * SCALE), f"{game.score.combo} COMBO", COLOR_COMBO_TEXT, center=True)


def draw_danger_border(player, frame):
    """HPが20を下回っているとき、画面の縁を赤く点滅させる"""
    if player.hp >= LOW_HP or frame // DANGER_BLINK_FRAMES % 2 == 1:
        return
    for i in range(DANGER_BORDER_WIDTH):
        pyxel.rectb(i, i, SCREEN_WIDTH - i * 2, SCREEN_HEIGHT - i * 2, COLOR_DANGER)
