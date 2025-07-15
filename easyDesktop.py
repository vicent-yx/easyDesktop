from icoextract import IconExtractor
import os
import win32com.client
import win32gui
import win32api
import time
import webview
import pyautogui
import subprocess
from pypinyin import pinyin, Style ,lazy_pinyin
import shutil
import darkdetect
import json
from PIL import Image

if os.path.exists("config.json"):
    config = json.load(open("config.json"))
else:
    config = {
        "theme":"light",
        "language":"zh-CN",
        "follow_sys":True,
        "theme": "light",
        "view":"block"
    }
    json.dump(config, open("config.json", "w"))

had_load_exe = {}
window_state = False
moving = False
screen_size = pyautogui.size()
file_ico_path = "./resources/file_icos/"
scripts_type=[".py",".java",".c",".vbs",".cpp",".h",".hpp",".cs",".php",".rb",".go",".swift",".kt",".m",".pl",".r",".sh",".bash",".zsh",".lua",".scala",".groovy",".dart",".rs",".jl",".hs",".f",".f90",".f95",".v",".vhd",".clj",".ex",".exs",".elm",".purs",".erl",".hrl",".fs",".fsx",".fsi",".ml",".mli",".pas",".pp",".d",".nim",".cr",".cbl",".cob",".ada",".adb",".ads"]
file_ico = {
    ".mp3":"./resources/file_icos/mp3.png",
    ".mp4":"./resources/file_icos/mp4.png",
    ".mkv":"./resources/file_icos/mkv.png",
    ".m4a":"./resources/file_icos/m4a.png",
    ".doc":"./resources/file_icos/doc.png",
    ".docx":"./resources/file_icos/docx.png",
    ".xls":"./resources/file_icos/xls.png",
    ".xlsx":"./resources/file_icos/xlsx.png",
    ".pdf":"./resources/file_icos/pdf.png",
    ".ppt":"./resources/file_icos/ppt.png",
    ".pptx":"./resources/file_icos/pptx.png",

    ".zip":"./resources/file_icos/zip.png",
    ".rar":"./resources/file_icos/zip.png",
    ".png":"./resources/file_icos/image.png",
    ".jpg":"./resources/file_icos/image.png",
    ".jpeg":"./resources/file_icos/image.png",
    ".gif":"./resources/file_icos/image.png",

    ".txt":"./resources/file_icos/txt.png",
    ".html":"./resources/file_icos/html.png",
    ".css":"./resources/file_icos/css.png",
    ".js":"./resources/file_icos/js.png",
    ".bat":"./resources/file_icos/bat.png",

    "unkonw":"./resources/file_icos/unkonw.png"
}
def turn_png(file_path):
    """
    将ICO文件转换为PNG格式并替换原始ICO文件
    
    参数:
        file_path (str): ICO文件的路径
        
    返回:
        bool: 转换是否成功
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误：文件 '{file_path}' 不存在")
            return False
            
        # 检查文件扩展名是否为ico
        if not file_path.lower().endswith('.ico'):
            print(f"错误：文件 '{file_path}' 不是ICO文件")
            return False
            
        # 打开ICO文件
        with Image.open(file_path) as img:
            png_path = os.path.splitext(file_path)[0] + '.png'
            img.save(png_path, 'PNG')
            # os.remove(file_path)
            new_path = os.path.splitext(file_path)[0] + '.png'
            os.rename(png_path, new_path)
            return new_path
            
    except Exception as e:
        print(f"转换过程中发生错误: {str(e)}")
        return "/resources/file_icos/exe.png"
def get_desktop_path():
    shell = win32com.client.Dispatch("WScript.Shell")
    return shell.SpecialFolders("Desktop")
def get_icon(exe_path,name):
    try:
        dir_name = os.path.dirname(exe_path).replace("/","-").replace(R"\\","-").replace(":","-")
        if not os.path.exists("./desktopICO/"+dir_name):
            os.makedirs("./desktopICO/"+dir_name)
        output_path = "./desktopICO/"+dir_name+"/"+name+'.ico'
        extractor = IconExtractor(exe_path)
        extractor.export_icon(output_path)
        had_load_exe[exe_path]=output_path
        output_path=turn_png(output_path)
        return output_path
    except Exception as e:
        print(e, "\n", exe_path)
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

def update_inf(current_dir):
    out_data = []
    exe_data = []
    dir_data = []
    file_data = []
    # if os.path.exists("desktopICO"):
    #     os.remove("desktopICO")
    # os.mkdir("desktopICO")
    for item in os.listdir(current_dir):
        if "desktop.ini" in item:
            continue
        filename, _ = os.path.splitext(item)
        full_path = os.path.join(current_dir, item)
        if os.path.isfile(full_path):
            extension = os.path.splitext(full_path)[1]
            if ".lnk" in extension:
                target_path = get_shortcut_target(full_path)
                extension = os.path.splitext(target_path)[1]
                if ".exe" in extension:
                    # 针对米哈游游戏的适配
                    if "miHoYo" in target_path and "launcher" in target_path:
                        if "原神" in item or "Genshin Impact" in item:
                            exe_icon = "./resources/file_icos/ys.ico"
                            game = "ys"
                        elif "星穹铁道" in item or "Star Rail" in item:
                            exe_icon = "./resources/file_icos/sr.ico"
                            game = "sr"
                        elif "绝区零" in item or "Zero" in item:
                            exe_icon = "./resources/file_icos/zzz.ico"
                            game = "zzz"
                        elif "崩坏3" in item or "Honkai Impact 3" in item:
                            exe_icon = "./resources/file_icos/bh3.ico"
                            game = "bh3"
                        else:
                            exe_icon = "./resources/file_icos/mhy_lancher.ico"
                            game = "mhy"
                        exe_data.append({"fileName":filename,"fileType":extension,"file":os.path.basename(target_path),"filePath":target_path,"ico":exe_icon,"game":game})
                    else:
                        if not target_path in had_load_exe:
                            exe_icon=get_icon(target_path,item)
                        else:
                            exe_icon = had_load_exe[target_path]
                        exe_data.append({"fileName":filename,"fileType":extension,"file":os.path.basename(target_path),"filePath":target_path,"ico":exe_icon})
                    continue
                else:
                    if os.path.isfile(target_path):
                        file_data.append({"fileName":filename,"fileType":extension,"file":item,"filePath":target_path,"ico":match_ico(item)})
                    else:
                        dir_data.append({"fileName":filename,"fileType":"文件夹","file":item,"filePath":target_path,"ico":"./resources/file_icos/dir.png","mark":1})
                    continue
            else:
                file_data.append({"fileName":filename,"fileType":extension,"file":item,"filePath":full_path,"ico":match_ico(item)})
        else:
            dir_data.append({"fileName":filename,"fileType":"文件夹","file":item,"filePath":full_path,"ico":"./resources/file_icos/dir.png","mark":2})
    for item in exe_data:
        out_data.append(item)
    for item in dir_data:
        out_data.append(item)
    for item in file_data:
        out_data.append(item)
    return out_data
def is_desktop_and_mouse_in_corner():
    try:
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)
        corner_size = 100  # 角落区域的边长
        corner_rect = (0, screen_height - corner_size, corner_size, screen_height)
        mouse_x, mouse_y = win32api.GetCursorPos()
        in_corner = (corner_rect[0] <= mouse_x <= corner_rect[2] and 
                     corner_rect[1] <= mouse_y <= corner_rect[3])
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
    while True:
        if is_desktop_and_mouse_in_corner():
            out_window()
            break
        if window_state==True:
            break
        time.sleep(0.5)
def ease_out_quad(t):
    # 缓动函数
    return t * (2 - t)

def get_window_rect(hwnd):
    # 获取窗口矩形区域
    rect = win32gui.GetWindowRect(hwnd)
    return {
        'left': rect[0],
        'top': rect[1],
        'right': rect[2],
        'bottom': rect[3],
        'width': rect[2] - rect[0],
        'height': rect[3] - rect[1]
    }

def animate_window(hwnd, start_x, start_y, end_x, end_y, width, height, steps=60, delay=0.005):
    for i in range(steps + 1):
        progress = i / steps
        eased_progress = ease_out_quad(progress)
        current_x = start_x + (end_x - start_x) * eased_progress
        current_y = start_y + (end_y - start_y) * eased_progress
        win32gui.MoveWindow(hwnd, int(current_x), int(current_y), width, height, True)
        time.sleep(delay)

def out_window():
    global moving
    if moving == True:
        return
    moving = True
    window_state=True
    window.evaluate_js("document.getElementById('b2d').click();document.getElementById('themeSettingsPanel').style.display='none';enableScroll();")
    """将窗口从初始位置丝滑移出到目标位置"""
    window.show()
    hwnd = win32gui.FindWindow(None, "easyDesktop")
    if not hwnd:
        print("未找到名为 'easyDesktop' 的窗口")
        return False
    try:
        win32gui.SetForegroundWindow(hwnd)
    except:
        pass
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)
    rect = get_window_rect(hwnd)
    width = rect['width']
    height = rect['height']
    start_x = -width
    start_y = screen_height - height // 2
    end_x = int(screen_width * 0.1)
    end_y = int(screen_height * 0.4)
    win32gui.MoveWindow(hwnd, start_x, start_y, width, height, True)
    win32gui.UpdateWindow(hwnd)
    time.sleep(0.1)
    animate_window(hwnd, start_x, start_y, end_x, end_y, width, height)
    while True:
        hwnd = win32gui.FindWindow(None, "easyDesktop")
        if not hwnd:
            break
        try:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            point = win32api.GetCursorPos()
            above_window = (point[1] <= bottom and point[0] >= left and point[0] <= right)
        except:
            break
        finally:
            if above_window:
                break
    moving = False
    while True:
        if is_mouse_in_easyDesktop()==False:
            moveIn_window()
            break
        if window_state==False:
            break
        time.sleep(0.1)

def moveIn_window():
    # return
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
    width = rect['width']
    height = rect['height']
    current_x = rect['left']
    current_y = rect['top']
    start_x = -width
    start_y = screen_height - height // 2
    animate_window(hwnd, current_x, current_y, start_x, start_y, width, height)
    window.hide()
    moving = False
    wait_open()
def sys_theme():
    if darkdetect.isDark()==True:
        window.evaluate_js("load_theme('dark')")
    else:
        window.evaluate_js("load_theme('light')")
def on_loaded():
    sys_theme()
    if config["view"]=="list":
        window.evaluate_js("list_view()")
    else:
        window.evaluate_js("grid_view()")
    moveIn_window()
    # wait_open()

desktop_path = get_desktop_path()
def get_initials(text):
    initials = pinyin(text, style=Style.FIRST_LETTER,errors="default")
    return ''.join([item[0] for item in initials])
def getPinyin(text):
    result = "".join(lazy_pinyin(text, style=Style.NORMAL, errors="default"))
    return result
class appAPI():
    def get_config(self):
        global config
        return config
    def update_config(self,part,data):
        print("update_config",part,data)
        global config
        config[part]=data
        json.dump(config, open("config.json", "w"))
        if part=="follow_sys" and data==True:
            sys_theme()
    def where_d(self):
        return desktop_path
    def get_parent(self,path):
        return os.path.dirname(path)
    def load_search_index(self,data):
        outData = {}
        for f in data:
            outData[f["fileName"]]={"sxpy":get_initials(f["fileName"]),"py":getPinyin(f["fileName"])}
        return outData
    def get_inf(self,path):
        if path == "desktop" or path=="" or path=="\\":
            path = os.path.join(os.path.expanduser("~"), "Desktop")
        data = update_inf(path)
        return {"success":True,"data":data}
    def open_file(self,file_path):
        os.startfile(file_path)
        moveIn_window()
        return {"success":True}
    def open_mhyGame(self,file_path,game):
        open_command = {
            "ys":"--game=hk4e_cn",
            "sr":"--game=hkrpg_cn",
            "zzz":"--game=nap_cn",
            "bh3":"--game=bh3_cn"
        }
        game_c = ""
        if game in open_command.keys():
            game_c = open_command[game]
        subprocess.Popen(f'"{file_path}" {game_c}', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
    def copy_file(self,file_path):
        subprocess.run(['powershell', '-Command', f'Get-Item {file_path} | Set-Clipboard'],shell=False)
        return {"success":True}
    def rename_file(self,file_path,new_name):
        if os.path.isfile(file_path):
            new_path = os.path.join(os.path.dirname(file_path), new_name+os.path.splitext(file_path)[1])
        else:
            new_path = os.path.join(os.path.dirname(file_path), new_name)
        os.rename(file_path, os.path.join(os.path.dirname(file_path), new_path))
        return {"success":True}
    def remove_file(self,file_path):
        try:
            os.remove(file_path)
        except:
            return {"success":False,"message":"拒绝访问（无权限）"}
        finally:
            return {"success":True}
    def new_file(self,suffix):
        try:
            if suffix == "folder":
                base_name = "新建文件夹"
            else:
                base_name = f"新建文档.{suffix}"
            file_path = os.path.join(desktop_path, base_name)
            if not os.path.exists(file_path):
                if suffix == "folder":
                    os.mkdir(file_path)
                else:
                    with open(file_path, 'w')as f:
                        f.write("")
                        f.close()
                print(f"已创建: {file_path}")
                return file_path
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
                    else:
                        with open(new_path, 'w')as f:
                            f.write("")
                            f.close()
                    print(f"已创建: {new_path}")
                    return {"success":True}
                count += 1
        except:
            return {"success":False,"message":"拒绝访问"}
        finally:
            return {"success":True}
    def put_file(file_path):
        saved_files = []
        try:
            command = [
                'powershell',
                '-Command',
                '$files = Get-Clipboard -Format FileDropList; '
                'if ($files) { $files | ForEach-Object { $_.FullName } }'
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=True,shell=False)
            output = result.stdout.strip()
            if not output:
                return {"success":True}
            file_paths = [path.strip() for path in output.splitlines() if path.strip()]
            
            # 验证所有文件路径是否有效
            valid_paths = []
            for file_path in file_paths:
                if os.path.exists(file_path):
                    valid_paths.append(file_path)
                else:
                    return {"success":False,"message":"剪切板中没有有效的文件"}
            
            if not valid_paths:
                return {"success":False,"message":"剪切板中没有有效的文件"}
            for src_path in valid_paths:
                filename = os.path.basename(src_path)
                dest_path = os.path.join(desktop_path, filename)
                # 处理文件名冲突
                counter = 1
                base_name, extension = os.path.splitext(filename)
                while os.path.exists(dest_path):
                    new_filename = f"{base_name}_{counter}{extension}"
                    dest_path = os.path.join(desktop_path, new_filename)
                    counter += 1
                shutil.copy2(src_path, dest_path)
                saved_files.append(dest_path)
            return {"success":True}
        except subprocess.CalledProcessError as e:
            return {"success":False,"message":f"粘贴失败: {e.stderr}"}
        except Exception as e:
            return {"success":False,"message":f"粘贴失败: {str(e)}"}
        finally:
            return {"success":True}


width = int(screen_size.width*0.4)
height = int(screen_size.height*0.3)

window = webview.create_window(
    'easyDesktop',
    'easyFileDesk.html',
    width=width,
    height=height,
    js_api=appAPI(),
    confirm_close=False,
    frameless=True,
    shadow=True,
    on_top=True,
    hidden=True,
    easy_drag=False
)
webview.start(func=on_loaded,debug=True)
