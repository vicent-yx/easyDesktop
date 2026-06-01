


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
import keyboard
from threading import Thread


SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004


class hotkeyMgr:

    def __init__(self):
        self.hotKey = ""
        self._kb_event = None
        self._kb_thread = None
        self._kb_running = False

    def hotKey_action(self):
        if windowMgr.ignore_action == True:
            return
        try:
            if windowMgr.window_state == False:
                windowMgr.key_quick_start = True
            else:
                windowMgr.fullscreen_close = True
            windowMgr.call_js("document.body.focus()")
        except:
            self.reRegister()

    def register(self, hotKey):
        """注册热键，每 60 秒自动刷新钩子防止被 Windows 静默移除"""
        self.hotKey = hotKey
        self._clear()
        self._start_kb(hotKey)

    def _clear(self):
        self._kb_running = False
        try:
            if self._kb_event is not None:
                keyboard.remove_hotkey(self._kb_event)
                self._kb_event = None
        except:
            pass

    def _start_kb(self, hotKey):
        try:
            self._kb_event = keyboard.add_hotkey(hotKey, self.hotKey_action)
        except Exception as e:
            print(f"[hotkeyMgr] keyboard 注册异常: {e}")

        if self._kb_thread is None or not self._kb_thread.is_alive():
            self._kb_running = True
            self._kb_thread = Thread(target=self._keyboard_refresh_loop, daemon=True)
            self._kb_thread.start()

    def _keyboard_refresh_loop(self):
        """每 60 秒重置 keyboard 钩子，防止 WH_KEYBOARD_LL 被 Windows 静默移除"""
        while self._kb_running:
            time.sleep(60)
            if not self._kb_running:
                break
            try:
                keyboard.unhook_all()
                time.sleep(0.1)
                self._kb_event = keyboard.add_hotkey(self.hotKey, self.hotKey_action)
                print("[hotkeyMgr] keyboard 钩子已刷新")
            except Exception as e:
                print(f"[hotkeyMgr] keyboard 刷新失败: {e}")

    def hotkey_init(self):
        if ucfg.data["cf_type"] == "2":
            self.register("left windows+shift")
        if ucfg.data["cf_type"] == "3":
            self.register("left windows+escape")
        if ucfg.data["cf_type"] == "4":
            self.register(ucfg.data["cf_hotkey"])

    def reRegister(self):
        self.register(self.hotKey)

    def cleanup(self):
        """程序退出时清理所有热键资源"""
        self._clear()


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
        self.fit_hwnd = fit_hwnd
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
        screen_width,screen_height,ox,oy = screen.get_active_screen_size(True)
        self.key_quick_start = False
        if self.moving == True:
            return
        self.moving = True
        self.window_state = True
        self.window.evaluate_js("document.getElementById('themeSettingsPanel').style.display='none';enableScroll();")
        if ucfg.data["full_screen"] == True:
            w,h = screen.get_screen_size()
            self.window.resize(w, h)
        else:
            self.window.resize(ucfg.data["width"], ucfg.data["height"])
        hwnd = win32gui.FindWindow(None, cfg.DEFAULT_WINDOW_TITLE)
        if not hwnd:
            print(f"未找到名为 '{cfg.DEFAULT_WINDOW_TITLE}' 的窗口")
            return False
        try:
            windll.user32.keybd_event(0x12, 0, 0, 0)
            windll.user32.SetForegroundWindow(hwnd)
            windll.user32.keybd_event(0x12, 0, 0x0002, 0)
        except:
            pass
        screen_width,screen_height,ox,oy = screen.get_active_screen_size(True)
        rect = tool.get_window_rect(hwnd)
        width = rect["width"]
        height = rect["height"]
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
        win32gui.MoveWindow(hwnd, start_x, start_y, rect["width"], rect["height"], True)
        win32gui.UpdateWindow(hwnd)

        Thread(target=self.fit_blur_effect, daemon=True).start()

        self.window.show()
        time.sleep(0.1)
        print("outwindow_ani")
        self.animateWindow(start_x, start_y, end_x, end_y, rect["width"], rect["height"])
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
        screen_width, screen_height = screen.get_screen_size()
        if part == "themeChangeType":
            if data == "1":
                self.sys_theme()
            elif data == "2":
                windowMgr.fit_blur_effect()
                
        if part == "auto_start":
            if data == True:
                tool.autoStart_registry()
            else:
                tool.remove_autoStart_registry()
        if part == "full_screen":
            if data == False:
                self.ignore_action = True
                self.window.resize(ucfg.data["width"], ucfg.data["height"])
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
