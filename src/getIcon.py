import os
import time
import re
import config as cfg
import win32com.client
import win32gui
import shutil
from PIL import Image
import win32api
import win32con
import win32gui
import win32ui
from icoextract import IconExtractor

def turn_png(file_path):
    # try:
    # 检查文件是否存在
    file_ok = False
    range_time = 0
    while True:
        if os.path.exists(file_path):
            file_ok = True
            break
        else:
            time.sleep(0.1)
            range_time += 1
            if range_time>100:
                break
    if file_ok==False:
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
                png_path = os.path.splitext(file_path)[0] + ".webp"
                img.save(png_path, "WEBP")
                return png_path
            else:
                return "./resources/file_icos/exe.png"


    # except Exception as e:
    #     print(f"转换ICO到PNG过程中发生错误: {str(e)}")
    #     return "./resources/file_icos/exe.png"

def get_shortcut_icon_win32(lnk_path,name):
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(lnk_path)
        result = ""
        # 获取图标位置
        icon_location = shortcut.IconLocation
        if icon_location:
            if ',' in icon_location:
                path_part, index_part = icon_location.rsplit(',', 1)
                result = path_part.strip()
            else:
                result = icon_location.strip()
        
        if result:
            if result.split(".")[-1] in ["ico","png","jpg","jpeg"]:
                dir_name = os.path.dirname(lnk_path).replace("/", "-").replace(R"\\", "-").replace(":", "-")
                if not os.path.exists(cfg.DESKTOP_ICO_PATH + dir_name):
                    os.makedirs(cfg.DESKTOP_ICO_PATH + dir_name)
                output_path = cfg.DESKTOP_ICO_PATH + dir_name + "/" + name + ".ico"
                relative_path = cfg.DESKTOP_ICO_RELATIVE_PATH + dir_name + "/" + name + ".webp"
                shutil.copyfile(result, output_path)
                output_path = turn_png(output_path)
                return relative_path
            elif result.split(".")[-1] in ["exe",".EXE"]:
                return get_icon(result,name)
            else:
                return None
        
        return None
    except Exception as e:
        print(f"处理快捷方式 {lnk_path} 时出错: {e}")
        return None

def get_icon(exe_path, name):
    try:
        dir_name = os.path.dirname(exe_path).replace("/", "-").replace(R"\\", "-").replace(":", "-")
        if not os.path.exists(cfg.DESKTOP_ICO_PATH + dir_name):
            os.makedirs(cfg.DESKTOP_ICO_PATH + dir_name)
        ico_path = output_path = cfg.DESKTOP_ICO_PATH + dir_name + "/" + name + ".ico"
        relative_path = cfg.DESKTOP_ICO_RELATIVE_PATH + dir_name + "/" + name + ".webp"

        if(os.path.exists(relative_path)):
            return relative_path

        if os.path.exists(relative_path):
            return relative_path

        # 检查exe文件是否存在
        if not os.path.exists(exe_path):
            print(f"警告：EXE文件不存在 {exe_path}")
            return None
 
        try:
            extractor = IconExtractor(exe_path)
            extractor.export_icon(output_path)
            output_path = turn_png(output_path)
            if os.path.exists(ico_path):
                os.remove(ico_path)
            if output_path!=False and output_path != "./resources/file_icos/exe.png":
                return relative_path
            else:
                # 如果转换失败，使用默认图标
                print(f"图标转换失败，使用默认图标: {exe_path}")
                return None
        except Exception as extract_error:
            print(f"exe图标提取失败: {extract_error} - {exe_path}")
            return None

    except Exception as e:
        print(f"获取图标时发生未知错误: {e} - {exe_path}")
        return None


def get_url_icon(url_path):
    print("new "+url_path)
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
        print(f"解析URL文件 {url_path} 时出错: {e}")
        return None

    if not icon_file or not os.path.exists(icon_file):
        print(f"图标文件不存在: {icon_file}")
        return None

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
        image.save(cfg.DESKTOP_ICO_PATH + dir_name + "/" + os.path.basename(url_path) + ".webp")
        image.close()
        return cfg.DESKTOP_ICO_RELATIVE_PATH + dir_name + "/" + os.path.basename(url_path) + ".webp"
    except Exception as e:
        print(f"提取图标失败: {e}")
        return None


def get_shortcut_target(shortcut_path):
    if not os.path.exists(shortcut_path):
        raise FileNotFoundError(f"快捷方式文件 {shortcut_path} 不存在")

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    return shortcut.TargetPath


def match_ico(file_name):
    print("match_ico "+file_name)
    extension = os.path.splitext(file_name)[1]
    if extension in cfg.FILE_ICO:
        return cfg.FILE_ICO[extension]
    elif extension in cfg.SCRIPTS_TYPE:
        return "./resources/file_icos/script.png"
    else:
        return cfg.FILE_ICO["unkonw"]
    
def get_file_icon_path(extension):
    """
    获取特定后缀名文件关联的图标路径
    
    Args:
        extension: 文件后缀，如 '.txt', '.py', '.exe'
    
    Returns:
        图标文件的路径，如果没有关联则返回None
    """
    try:
        # 获取文件关联的命令
        command = win32api.RegQueryValue(
            win32con.HKEY_CLASSES_ROOT, 
            extension
        )
        
        # 获取默认图标
        icon_path = win32api.RegQueryValue(
            win32con.HKEY_CLASSES_ROOT,
            f"{command}\\DefaultIcon"
        )
        
        # 解析图标路径（可能包含索引，如 "C:\path\file.dll,0"）
        if ',' in icon_path:
            icon_path = icon_path.split(',')[0].strip()
        
        return icon_path
        
    except Exception as e:
        print(f"获取图标失败: {e}")
        return None

def get_file_icon_path(file_path):
    extension = os.path.splitext(file_path)[1]
    """
    获取特定后缀名文件关联的图标路径
    
    Args:
        file_path: 文件路径
    Returns:
        图标文件的路径，如果没有关联则返回None
    """
    try:
        # 获取文件关联的命令
        command = win32api.RegQueryValue(
            win32con.HKEY_CLASSES_ROOT, 
            extension
        )
        
        # 获取默认图标
        icon_path = win32api.RegQueryValue(
            win32con.HKEY_CLASSES_ROOT,
            f"{command}\\DefaultIcon"
        )
        
        # 解析图标路径（可能包含索引，如 "C:\path\file.dll,0"）
        if ',' in icon_path:
            icon_path = icon_path.split(',')[0].strip()
        
        return icon_path
        
    except Exception as e:
        return None
    
def get_fileIcon(file_path):
    ext = os.path.splitext(file_path)[1]
    if ext in cfg.SCRIPTS_TYPE+[".js",".bat",".css",".doc",".docx",".xls",".xlsx",".pdf",".ppt",".pptx"]:
        return match_ico(file_path)
    icon_path = get_file_icon_path(file_path)
    if icon_path == None:
        return match_ico(file_path)
    else:
        try:
            ext = os.path.splitext(icon_path)[1]
            if ext in [".exe",".EXE"]:
                icon = get_icon(icon_path,os.path.basename(file_path))
                if icon!=None:
                    return icon
                else:
                    return match_ico(file_path)
            elif ext in [".ico",".ICO",".png",".PNG",".jpg",".jpeg",".JPG",".JPEG",".bmp"]:
                icon = turn_png(icon_path)
            else:
                icon = match_ico(file_path)
        except:
            icon = match_ico(file_path)
    return icon