import os
import win32com.client
import win32gui
import win32api
import time
from PIL import ImageGrab
import winreg as reg
import sys
from easygui import msgbox, buttonbox
from ctypes import windll,WinDLL,wintypes
from requests import get as requests_get
import config as cfg
from .ucfg import ucfg
from . import screen
from pynput import mouse
from threading import Thread

def is_screenshot_light(region=None,threshold=0.4):
    try:
        if region:
            screenshot = ImageGrab.grab(bbox=region)
        else:
            screenshot = ImageGrab.grab()
        screenshot = screenshot.convert('RGB')
        # screenshot.save("screenshot_debug.png")
        resized = screenshot.resize((100, 100))
        pixels = list(resized.getdata())

        # 统计颜色频率
        color_count = {}
        for pixel in pixels:
            quantized = tuple((x // 32) * 32 for x in pixel)
            color_count[quantized] = color_count.get(quantized, 0) + 1   

        dominant_color = max(color_count, key=color_count.get)
        r, g, b = dominant_color
        brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        is_light = brightness > threshold
        return is_light
        
    except Exception as e:
        print(f"截图或颜色分析失败: {e}")
        return True
    
def get_window_inf(title=cfg.DEFAULT_WINDOW_TITLE):
    # global ucfg.data
    hwnd = win32gui.FindWindow(None, title)
    rect = get_window_rect(hwnd)
    width = rect["width"]
    height = rect["height"]
    end_x, end_y = get_targetPos(width, height)
    return width, height, end_x, end_y

def get_window_rect(hwnd):
    # 获取窗口矩形区域
    rect = win32gui.GetWindowRect(hwnd)
    return {
        "left": rect[0],
        "top": rect[1],
        "right": rect[2],
        "bottom": rect[3],
        "width": rect[2] - rect[0],
        "height": rect[3] - rect[1],
    }
def get_targetPos(win_width=None,win_height=None):
    screen_width, screen_height = screen.get_screen_size()
    print(screen_width, screen_height)
    width = int(screen_width * cfg.WINDOW_WIDTH_RATIO)
    height = int(screen_height * cfg.WINDOW_HEIGHT_RATIO)
    if win_width==None:
        win_width = width
    if win_height==None:
        win_height = height
    # global ucfg.data
    screen_width,screen_height,ox,oy = screen.get_active_screen_size(True)
    if ucfg.data["outPos"]=="1":
        end_x = ox+(int(screen_width * cfg.WINDOW_POSITION_RATIO))
        end_y = oy+(int(screen_height - ((screen_height * cfg.WINDOW_POSITION_RATIO) + win_height)))
    elif ucfg.data["outPos"]=="2":
        end_x = ox+(int(screen_width * cfg.WINDOW_POSITION_RATIO))
        end_y = oy+(int((screen_height * cfg.WINDOW_POSITION_RATIO)))
    elif ucfg.data["outPos"]=="3":
        end_x = ox+(int((screen_width-win_width)//2))
        end_y = oy+(int(screen_height - ((screen_height * cfg.WINDOW_POSITION_RATIO) + win_height)))
    elif ucfg.data["outPos"]=="4":
        end_x = ox+(int((screen_width-win_width)//2))
        end_y = oy+(int((screen_height * cfg.WINDOW_POSITION_RATIO)))
    return end_x,end_y
def read_windowTitle(hwnd):
    window_title = win32gui.GetWindowText(hwnd)
    return window_title

def is_ed_focused():
    active_hwnd = get_active_window()
    if not active_hwnd:
        return False
    window_title = read_windowTitle(active_hwnd)
    return window_title == cfg.DEFAULT_WINDOW_TITLE

def get_active_window():
    """获取当前活动窗口的句柄，如果没有则返回 None"""
    a_hwnd = win32gui.GetForegroundWindow()
    return a_hwnd if a_hwnd else None

def is_mouse_in_easyDesktop():
    hwnd = win32gui.FindWindow(None, cfg.DEFAULT_WINDOW_TITLE)
    if not hwnd:
        return False
    try:
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        window_rect = (left, top, right, bottom)
        point = win32api.GetCursorPos()
        in_window = (left <= point[0] <= right) and (top <= point[1] <= bottom)
        return in_window
    except:
        return False
    
def is_focused_window_fullscreen():
    try:
        # 获取当前获焦窗口
        active_hwnd = get_active_window()

        if not active_hwnd:
            return False

        # 获取窗口标题
        window_title = win32gui.GetWindowText(active_hwnd)
        if window_title == "Program Manager" or window_title == "":
            return False
        if window_title in cfg.common_game_windows:
            return True

        # 获取窗口尺寸和位置信息
        rect = win32gui.GetWindowRect(active_hwnd)
        window_left, window_top = rect[0], rect[1]
        window_width, window_height = rect[2] - rect[0], rect[3] - rect[1]
        screen_width, screen_height = screen.get_screen_size()
        # 检查窗口是否覆盖整个屏幕（允许几个像素的误差）
        tolerance = cfg.TOLERANCE  # 像素容差
        return (
            abs(window_left) <= tolerance
            and abs(window_top) <= tolerance
            and abs(window_width - screen_width) <= tolerance
            and abs(window_height - screen_height) <= tolerance
        )

    except Exception as e:
        print(f"检测全屏时出错: {e}")
        return False
    
def is_desktop_and_mouse_in_corner():
    # global ucfg.data
    try:
        screen_width = win32api.GetSystemMetrics(cfg.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(cfg.SM_CYSCREEN)
        corner_size = cfg.CORNER_SIZE  # 角落区域的边长
        if ucfg.data["outPos"]=="1":
            corner_rect = (0, screen_height - corner_size, corner_size, screen_height)
        elif ucfg.data["outPos"]=="2":
            corner_rect = (0, 0, corner_size, corner_size)
        elif ucfg.data["outPos"]=="3":
            cw = int(screen_width//3)
            corner_rect = (cw,screen_height-corner_size,screen_width-cw,screen_height)
        elif ucfg.data["outPos"]=="4":
            cw = int(screen_width//3)
            corner_rect = (cw,0,screen_width-cw,corner_size)
        while True:
            try:
                mouse_x, mouse_y = win32api.GetCursorPos()
                break
            except:
                time.sleep(0.5)
        in_corner = corner_rect[0] <= mouse_x <= corner_rect[2] and corner_rect[1] <= mouse_y <= corner_rect[3]
        return in_corner
    except Exception as e:
        print(f"Error: {e}")
        return False
    
def autoStart_registry():
    python_exe = sys.executable
    script_path = os.path.abspath(sys.argv[0])
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
    reg.SetValueEx(key, cfg.APP_NAME, 0, reg.REG_SZ, f'"{python_exe}" "{script_path}"')
    reg.CloseKey(key)


def remove_autoStart_registry():
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
    reg.DeleteValue(key, cfg.APP_NAME)
    reg.CloseKey(key)
    print("成功从开机启动项中移除")

def get_desktop_path():
    shell = win32com.client.Dispatch("WScript.Shell")
    return shell.SpecialFolders("Desktop")

user32 = WinDLL('user32', use_last_error=True)
WTS_CURRENT_SERVER_HANDLE = wintypes.HANDLE(0)
def remove_title_bar(hwnd):
    GWL_STYLE = -16
    WS_CAPTION = 0x00C00000
    # 获取当前窗口样式
    current_style = user32.GetWindowLongW(hwnd, GWL_STYLE)
    
    # 移除标题栏样式
    new_style = current_style & ~WS_CAPTION
    
    # 设置新的窗口样式
    user32.SetWindowLongW(hwnd, GWL_STYLE, new_style)
    
    # 刷新窗口
    user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0027)

def get_windowCurrentTargetPos():
    px,py = get_targetPos(ucfg.data["width"],ucfg.data["height"])
    if ucfg.data["full_screen"]==True:
        win_width,win_height = screen.get_screen_size()
        px,py = 0,0
    else:
        win_width,win_height = ucfg.data["width"],ucfg.data["height"]
    return win_width,win_height,px,py

class mouse_state:
    def __init__(self):
        self.had_click = False
        self.receive = False
        Thread(target=self.reg_listener).start()
    def reg_listener(self):
        with mouse.Listener(on_click=self.onclick) as listener:
            listener.join()

    def onclick(self):
        if self.receive==True:
            self.had_click = True
    
    def get_state(self):
        if self.receive==True:
            if self.had_click==True:
                self.receive = False
            return self.had_click
        else:
            return False
    def reset(self):
        self.had_click = False
        self.receive = True

mouseState = mouse_state()