import ctypes
import sys
import tkinter as tk

fullscreen = False


def enable_dpi_awareness():
    """Windowsの表示スケールで画面が拡大されて端が欠けないように、プロセスをDPI対応にする"""
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        ctypes.windll.user32.SetProcessDPIAware()


def select():
    """起動時にウィンドウモードかフルスクリーンかを選ぶダイアログを表示し、選ばれたらTrueを返す"""
    global fullscreen
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

    if chosen["value"] is None:
        return False
    fullscreen = chosen["value"]
    return True
