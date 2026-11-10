import pyxel

import controls
import ranking
import screen_mode
import share
from constants import (
    CENTER_X, COLOR_ACCENT, COLOR_SHARE_HOVER, COLOR_SHARE_LOGO_ACCENT, COLOR_SHARE_LOGO_FILL,
    COLOR_SHARE_LOGO_OUTLINE, COLOR_SHARE_TEXT, COLOR_SUB_TEXT, COLOR_TEXT, CONNECTION_ERROR_TEXT, FONT_SIZES,
    LOADING_TEXT, NAME_MAX_LENGTH, RESULT_INPUT_LOCK_FRAMES, SCALE, SCREEN_HEIGHT, SHARE_BUTTON_TEXT, SHARE_BUTTON_X,
    SHARE_BUTTON_Y, SHARE_LOGO_DOT, SHARE_TEXT_GAP,
)
from render import draw_stage
from score import clear_bonus
from text import draw_clear_mark, draw_text, text_width


class ResultScene:
    def __init__(self, app, score, max_combo, cleared, survival_seconds):
        """スコア確認画面を作る。ゲームクリアしていたらボーナス点を加える。
        ランキングの読み込みなどは時間がかかるので、読み込み中の表示を描画してから行う。
        max_combo はプレイ中の最大コンボ数、survival_seconds は生き残った秒数。Web版ではXでシェアできる"""
        self.app = app
        self.max_combo = max_combo
        self.cleared = cleared
        self.survival_seconds = survival_seconds
        self.can_share = screen_mode.IS_WEB
        self.base_score = score
        self.bonus = clear_bonus(cleared)
        self.score = score + self.bonus
        self.loading = True
        self.loading_drawn = False
        self.input_lock = 0
        self.rank = None
        self.rank_error = False
        self.entering = False
        self.name = ""

    def load(self):
        """ランキングを読み込みなおし、プレイのスコアを記録して順位を求め、上位5名に入るなら名前入力を行う"""
        app = self.app
        app.ranking = app.ranking_store.load()
        app.ranking_store.record_play(self.score, self.cleared)
        self.rank = app.ranking_store.rank(app.ranking, self.score)
        self.rank_error = app.ranking_store.rank_error
        self.entering = ranking.qualifies(app.ranking, self.score)

    def update(self):
        """読み込み、名前入力とランキングへの保存、画面の移動を処理する。
        読み込みは読み込み中の表示を描画した後に行う（1回の描画の間に更新が複数回呼ばれることがあるため）。
        読み込み中と読み込みが終わってからしばらくの間は操作を受け付けない"""
        if self.loading:
            if not self.loading_drawn:
                return
            self.load()
            self.loading = False
            self.input_lock = RESULT_INPUT_LOCK_FRAMES
            if self.can_share:
                controls.show_mouse(True)
            return
        if self.input_lock > 0:
            self.input_lock -= 1
            return
        if self.can_share and controls.click_pressed() and self.share_hovered():
            share.open_share(share.share_url(self.share_text()))
        if not self.entering:
            if controls.decide_pressed():
                self.leave()
                self.app.show_title()
            return
        for ch in controls.typed_chars():
            if len(self.name) < NAME_MAX_LENGTH:
                self.name += ch
        if controls.backspace_pressed():
            self.name = self.name[:-1]
        if controls.confirm_name_pressed():
            index = self.app.save_score(ranking.entry_name(self.name), self.score, self.cleared)
            self.leave()
            self.app.show_ranking(index)

    def leave(self):
        """ほかの画面に移る前に、表示していたマウスカーソルを消す"""
        if self.can_share:
            controls.show_mouse(False)

    def share_text(self):
        """Xに投稿する本文を返す"""
        return share.share_text(self.score, self.max_combo, self.survival_seconds, self.cleared, self.rank)

    def share_button_rect(self):
        """シェアボタン（Xのロゴとその下の文字）全体の左上の位置と幅・高さを返す"""
        logo_size = share.X_LOGO_SIZE * SHARE_LOGO_DOT
        w = max(logo_size, text_width(SHARE_BUTTON_TEXT))
        h = logo_size + SHARE_TEXT_GAP + FONT_SIZES["s"]
        return SHARE_BUTTON_X, SHARE_BUTTON_Y, w, h

    def share_hovered(self):
        """マウスカーソルがシェアボタンの上にあるかを返す"""
        x, y, w, h = self.share_button_rect()
        mx, my = controls.mouse_position()
        return x <= mx < x + w and y <= my < y + h

    def draw_share_button(self):
        """ドット絵のXのロゴと、その下に「でシェア」の文字を描画する。
        マウスが乗っているときはロゴの白い縁取りと文字を黄色にする"""
        x, y, w, _ = self.share_button_rect()
        hovered = self.share_hovered()
        colors = {
            share.LOGO_FILL: COLOR_SHARE_LOGO_FILL,
            share.LOGO_OUTLINE: COLOR_SHARE_HOVER if hovered else COLOR_SHARE_LOGO_OUTLINE,
            share.LOGO_ACCENT: COLOR_SHARE_LOGO_ACCENT,
        }
        logo_size = share.X_LOGO_SIZE * SHARE_LOGO_DOT
        logo_x = x + (w - logo_size) // 2
        for (dx, dy), kind in share.x_logo_dots().items():
            pyxel.rect(logo_x + dx * SHARE_LOGO_DOT, y + dy * SHARE_LOGO_DOT, SHARE_LOGO_DOT, SHARE_LOGO_DOT,
                       colors[kind])
        draw_text(x + w // 2, y + logo_size + SHARE_TEXT_GAP, SHARE_BUTTON_TEXT,
                  COLOR_SHARE_HOVER if hovered else COLOR_SHARE_TEXT, center=True)

    def draw(self):
        """スコアと名前入力欄を描画する。読み込み中は読み込み中の表示だけを出す"""
        draw_stage()
        draw_text(CENTER_X, SCREEN_HEIGHT * 0.12, "RESULT", COLOR_ACCENT, "l", center=True)
        if self.loading:
            draw_text(CENTER_X, SCREEN_HEIGHT * 0.45, LOADING_TEXT, COLOR_TEXT, "m", center=True)
            self.loading_drawn = True
            return
        if self.bonus:
            draw_text(CENTER_X, SCREEN_HEIGHT * 0.21, f"SCORE {self.base_score}", COLOR_TEXT, "m", center=True)
            draw_text(CENTER_X, SCREEN_HEIGHT * 0.275, f"CLEAR BONUS +{self.bonus}", COLOR_ACCENT, "m", center=True)
            total = f"TOTAL {self.score}"
            draw_text(CENTER_X, SCREEN_HEIGHT * 0.34, total, COLOR_TEXT, "m", center=True)
            draw_clear_mark(CENTER_X + text_width(total, "m") // 2, SCREEN_HEIGHT * 0.34, "m")
            combo_y = SCREEN_HEIGHT * 0.405
        else:
            draw_text(CENTER_X, SCREEN_HEIGHT * 0.24, f"SCORE {self.score}", COLOR_TEXT, "m", center=True)
            combo_y = SCREEN_HEIGHT * 0.33
        if self.rank:
            rank = f"RANK {self.rank}"
        elif self.rank_error:
            rank = f"RANK {CONNECTION_ERROR_TEXT}"
        else:
            rank = "ランクがい"
        draw_text(CENTER_X, combo_y, f"MAX COMBO {self.max_combo}   {rank}", COLOR_TEXT, "m", center=True)
        if self.can_share:
            self.draw_share_button()
        if not self.entering:
            draw_text(CENTER_X, SCREEN_HEIGHT * 0.85, "Enter / Space : タイトルへ", COLOR_SUB_TEXT, center=True)
            return
        draw_text(CENTER_X, SCREEN_HEIGHT * 0.48, "ランクイン！ なまえを いれてください", COLOR_ACCENT, center=True)
        box_w, box_h = int(340 * SCALE), int(50 * SCALE)
        box_y = int(SCREEN_HEIGHT * 0.55)
        pyxel.rect(CENTER_X - box_w // 2, box_y, box_w, box_h, 0)
        pyxel.rectb(CENTER_X - box_w // 2, box_y, box_w, box_h, COLOR_TEXT)
        draw_text(CENTER_X, box_y + int(6 * SCALE), self.name + "_", COLOR_TEXT, "m", center=True)
        draw_text(CENTER_X, SCREEN_HEIGHT * 0.72,
                  f"A~Z / 0~9 : にゅうりょく ({NAME_MAX_LENGTH}もじまで)  BackSpace : けす  Enter : けってい",
                  COLOR_SUB_TEXT, center=True)
