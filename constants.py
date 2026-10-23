from pathlib import Path

import screen_mode

FULLSCREEN = screen_mode.fullscreen
SCREEN_WIDTH, SCREEN_HEIGHT = (1920, 1080) if FULLSCREEN else (800, 600)
SCALE = SCREEN_HEIGHT / 600
CENTER_X = SCREEN_WIDTH // 2
# 地面の高さ
GROUND_Y = int(SCREEN_HEIGHT * 0.8)
FPS = 60
WINDOW_TITLE = "MindPuncher"

BASE_DIR = Path(__file__).resolve().parent
FONT_PATH = BASE_DIR / "assets" / "x10y12pxDonguriDuel.ttf"
FONT_SCALE = max(1, round(SCALE))
# 文字の大きさごとのフォントサイズ
FONT_SIZES = {"s": int(18 * SCALE), "m": int(32 * SCALE), "l": int(64 * SCALE)}

GAME_FRAMES = 120 * FPS
# ゲームオーバー/クリアのテキストを表示してからスコア確認画面に移るまでのフレーム数
FINISH_TEXT_FRAMES = 60

MAX_HP = 100
MAX_STAMINA = 100
LOW_HP = 30
# チャージしていないときの1フレームごとのスタミナ自然回復量
STAMINA_REGEN = 0.25
# HPが30を下回っているときの1フレームごとのスタミナ自然回復量
STAMINA_REGEN_LOW_HP = 0.5
EXTRA_STAMINA_FRAMES = 120
# プレイヤーの横幅の半分と高さ
PLAYER_HALF_WIDTH = int(18 * SCALE)
PLAYER_HEIGHT = int(80 * SCALE)

NORMAL, MID, BIG = "normal", "mid", "big"
PUNCH_KINDS = (NORMAL, MID, BIG)
MID_PUNCH_HOLD = 15
BIG_PUNCH_HOLD = 60
NO_STAMINA_CHARGE_LIMIT = 10
# チャージゲージが満タンになる長押しフレーム数
CHARGE_GAUGE_FULL_FRAMES = 90
# チャージゲージの幅と高さ
CHARGE_GAUGE_WIDTH = int(90 * SCALE)
CHARGE_GAUGE_HEIGHT = int(8 * SCALE)
# 大パンチのチャージ中に拳が点滅する周期フレーム数
GLOVE_BLINK_FRAMES = 4
# パンチごとのスタミナ消費量
PUNCH_COST = {NORMAL: 5, MID: 20, BIG: 40}
# 通常パンチの射程（最低射程）
MIN_RANGE = int(60 * SCALE)
# 中パンチの初期射程（15フレーム長押ししたときの射程）
MID_RANGE = int(180 * SCALE)
# 中パンチの最大射程（大パンチになる直前まで長押ししたときの射程）
MID_RANGE_MAX = int(240 * SCALE)
# 大パンチの基本射程
BIG_RANGE = int(320 * SCALE)
# 大パンチで60フレームを超えて長押ししたとき1フレームごとに伸びる射程
BIG_RANGE_GROWTH = 2.5 * SCALE
# 大パンチの射程の上限
BIG_RANGE_MAX = SCREEN_WIDTH // 2
# パンチや吹き飛んだ敵が当たる敵の高度の上限。これより高く飛んでいる敵には当たらない
HIT_MAX_ALTITUDE = int(10 * SCALE)
NORMAL_DAMAGE = 1
MID_DAMAGE = 1
KNOCKBACK_DAMAGE = 2
KNOCKBACK_HIT_DAMAGE = 1
BIG_DAMAGE = 3
# 中パンチで吹き飛ぶ敵の1フレームごとの移動量
KNOCKBACK_SPEED = 14 * SCALE
# ヒットストップのフレーム数（パンチの種類ごと、当たった敵の最大の大きさ 小/中/大 ごと）
HITSTOP_FRAMES = {NORMAL: (3, 3, 3), MID: (4, 6, 8), BIG: (6, 9, 12)}
# 中パンチで吹き飛んだ敵がほかの敵に当たったときのヒットストップのフレーム数（当たった敵の大きさ 小/中/大 ごと）（仮）
KNOCK_HIT_HITSTOP_FRAMES = (3, 5, 7)
# パンチの軌跡・衝撃波を表示するフレーム数
PUNCH_ANIM_FRAMES = {NORMAL: 10, MID: 14, BIG: 20}
# パンチが当たったときの画面揺れの強さ
PUNCH_SHAKE = {NORMAL: 3, MID: 6, BIG: 12}
# 吹き飛んだ敵が止まったときの画面揺れの強さ
KNOCK_STOP_SHAKE = 6
# 敵がダメージを受けたとき・吹き飛んだときに白く点滅するフレーム数
HIT_FLASH_FRAMES = 12
KNOCK_FLASH_FRAMES = 20
# プレイヤーがダメージを受けたときに赤く点滅するフレーム数
HURT_FRAMES = 20
# ダメージを受けた敵がノックバックする初速と、1フレームごとの減速率
HIT_PUSH_SPEED = 8 * SCALE
HIT_PUSH_DECAY = 0.8
# 敵の攻撃を受けたときの画面揺れの強さ（フレーム数と揺れ幅を兼ねる）
DAMAGE_SHAKE = 10

SMALL, MEDIUM, LARGE = 0, 1, 2
# 敵の大きさごとの幅と高さ
ENEMY_WIDTH = (int(26 * SCALE), int(38 * SCALE), int(54 * SCALE))
ENEMY_HEIGHT = (int(30 * SCALE), int(46 * SCALE), int(66 * SCALE))
SIZE_DAMAGE_BONUS = (0, 5, 10)
# 敵の大きさごとの移動速度の倍率
SIZE_SPEED_RATE = (1.0, 0.75, 0.5)
KILL_STAMINA = (1, 2, 3)

WALKER, FLYER, CHARGER = "walker", "flyer", "charger"
ENEMY_KINDS = (WALKER, FLYER, CHARGER)
# 敵の種類ごとのパラメーター
#   damage: プレイヤーに与えるダメージ（大きさによる加算前）
#   speed: 1フレームごとの移動量
#   attack_range: 攻撃射程（プレイヤーとの距離）
#   attack_interval: 攻撃の間隔フレーム数
#   first_attack_delay: 攻撃射程に入ってから最初の予備動作までのフレーム数
#   windup: 攻撃前に点滅する予備動作のフレーム数
ENEMY_PARAMS = {
    WALKER: {"damage": 8, "speed": 1.0 * SCALE, "attack_range": int(40 * SCALE),
             "attack_interval": 45, "first_attack_delay": 15, "windup": 24},
    FLYER: {"damage": 5, "speed": 1.3 * SCALE, "attack_range": int(50 * SCALE),
            "attack_interval": 40, "first_attack_delay": 10, "windup": 14},
    CHARGER: {"damage": 12, "speed": 0.8 * SCALE, "attack_range": int(20 * SCALE),
              "attack_interval": 60, "first_attack_delay": 0, "windup": 20},
}
# 突進する敵が突進の構えに入る距離、構えて点滅するフレーム数、突進の速さ
CHARGER_AIM_DISTANCE = int(280 * SCALE)
CHARGER_AIM_FRAMES = 35
CHARGER_DASH_SPEED = 7 * SCALE
# 飛行する敵の高度（上空と低空）
FLYER_HIGH_ALTITUDE = int(150 * SCALE)
FLYER_LOW_ALTITUDE = int(10 * SCALE)
# 飛行する敵の上昇・下降の1周期のフレーム数と、急上昇・急降下にかけるフレーム数
FLYER_CYCLE_FRAMES = 60
FLYER_MOVE_FRAMES = 6

KILL_SCORE = {1: 100, 2: 200, 3: 300}
COMBO_BONUS = 20

# 敵の出現間隔フレーム数（ゲーム開始時と終了時。間は時間に応じて変化）
SPAWN_INTERVAL_START = 75
SPAWN_INTERVAL_END = 25
# 敵の体力 1/2/3 の出やすさ（ゲーム開始時と終了時。間は時間に応じて変化）
ENEMY_HP_WEIGHTS_START = (6, 3, 1)
ENEMY_HP_WEIGHTS_END = (3, 2, 5)
# 敵の種類と大きさの出やすさ
ENEMY_KIND_WEIGHTS = (5, 3, 3)
ENEMY_SIZE_WEIGHTS = (3, 5, 2)

RANKING_SIZE = 5
NAME_MAX_LENGTH = 10
NAME_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
DEFAULT_NAME = "PLAYER"
RANKING_FILE_NAME = "ranking.json"
USER_DATA_VENDOR = "densan"
USER_DATA_APP = "MindPuncher"

MENU_ITEMS = ("ゲームスタート", "あそびかた", "ランキング")

COLOR_BACKGROUND = 1
COLOR_GROUND = 4
COLOR_GROUND_LINE = 9
COLOR_TEXT = 7
COLOR_SUB_TEXT = 13
COLOR_ACCENT = 10
COLOR_RANKING_TITLE = 9
COLOR_HP_BAR = 11
COLOR_STAMINA_BAR = 10
COLOR_EXTRA_STAMINA = 9
COLOR_STAMINA_TICK = 13
COLOR_DANGER = 8
COLOR_TRAIL = 6
COLOR_KNOCKBACK_OUTLINE = 6
COLOR_ENEMY_OUTLINE = 0
COLOR_ENEMY_WINDUP = 8
COLOR_CHARGE_EMPTY = 13
COLOR_BIG_GLOVE_BLINK = 9
ENEMY_HP_BAR_COLOR = {3: 11, 2: 10, 1: 8}
# 敵の頭上のHPバーの高さと、敵の頭からの間隔
ENEMY_HP_BAR_HEIGHT = max(2, int(4 * SCALE))
ENEMY_HP_BAR_GAP = int(6 * SCALE)
# 敵が予備動作中に点滅する周期フレーム数
WINDUP_BLINK_FRAMES = 6
ENEMY_BODY_COLOR = {WALKER: 13, FLYER: 12, CHARGER: 2}
PUNCH_COLOR = {NORMAL: 7, MID: 10, BIG: 8}
COLOR_PLAYER = 9
COLOR_PLAYER_SKIN = 15
COLOR_GLOVE = 8
# 背景の星の数
STAR_COUNT = 20
# HPが30を下回ったときの画面の縁の点滅周期フレーム数と縁の太さ
DANGER_BLINK_FRAMES = 15
DANGER_BORDER_WIDTH = int(6 * SCALE)
# 射程表示の濃さ（0～1）
RANGE_DITHER = 0.25
# ヒットエフェクトの基本の大きさと色
HIT_EFFECT_RADIUS = {NORMAL: 14 * SCALE, MID: 24 * SCALE, BIG: 40 * SCALE}
HIT_RING_COLOR = {NORMAL: 7, MID: 10, BIG: 9}
# パンチが当たったときの火花の数
HIT_SPARK_COUNT = {NORMAL: 6, MID: 9, BIG: 14}
# 吹き飛ばしたとき・吹き飛びが止まったとき・大の敵が小の敵を倒したときの火花の数
KNOCK_SPARK_COUNT = 10
KNOCK_STOP_SPARK_COUNT = 8
CRUSH_SPARK_COUNT = 8
# 敵を倒したときに飛び散る粒の数
KILL_PARTICLE_COUNT = 14
# ガードしたときに飛び散る粒の数
GUARD_PARTICLE_COUNT = 6
# 大パンチの衝撃波を表示するフレーム数と、射程を走る衝撃波の数（仮）
BIG_SHOCK_FRAMES = 24
BIG_SHOCK_WAVES = 3
# 大パンチの風圧の筋の数、1フレームごとの移動量、表示するフレーム数（仮）
BIG_WIND_COUNT = 20
BIG_WIND_SPEED = 12 * SCALE
BIG_WIND_FRAMES = 18
COLOR_WIND = (7, 6)
# 獲得スコアなどの文字が浮かんで消えるまでのフレーム数と、そのうちフェードアウトにかけるフレーム数
FLOAT_TEXT_FRAMES = 50
FLOAT_TEXT_FADE_FRAMES = 20
# 獲得スコアなどの文字が上昇し始めるときの1フレームごとの移動量（だんだん遅くなる）
FLOAT_TEXT_RISE_SPEED = 1.6 * SCALE
COLOR_TEXT_SHADOW = 0
# 残り時間を赤く表示し始める秒数
TIME_WARNING_SECONDS = 10
PUNCH_LABEL = {NORMAL: "ふつう", MID: "ちゅう", BIG: "だい"}
COLOR_SCORE_TEXT = 10
COLOR_COMBO_TEXT = 9
COLOR_HEAL_TEXT = 11
COLOR_DAMAGE_TEXT = 8
COLOR_GUARD = 6
COLOR_GUARD_FRAME = 12
COLOR_HIT_FLASH = 7
COLOR_HURT = 8
