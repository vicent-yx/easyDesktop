#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import win32gui
import win32api
import time
import webview
import sys
from easygui import msgbox
from ctypes import windll,WinDLL,wintypes
from threading import Thread
import config as cfg
import winerror
import win32event
import win32file
import win32pipe
print("正在启动中...")
from window_effect import set_window_rounded_corners
from src.windowMgr import windowMgr,hotkeyReg
from src import tool
from src.ucfg import ucfg
from src import screen
from src import api
from src.appAction import report
from src.shutdown import ShutdownHandler, set_shutdown_registry
from src.nonblocking import nonblocking
sys.stdout.reconfigure(encoding='utf-8')


print(f"Starting {cfg.APP_NAME}...")
# keyboard_monitor = kb_tool.KeyboardMonitor()
def activate_existing_instance():
    """激活已存在的实例"""
    try:
        # 连接到命名管道
        handle = win32file.CreateFile(
            r'\\.\pipe\easydesktop_pipe',
            win32file.GENERIC_WRITE,
            0, None,
            win32file.OPEN_EXISTING,
            0, None
        )
        
        # 发送激活命令
        win32file.WriteFile(handle, b'activate')
        win32file.CloseHandle(handle)
        return True
    except:
        return False

# 在 mutex 检查后添加管道服务端
def start_pipe_server():
    """启动管道服务端，监听激活命令"""
    def pipe_thread():
        while True:
            try:
                # 创建命名管道
                pipe = win32pipe.CreateNamedPipe(
                    r'\\.\pipe\easydesktop_pipe',
                    win32pipe.PIPE_ACCESS_INBOUND,
                    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
                    1, 65536, 65536,
                    0, None
                )
                
                # 等待客户端连接
                win32pipe.ConnectNamedPipe(pipe, None)
                
                # 读取数据
                result, data = win32file.ReadFile(pipe, 64*1024)
                if data == b'activate':
                    # 在主线程中执行呼出操作
                    window.evaluate_js("document.getElementById('b2d').click();fit_btnBar();")
                    if windowMgr.window_state == False:
                        # global key_quick_start
                        windowMgr.key_quick_start = True
                    else:
                        # global fullscreen_close
                        windowMgr.fullscreen_close = True
                
                win32file.CloseHandle(pipe)
            except Exception as e:
                print(f"管道服务异常: {e}")
                break
    
    # 在新线程中运行管道服务
    tube_thread = Thread(target=pipe_thread,daemon=True)
    tube_thread.start()

mutex = win32event.CreateMutex(None, 1, 'easydesktop_mutex')
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    activate_existing_instance()
    os._exit(0)

# 打包后纠正工作目录
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(os.path.realpath(sys.executable))
    os.chdir(base_path)

# 不做 SetPriorityClass：长期 HIGH 会抢 CPU；开机慢靠任务计划更早触发 + 冷启动减负

resize_window = None
icon = None
os.environ["FUSION_LOG"] = "1"
os.environ["FUSION_LOG_PATH"] = "/logs/"
# 加载Windows API
user32 = WinDLL('user32', use_last_error=True)
WTS_CURRENT_SERVER_HANDLE = wintypes.HANDLE(0)

# 定义Windows消息常量
WM_WTSSESSION_CHANGE = 0x02B1
WTS_SESSION_UNLOCK = 0x8

try:
    dll_path = os.environ.get("PYTHONNET_PYDLL")
    if dll_path and os.path.exists(dll_path):
        windll(dll_path)  # 测试直接加载
except:
    msgbox("无法加载pythonnet")

try:
    if not os.path.exists("./_internal"):
        os.makedirs("./_internal")
    if os.path.exists(cfg.DESKTOP_ICO_PATH) == False:
        os.mkdir(cfg.DESKTOP_ICO_PATH)
except:
    msgbox(os.getcwd())
def get_real_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


os.chdir(get_real_path())

sfb = screen.get_sfb()
print("sfb = ",sfb)
screen_width, screen_height = screen.get_screen_size()
print(screen_width, screen_height)
width = int(screen_width * cfg.WINDOW_WIDTH_RATIO)
height = int(screen_height * cfg.WINDOW_HEIGHT_RATIO)

def hide_from_taskbar(window):
    hwnd = windll.user32.FindWindowW(None, window.title)
    style = windll.user32.GetWindowLongW(hwnd, cfg.GWL_EXSTYLE)
    style = (style | cfg.WS_EX_TOOLWINDOW) & ~cfg.WS_EX_APPWINDOW
    windll.user32.SetWindowLongW(hwnd, cfg.GWL_EXSTYLE, style)

def ease_out_quad(t):
    # 缓动函数
    return t * (2 - t)

SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004


ox = oy = 0

def sys_theme():
    import darkdetect  # 惰性：仅主题同步
    if darkdetect.isDark() == True:
        window.evaluate_js("load_theme('dark')")
    else:
        window.evaluate_js("load_theme('light')")

def on_loaded():
    # global hwnd, ucfg.data,window
    windowMgr.update_hwnd()
    window.hide()
    if ucfg.data["full_screen"] == True:
        window.resize(screen_width, screen_height)
    hotkeyReg.hotkey_init()
    def _run_app_action():
        from src.appAction import app_action  # 惰性：更新检查不挡冷启动
        app_action.main()
    Thread(target=_run_app_action, daemon=True).start()
    Thread(target=stray, daemon=True).start()
    # Thread(target=hotkey_detect).start()
    start_pipe_server()
    hwnd = win32gui.FindWindow(None, cfg.DEFAULT_WINDOW_TITLE)
    hide_from_taskbar(window)
    windowMgr.set_blur(ucfg.data["blur_bg"])

    win_width,win_height,px,py = tool.get_windowCurrentTargetPos()
    win32gui.MoveWindow(hwnd, px, py, win_width, win_height, True)
    sys_theme()
    # 【启动优化】合并 view_mode 切换与 panel 隐藏为一次 evaluate_js，减少 UI 线程阻塞次数
    view_mode_js = "DisplayModeManager.list_view()" if ucfg.data["view"] == "list" else "DisplayModeManager.grid_view()"
    if ucfg.data["view"] == "list":
        print("视图list")
    window.evaluate_js(view_mode_js + ";document.getElementById('themeSettingsPanel').style.display='none';enableScroll();")
    # 【启动优化 P0｜风险:中】fit_blur_effect 内部会做窗口区域截图+像素直方图判主题（~30-120ms 同步阻塞）。
    # 延迟 3s 执行，避开启动阶段 WebView2 GPU 初始化与 DWM 合成竞争，避免鼠标卡顿。
    def delayed_fit_blur():
        time.sleep(3)
        windowMgr.fit_blur_effect()
    Thread(target=delayed_fit_blur, daemon=True).start()
    set_window_rounded_corners(hwnd)
    windowMgr.moveIn_window()
    Thread(target=windowMgr._lifecycle_loop, daemon=True).start()
    # wait_open()


desktop_path = tool.get_desktop_path()
public_desktop = os.path.join(os.environ["PUBLIC"], "Desktop")

def quit_ed():
    global icon
    hotkeyReg.cleanup()
    try:
        tool.mouseState.stop()
    except:
        pass
    try:
        import keyboard as _kb
        _kb.unhook_all()
    except:
        pass
    try:
        window.destroy()
    except:
        pass
    try:
        if icon:
            icon.stop()
    except:
        pass
    try:
        def _force_exit():
            time.sleep(0.6)
            os._exit(0)
        Thread(target=_force_exit, daemon=True).start()
    except:
        return
def start_out():
    windowMgr.start_action=True

def stray():
    global icon
    # 【启动优化 P2｜风险:低】pystray / PIL 仅托盘使用，惰性导入移出冷启动链
    import pystray
    from PIL import Image
    image = Image.open("ed_logo.png")
    icon = pystray.Icon("name", image, "title")
    menu = (pystray.MenuItem("呼出", start_out),pystray.MenuItem("退出", nonblocking(quit_ed)))
    icon.menu = menu
    icon.title = "EasyDesktop"
    icon.run()

# api 仅 create_window 需要，延后 import 以缩短 mutex 前依赖链
from src import api

webview.settings["ALLOW_FILE_URLS"] = True
win_width,win_height,px,py = tool.get_windowCurrentTargetPos()
window = webview.create_window(
    cfg.DEFAULT_WINDOW_TITLE,
    "easyFileDesk.html",
    width=win_width,
    height=win_height,
    x=px,y=py,
    js_api=api.AppAPI(),
    confirm_close=False,
    frameless=True,
    shadow=True,
    hidden=True,
    easy_drag=False,
    resizable=False,
    transparent=True,
    on_top=True,
)

windowMgr.set_window(window)
report.window = window
set_shutdown_registry()
shutdown_handler = ShutdownHandler(window)
webview.start(func=on_loaded,debug=not getattr(sys, 'frozen', False))
