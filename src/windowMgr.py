


import win32gui
import win32con
import time
from ctypes import windll, wintypes
import ctypes as ct
import config as cfg
from window_effect import WindowEffect,set_window_rounded_corners
from . import tool
import darkdetect
from .ucfg import ucfg
from .ucfg import get_windowSize,update_windowSize
from . import screen
import webview
from threading import Thread, Event

windll.user32.SetProcessDPIAware()


SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004


# ========== 纯 ctypes 窗口过程回调类型 ==========
WNDPROC = ct.WINFUNCTYPE(ct.c_longlong, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

class WNDCLASSEXW(ct.Structure):
    _fields_ = [
        ("cbSize",        wintypes.UINT),
        ("style",         wintypes.UINT),
        ("lpfnWndProc",   WNDPROC),
        ("cbClsExtra",    ct.c_int),
        ("cbWndExtra",    ct.c_int),
        ("hInstance",     wintypes.HINSTANCE),
        ("hIcon",         wintypes.HICON),
        ("hCursor",       wintypes.HANDLE),
        ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName",  wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
        ("hIconSm",       wintypes.HICON),
    ]

# ---- 低级键盘钩子相关类型和常量 ----
HOOKPROC = ct.WINFUNCTYPE(ct.c_longlong, ct.c_int, wintypes.WPARAM, wintypes.LPARAM)

class KBDLLHOOKSTRUCT(ct.Structure):
    _fields_ = [
        ("vkCode",      wintypes.DWORD),
        ("scanCode",    wintypes.DWORD),
        ("flags",       wintypes.DWORD),
        ("time",        wintypes.DWORD),
        ("dwExtraInfo", ct.c_ulonglong),
    ]

_VK_LWIN   = 0x5B
_VK_RWIN   = 0x5C
_VK_LSHIFT = 0xA0
_VK_RSHIFT = 0xA1
_WH_KEYBOARD_LL = 13


class hotkeyMgr:

    _WND_CLASS_NAME = "EasyDesktop_HotkeyWindow_V2"

    def __init__(self):
        self.hotKey = ""
        self._hk_id = 1
        self._run = False
        self._thread = None
        self._hwnd = None
        # 键盘钩子相关
        self._hook_handle = None
        self._hook_proc = None
        self._win_pressed = False
        self._shift_pressed = False

    # ---------- 热键字符串 → 修饰符 + 虚拟键码 ----------

    @staticmethod
    def _parse_hotkey(hotKey: str):
        """将 'left windows+shift' 或 'ctrl+alt+a' 解析为 (mod, vk)"""
        parts = [p.strip().lower() for p in hotKey.split("+")]

        MOD_MAP = {
            "left windows":  win32con.MOD_WIN,
            "right windows": win32con.MOD_WIN,
            "windows":       win32con.MOD_WIN,
            "win":           win32con.MOD_WIN,
            "ctrl":          win32con.MOD_CONTROL,
            "control":       win32con.MOD_CONTROL,
            "alt":           win32con.MOD_ALT,
            "shift":         win32con.MOD_SHIFT,
        }

        VK_MAP = {
            "shift":        win32con.VK_SHIFT,
            "escape":       win32con.VK_ESCAPE,
            "esc":          win32con.VK_ESCAPE,
            "space":        win32con.VK_SPACE,
            "tab":          win32con.VK_TAB,
            "enter":        win32con.VK_RETURN,
            "return":       win32con.VK_RETURN,
            "backspace":    win32con.VK_BACK,
            "delete":       win32con.VK_DELETE,
            "insert":       win32con.VK_INSERT,
            "home":         win32con.VK_HOME,
            "end":          win32con.VK_END,
            "page up":      win32con.VK_PRIOR,
            "page down":    win32con.VK_NEXT,
            "up":           win32con.VK_UP,
            "down":         win32con.VK_DOWN,
            "left":         win32con.VK_LEFT,
            "right":        win32con.VK_RIGHT,
            "caps lock":    win32con.VK_CAPITAL,
            "print screen": win32con.VK_SNAPSHOT,
            "pause":        win32con.VK_PAUSE,
            "num lock":     win32con.VK_NUMLOCK,
            "scroll lock":  win32con.VK_SCROLL,
        }
        for i in range(1, 25):
            VK_MAP[f"f{i}"] = getattr(win32con, f"VK_F{i}", 0x6F + i)

        # 找出哪个键是"主键"（非修饰键）
        key_name = None
        for p in parts:
            if p not in MOD_MAP:
                key_name = p
                break
        # 全是修饰键 → 最后一个作为主键，其余作为修饰键
        if key_name is None and parts:
            key_name = parts[-1]

        mod = 0
        for p in parts:
            if p == key_name:
                continue
            mod |= MOD_MAP.get(p, 0)

        # 解析主键 → 虚拟键码
        vk = VK_MAP.get(key_name) if key_name else None
        if vk is None and key_name and len(key_name) == 1:
            vk = ord(key_name.upper())

        return mod, vk

    # ---------- 纯 ctypes 消息窗口 + 热键注册 ----------

    def _msg_loop(self):
        mod, vk = self._parse_hotkey(self.hotKey)
        if vk is None:
            print(f"[hotkeyMgr] 无法解析热键: '{self.hotKey}'")
            return

        hk_id = self._hk_id
        u32 = ct.windll.user32
        k32 = ct.windll.kernel32
        hinst = k32.GetModuleHandleW(None)

        # ---- 窗口过程 (ctypes 回调，保证能被 DispatchMessageW 调用) ----
        mgr = self  # 闭包引用，避免 self 在回调中绑定问题

        @WNDPROC
        def _wnd_proc(hwnd, msg, wparam, lparam):
            if msg == win32con.WM_HOTKEY:
                if wparam == hk_id:
                    print(f"[hotkeyMgr] 热键触发: {mgr.hotKey}")
                    mgr.hotKey_action()
                elif wparam == 99:
                    print("[hotkeyMgr] 测试热键 Ctrl+Alt+F12 触发成功！热键机制正常工作。")
                else:
                    print(f"[hotkeyMgr] WM_HOTKEY wparam={wparam:#x} (未知)")
            return u32.DefWindowProcW(hwnd, msg, wparam, lparam)

        # 设置 *W 函数的 argtypes，确保参数类型正确
        u32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        u32.DefWindowProcW.restype = ct.c_longlong

        u32.CreateWindowExW.argtypes = [
            wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
            ct.c_int, ct.c_int, ct.c_int, ct.c_int,
            wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID,
        ]
        u32.CreateWindowExW.restype = wintypes.HWND

        # ---- 注册窗口类 ----
        cls_name = self._WND_CLASS_NAME
        wc = WNDCLASSEXW()
        wc.cbSize = ct.sizeof(WNDCLASSEXW)
        wc.lpfnWndProc = _wnd_proc
        wc.hInstance = hinst
        wc.lpszClassName = cls_name

        if not u32.RegisterClassExW(ct.byref(wc)):
            err = k32.GetLastError()
            if err != 1410:  # ERROR_CLASS_ALREADY_EXISTS
                print(f"[hotkeyMgr] RegisterClassExW 失败，错误码: {err}")
                return

        # ---- 创建消息窗口 ----
        hwnd = u32.CreateWindowExW(
            0, cls_name, "", 0, 0, 0, 0, 0,
            win32con.HWND_MESSAGE, None, hinst, None
        )
        if not hwnd:
            print(f"[hotkeyMgr] CreateWindowExW 失败，错误码: {k32.GetLastError()}")
            return

        self._hwnd = hwnd

        # ---- 检测 Win+Shift 系统保留热键，使用低级键盘钩子 ---- #
        use_hook = False
        if mod & win32con.MOD_WIN:
            if vk in (win32con.VK_SHIFT,):
                use_hook = True
                print(f"[hotkeyMgr] '{self.hotKey}' 是系统保留热键，使用低级键盘钩子")

        if use_hook:
            # ---- 安装低级键盘钩子 ---- #
            u32.SetWindowsHookExW.argtypes = [
                ct.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD
            ]
            u32.SetWindowsHookExW.restype = ct.c_void_p
            u32.UnhookWindowsHookEx.argtypes = [ct.c_void_p]
            u32.UnhookWindowsHookEx.restype = wintypes.BOOL
            u32.CallNextHookEx.argtypes = [ct.c_void_p, ct.c_int, wintypes.WPARAM, wintypes.LPARAM]
            u32.CallNextHookEx.restype = ct.c_longlong

            @HOOKPROC
            def _hook_proc(nCode, wParam, lParam):
                if nCode == 0:  # HC_ACTION
                    p = ct.cast(lParam, ct.POINTER(KBDLLHOOKSTRUCT)).contents
                    down = wParam in (win32con.WM_KEYDOWN, win32con.WM_SYSKEYDOWN)
                    up   = wParam in (win32con.WM_KEYUP,   win32con.WM_SYSKEYUP)
                    if down or up:
                        vk_code = p.vkCode
                        if vk_code in (_VK_LWIN, _VK_RWIN):
                            # 放行 Win 键，不干扰系统快捷键（Win+R、Win+E 等）
                            mgr._win_pressed = down
                        elif vk_code in (_VK_LSHIFT, _VK_RSHIFT, win32con.VK_SHIFT):
                            mgr._shift_pressed = down
                            if down and mgr._win_pressed:
                                # Win+Shift 触发 → 关掉开始菜单 + 吃掉 Shift
                                print("[hotkeyMgr] 系统热键触发 (via Hook): Win+Shift")
                                u32.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
                                u32.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
                                mgr.hotKey_action()
                                return 1  # 吃掉 Shift，阻止切换键盘布局
                return u32.CallNextHookEx(None, nCode, wParam, lParam)

            self._hook_proc = _hook_proc  # 保持引用，防止 GC
            hook_handle = u32.SetWindowsHookExW(_WH_KEYBOARD_LL, _hook_proc, None, 0)
            if hook_handle:
                self._hook_handle = hook_handle
                print("[hotkeyMgr] 键盘钩子已安装")
            else:
                err = k32.GetLastError()
                print(f"[hotkeyMgr] 键盘钩子安装失败，错误码: {err}")
                u32.DestroyWindow(hwnd)
                self._hwnd = None
                return

            test_ok = False
        else:
            # ---- 注册系统热键 (RegisterHotKey) ---- #
            if not u32.RegisterHotKey(hwnd, hk_id, mod, vk):
                print(f"[hotkeyMgr] RegisterHotKey 失败: '{self.hotKey}' (可能被其他程序占用)")
                u32.DestroyWindow(hwnd)
                self._hwnd = None
                return

            print(f"[hotkeyMgr] 热键已注册: {self.hotKey} (mod={mod:#x}, vk={vk:#x})")

            # ---- 注册测试热键 Ctrl+Alt+F12（验证热键机制是否正常） ---- #
            test_ok = False
            TEST_HK_ID = 99
            test_ok = u32.RegisterHotKey(hwnd, TEST_HK_ID, win32con.MOD_CONTROL | win32con.MOD_ALT, win32con.VK_F12)
            if test_ok:
                print("[hotkeyMgr] 测试热键已注册: Ctrl+Alt+F12，请按下测试")

        # ---- 给自己发一条测试消息，验证消息循环是否正常 ---- #
        u32.PostMessageW(hwnd, win32con.WM_USER, 0xDEAD, 0xBEEF)
        print("[hotkeyMgr] 已发送 WM_USER 测试消息，如果收到说明消息循环正常")

        # ---- 消息循环 ---- #
        u32.GetMessageW.argtypes = [wintypes.LPMSG, wintypes.HWND, wintypes.UINT, wintypes.UINT]
        u32.GetMessageW.restype = wintypes.BOOL
        u32.TranslateMessage.argtypes = [ct.POINTER(wintypes.MSG)]
        u32.TranslateMessage.restype = wintypes.BOOL
        u32.DispatchMessageW.argtypes = [ct.POINTER(wintypes.MSG)]
        u32.DispatchMessageW.restype = ct.c_longlong

        msg = wintypes.MSG()
        try:
            while self._run:
                ret = u32.GetMessageW(ct.byref(msg), None, 0, 0)
                if ret == 0:
                    print("[hotkeyMgr] GetMessageW 返回 0 (WM_QUIT)，退出循环")
                    break
                if ret == -1:
                    err = k32.GetLastError()
                    print(f"[hotkeyMgr] GetMessageW 返回 -1，错误码: {err}，退出循环")
                    break
                u32.TranslateMessage(ct.byref(msg))
                u32.DispatchMessageW(ct.byref(msg))
        finally:
            if self._hook_handle:
                u32.UnhookWindowsHookEx(self._hook_handle)
                self._hook_handle = None
                self._hook_proc = None
                print("[hotkeyMgr] 键盘钩子已卸载")
            if not use_hook:
                u32.UnregisterHotKey(hwnd, hk_id)
                if test_ok:
                    u32.UnregisterHotKey(hwnd, 99)
            u32.DestroyWindow(hwnd)
            self._hwnd = None
            print("[hotkeyMgr] 热键已注销")

    # ---------- 对外接口 ----------

    def hotKey_action(self):
        if windowMgr.ignore_action:
            return
        try:
            if windowMgr.window_state == False:
                windowMgr.key_quick_start = True
            else:
                windowMgr.fullscreen_close = True
        except Exception as e:
            print(f"[hotkeyMgr] hotKey_action 异常: {e}")

    def startTread(self):
        print("start hotkey thread")
        self._run = True
        self._thread = Thread(target=self._msg_loop, daemon=True)
        self._thread.start()

    def register(self, hotKey):
        self.hotKey = hotKey
        # 先停止旧线程（不要跨线程卸载钩子，让 finally 同线程清理）
        self._run = False
        if self._hwnd:
            try:
                ct.windll.user32.PostMessageW(self._hwnd, win32con.WM_QUIT, 0, 0)
            except:
                pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        # 启动新线程
        self.startTread()

    def _clear(self):
        self._run = False

    def hotkey_init(self):
        if ucfg.data["cf_type"] == "2":
            self.register("left windows+shift")
        if ucfg.data["cf_type"] == "3":
            self.register("left windows+escape")
        if ucfg.data["cf_type"] == "4":
            self.register(ucfg.data["cf_hotkey"])

    def cleanup(self):
        self._run = False
        # 先发 WM_QUIT，让线程的 finally 同线程清理钩子
        if self._hwnd:
            try:
                ct.windll.user32.PostMessageW(self._hwnd, win32con.WM_QUIT, 0, 0)
            except:
                pass
        if self._thread:
            self._thread.join(timeout=2)
        # 兜底：如果线程未能正常退出，跨线程卸载钩子
        if self._hook_handle:
            try:
                ct.windll.user32.UnhookWindowsHookEx(self._hook_handle)
            except:
                pass
            self._hook_handle = None
            self._hook_proc = None


hotkeyReg = hotkeyMgr()


class resize_widnow_api:
    def fit_window_end(self):
        resize_win.fit_window_end()
    def fit_resize(self):
        # global fit_hwnd
        width, height, end_x, end_y = tool.get_window_inf("easyDesktop-fit")
        win32gui.MoveWindow(resize_win.fit_hwnd, end_x, end_y, width, height, True)
    def get_version(self):
        return {"success":True,"version":cfg.APP_VERSION}
        
class resize_window():
    def __init__(self):
        self.resize_window = None
        self.has_cleared_fit = False
        self.fit_hwnd = None
    def fit_window_start(self):
        # global ignore_action, ucfg.data, resize_window, hwnd, has_cleared_fit,fit_hwnd
        if ucfg.data["full_screen"] == True:
            return
        windowMgr.disable_autoClose()
        ww,hh = get_windowSize()
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
        self.resize_window.resize(ww, hh)
        self.resize_window.evaluate_js("disable_settings()")
        fit_hwnd = win32gui.FindWindow(None, "easyDesktop-fit")
        win32gui.MoveWindow(fit_hwnd, end_x, end_y, width, height, True)
        tool.remove_title_bar(fit_hwnd)
        self.fit_hwnd = fit_hwnd
        print("ucfg.data:", ww, hh)
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
        update_windowSize(width, height)
        # ucfg.update_config("width", width)
        # ucfg.update_config("height", height)
        self.resize_window.destroy()
        windowMgr.window.show()
        if ucfg.data['blur_bg']==True:
            windowMgr.fit_blur_effect()
        time.sleep(1)
        windowMgr.enable_autoClose()
resize_win = resize_window()

class windowMgr_main():
    def __init__(self):
        self.window = None
        self.ignore_action = False
        self.window_state = False
        self.key_quick_start = False
        self.fullscreen_close = False
        self.moving = False
        self.start_action = False
        self.hwnd = None
        
    def set_window(self, window):
        self.window = window
    def update_hwnd(self):
        self.hwnd = win32gui.FindWindow(None, cfg.DEFAULT_WINDOW_TITLE)
    def disable_autoClose(self):
        self.ignore_action = True
    def enable_autoClose(self):
        self.ignore_action = False
    def call_js(self,js_code):
        try:
            # 【复审修复】返回 evaluate_js 结果：res_load.delay_update_action 依赖它取
            # AppState.currentPath 判断是否仍在当前目录、决定是否刷新。原先无 return 恒为 None，
            # 会导致冷启动占位图标永远不刷新成真实图标（P1 后台刷新失效）。
            return self.window.evaluate_js(js_code)
        except:
            print(f"调用js失败: {js_code}")
            return None
        
    def animateWindow(
        self,start_x, start_y, end_x, end_y, width, height, steps=cfg.ANIMATION_STEPS, delay=cfg.ANIMATION_DELAY
    ):
        positions = []
        w = width
        h = height
        # print("w:",w,"h:",h,"start_x:",start_x,"start_y:",start_y,"end_x:",end_x,"end_y:")
        for i in range(steps + 1):
            progress = i / steps
            eased = progress * (2 - progress)  # easeOutQuad
            x = start_x + (end_x - start_x) * eased
            y = start_y + (end_y - start_y) * eased
            positions.append((int(x), int(y),int(w),int(h)))
        # print(positions)
        # 执行动画
        delay = 0.25 / steps  # 总时长250ms
        hwnd = win32gui.FindWindow(None, cfg.DEFAULT_WINDOW_TITLE)
        for x, y, w, h in positions:
            win32gui.MoveWindow(hwnd, x, y, w, h, False)
            time.sleep(delay)
    def out_window(self):
        screen.active_screen.markActive()
        self.window.evaluate_js("document.getElementById('screen_infShow').innerText='当前屏幕："+screen.get_info_str()+"';")
        ww,hh = get_windowSize()
        screen_width,screen_height,ox,oy = screen.get_active_screen_size(True)
        self.key_quick_start = False
        if self.moving == True:
            return
        self.moving = True
        self.window_state = True
        self.window.evaluate_js("document.getElementById('themeSettingsPanel').style.display='none';enableScroll();")
        hwnd = win32gui.FindWindow(None, cfg.DEFAULT_WINDOW_TITLE)
        if not hwnd:
            print(f"未找到名为 '{cfg.DEFAULT_WINDOW_TITLE}' 的窗口")
            return False
        # 闪屏问题出现在此处的resize方法，解决方案：使用win32api。全屏模式的适配，需要获取当前屏幕的顶点坐标
        if ucfg.data["full_screen"] == True:
            w,h = screen.get_screen_size()
            width = w
            height = h
        else:
            width = ww
            height = hh
        try:
            windll.user32.keybd_event(0x12, 0, 0, 0)
            windll.user32.SetForegroundWindow(hwnd)
            windll.user32.keybd_event(0x12, 0, 0x0002, 0)
        except:
            pass
        screen_width,screen_height,ox,oy = screen.get_active_screen_size(True)
        if ucfg.data["outPos"]=="1":
            start_x = ox+(-width)
            start_y = oy+(screen_height - height // 2)
        elif ucfg.data["outPos"]=="2":
            start_x = ox+(-width)
            start_y = oy+( - (height // 2))
        elif ucfg.data["outPos"]=="3":
            start_x = ox+(int((screen_width-width)//2))
            start_y = oy+(screen_height + height)
        elif ucfg.data["outPos"]=="4":
            start_x = ox+((screen_width-width)//2)
            start_y = oy+(-height)
        if ucfg.data["full_screen"] == True:
            end_x = ox
            end_y = oy
        else:
            end_x,end_y = tool.get_targetPos(width,height)
        if len(webview.screens)>1:
            offset = 1
        else:
            offset = 0
        need_dpi_fix = screen.is_point_on_other_screen(start_x, start_y) and len(webview.screens)>1
        if need_dpi_fix:
            win32gui.MoveWindow(hwnd, start_x, start_y, width, height+offset, True) # +1触发重绘（切换到副屏时可能dpi不正确）
            win32gui.UpdateWindow(hwnd)
        self.window.show()

        Thread(target=self.fit_blur_effect, daemon=True).start()
        print("outwindow_ani")
        self.animateWindow(start_x, start_y, end_x, end_y, width, height)
        if need_dpi_fix:
            win32gui.MoveWindow(hwnd, end_x, end_y, width, height+1, True)
            self.window.hide()
            self.window.show()
        self.window.evaluate_js("window_state=true;")
        self.window.evaluate_js("NavigationManager.refreshCurrentPath(true,false,false);fit_btnBar();")

        tool.mouseState.reset()
        while True:
            if self.fullscreen_close == True:
                break
            if ucfg.data["out_cf_type"] == "2" and (
                tool.is_ed_focused() == True
                or (tool.mouseState.get_state()==True and tool.is_ed_focused()==False)
            ):
                break
            if ucfg.data["out_cf_type"] == "1" and (tool.is_mouse_in_easyDesktop() == True or (tool.mouseState.get_state()==True and tool.is_ed_focused()==False)):
                break
            if ucfg.data["fdr"] == True and tool.is_focused_window_fullscreen() == True:
                break
            time.sleep(cfg.MOUSE_CHECK_INTERVAL)
        self.moving = False

        while True:
            if ucfg.data["out_cf_type"] == "1" or (ucfg.data["out_cf_type"]=="3" and ucfg.data["cf_type"]=="1"):
                tj = tool.is_mouse_in_easyDesktop() == False and self.ignore_action == False
            else:
                tj = tool.is_ed_focused() == False and self.ignore_action == False
            if (tj == True and ucfg.data["full_screen"] == False) or self.fullscreen_close == True:
                self.fullscreen_close = False
                if self.ignore_action == False:
                    return True
                break

            if self.window_state == False:
                break
            time.sleep(cfg.MOUSE_CHECK_INTERVAL)
        return False


    def moveIn_window(self,animate=True):
        screen_width,screen_height,ox,oy = screen.get_active_screen_size(True)

        if self.moving == True:
            return
        self.moving = True
        self.window_state = False
        hwnd = win32gui.FindWindow(None, cfg.DEFAULT_WINDOW_TITLE)
        if not hwnd:
            print(f"未找到名为 '{cfg.DEFAULT_WINDOW_TITLE}' 的窗口")
            return False
        screen_width,screen_height,_,_ = screen.get_active_screen_size(True)
        rect = tool.get_window_rect(hwnd)
        print("rect:")
        print(rect)
        width = rect["width"]
        height = rect["height"]
        current_x = rect["left"]
        current_y = rect["top"]
        if ucfg.data["outPos"]=="1":
            start_x = ox+(-width)
            start_y = oy+(screen_height - height // 2)
        elif ucfg.data["outPos"]=="2":
            start_x = ox+(-width)
            start_y = oy+(0 - (height // 2))
        elif ucfg.data["outPos"]=="3":
            start_x = ox+(int((screen_width-width)//2))
            start_y = oy+(screen_height + height)
        elif ucfg.data["outPos"]=="4":
            start_x = ox+((screen_width-width)//2)
            start_y = oy+(-height)
        print("start_x:",start_x,"start_y:",start_y,"current_x:",current_x,"current_y:",current_y,"width:",width,"height:",height)
        self.window.evaluate_js("window_state=false;preview_runing = false;MenuManager.hideAllMenus();")
        print("movein_ani")
        print(current_x, current_y, start_x, start_y, width, height)
        if animate:
            self.animateWindow(current_x, current_y, start_x, start_y, width, height)
        else:
            # 【启动优化 P0】跳过 81 步动画，直接把（仍隐藏的）窗口一步定位到屏外起始点
            win32gui.MoveWindow(hwnd, start_x, start_y, width, height, False)
        self.window.hide()
        self.moving = False
        self.window.evaluate_js("GroupManager.closeGroup();")

    def _lifecycle_loop(self):
        """主生命周期循环，消除递归调用栈累积"""
        while True:
            triggered = self.wait_open()
            if triggered:
                should_hide = self.out_window()
                if should_hide:
                    self.moveIn_window()
            else:
                time.sleep(cfg.SLEEP_INTERVAL)
    def wait_open(self):
        """等待呼出触发条件。返回 True 表示触发，返回 False 表示窗口已被其他方式打开"""
        start_wait_time = int(time.time())
        self.had_refresh = False
        
        while True:
            if int(time.time()) - start_wait_time > cfg.WAIT_TIMEOUT:
                if self.had_refresh == False:
                    self.call_refresh()
                    self.had_refresh = True
            if ucfg.data["fdr"] == True:
                if tool.is_focused_window_fullscreen() == True:
                    time.sleep(cfg.SLEEP_INTERVAL)
                    continue
            if ucfg.data["cf_type"] == "2" or ucfg.data["cf_type"] == "3" or ucfg.data["cf_type"]=="4":
                if self.key_quick_start == True:
                    return True
            if self.start_action == True:
                self.start_action = False
                return True
            else:
                if tool.is_desktop_and_mouse_in_corner(wait=cfg.cornerSize_m[ucfg.data["corner_size"]][1]) and ucfg.data["cf_type"] == "1":
                    return True
            if self.window_state == True:
                return False
            time.sleep(cfg.SLEEP_INTERVAL)
    def fit_blur_effect(self):
        
        width, height, end_x, end_y = tool.get_window_inf()
        if ucfg.data["themeChangeType"]=="2":
            color_r = tool.is_screenshot_light((end_x,end_y,end_x+width,end_y+height),threshold=0.4)
            if color_r == True:
                if ucfg.data["theme"]!="custom":
                    self.window.evaluate_js("load_theme('light',true)")
                if ucfg.data['blur_bg']==True:
                    WindowEffect.setLightBlurEffect(self.hwnd,effect=ucfg.data["blur_effect"])
                    print("from fbe")
            else:
                if ucfg.data["theme"]!="custom":
                    self.window.evaluate_js("load_theme('dark',true)")
                if ucfg.data['blur_bg']==True:
                    WindowEffect.setDarkBlurEffect(self.hwnd,effect=ucfg.data["blur_effect"])
                    print("from fbe")
        if ucfg.data['blur_bg']==False:
            time.sleep(0.2)
            WindowEffect.setLightBlurEffect(self.hwnd,effect=ucfg.data["blur_effect"])
            WindowEffect.resetEffect(self.hwnd)

    def load_blur_effect(self,b_type='Acrylic'):
        self.update_hwnd()
        if ucfg.data['blur_bg']==False:
            return
        WindowEffect.resetEffect(self.hwnd)
        print("from lbe")
        if b_type=='Acrylic':
            WindowEffect.setLightBlurEffect(self.hwnd,effect=ucfg.data["blur_effect"])
        else:
            WindowEffect.setDarkBlurEffect(self.hwnd,effect=ucfg.data["blur_effect"])
    def set_blur(self,open_state,real_theme=None):
        # global hwnd,ucfg.data
        hwnd = windowMgr.hwnd
        if ucfg.data["blur_bg"]==False:
            return
        if real_theme == None:
            real_theme = ucfg.data["theme"]
        if open_state==True:
            if real_theme=="light":
                WindowEffect.setLightBlurEffect(hwnd,effect=ucfg.data["blur_effect"])
                print("from sb")
            else:
                WindowEffect.setDarkBlurEffect(hwnd,effect=ucfg.data["blur_effect"])
                print("from sb")
        else:
            WindowEffect.resetEffect(hwnd)

    def sys_theme(self):
        if darkdetect.isDark() == True:
            self.window.evaluate_js("load_theme('dark')")
        else:
            self.window.evaluate_js("load_theme('light')")
    def update_state(self,part,data):
        hwnd = self.hwnd
        ww,hh = get_windowSize()
        screen_width, screen_height = screen.get_screen_size()
        if part == "themeChangeType":
            if data == "1":
                self.sys_theme()
            elif data == "2":
                windowMgr.fit_blur_effect()
                
        if part == "auto_start":
            if data == True:
                # 若已开任务计划快速自启，只保留任务，不写 Run（避免双启动）
                if tool.is_taskScheduler_enabled():
                    pass
                else:
                    tool.autoStart_registry()
            else:
                tool.remove_autoStart_registry()
                # 关闭自启动时一并取消任务计划快速自启
                tool.remove_autoStart_taskScheduler()
        if part == "auto_start_priority":
            if data == True:
                rs = tool.autoStart_taskScheduler()
                if rs:
                    # 任务计划成功后移除注册表 Run，避免登录双拉起
                    tool.remove_autoStart_registry()
                    self.window.evaluate_js("setPriorityBtnActive(true)")
            else:
                rs = tool.remove_autoStart_taskScheduler()
                if rs:
                    # 仍开启自启动时写回 Run
                    if ucfg.data.get("auto_start"):
                        tool.autoStart_registry()
                    self.window.evaluate_js("setPriorityBtnActive(false)")
        if part == "get_taskScheduler_state":
            enabled = tool.is_taskScheduler_enabled()
            self.window.evaluate_js(f"setPriorityBtnActive({str(enabled).lower()})")
        if part == "full_screen":
            if data == False:
                self.ignore_action = True
                self.window.resize(ww, hh)
                width, height, end_x, end_y = tool.get_window_inf(self.window.title)
                win32gui.MoveWindow(hwnd, int(end_x), int(end_y), width, height, True)
                time.sleep(1)
                self.ignore_action = False
            else:
                self.window.hide()
                win32gui.MoveWindow(windowMgr.hwnd, 0, 0, screen_width, screen_height, True)
                self.window.show()
        if part == "show_sysApp":
            self.call_refresh()
        if part == "cf_hotkey":
            ucfg.update_config("cf_type","4")
        if part == "outPos":
            rect = tool.get_window_rect(hwnd)
            width = rect["width"]
            height = rect["height"]
            current_x = rect["left"]
            current_y = rect["top"]
            go_x,go_y = tool.get_targetPos(width,height)
            print("update_ani")
            self.animateWindow(current_x, current_y, go_x, go_y, width, height)
        if part == "blur_effect":
            if ucfg.data['blur_bg']== True and ucfg.data['bgType']!="1":
                now_t = self.window.evaluate_js("ThemeManager.now_theme")
                if now_t=="light":
                    WindowEffect.setLightBlurEffect(hwnd,effect=ucfg.data['blur_effect'])
                    print("from uc")
        if part == "blur_bg":
            if ucfg.data['blur_bg']==False:
                WindowEffect.resetEffect(hwnd)
        if part == "bgType":
            if data!='1':
                if ucfg.data['blur_bg']==False:
                    WindowEffect.resetEffect(hwnd,True)
            else:
                set_window_rounded_corners(hwnd)
        if part == "cf_type" or part == "cf_hotkey":
            hotkeyReg.hotkey_init()
    def call_refresh(self):
        self.window.evaluate_js("document.getElementById('b2d').click();fit_btnBar();scroll_top();")

windowMgr = windowMgr_main()
