from icoextract import IconExtractor
import os
import win32com.client
import win32gui
import win32api
import win32con
import time
import webview
import pystray
import subprocess
from pypinyin import pinyin, Style, lazy_pinyin
import shutil
import darkdetect
import json
from PIL import Image
import winreg as reg
import sys
from easygui import msgbox, buttonbox
from ctypes import windll,WinDLL,wintypes
from threading import Thread
from requests import get as requests_get
import webbrowser
import keyboard
import send2trash
import re
import win32ui
import config as cfg
from pyautogui import size
import traceback
import winerror
import win32event
import win32file
import win32pipe
import base64
import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
                    if window_state == False:
                        global key_quick_start
                        key_quick_start = True
                    else:
                        global fullscreen_close
                        fullscreen_close = True
                
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

has_opened_window = False
key_quick_start = False
start_action = False
has_cleared_fit = False
fullscreen_close = False
resize_window = None
ignore_action = False
loaded_exe_cache = {}
window_state = False
moving = False
icon = None
hwnd = None
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


def get_real_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


os.chdir(get_real_path())

def bugs_report(part,data,note=True):
    if not os.path.exists(cfg.BUGS_REPORT_DIR):
        os.mkdir(cfg.BUGS_REPORT_DIR)
    bugs_report_file = cfg.BUGS_REPORT_DIR + "/" + str(int(time.time())) + ".txt"
    with open(bugs_report_file, "w") as f:
        f.write(
            f"""
part: {part},
error: {data}
"""
        )
        f.close()
        if note==True:
            msgbox(
                "程序运行出现严重错误，请反馈给开发者，谢谢！\n错误已保存至bugs_report文件夹中\n点击ok将打开错误报告",
                cfg.APP_NAME+" 提示",
            )
            os.startfile(os.path.abspath(bugs_report_file))
def get_screen_size():
    r1_width = win32api.GetSystemMetrics(0)
    r1_height = win32api.GetSystemMetrics(1)

    r2_width,r2_height = size()
    if r1_width==r2_width and r1_height==r2_height:
        return r2_width,r2_height
    else:
        add_c_1 = r1_width+r1_width
        add_c_2 = r2_height+r2_height
        if add_c_1>add_c_2:
            return r1_width,r1_height
        else:
            return r2_width,r2_height


def get_active_window():
    """获取当前活动窗口的句柄，如果没有则返回 None"""
    a_hwnd = win32gui.GetForegroundWindow()
    return a_hwnd if a_hwnd else None

def get_sfb():
    windll.user32.SetProcessDPIAware()
    try:
        # 获取系统DPI（Windows 10 1607+）
        dpi = windll.user32.GetDpiForSystem()
        scaling_percentage = round(dpi / 96)
        return scaling_percentage
    except AttributeError:
        return 1.5

sfb = 1
print("sfb = ",sfb)
screen_width, screen_height = get_screen_size()
print(screen_width, screen_height)
width = int(screen_width * cfg.WINDOW_WIDTH_RATIO)
height = int(screen_height * cfg.WINDOW_HEIGHT_RATIO)

default_config = cfg.get_default_config(width, height)
if os.path.exists(cfg.CONFIG_FILE):
    config = json.load(open(cfg.CONFIG_FILE))
    for c_item in default_config.keys():
        if c_item not in config.keys():
            config[c_item] = default_config[c_item]
    json.dump(config, open(cfg.CONFIG_FILE, "w"))
else:
    config = default_config
    json.dump(config, open(cfg.CONFIG_FILE, "w"))

if not os.path.exists(cfg.CL_DATA_FILE):
    with open(cfg.CL_DATA_FILE, "w") as f:
        json.dump({}, f)
        f.close()

if not os.path.exists(cfg.USER_CLASS_FILE):
    itemClass = {config["df_dir"]:{}}
    with open(cfg.USER_CLASS_FILE, "w",encoding="utf-8") as f:
        json.dump(itemClass, f)
        f.close()
else:
    with open(cfg.USER_CLASS_FILE, "r",encoding="utf-8") as f:
        itemClass = json.load(f)
        f.close()

def hotKey_outAction():
    print("hotkey_go")
    global key_quick_start,window_state, fullscreen_close
    if window_state == False:
        key_quick_start = True
    else:
        fullscreen_close = True
    window.evaluate_js("document.body.focus()")
def hotkey_detect():
    while True:
        time.sleep(0.1)
        if config["cf_type"]=="2":
            if keyboard.is_pressed('left windows') and keyboard.is_pressed('shift'):
                hotKey_outAction()
                keyboard.read_key()
        if config["cf_type"]=="3":
            if keyboard.is_pressed('left windows') and keyboard.is_pressed('`'):
                hotKey_outAction()
                keyboard.read_key()
        if config["cf_type"]=="4":
            hk = config["cf_hotkey"].split("+")
            ok = 0
            for i in range(len(hk)):
                if keyboard.is_pressed(hk[i]):
                    ok += 1
            if ok == len(hk):
                hotKey_outAction()
                keyboard.read_key()

def turn_png(file_path):
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误：文件 '{file_path}' 不存在")
            return False

        # 检查文件扩展名是否为ico
        if not file_path.lower().endswith(".ico"):
            print(f"错误：文件 '{file_path}' 不是ICO文件")
            return False

        # 打开ICO文件并抑制警告
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with Image.open(file_path) as img:
                # 获取最大尺寸的图标
                if hasattr(img, "size") and img.size[0] > 0:
                    png_path = os.path.splitext(file_path)[0] + ".png"
                    img.save(png_path, "PNG")
                    return png_path
                else:
                    return "./resources/file_icos/exe.png"

    except Exception as e:
        print(f"转换ICO到PNG过程中发生错误: {str(e)}")
        return "./resources/file_icos/exe.png"


def get_desktop_path():
    shell = win32com.client.Dispatch("WScript.Shell")
    return shell.SpecialFolders("Desktop")


def get_icon(exe_path, name):
    try:
        dir_name = os.path.dirname(exe_path).replace("/", "-").replace(R"\\", "-").replace(":", "-")
        if not os.path.exists(cfg.DESKTOP_ICO_PATH + dir_name):
            os.makedirs(cfg.DESKTOP_ICO_PATH + dir_name)
        output_path = cfg.DESKTOP_ICO_PATH + dir_name + "/" + name + ".ico"

        # 检查exe文件是否存在
        if not os.path.exists(exe_path):
            print(f"警告：EXE文件不存在 {exe_path}")
            return "./resources/file_icos/exe.png"

        try:
            extractor = IconExtractor(exe_path)
            extractor.export_icon(output_path)
            output_path = turn_png(output_path)
            if output_path and output_path != "./resources/file_icos/exe.png":
                loaded_exe_cache[exe_path] = output_path
                return output_path
            else:
                # 如果转换失败，使用默认图标
                print(f"图标转换失败，使用默认图标: {exe_path}")
                return "./resources/file_icos/exe.png"
        except Exception as extract_error:
            print(f"图标提取失败: {extract_error} - {exe_path}")
            return "./resources/file_icos/exe.png"

    except Exception as e:
        print(f"获取图标时发生未知错误: {e} - {exe_path}")
        return "./resources/file_icos/exe.png"


def get_url_icon(url_path):
    # print(url_path)
    dir_name = os.path.dirname(url_path).replace("/", "-").replace(R"\\", "-").replace(":", "-")
    # 解析 .url 文件
    icon_file = None
    icon_index = 0
    try:
        with open(url_path, "r", encoding="utf-8") as f:
            content = f.read()
        icon_match = re.search(r"IconFile\s*=\s*(.*)", content, re.IGNORECASE)
        index_match = re.search(r"IconIndex\s*=\s*(\d+)", content, re.IGNORECASE)

        if icon_match:
            icon_file = icon_match.group(1).strip()
            if icon_file.startswith('"') and icon_file.endswith('"'):
                icon_file = icon_file[1:-1]
            icon_file = os.path.expandvars(icon_file)
            if not os.path.isabs(icon_file):
                base_dir = os.path.dirname(os.path.abspath(url_path))
                icon_file = os.path.join(base_dir, icon_file)

        if index_match:
            icon_index = int(index_match.group(1))
    except Exception as e:
        # print(f"解析 .url 文件失败: {e}")
        return "/resources/file_icos/exe.png"

    if not icon_file or not os.path.exists(icon_file):
        # print(f"图标文件不存在: {icon_file}")
        return "/resources/file_icos/exe.png"

    # 从文件资源中提取图标
    try:
        large, small = win32gui.ExtractIconEx(icon_file, icon_index)
        if not large and not small:
            return "/resources/file_icos/exe.png"
        hicon = large[0] if large else small[0]
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
        hdc = hdc.CreateCompatibleDC()
        hdc.SelectObject(hbmp)
        hdc.DrawIcon((0, 0), hicon)
        bmp_info = hbmp.GetInfo()
        bmp_bytes = hbmp.GetBitmapBits(True)
        image = Image.frombuffer("RGBA", (bmp_info["bmWidth"], bmp_info["bmHeight"]), bmp_bytes, "raw", "BGRA", 0, 1)

        # 清理资源
        win32gui.DestroyIcon(hicon)
        del hdc
        del hbmp
        if not os.path.exists(cfg.DESKTOP_ICO_PATH + dir_name):
            os.makedirs(cfg.DESKTOP_ICO_PATH + dir_name)
        image.save(cfg.DESKTOP_ICO_PATH + dir_name + "/" + os.path.basename(url_path) + ".png")
        return cfg.DESKTOP_ICO_PATH + dir_name + "/" + os.path.basename(url_path) + ".png"
    except Exception as e:
        print(f"提取图标失败: {e}")
        return "/resources/file_icos/exe.png"


def get_shortcut_target(shortcut_path):
    if not os.path.exists(shortcut_path):
        raise FileNotFoundError(f"快捷方式文件 {shortcut_path} 不存在")

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    return shortcut.TargetPath


def match_ico(file_name):
    extension = os.path.splitext(file_name)[1]
    if extension in cfg.FILE_ICO:
        return cfg.FILE_ICO[extension]
    elif extension in cfg.SCRIPTS_TYPE:
        return "./resources/file_icos/script.png"
    else:
        return cfg.FILE_ICO["unkonw"]


def check_recover(data, match):
    result = False
    for d in data:
        if d["filePath"] == match["filePath"] and d["fileName"] == match["fileName"]:
            result = True
            break
    return result
def is_cl(file_path):
    try:
        cl_data = json.load(open(cfg.CL_DATA_FILE, "r"))
        if file_path in cl_data:
            return cl_data[file_path]
        else:
            return False
    except Exception as e:
        print(f"读取收藏数据失败: {e}")
        return False

def update_inf(dir_path):
    print("update")
    try:
        if dir_path == "/\\":
            dir_path = "desktop"

        global config
        out_data = []
        exe_data = []
        dir_data = []
        file_data = []

        if dir_path == "desktop":
            get_count = 2
            path_list = [desktop_path, public_desktop]
        else:
            get_count = 1
            path_list = [dir_path]
        for i in range(get_count):
            current_dir = path_list[i]
            for item in os.listdir(current_dir):
                try:
                    if "desktop.ini" in item:
                        continue
                    filename, _ = os.path.splitext(item)
                    full_path = os.path.join(current_dir, item)
                    if os.path.isfile(full_path):
                        extension = os.path.splitext(full_path)[1]
                        if ".lnk" == extension or ".exe" == extension or ".EXE" == extension:
                            if ".lnk" == extension:
                                target_path = get_shortcut_target(full_path)
                                extension = os.path.splitext(target_path)[1]
                            else:
                                target_path = full_path
                                extension = os.path.splitext(target_path)[1]
                            if ".exe" == extension or ".EXE" == extension:
                                # 针对米哈游游戏的适配
                                if "miHoYo" in target_path and "launcher" in target_path:
                                    exe_icon = cfg.MIHOYO_GAMES["default"]  # 默认值
                                    for game_name, icon_path in cfg.MIHOYO_GAMES.items():
                                        if game_name != "default" and game_name in item:
                                            exe_icon = icon_path
                                            break
                                    exe_data.append(
                                        {
                                            "fileName": filename,
                                            "fileType": extension,
                                            "file": os.path.basename(target_path),
                                            "filePath": full_path,
                                            "realPath": target_path,
                                            "ico": exe_icon,
                                            "cl": is_cl(full_path),
                                        }
                                    )
                                else:
                                    if not target_path in loaded_exe_cache:
                                        exe_icon = get_icon(target_path, item)
                                    else:
                                        exe_icon = loaded_exe_cache[target_path]
                                    exe_data.append(
                                        {
                                            "fileName": filename,
                                            "fileType": extension,
                                            "file": os.path.basename(target_path),
                                            "filePath": full_path,
                                            "realPath": target_path,
                                            "ico": exe_icon,
                                            "cl": is_cl(full_path),
                                        }
                                    )
                                continue
                            elif ".url" == extension:
                                icon_image = get_url_icon(target_path)
                                exe_data.append(
                                    {
                                        "fileName": filename,
                                        "fileType": extension,
                                        "file": os.path.basename(full_path),
                                        "filePath": full_path,
                                        "ico": icon_image,
                                        "cl":is_cl(full_path),
                                    }
                                )
                            else:
                                if os.path.isfile(target_path):
                                    file_data.append(
                                        {
                                            "fileName": filename,
                                            "fileType": extension,
                                            "file": item,
                                            "filePath": target_path,
                                            "ico": match_ico(item),
                                            "cl": is_cl(target_path),
                                        }
                                    )
                                else:
                                    if target_path=="" or target_path==None:
                                        exe_data.append(
                                            {
                                                "fileName": os.path.basename(full_path),
                                                "fileType": extension,
                                                "file": item,
                                                "filePath": full_path,
                                                "ico":  get_url_icon(full_path),
                                                "cl": is_cl(target_path),
                                            }
                                        )
                                    else:
                                        dir_data.append(
                                            {
                                                "fileName": os.path.basename(full_path),
                                                "fileType": "文件夹",
                                                "file": item,
                                                "filePath": target_path,
                                                "ico": "./resources/file_icos/dir.png",
                                                "cl": is_cl(target_path),
                                            }
                                        )
                                continue
                        elif ".url" == extension:
                            icon_image = get_url_icon(full_path)
                            exe_data.append(
                                {
                                    "fileName": filename,
                                    "fileType": extension,
                                    "file": os.path.basename(full_path),
                                    "filePath": full_path,
                                    "ico": icon_image,
                                    "cl": is_cl(full_path),
                                }
                            )
                        else:
                            file_data.append(
                                {
                                    "fileName": filename,
                                    "fileType": extension,
                                    "file": item,
                                    "filePath": full_path,
                                    "ico": match_ico(item),
                                    "cl": is_cl(full_path),
                                }
                            )
                    else:
                        dir_data.append(
                            {
                                "fileName": item,
                                "fileType": "文件夹",
                                "file": item,
                                "filePath": full_path,
                                "ico": "./resources/file_icos/dir.png",
                                "cl": is_cl(full_path),
                            }
                        )
                except:
                    bugs_report(
                        "python-update_inf_item",
                        traceback.format_exc(),
                        False
                    )
        # if config["show_sysApp"]==True:
        if config["show_sysApp"] == True and (
            dir_path == "desktop"
            or dir_path == ""
            or dir_path == "/"
            or dir_path == desktop_path
            or dir_path == public_desktop
        ):
            for item in cfg.SYSTEM_APPS:
                item["cl"]=False
                out_data.append(item)
        for i in range(2):
            r = i==False
            for item in exe_data:
                if check_recover(out_data, item) == True:
                    continue
                if r==True and item["cl"]!=True:
                    continue
                out_data.append(item)
            for item in dir_data:
                if check_recover(out_data, item) == True:
                    continue
                if r==True and item["cl"]!=True:
                    continue
                out_data.append(item)
            for item in file_data:
                if check_recover(out_data, item) == True:
                    continue
                if r==True and item["cl"]!=True:
                    continue
                out_data.append(item)
        return out_data
    except:
        bugs_report(
            "python-update_inf",
            traceback.format_exc()
        )


def hide_from_taskbar(window):
    hwnd = windll.user32.FindWindowW(None, window.title)
    style = windll.user32.GetWindowLongW(hwnd, cfg.GWL_EXSTYLE)
    style = (style | cfg.WS_EX_TOOLWINDOW) & ~cfg.WS_EX_APPWINDOW
    windll.user32.SetWindowLongW(hwnd, cfg.GWL_EXSTYLE, style)


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

        # 获取窗口尺寸和位置信息
        rect = win32gui.GetWindowRect(active_hwnd)
        window_left, window_top = rect[0], rect[1]
        window_width, window_height = rect[2] - rect[0], rect[3] - rect[1]
        screen_width, screen_height = get_screen_size()
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


def is_ed_focused():
    active_hwnd = get_active_window()
    if not active_hwnd:
        return False
    window_title = win32gui.GetWindowText(active_hwnd)
    return window_title == cfg.DEFAULT_WINDOW_TITLE


def is_desktop_and_mouse_in_corner():
    global config
    try:
        screen_width = win32api.GetSystemMetrics(cfg.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(cfg.SM_CYSCREEN)
        corner_size = cfg.CORNER_SIZE  # 角落区域的边长
        if config["outPos"]=="1":
            corner_rect = (0, screen_height - corner_size, corner_size, screen_height)
        elif config["outPos"]=="2":
            corner_rect = (0, 0, corner_size, corner_size)
        elif config["outPos"]=="3":
            cw = int(screen_width//3)
            corner_rect = (cw,screen_height-corner_size,screen_width-cw,screen_height)
        elif config["outPos"]=="4":
            cw = int(screen_width//3)
            corner_rect = (cw,0,screen_width-cw,corner_size)
        mouse_x, mouse_y = win32api.GetCursorPos()
        in_corner = corner_rect[0] <= mouse_x <= corner_rect[2] and corner_rect[1] <= mouse_y <= corner_rect[3]
        return in_corner
    except Exception as e:
        print(f"Error: {e}")
        return False


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


def wait_open():
    global key_quick_start, config,window_state,start_action
    start_wait_time = int(time.time())
    had_refresh = False
    while True:
        if int(time.time()) - start_wait_time > cfg.WAIT_TIMEOUT:
            if had_refresh == False:
                window.evaluate_js("document.getElementById('b2d').click();fit_btnBar();")
                had_refresh = True
        if config["fdr"] == True:
            if is_focused_window_fullscreen() == True:
                time.sleep(1)
                continue
        if config["cf_type"] == "2" or config["cf_type"] == "3" or config["cf_type"]=="4":
            if key_quick_start == True:
                out_window()
                break
        if start_action == True:
            start_action = False
            out_window()
            break
        else:
            if is_desktop_and_mouse_in_corner() and config["cf_type"] == "1":
                out_window()
                break
        if window_state == True:
            break
        time.sleep(cfg.SLEEP_INTERVAL)


def ease_out_quad(t):
    # 缓动函数
    return t * (2 - t)


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


def animate_window(
    hwnd, start_x, start_y, end_x, end_y, width, height, steps=cfg.ANIMATION_STEPS, delay=cfg.ANIMATION_DELAY
):
    global window, config
    screen_width, screen_height = get_screen_size()
    for i in range(steps + 1):
        progress = i / steps
        eased_progress = ease_out_quad(progress)
        current_x = start_x + (end_x - start_x) * eased_progress
        current_y = start_y + (end_y - start_y) * eased_progress
        if config["full_screen"] == True:
            if start_x < end_x:
                win32gui.MoveWindow(hwnd, int(current_x), int(current_y), screen_width, screen_height, True)
            else:
                win32gui.MoveWindow(
                    hwnd,
                    int(current_x),
                    int(current_y),
                    int(screen_width),
                    int(screen_height),
                    # int(screen_width - (screen_width * eased_progress)),
                    # int(screen_height - (screen_height * eased_progress)),
                    True,
                )
        else:
            if (
                ((config["outPos"] in ["1","2"]) and (start_x < end_x)) or (config["outPos"]=="3" and start_y>end_y) or (config["outPos"]=="4" and end_y>start_y)
            ):
                win32gui.MoveWindow(hwnd, int(current_x), int(current_y), width, height, True)
            else:
                win32gui.MoveWindow(
                    hwnd,
                    int(current_x),
                    int(current_y),
                    int(config["width"]),
                    int(config["height"]),
                    # int(config["width"] - (config["width"] * eased_progress)),
                    # int(config["height"] - (config["height"] * eased_progress)),
                    True,
                )
        time.sleep(delay)

def get_targetPos(win_width=None,win_height=None):
    if win_width==None:
        win_width = width
    if win_height==None:
        win_height = height
    global config
    screen_width = win32api.GetSystemMetrics(cfg.SM_CXSCREEN)
    screen_height = win32api.GetSystemMetrics(cfg.SM_CYSCREEN)
    if config["outPos"]=="1":
        end_x = int(screen_width * cfg.WINDOW_POSITION_RATIO)
        end_y = int(screen_height - ((screen_height * cfg.WINDOW_POSITION_RATIO) + win_height))
    elif config["outPos"]=="2":
        end_x = int(screen_width * cfg.WINDOW_POSITION_RATIO)
        end_y = int((screen_height * cfg.WINDOW_POSITION_RATIO))
    elif config["outPos"]=="3":
        end_x = int((screen_width-win_width)//2)
        end_y = int(screen_height - ((screen_height * cfg.WINDOW_POSITION_RATIO) + win_height))
    elif config["outPos"]=="4":
        end_x = int((screen_width-win_width)//2)
        end_y = int((screen_height * cfg.WINDOW_POSITION_RATIO))
    return end_x,end_y
def out_window():
    global moving, ignore_action, fullscreen_close, key_quick_start,window_state,config
    key_quick_start = False
    if moving == True:
        return
    moving = True
    window_state = True
    if config["full_screen"] == False:
        window.resize(config["width"], config["height"])
    window.evaluate_js("document.getElementById('themeSettingsPanel').style.display='none';enableScroll();NavigationManager.refreshCurrentPath();fit_btnBar();")
    hwnd = win32gui.FindWindow(None, cfg.DEFAULT_WINDOW_TITLE)
    hide_from_taskbar(window)
    if not hwnd:
        print(f"未找到名为 '{cfg.DEFAULT_WINDOW_TITLE}' 的窗口")
        return False
    try:
        windll.user32.keybd_event(0x12, 0, 0, 0)
        windll.user32.SetForegroundWindow(hwnd)
        windll.user32.keybd_event(0x12, 0, 0x0002, 0)
    except:
        pass
    screen_width = win32api.GetSystemMetrics(cfg.SM_CXSCREEN)
    screen_height = win32api.GetSystemMetrics(cfg.SM_CYSCREEN)
    rect = get_window_rect(hwnd)
    width = rect["width"]
    height = rect["height"]
    if config["outPos"]=="1":
        start_x = -width
        start_y = screen_height - height // 2
    elif config["outPos"]=="2":
        start_x = -width
        start_y = 0 - (height // 2)
    elif config["outPos"]=="3":
        start_x = int((screen_width-width)//2)
        start_y = screen_height + height
    elif config["outPos"]=="4":
        start_x = (screen_width-width)//2
        start_y = -height
    if config["full_screen"] == True:
        end_x = 0
        end_y = 0
    else:
        end_x,end_y = get_targetPos(width,height)
    print(end_y)
    win32gui.MoveWindow(hwnd, start_x, start_y, rect["width"], rect["height"], True)
    win32gui.UpdateWindow(hwnd)

    time.sleep(0.1)
    window.show()
    animate_window(hwnd, start_x, start_y, end_x, end_y, rect["width"], rect["height"])
    window.evaluate_js("window_state=true;")

    while True:
        if fullscreen_close == True:
            break
        if config["out_cf_type"] == "2" and is_ed_focused() == False:
            break
        if is_mouse_in_easyDesktop() == True:
            break
        time.sleep(cfg.MOUSE_CHECK_INTERVAL)
    moving = False

    while True:
        if config["out_cf_type"] == "1" or (config["out_cf_type"]=="3" and config["cf_type"]=="1"):
            tj = is_mouse_in_easyDesktop() == False and ignore_action == False
        else:
            tj = is_ed_focused() == False and ignore_action == False
        if (tj == True and config["full_screen"] == False) or fullscreen_close == True:
            fullscreen_close = False
            if ignore_action == False:
                moveIn_window()
            break

        if window_state == False:
            break
        time.sleep(cfg.MOUSE_CHECK_INTERVAL)


def moveIn_window():
    global moving,window_state,hwnd,ignore_action
    if moving == True:
        return
    moving = True
    window_state = False
    hwnd = win32gui.FindWindow(None, cfg.DEFAULT_WINDOW_TITLE)
    if not hwnd:
        print(f"未找到名为 '{cfg.DEFAULT_WINDOW_TITLE}' 的窗口")
        return False
    screen_width = win32api.GetSystemMetrics(cfg.SM_CXSCREEN)
    screen_height = win32api.GetSystemMetrics(cfg.SM_CYSCREEN)
    rect = get_window_rect(hwnd)
    width = rect["width"]
    height = rect["height"]
    current_x = rect["left"]
    current_y = rect["top"]
    if config["outPos"]=="1":
        start_x = -width
        start_y = screen_height - height // 2
    elif config["outPos"]=="2":
        start_x = -width
        start_y = 0 - (height // 2)
    elif config["outPos"]=="3":
        start_x = int((screen_width-width)//2)
        start_y = screen_height + height
    elif config["outPos"]=="4":
        start_x = (screen_width-width)//2
        start_y = -height
    window.evaluate_js("window_state=false;preview_runing = false;")
    animate_window(hwnd, current_x, current_y, start_x, start_y, width, height)
    window.hide()
    moving = False
    wait_open()


def sys_theme():
    if darkdetect.isDark() == True:
        window.evaluate_js("load_theme('dark')")
    else:
        window.evaluate_js("load_theme('light')")


def check_update():
    global config
    try:
        r = requests_get("https://api.codevicent.xyz/app_inf/ed")
    except:
        print("无法访问更新服务器")
        return
    if r.status_code != 200:
        print("无法访问更新服务器")
        return
    r = json.loads(str(r.content, "utf-8"))
    if r["v"] != cfg.APP_VERSION:
        print("有新版本")
        if config["ign_update"] == r["v"]:
            return
        ask = buttonbox(
            f"{cfg.APP_NAME}有新版本，是否前往更新？\n" + r["update_inf"],
            f"{cfg.APP_NAME}更新检查",
            choices=("前往更新", "忽略此版本", "取消"),
        )
        if ask == "前往更新":
            webbrowser.open(r["download_url"])
        elif ask == "忽略此版本":
            update_config("ign_update", r["v"])
        else:
            pass
    else:
        print("无新版本")


def on_loaded():
    global hwnd, config
    if config["full_screen"] == True:
        window.resize(screen_width, screen_height)
    window.hide()
    Thread(target=check_update).start()
    Thread(target=stray).start()
    Thread(target=hotkey_detect).start()
    start_pipe_server()
    sys_theme()
    if config["view"] == "list":
        window.evaluate_js("list_view()")
    else:
        window.evaluate_js("grid_view()")
    hwnd = win32gui.FindWindow(None, cfg.DEFAULT_WINDOW_TITLE)
    moveIn_window()
    # wait_open()


def update_config(part, data):
    global config, ignore_action,hwnd
    config[part] = data
    json.dump(config, open("config.json", "w"))
    if part == "follow_sys" and data == True:
        sys_theme()
    if part == "auto_start":
        if data == True:
            autoStart_registry()
        else:
            remove_autoStart_registry()
    if part == "full_screen":
        if data == False:
            ignore_action = True
            window.resize(config["width"], config["height"])
            width, height, end_x, end_y = get_window_inf(window.title)
            win32gui.MoveWindow(hwnd, int(end_x), int(end_y), width, height, True)
            time.sleep(1)
            ignore_action = False
        else:
            win32gui.MoveWindow(hwnd, 0, 0, screen_width, screen_height, True)
    if part == "show_sysApp":
        window.evaluate_js("document.getElementById('b2d').click();fit_btnBar();")
    if part == "cf_hotkey":
        update_config("cf_type","4")
    if part == "outPos":
        rect = get_window_rect(hwnd)
        width = rect["width"]
        height = rect["height"]
        current_x = rect["left"]
        current_y = rect["top"]
        go_x,go_y = get_targetPos(width,height)
        animate_window(hwnd, current_x, current_y, go_x, go_y, width, height)

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


def get_window_inf(title=cfg.DEFAULT_WINDOW_TITLE):
    global config
    hwnd = win32gui.FindWindow(None, title)
    rect = get_window_rect(hwnd)
    width = rect["width"]
    height = rect["height"]
    end_x, end_y = get_targetPos(width, height)
    return width, height, end_x, end_y


desktop_path = get_desktop_path()
public_desktop = os.path.join(os.environ["PUBLIC"], "Desktop")


def get_initials(text):
    initials = pinyin(text, style=Style.FIRST_LETTER, errors="default")
    return "".join([item[0] for item in initials])


def getPinyin(text):
    result = "".join(lazy_pinyin(text, style=Style.NORMAL, errors="default"))
    return result


def quit_ed():
    global icon
    window.destroy()
    icon.stop()
    os._exit(0)
def start_out():
    global start_action
    start_action=True

def stray():
    global icon
    image = Image.open("ed_logo.png")
    icon = pystray.Icon("name", image, "title")
    menu = (pystray.MenuItem("呼出", start_out),pystray.MenuItem("退出", quit_ed))
    icon.menu = menu
    icon.title = "EasyDesktop"
    icon.run()


def open_sysApp_action(component_name):
    if component_name not in cfg.SYSTEM_COMMANDS:
        return False
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        subprocess.Popen(cfg.SYSTEM_COMMANDS[component_name], startupinfo=startupinfo, shell=True)
        return True
    except Exception as e:
        print(f"打开 {component_name} 时出错: {str(e)}")
        return False

class AppAPI:
    def bug_report(self, part, data):
        bugs_report(
            part,
            data
        )
    def is_path_abs(self,path):
        return os.path.isabs(path)
    def change_cl_state(self,filePath, state):
        cl_data = json.load(open(cfg.CL_DATA_FILE,"r"))
        cl_data[filePath] = not state
        json.dump(cl_data,open(cfg.CL_DATA_FILE,"w"))
    def set_background(self):
        try:
            global ignore_action
            file_types = ("Image Files (*.bmp;*.jpg;*.gif;*.png;*.jpeg)", "All files (*.*)")
            ignore_action = True
            bg_file = window.create_file_dialog(file_types=file_types, allow_multiple=False)
            ignore_action = False
            bg_file = bg_file[0]
            if bg_file:
                file_path = "bg." + str(bg_file).split(".")[-1]
                if os.path.exists(config["bg"]):
                    os.remove(config["bg"])
                shutil.copy(bg_file, file_path)
                return file_path
            return ""
        except:
            return ""

    def get_config(self):
        global config
        return config

    def update_config(self, part, data):
        update_config(part, data)

    def search_desktop_path(self):
        return desktop_path

    def get_parent(self, path):
        pr_path = os.path.dirname(path)
        if pr_path == desktop_path or pr_path == public_desktop:
            return "desktop"
        return pr_path

    def load_search_index(self, data):
        outData = {}
        for f in data:
            outData[f["fileName"]] = {"sxpy": get_initials(f["fileName"]), "py": getPinyin(f["fileName"])}
        return outData

    def fit_window_start(self):
        global ignore_action, config, resize_window, hwnd, has_cleared_fit
        if config["full_screen"] == True:
            return
        ignore_action = True
        width, height, end_x, end_y = get_window_inf()
        window.hide()
        resize_window = webview.create_window(
            "easyDesktop-fit",
            "easyFileDesk.html",
            x=end_x,
            y=end_y,
            js_api=AppAPI(),
            confirm_close=False,
            shadow=True,
            on_top=True,
            easy_drag=False,
            resizable=True,
            draggable=False
        )
        has_cleared_fit = False
        resize_window.resize(config["width"], config["height"])
        resize_window.evaluate_js("disable_settings()")
        print("config:", config["width"], config["height"])
        print("window: ", width, height)
        print("webview:", window.width, window.height)
        time.sleep(3)
        while True:
            try:
                resize_window.get_cookies()
                active_hwnd = get_active_window()
                if not active_hwnd:
                    break
                window_title = win32gui.GetWindowText(active_hwnd)
                if window_title != "easyDesktop-fit":
                    break
            except:
                break
            time.sleep(cfg.MOUSE_CHECK_INTERVAL)
        if has_cleared_fit == False:
            self.fit_window_end()

    def fit_window_end(self):
        global ignore_action, config, resize_window, has_cleared_fit
        has_cleared_fit = True
        try:
            width, height, end_x, end_y = get_window_inf(resize_window.title)
        except:
            window.show()
            return
        window.resize(width, height)
        update_config("width", width)
        update_config("height", height)
        resize_window.destroy()
        window.show()
        width, height, end_x, end_y = get_window_inf(window.title)
        win32gui.MoveWindow(hwnd, int(end_x), int(end_y)
                            , width, height, True)
        time.sleep(1)
        ignore_action = False

    def change_default_dir(self, path):
        if path == None:
            path = window.create_file_dialog(dialog_type=webview.FOLDER_DIALOG)
            if path != None:
                path = path[0]
                update_config("df_dir", path)
                name = os.path.basename(path)
                if name == "":
                    name = path.split("\\")[-2]
                update_config("df_dir_name", name)
                return {"success": True, "data": path, "name": name}
            else:
                return {"success": True, "data": config["df_dir"], "name": config["df_dir_name"]}
        else:
            update_config("df_dir", "desktop")
            update_config("df_dir_name", "桌面")
            return {"success": True, "data": path, "name": "桌面"}

    def get_fileinfo(self, path):
        if path == "desktop" or path == "" or path == "\\":
            path = "desktop"
        data = update_inf(path)
        return {"success": True, "data": data}

    def close_fullscreen_window(self):
        global fullscreen_close, config
        if config["full_screen"] == True:
            fullscreen_close = True

    def open_file(self, file_path):
        global fullscreen_close, config
        os.startfile(file_path)
        if config["of_s"] == True:
            fullscreen_close = True
        return {"success": True}

    def show_file(self, file_path):
        global fullscreen_close
        file = os.path.realpath(file_path)
        subprocess.Popen(
            f"explorer /select, {file}", shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8"
        )
        fullscreen_close = True
        return {"success": True}

    def open_mhyGame(self, file_path, game):
        """打开米哈游游戏"""
        try:
            os.startfile(file_path)
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": f"无法打开游戏: {str(e)}"}

    def copy_file(self, file_path):
        subprocess.run(
            ["powershell", "-Command", f"Get-Item {file_path} | Set-Clipboard"],
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return {"success": True}

    def rename_file(self, file_path, new_name):
        if os.path.isfile(file_path):
            new_path = os.path.join(os.path.dirname(file_path), new_name + os.path.splitext(file_path)[1])
        else:
            new_path = os.path.join(os.path.dirname(file_path), new_name)
        os.rename(file_path, os.path.join(os.path.dirname(file_path), new_path))
        return {"success": True, "file": new_path}

    def remove_file(self, file_path, del_type="remove"):
        try:
            if del_type == "rubbish":
                send2trash.send2trash(file_path)
                return {"success": True}
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except:
            return {"success": False, "message": "拒绝访问（无权限）"}
        finally:
            return {"success": True}

    def new_file(self, suffix, current_path):
        if current_path == "desktop" or current_path == "" or current_path == "\\":
            current_path = desktop_path
        try:
            if suffix == "folder":
                base_name = "新建文件夹"
            else:
                base_name = f"新建文档.{suffix}"
            file_path = os.path.join(current_path, base_name)
            if not os.path.exists(file_path):
                if suffix == "folder":
                    os.mkdir(file_path)
                elif suffix == "xlsx":
                    print("创建表格：", file_path)
                    shutil.copy(cfg.EMPTY_XLSX_TEMPLATE, file_path)
                else:
                    with open(file_path, "w") as f:
                        f.write("")
                print(f"已创建: {file_path}")
                return {"success": True, "file": file_path}
            count = 1
            while True:
                if suffix == "folder":
                    new_name = f"新建文件夹{count}"
                else:
                    new_name = f"新建文档{count}.{suffix}"
                new_path = os.path.join(desktop_path, new_name)
                if not os.path.exists(new_path):
                    if suffix == "folder":
                        os.mkdir(new_path)
                    elif suffix == "xlsx":
                        print("创建表格：", new_path)
                        shutil.copy(cfg.EMPTY_XLSX_TEMPLATE, new_path)
                    else:
                        with open(new_path, "w") as f:
                            f.write("")
                    print(f"已创建: {new_path}")
                    return {"success": True, "file": new_path}
                count += 1
        except:
            return {"success": False, "message": "拒绝访问"}

    def lock_window_visibility(self):
        """锁定窗口可见性（不自动隐藏）"""
        global ignore_action
        ignore_action = True

    def unlock_window_visibility(self):
        """解锁窗口可见性（恢复自动隐藏）"""
        global ignore_action
        ignore_action = False

    def open_sysApp(self,app_name):
        open_sysApp_action(app_name)
    def put_file(self, target_path):
        if target_path == "desktop" or target_path == "" or target_path == "\\":
            target_path = desktop_path
        saved_files = []
        command = [
            "powershell",
            "-Command",
            "$files = Get-Clipboard -Format FileDropList; "
            "if ($files) { $files | ForEach-Object { $_.FullName } }",
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        output = result.stdout.strip()
        if not output:
            return {"success": True}
        file_paths = [path.strip() for path in output.splitlines() if path.strip()]

        # 验证所有文件路径是否有效
        valid_paths = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                valid_paths.append(file_path)
            else:
                return {"success": False, "message": "剪切板中没有有效的文件"}

        if not valid_paths:
            return {"success": False, "message": "剪切板中没有有效的文件"}
        for src_path in valid_paths:
            filename = os.path.basename(src_path)
            dest_path = os.path.join(target_path, filename)
            # 处理文件名冲突
            counter = 1
            base_name, extension = os.path.splitext(filename)
            while os.path.exists(dest_path):
                new_filename = f"{base_name}_{counter}{extension}"
                dest_path = os.path.join(desktop_path, new_filename)
                counter += 1
            shutil.copy2(src_path, dest_path)
            saved_files.append(os.path.abspath(dest_path))
        return {"success": True, "files": saved_files}
    def add_class(self,files,key):
        global itemClass,config
        itemClass[config["df_dir"]][key] = files
        with open(cfg.USER_CLASS_FILE,"w",encoding="utf-8") as f:
            json.dump(itemClass,f,ensure_ascii=False)
        return {"success":True}
    def read_class(self,key):
        global itemClass
        if key=="" or key=="all" or key=="全部":
            if not config["df_dir"] in itemClass:
                itemClass[config["df_dir"]]={}
            return {"success":True,"data":itemClass[config["df_dir"]]}
        if key in itemClass[config["df_dir"]]:
            return {"success":True,"files":itemClass[config["df_dir"]][key]}
        else:
            return {"success":False,"files":[],"message":"没有找到该分类的文件"}
    def remove_class(self,key):
        global itemClass
        if key in itemClass[config["df_dir"]]:
            del itemClass[config["df_dir"]][key]
            with open(cfg.USER_CLASS_FILE,"w",encoding="utf-8") as f:
                json.dump(itemClass,f,ensure_ascii=False)
        return {"success":True}

    def get_imageBase64(self,file_path):
        max_size_kb = 200
        quality=85
        step=5
        # try:
        img = Image.open(file_path)
        
        # 保持原比例
        original_width, original_height = img.size
        
        # 转换为RGB模式（如果是RGBA或其他模式）
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 逐步降低质量直到满足大小要求
        output_buffer = io.BytesIO()
        current_quality = quality
        
        while current_quality > 10:  # 设置最低质量限制
            output_buffer.seek(0)
            output_buffer.truncate(0)
            
            # 保存图片到内存缓冲区
            img.save(output_buffer, format='JPEG', quality=current_quality, optimize=True)
            
            # 检查文件大小
            file_size_kb = len(output_buffer.getvalue()) / 1024
            
            if file_size_kb <= max_size_kb:
                break
            
            # 如果仍然太大，降低质量
            current_quality -= step
        
        # 如果仍然太大，尝试调整尺寸（保持比例）
        if len(output_buffer.getvalue()) / 1024 > max_size_kb:
            # 计算需要缩小的比例
            scale_factor = (max_size_kb * 1024 / len(output_buffer.getvalue())) ** 0.5
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            # 调整尺寸
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 重新压缩
            output_buffer.seek(0)
            output_buffer.truncate(0)
            img_resized.save(output_buffer, format='JPEG', quality=80, optimize=True)
        
        # 转换为base64字符串
        base64_string = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        blob_string = f"data:image/jpeg;base64,{base64_string}"
        
        return blob_string
        # except:
        #     return None
    
    def disable_autoClose(self):
        global ignore_action
        ignore_action = True
    def enable_autoClose(self):
        global ignore_action
        ignore_action = False

webview.settings["ALLOW_FILE_URLS"] = True
window = webview.create_window(
    cfg.APP_NAME,
    "easyFileDesk.html",
    width=config["width"],
    height=config["height"],
    js_api=AppAPI(),
    confirm_close=False,
    frameless=True,
    shadow=True,
    on_top=True,
    hidden=True,
    easy_drag=False,
    resizable=False,
)
webview.start(func=on_loaded,debug=True)