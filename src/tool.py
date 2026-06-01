import os
import win32com.client
import win32gui
import win32api
import time
from PIL import ImageGrab
import winreg as reg
import sys
import subprocess
from easygui import msgbox, buttonbox
from ctypes import windll,WinDLL,wintypes
from requests import get as requests_get
import config as cfg
from .ucfg import ucfg
from . import screen
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
def get_mousePosition():
    while True:
        try:
            mouse_x, mouse_y = win32api.GetCursorPos()
            break
        except:
            time.sleep(0.5)
    return mouse_x, mouse_y
def is_desktop_and_mouse_in_corner(wait=0):
    # 使用鼠标所在实际显示器的尺寸和原点，支持多显示器
    screen_width, screen_height, ox, oy = screen.get_active_screen_size(True)
    corner_size = cfg.cornerSize_m[ucfg.data["corner_size"]][0]  # 角落区域的边长
    if ucfg.data["outPos"]=="1":
        corner_rect = (ox, oy + screen_height - corner_size, ox + corner_size, oy + screen_height)
    elif ucfg.data["outPos"]=="2":
        corner_rect = (ox, oy, ox + corner_size, oy + corner_size)
    elif ucfg.data["outPos"]=="3":
        cw = int(screen_width//3)
        corner_rect = (ox + cw, oy + screen_height - corner_size, ox + screen_width - cw, oy + screen_height)
    elif ucfg.data["outPos"]=="4":
        cw = int(screen_width//3)
        corner_rect = (ox + cw, oy, ox + screen_width - cw, oy + corner_size)
    mouse_x, mouse_y = get_mousePosition()
    in_corner = corner_rect[0] <= mouse_x <= corner_rect[2] and corner_rect[1] <= mouse_y <= corner_rect[3]
    if wait>0 and in_corner==True:
        time.sleep(wait)
        nmx,nmy = get_mousePosition()
        if nmx==mouse_x and nmy==mouse_y:
            return in_corner
        else:
            return False
    return in_corner
    
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
    try:
        reg.DeleteValue(key, cfg.APP_NAME)
        print("成功从开机启动项中移除")
    except FileNotFoundError:
        pass
    reg.CloseKey(key)

# ========== 任务计划程序自启动（比注册表 Run 启动更早） ==========

TASK_SCHEDULER_NAME = "EasyDesktop"

def autoStart_taskScheduler():
    """使用任务计划程序设置自启动（比注册表 Run 更早触发，弹 UAC 提权）"""
    if getattr(sys, 'frozen', False):
        exe_path = os.path.join(os.path.dirname(sys.executable), "easyDesktop.exe")
    else:
        exe_path = sys.executable
    
    # 路径用反斜杠转义引号包裹，避免空格问题
    params = f'/Create /TN "{TASK_SCHEDULER_NAME}" /SC ONLOGON /TR "\\"{exe_path}\\"" /F'
    print(f"[任务计划] 请求管理员权限创建: schtasks {params}")
    
    # ShellExecuteW + runas → 弹出 UAC 提权窗口
    ret = windll.shell32.ShellExecuteW(
        None,           # hwnd
        "runas",        # 触发 UAC
        "schtasks.exe", # 目标程序
        params,         # 参数
        None,           # 工作目录
        0               # SW_HIDE，不闪 cmd 窗口
    )
    
    if ret > 32:
        print(f"任务计划 '{TASK_SCHEDULER_NAME}' 创建成功（已提权）")
        return True
    else:
        print(f"任务计划创建失败或用户取消，错误码: {ret}")
        return False

def remove_autoStart_taskScheduler():
    """移除任务计划自启动（先尝试不弹窗删除，失败则弹 UAC 提权）"""
    # 任务不存在则直接返回成功
    if not is_taskScheduler_enabled():
        return True
    
    # 先尝试普通删除（部分系统不需要提权即可删除自己的任务）
    try:
        subprocess.run(
            f'schtasks /Delete /TN "{TASK_SCHEDULER_NAME}" /F',
            shell=True, check=True, capture_output=True, text=True
        )
        print(f"任务计划 '{TASK_SCHEDULER_NAME}' 已删除（无需提权）")
        return True
    except subprocess.CalledProcessError:
        pass
    
    # 普通删除失败，弹 UAC 提权删除
    params = f'/Delete /TN "{TASK_SCHEDULER_NAME}" /F'
    ret = windll.shell32.ShellExecuteW(
        None, "runas", "schtasks.exe", params, None, 0
    )
    ok = ret > 32
    print(f"任务计划 '{TASK_SCHEDULER_NAME}' 删除操作完成, ret={ret}, ok={ok}")
    return ok

def is_taskScheduler_enabled():
    """检查任务计划是否已设置"""
    try:
        result = subprocess.run(
            f'schtasks /Query /TN "{TASK_SCHEDULER_NAME}"',
            shell=True, capture_output=True, text=True
        )
        return result.returncode == 0
    except:
        return False

_desktop_path_cache = None
def get_desktop_path():
    # 【启动优化 P1｜风险:低】原用 win32com COM Dispatch("WScript.Shell")（首次 ~30-120ms 含 COM 初始化），
    # 且被 res_load/api/入口三处模块级各调一次。改为读注册表 Shell Folders（<1ms，无 COM）+ 单例缓存，
    # 消除重复 COM 初始化。结果与 COM 一致（OneDrive/重定向后的桌面同样反映在该注册表项）。
    global _desktop_path_cache
    if _desktop_path_cache is not None:
        return _desktop_path_cache
    path = None
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
        value, _ = reg.QueryValueEx(key, "Desktop")
        reg.CloseKey(key)
        path = os.path.expandvars(value)
    except Exception:
        path = None
    if not path:
        path = os.path.join(os.environ.get("USERPROFILE") or os.path.expanduser("~"), "Desktop")
    _desktop_path_cache = path
    return path

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
        self.listener = None
        self._started = False
        # 【启动优化 P2｜风险:低】不在 import/构造期启动 pynput 监听线程与 WH_MOUSE_LL 钩子，
        # 推迟到首次呼出（reset()）时再起；监听仅在 receive=True（呼出之后）才有意义。
    def _ensure_started(self):
        if not self._started:
            self._started = True
            Thread(target=self.reg_listener, daemon=True).start()
    def reg_listener(self):
        from pynput import mouse  # 惰性导入，移出冷启动 import 链
        self.listener = mouse.Listener(on_click=self.onclick)
        self.listener.start()
        self.listener.join()

    def onclick(self):
        if self.receive==True:
            self.had_click = True
    
    def get_state(self):
        now_S = self.get_live_state()
        if now_S == True:
            self.had_click = True
        if self.receive==True:
            if self.had_click==True:
                self.receive = False
            return self.had_click
        else:
            return False
    def get_live_state(self):
        return windll.user32.GetAsyncKeyState(0x01) & 0x8000 != 0
    def reset(self):
        self.had_click = False
        self.receive = True
        self._ensure_started()
    def stop(self):
        self.receive = False
        try:
            if self.listener:
                self.listener.stop()
        except:
            pass

mouseState = mouse_state()
