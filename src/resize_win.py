
import win32gui
import time
from ctypes import windll
import config as cfg
from window_effect import WindowEffect,set_window_rounded_corners
from . import tool
import darkdetect
from .ucfg import ucfg
from . import screen
import webview
from ctypes import windll,WinDLL,wintypes
from src.windowMgr import windowMgr


SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004


class resize_widnow_api:
    def fit_window_end(self):
        resize_win.fit_window_end()
    def get_version(self):
        return {"success":True,"version":cfg.APP_VERSION}
        
class resize_window():
    def __init__(self):
        self.resize_window = None
        self.has_cleared_fit = False
    def fit_window_start(self):
        # global ignore_action, ucfg.data, resize_window, hwnd, has_cleared_fit,fit_hwnd
        if ucfg.data["full_screen"] == True:
            return
        windowMgr.disable_autoClose()
        width, height, end_x, end_y = tool.get_window_inf()
        windowMgr.window.hide()
        self.resize_window = webview.create_window(
            "easyDesktop-fit",
            "easyFileDesk.html",
            x=end_x,
            y=end_y,
            js_api=resize_widnow_api(),
            confirm_close=False,
            shadow=True,
            on_top=True,
            resizable=True,
            draggable=False,
        )
        self.has_cleared_fit = False
        self.resize_window.resize(ucfg.data["width"], ucfg.data["height"])
        self.resize_window.evaluate_js("disable_settings()")
        fit_hwnd = win32gui.FindWindow(None, "easyDesktop-fit")
        win32gui.MoveWindow(fit_hwnd, end_x, end_y, width, height, True)
        tool.remove_title_bar(fit_hwnd)
        print("ucfg.data:", ucfg.data["width"], ucfg.data["height"])
        print("window: ", width, height)
        print("webview:", windowMgr.window.width, windowMgr.window.height)
        time.sleep(3)
        while True:
            try:
                self.resize_window.get_cookies()
                active_hwnd = tool.get_active_window()
                if not active_hwnd:
                    break
                window_title = win32gui.GetWindowText(active_hwnd)
                if window_title != "easyDesktop-fit":
                    break
            except:
                break
            time.sleep(cfg.MOUSE_CHECK_INTERVAL)
        if self.has_cleared_fit == False:
            self.fit_window_end()
    def fit_window_end(self):
        # global ignore_action, ucfg.data, resize_window, has_cleared_fit
        self.has_cleared_fit = True
        try:
            width, height, end_x, end_y = tool.get_window_inf(self.resize_window.title)
        except:
            windowMgr.window.show()
            return
        flags = SWP_NOMOVE | SWP_NOZORDER | 0x0008 # 组合标志位
        endx,endy = tool.get_targetPos(width, height)
        win32gui.MoveWindow(windowMgr.hwnd, endx, endy, width, height, True)
        ucfg.update_config("width", width)
        ucfg.update_config("height", height)
        self.resize_window.destroy()
        windowMgr.window.show()
        if ucfg.data['blur_bg']==True:
            windowMgr.fit_blur_effect()
        time.sleep(1)
        windowMgr.enable_autoClose()
resize_win = resize_window()