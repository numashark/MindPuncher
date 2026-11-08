import sys

IS_WEB = sys.platform == "emscripten"
WEB_FULLSCREEN_FLAG = "mindPuncherFullscreen"

fullscreen = False


def enable_dpi_awareness():
    """Windowsの表示スケールで画面が拡大されて端が欠けないように、プロセスをDPI対応にする"""
    if sys.platform != "win32":
        return
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        ctypes.windll.user32.SetProcessDPIAware()


def select():
    """起動時にウィンドウモードかフルスクリーンかを選ばせ、選ばれたらTrueを返す。Web版は起動ページで選ばれたモードを使う"""
    global fullscreen
    if IS_WEB:
        fullscreen = web_fullscreen_flag()
        return True
    chosen = select_by_dialog()
    if chosen is None:
        return False
    fullscreen = chosen
    return True


def web_fullscreen_flag():
    """Web版の起動ページでフルスクリーンが選ばれていればTrueを返す"""
    import js
    return bool(getattr(js.window, WEB_FULLSCREEN_FLAG, False))


def select_by_dialog():
    """ウィンドウモードかフルスクリーンかを選ぶダイアログを表示し、フルスクリーンならTrue、閉じられたらNoneを返す"""
    import tkinter as tk
    chosen = {"value": None}
    root = tk.Tk()
    root.title("MindPuncher")
    root.resizable(False, False)

    def choose(value):
        """選択結果を記録してダイアログを閉じる"""
        chosen["value"] = value
        root.destroy()

    tk.Label(root, text="がめんモードを えらんでください", padx=20, pady=12).pack()
    tk.Button(root, text="ウィンドウ (800×600)", width=24, command=lambda: choose(False)).pack(padx=20, pady=4)
    tk.Button(root, text="フルスクリーン (1920×1080)", width=24, command=lambda: choose(True)).pack(padx=20, pady=(4, 16))
    root.mainloop()
    return chosen["value"]
