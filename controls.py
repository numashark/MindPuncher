from collections import namedtuple

import pyxel

from constants import NAME_CHARS

Inputs = namedtuple("Inputs", "left right punch_pressed punch_held")

PUNCH_KEYS = (pyxel.KEY_RETURN, pyxel.KEY_KP_ENTER, pyxel.KEY_SPACE)


def any_pressed(keys):
    """keys のどれかがこのフレームで押されたかを返す"""
    return any(pyxel.btnp(k) for k in keys)


def read_play_inputs():
    """ゲーム中のキー入力を読み取る"""
    return Inputs(
        left=any_pressed((pyxel.KEY_A, pyxel.KEY_LEFT)),
        right=any_pressed((pyxel.KEY_D, pyxel.KEY_RIGHT)),
        punch_pressed=any_pressed(PUNCH_KEYS),
        punch_held=any(pyxel.btn(k) for k in PUNCH_KEYS),
    )


def up_pressed():
    """メニューで上が押されたかを返す"""
    return any_pressed((pyxel.KEY_W, pyxel.KEY_UP))


def down_pressed():
    """メニューで下が押されたかを返す"""
    return any_pressed((pyxel.KEY_S, pyxel.KEY_DOWN))


def left_pressed():
    """メニューで左が押されたかを返す"""
    return any_pressed((pyxel.KEY_A, pyxel.KEY_LEFT))


def right_pressed():
    """メニューで右が押されたかを返す"""
    return any_pressed((pyxel.KEY_D, pyxel.KEY_RIGHT))


def decide_pressed():
    """決定キーが押されたかを返す"""
    return any_pressed(PUNCH_KEYS)


def confirm_name_pressed():
    """名前入力の決定キーが押されたかを返す"""
    return any_pressed((pyxel.KEY_RETURN, pyxel.KEY_KP_ENTER))


def retry_pressed():
    """リトライキーが押されたかを返す"""
    return pyxel.btnp(pyxel.KEY_R)


def backspace_pressed():
    """BackSpaceキーが押されたかを返す"""
    return pyxel.btnp(pyxel.KEY_BACKSPACE)


def typed_chars():
    """このフレームで入力された英大文字と数字を返す"""
    return "".join(ch for ch in NAME_CHARS if pyxel.btnp(getattr(pyxel, f"KEY_{ch}")))
