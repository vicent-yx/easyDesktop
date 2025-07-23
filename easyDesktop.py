from icoextract import IconExtractor
import os
import win32com.client
import win32gui
import win32api
import win32con

# import win32event
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
from ctypes import windll
from threading import Thread
from requests import get as requests_get
import webbrowser

import keyboard
import send2trash
import re
import win32ui


try:
    json.dump("", open("test.json", "w", encoding="utf-8"))
except PermissionError:
    msgbox(
        "遇到权限问题，请以管理员身份运行或将软件安装到非C盘目录，否则将无法使用自定义背景及设置保存功能。",
        "EasyDesktop",
    )
finally:
    if os.path.exists("test.json"):
        os.remove("test.json")

icon = None
hwnd = None
os.environ["FUSION_LOG"] = "1"
os.environ["FUSION_LOG_PATH"] = "/logs/"
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


def get_screenSize():
    # 使用原生 Windows API 获取屏幕尺寸
    screen_width = win32api.GetSystemMetrics(0)  # SM_CXSCREEN
    screen_height = win32api.GetSystemMetrics(1)  # SM_CYSCREEN
    return screen_width, screen_height


def getActiveWindow():
    """获取当前活动窗口的句柄，如果没有则返回 None"""
    hwnd = win32gui.GetForegroundWindow()
    return hwnd if hwnd else None


screen_width, screen_height = get_screenSize()
print(screen_width, screen_height)
width = int(screen_width * 0.65)
height = int(screen_height * 0.4)
defeat_config = {
    "theme": "light",
    "language": "zh-CN",
    "follow_sys": True,
    "theme": "light",
    "view": "block",
    "auto_start": False,
    "use_bg": False,
    "bg": "",
    "ms_ef": 0,
    "ign_update": "",
    "width": width,
    "height": height,
    "full_screen": False,
    "fdr": True,
    "cf_type": "1",
    "out_cf_type": "1",
    "show_sysApp": False,
    "scale": 100,
    "df_dir": "desktop",
    "df_dir_name": "桌面",
    "of_s": True,
}
if os.path.exists("config.json"):
    config = json.load(open("config.json"))
    for c_item in defeat_config.keys():
        if c_item not in config.keys():
            config[c_item] = defeat_config[c_item]
    json.dump(config, open("config.json", "w"))
else:
    config = defeat_config
    json.dump(config, open("config.json", "w"))

had_open_win = False
key_quik_start = False
had_clear_fit = False
fullS_close = False
resize_window = None
ignore_action = False
had_load_exe = {}
window_state = False
moving = False
file_ico_path = "./resources/file_icos/"
scripts_type = [
    ".py",
    ".java",
    ".c",
    ".vbs",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".php",
    ".rb",
    ".go",
    ".swift",
    ".kt",
    ".m",
    ".pl",
    ".r",
    ".sh",
    ".bash",
    ".zsh",
    ".lua",
    ".scala",
    ".groovy",
    ".dart",
    ".rs",
    ".jl",
    ".hs",
    ".f",
    ".f90",
    ".f95",
    ".v",
    ".vhd",
    ".clj",
    ".ex",
    ".exs",
    ".elm",
    ".purs",
    ".erl",
    ".hrl",
    ".fs",
    ".fsx",
    ".fsi",
    ".ml",
    ".mli",
    ".pas",
    ".pp",
    ".d",
    ".nim",
    ".cr",
    ".cbl",
    ".cob",
    ".ada",
    ".adb",
    ".ads",
]
file_ico = {
    ".mp3": "./resources/file_icos/mp3.png",
    ".mp4": "./resources/file_icos/mp4.png",
    ".mkv": "./resources/file_icos/mkv.png",
    ".m4a": "./resources/file_icos/m4a.png",
    ".doc": "./resources/file_icos/doc.png",
    ".docx": "./resources/file_icos/docx.png",
    ".xls": "./resources/file_icos/xls.png",
    ".xlsx": "./resources/file_icos/xlsx.png",
    ".pdf": "./resources/file_icos/pdf.png",
    ".ppt": "./resources/file_icos/ppt.png",
    ".pptx": "./resources/file_icos/pptx.png",
    ".zip": "./resources/file_icos/zip.png",
    ".rar": "./resources/file_icos/zip.png",
    ".png": "./resources/file_icos/image.png",
    ".jpg": "./resources/file_icos/image.png",
    ".jpeg": "./resources/file_icos/image.png",
    ".gif": "./resources/file_icos/image.png",
    ".txt": "./resources/file_icos/txt.png",
    ".html": "./resources/file_icos/html.png",
    ".css": "./resources/file_icos/css.png",
    ".js": "./resources/file_icos/js.png",
    ".bat": "./resources/file_icos/bat.png",
    "unkonw": "./resources/file_icos/unkonw.png",
}


def putOut_window(cf):
    global key_quik_start, config, window_state, fullS_close
    if cf == config["cf_type"]:
        if window_state == False:
            key_quik_start = True
        else:
            fullS_close = True


def key_cf2():
    putOut_window("2")


def key_cf3():
    putOut_window("3")


keyboard.add_hotkey("windows+shift", key_cf2)
keyboard.add_hotkey("windows+`", key_cf3)


def get_sfb():
    windll.user32.SetProcessDPIAware()
    try:
        # 获取系统DPI（Windows 10 1607+）
        dpi = windll.user32.GetDpiForSystem()
        scaling_percentage = round(dpi / 96)
        return scaling_percentage
    except AttributeError:
        return 1.5


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

        # 打开ICO文件
        with Image.open(file_path) as img:
            png_path = os.path.splitext(file_path)[0] + ".png"
            img.save(png_path, "PNG")
            # os.remove(file_path)
            return png_path

    except Exception as e:
        print(f"转换过程中发生错误: {str(e)}")
        return "/resources/file_icos/exe.png"


def get_desktop_path():
    shell = win32com.client.Dispatch("WScript.Shell")
    return shell.SpecialFolders("Desktop")


def get_icon(exe_path, name):
    try:
        dir_name = os.path.dirname(exe_path).replace("/", "-").replace(R"\\", "-").replace(":", "-")
        if not os.path.exists("./desktopICO/" + dir_name):
            os.makedirs("./desktopICO/" + dir_name)
        output_path = "./desktopICO/" + dir_name + "/" + name + ".ico"
        extractor = IconExtractor(exe_path)
        extractor.export_icon(output_path)
        output_path = turn_png(output_path)
        had_load_exe[exe_path] = output_path
        return output_path
    except Exception as e:
        print(e, "\n", exe_path)
        return "/resources/file_icos/exe.png"


def get_url_icon(url_path):
    print(url_path)
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
        print(f"解析 .url 文件失败: {e}")
        return "/resources/file_icos/exe.png"

    if not icon_file or not os.path.exists(icon_file):
        print(f"图标文件不存在: {icon_file}")
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
        if not os.path.exists("./desktopICO/" + dir_name):
            os.makedirs("./desktopICO/" + dir_name)
        image.save("./desktopICO/" + dir_name + "/" + os.path.basename(url_path) + ".png")
        return "./desktopICO/" + dir_name + "/" + os.path.basename(url_path) + ".png"
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
    if extension in file_ico:
        return file_ico[extension]
    elif extension in scripts_type:
        return "/resources/file_icos/script.png"
    else:
        return file_ico["unkonw"]


def check_recover(data, match):
    result = False
    for d in data:
        if d["filePath"] == match["filePath"] and d["fileName"] == match["fileName"]:
            result = True
            break
    return result


def update_inf(dir_path):
    global config
    out_data = []
    exe_data = []
    dir_data = []
    file_data = []
    # if os.path.exists("desktopICO"):
    #     os.remove("desktopICO")
    # os.mkdir("desktopICO")
    if dir_path == "desktop":
        get_count = 2
        path_list = [desktop_path, public_desktop]
    else:
        get_count = 1
        path_list = [dir_path]
    for i in range(get_count):
        current_dir = path_list[i]
        for item in os.listdir(current_dir):
            if "desktop.ini" in item:
                continue
            filename, _ = os.path.splitext(item)
            full_path = os.path.join(current_dir, item)
            if os.path.isfile(full_path):
                extension = os.path.splitext(full_path)[1]
                if ".lnk" == extension:
                    target_path = get_shortcut_target(full_path)
                    extension = os.path.splitext(target_path)[1]
                    if ".exe" == extension:
                        # 针对米哈游游戏的适配
                        if "miHoYo" in target_path and "launcher" in target_path:
                            if "原神" in item or "Genshin Impact" in item:
                                exe_icon = "./resources/file_icos/ys.ico"
                            elif "星穹铁道" in item or "Star Rail" in item:
                                exe_icon = "./resources/file_icos/sr.ico"
                            elif "绝区零" in item or "Zero" in item:
                                exe_icon = "./resources/file_icos/zzz.ico"
                            elif "崩坏3" in item or "Honkai Impact 3" in item:
                                exe_icon = "./resources/file_icos/bh3.ico"
                            else:
                                exe_icon = "./resources/file_icos/mhy_lancher.ico"
                            exe_data.append(
                                {
                                    "fileName": filename,
                                    "fileType": extension,
                                    "file": os.path.basename(target_path),
                                    "filePath": full_path,
                                    "ico": exe_icon,
                                }
                            )
                        else:
                            if not target_path in had_load_exe:
                                exe_icon = get_icon(target_path, item)
                            else:
                                exe_icon = had_load_exe[target_path]
                            exe_data.append(
                                {
                                    "fileName": filename,
                                    "fileType": extension,
                                    "file": os.path.basename(target_path),
                                    "filePath": full_path,
                                    "ico": exe_icon,
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
                                    "mark": 1,
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
                        "mark": 2,
                    }
                )
    # if config["show_sysApp"]==True:
    if config["show_sysApp"] == True and (
        dir_path == "desktop"
        or dir_path == ""
        or dir_path == "/"
        or dir_path == desktop_path
        or dir_path == public_desktop
    ):
        sys_app_data = [
            {
                "fileName": "此电脑",
                "fileType": "应用程序",
                "file": "_.exe",
                "filePath": "此电脑",
                "ico": "./resources/file_icos/cdn.png",
                "sysApp": True,
            },
            {
                "fileName": "控制面板",
                "fileType": "应用程序",
                "file": "_.exe",
                "filePath": "控制面板",
                "ico": "./resources/file_icos/kzmb.png",
                "sysApp": True,
            },
            {
                "fileName": "回收站",
                "fileType": "应用程序",
                "file": "_.exe",
                "filePath": "回收站",
                "ico": "./resources/file_icos/rbs.png",
                "sysApp": True,
            },
        ]
        for item in sys_app_data:
            out_data.append(item)
    for item in exe_data:
        if check_recover(out_data, item) == True:
            continue
        out_data.append(item)
    for item in dir_data:
        if check_recover(out_data, item) == True:
            continue
        out_data.append(item)
    for item in file_data:
        if check_recover(out_data, item) == True:
            continue
        out_data.append(item)
    return out_data


GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000


def hide_from_taskbar(window):
    hwnd = windll.user32.FindWindowW(None, window.title)
    style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style = (style | WS_EX_TOOLWINDOW) & ~WS_EX_APPWINDOW
    windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)


def is_focused_window_fullscreen():
    try:
        # 获取当前获焦窗口
        active_hwnd = getActiveWindow()

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
        screen_width, screen_height = get_screenSize()
        # 检查窗口是否覆盖整个屏幕（允许几个像素的误差）
        tolerance = 5  # 像素容差
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
    active_hwnd = getActiveWindow()
    if not active_hwnd:
        return False
    window_title = win32gui.GetWindowText(active_hwnd)
    return window_title == "easyDesktop"


def is_desktop_and_mouse_in_corner():
    try:
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)
        corner_size = 100  # 角落区域的边长
        corner_rect = (0, screen_height - corner_size, corner_size, screen_height)
        mouse_x, mouse_y = win32api.GetCursorPos()
        in_corner = corner_rect[0] <= mouse_x <= corner_rect[2] and corner_rect[1] <= mouse_y <= corner_rect[3]
        return in_corner
    except Exception as e:
        print(f"Error: {e}")
        return False


def is_mouse_in_easyDesktop():
    hwnd = win32gui.FindWindow(None, "easyDesktop")
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
    global key_quik_start, config
    start_wait_time = int(time.time())
    had_reflesh = False
    while True:
        if int(time.time()) - start_wait_time > 3:
            if had_reflesh == False:
                window.evaluate_js("document.getElementById('b2d').click()")
                had_reflesh = True
        if config["fdr"] == True:
            if is_focused_window_fullscreen() == True:
                time.sleep(1)
                continue
        if config["cf_type"] == "2" or config["cf_type"] == "3":
            if key_quik_start == True:
                out_window()
                break
        else:
            if is_desktop_and_mouse_in_corner():
                out_window()
                break
        if window_state == True:
            break
        time.sleep(0.4)


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


def animate_window(hwnd, start_x, start_y, end_x, end_y, width, height, steps=60, delay=0.003):
    global window, config
    screen_width, screen_height = get_screenSize()
    for i in range(steps + 1):
        progress = i / steps
        eased_progress = ease_out_quad(progress)
        current_x = start_x + (end_x - start_x) * eased_progress
        current_y = start_y + (end_y - start_y) * eased_progress
        if config["full_screen"] == True:
            if start_x < end_x:
                win32gui.MoveWindow(hwnd, int(current_x), int(current_y), screen_width, screen_height, True)
                # win32gui.MoveWindow(hwnd, int(current_x), int(current_y), int(screen_width*eased_progress), int(screen_height*eased_progress), True)
            else:
                win32gui.MoveWindow(
                    hwnd,
                    int(current_x),
                    int(current_y),
                    int(screen_width - (screen_width * eased_progress)),
                    int(screen_height - (screen_height * eased_progress)),
                    True,
                )
        else:
            if start_x < end_x:
                win32gui.MoveWindow(hwnd, int(current_x), int(current_y), width, height, True)
                # win32gui.MoveWindow(hwnd, int(current_x), int(current_y), int(0+(config["width"])*eased_progress), int(0+(config["height"])*eased_progress), True)
            else:
                win32gui.MoveWindow(
                    hwnd,
                    int(current_x),
                    int(current_y),
                    int(config["width"] - (config["width"] * eased_progress)),
                    int(config["height"] - (config["height"] * eased_progress)),
                    True,
                )
        time.sleep(delay)


def out_window():
    global moving, ignore_action, fullS_close, key_quik_start
    key_quik_start = False
    if moving == True:
        return
    moving = True
    window_state = True
    if config["full_screen"] == False:
        window.resize(config["width"], config["height"])
    window.evaluate_js("document.getElementById('themeSettingsPanel').style.display='none';enableScroll();")
    hwnd = win32gui.FindWindow(None, "easyDesktop")
    hide_from_taskbar(window)
    if not hwnd:
        print("未找到名为 'easyDesktop' 的窗口")
        return False
    try:
        windll.user32.keybd_event(0x12, 0, 0, 0)
        windll.user32.SetForegroundWindow(hwnd)
        windll.user32.keybd_event(0x12, 0, 0x0002, 0)
    except:
        pass
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)
    rect = get_window_rect(hwnd)
    width = rect["width"]
    height = rect["height"]
    start_x = -width
    start_y = screen_height - height // 2
    if config["full_screen"] == True:
        end_x = 0
        end_y = 0
    else:
        end_x = int(screen_width * 0.1)
        end_y = int(screen_height - ((screen_height * 0.1) + height))
    win32gui.MoveWindow(hwnd, start_x, start_y, width, height, True)
    win32gui.UpdateWindow(hwnd)

    time.sleep(0.1)
    window.show()
    animate_window(hwnd, start_x, start_y, end_x, end_y, width, height)
    # if config["full_screen"]==True:
    #     while True:
    #         if is_desktop_and_mouse_in_corner()==False:
    #             break
    #         time.sleep(0.1)
    while True:
        if is_mouse_in_easyDesktop() == True:
            break
        time.sleep(0.1)
    moving = False
    while True:
        if config["out_cf_type"] == "1":
            tj = is_mouse_in_easyDesktop() == False and ignore_action == False
        else:
            tj = is_ed_focused() == False and ignore_action == False
        if (tj == True and config["full_screen"] == False) or fullS_close == True:
            fullS_close = False
            moveIn_window()
            break
        # if config["full_screen"] == True and is_desktop_and_mouse_in_corner()==True:
        #     fullS_close = True
        if window_state == False:
            break
        time.sleep(0.1)


def moveIn_window():
    global moving
    if moving == True:
        return
    moving = True
    window_state = False
    hwnd = win32gui.FindWindow(None, "easyDesktop")
    if not hwnd:
        print("未找到名为 'easyDesktop' 的窗口")
        return False
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)
    rect = get_window_rect(hwnd)
    width = rect["width"]
    height = rect["height"]
    current_x = rect["left"]
    current_y = rect["top"]
    start_x = -width
    start_y = screen_height - height // 2
    animate_window(hwnd, current_x, current_y, start_x, start_y + 500, width, height)
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
    if r["v"] != "1.8.0":
        print("有新版本")
        if config["ign_update"] == r["v"]:
            return
        ask = buttonbox(
            "EasyDesktop有新版本，是否前往更新？\n" + r["update_inf"],
            "EasyDesktop更新检查",
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
    sys_theme()
    if config["view"] == "list":
        window.evaluate_js("list_view()")
    else:
        window.evaluate_js("grid_view()")
    hwnd = win32gui.FindWindow(None, "easyDesktop")
    moveIn_window()
    # wait_open()


def update_config(part, data):
    global config, ignore_action
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
            width, height, end_x, end_y = get_windowInf(window.title)
            win32gui.MoveWindow(hwnd, int(end_x), int(end_y), width, height, True)
            time.sleep(1)
            ignore_action = False
        else:
            win32gui.MoveWindow(hwnd, 0, 0, screen_width, screen_height, True)
    if part == "show_sysApp":
        window.evaluate_js("document.getElementById('b2d').click();")


def autoStart_registry():
    python_exe = sys.executable
    script_path = os.path.abspath(sys.argv[0])
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
    reg.SetValueEx(key, "easyDesktop", 0, reg.REG_SZ, f'"{python_exe}" "{script_path}"')
    reg.CloseKey(key)


def remove_autoStart_registry():
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
    reg.DeleteValue(key, "easyDesktop")
    reg.CloseKey(key)
    print("成功从开机启动项中移除")


def get_windowInf(title="easyDesktop"):
    global config
    hwnd = win32gui.FindWindow(None, title)
    rect = get_window_rect(hwnd)
    width = rect["width"]
    height = rect["height"]
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)
    end_x = int(screen_width * 0.1)
    end_y = int(screen_height - ((screen_height * 0.1) + height))
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


def stray():
    global icon
    image = Image.open("ed_logo.png")
    icon = pystray.Icon("name", image, "title")
    menu = (pystray.MenuItem("Exit", quit_ed),)
    icon.menu = menu
    icon.run()


def open_windows_system_component(component_name):
    commands = {
        "此电脑": r"explorer.exe shell:MyComputerFolder",
        "控制面板": r"explorer.exe shell:::{26EE0668-A00A-44D7-9371-BEB064C98683}",
        "回收站": r"explorer.exe shell:RecycleBinFolder",
    }
    if component_name not in commands:
        return False
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        subprocess.Popen(commands[component_name], startupinfo=startupinfo, shell=True)
        return True
    except Exception as e:
        print(f"打开 {component_name} 时出错: {str(e)}")
        return False


class appAPI:
    def bug_report(self, part, data):
        if not os.path.exists("bugs_report"):
            os.mkdir("bugs_report")
        bugs_report_file = "bugs_report/" + str(int(time.time())) + ".txt"
        with open(bugs_report_file, "w") as f:
            f.write(
                f"""
part: {part},
error: {data}
"""
            )
            f.close()
            msgbox(
                "程序运行出现严重错误，请反馈给开发者，谢谢！\n错误已保存至bugs_report文件夹中\n点击ok将打开错误报告",
                "easydesktop",
            )
            os.startfile(os.path.abspath(bugs_report_file))

    def set_bg(self):
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

    def get_config(self):
        global config
        return config

    def update_config(self, part, data):
        update_config(part, data)

    def where_d(self):
        return desktop_path

    def get_parent(self, path):
        return os.path.dirname(path)

    def load_search_index(self, data):
        outData = {}
        for f in data:
            outData[f["fileName"]] = {"sxpy": get_initials(f["fileName"]), "py": getPinyin(f["fileName"])}
        return outData

    def fit_window_start(self):
        global ignore_action, config, resize_window, hwnd, had_clear_fit
        if config["full_screen"] == True:
            return
        ignore_action = True
        width, height, end_x, end_y = get_windowInf()
        window.hide()
        resize_window = webview.create_window(
            "easyDesktop-fit",
            "easyFileDesk.html",
            x=end_x,
            y=end_y,
            js_api=appAPI(),
            confirm_close=False,
            shadow=True,
            on_top=True,
            easy_drag=False,
            resizable=True,
        )
        had_clear_fit = False
        resize_window.resize(config["width"], config["height"])
        resize_window.evaluate_js("disable_settings()")
        print("config:", config["width"], config["height"])
        print("window: ", width, height)
        print("webview:", window.width, window.height)
        time.sleep(3)
        while True:
            try:
                resize_window.get_cookies()
                active_hwnd = getActiveWindow()
                if not active_hwnd:
                    break
                window_title = win32gui.GetWindowText(active_hwnd)
                if window_title != "easyDesktop-fit":
                    break
            except:
                break
            time.sleep(0.1)
        if had_clear_fit == False:
            self.fit_window_end()

    def fit_window_end(self):
        global ignore_action, config, resize_window, had_clear_fit
        had_clear_fit = True
        try:
            width, height, end_x, end_y = get_windowInf(resize_window.title)
        except:
            window.show()
            return
        window.resize(width, height)
        update_config("width", width)
        update_config("height", height)
        resize_window.destroy()
        window.show()
        width, height, end_x, end_y = get_windowInf(window.title)
        win32gui.MoveWindow(hwnd, int(end_x), int(end_y), width, height, True)
        time.sleep(1)
        ignore_action = False

    def change_defeatDir(self, path):
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

    def get_inf(self, path):
        if path == "desktop" or path == "" or path == "\\":
            path = "desktop"
        data = update_inf(path)
        return {"success": True, "data": data}

    def fullS_close(self):
        global fullS_close, config
        if config["full_screen"] == True:
            fullS_close = True

    def open_file(self, file_path):
        global fullS_close, config
        os.startfile(file_path)
        if config["of_s"] == True:
            fullS_close = True
        return {"success": True}

    def show_file(self, file_path):
        global fullS_close
        file = os.path.realpath(file_path)
        subprocess.Popen(
            f"explorer /select, {file}", shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8"
        )
        fullS_close = True
        return {"success": True}

    def open_sysApp(self, file_path):
        open_windows_system_component(file_path)

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
                    shutil.copy("resources/empty.xlsx", file_path)
                else:
                    with open(file_path, "w") as f:
                        f.write("")
                        f.close()
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
                        shutil.copy("/resources/empty.xlsx", new_path)
                    else:
                        with open(new_path, "w") as f:
                            f.write("")
                            f.close()
                    print(f"已创建: {new_path}")
                    return {"success": True, "file": new_path}
                count += 1
        except:
            return {"success": False, "message": "拒绝访问"}

    def disable_autoshount(self):
        global ignore_action
        ignore_action = True

    def enable_autoshount(self):
        global ignore_action
        ignore_action = False

    def put_file(self, target_path):
        saved_files = []
        try:
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
        except subprocess.CalledProcessError as e:
            return {"success": False, "message": f"粘贴失败: {e.stderr}"}
        except Exception as e:
            return {"success": False, "message": f"粘贴失败: {str(e)}"}
        finally:
            return {"success": True, "files": saved_files}


webview.settings["ALLOW_FILE_URLS"] = True
window = webview.create_window(
    "easyDesktop",
    "easyFileDesk.html",
    width=config["width"],
    height=config["height"],
    js_api=appAPI(),
    confirm_close=False,
    frameless=True,
    shadow=True,
    on_top=True,
    hidden=True,
    easy_drag=False,
    resizable=False,
)
webview.start(func=on_loaded)
