import os
import time
import re
import shutil
import tempfile
import ctypes
from ctypes import wintypes

import config as cfg
import win32com.client
import win32gui
import win32api
import win32con
import win32ui
from PIL import Image
from icoextract import IconExtractor

def _ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def _hicon_to_pil_image(hicon) -> Image.Image:
    ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
    ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)

    try:
        icon_info = win32gui.GetIconInfo(hicon)
        hbm_color = icon_info[4]  # hbmColor
        if hbm_color:
            bmp = win32ui.CreateBitmapFromHandle(hbm_color)
            bmp_info = bmp.GetInfo()
            ico_x = bmp_info["bmWidth"]
            ico_y = bmp_info["bmHeight"]
            # 释放对象
            try:
                win32gui.DeleteObject(hbm_color)
            except Exception:
                pass
        try:
            if icon_info[3]:
                win32gui.DeleteObject(icon_info[3])
        except Exception:
            pass
    except Exception:
        pass

    hdc_screen = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(hdc_screen, ico_x, ico_y)

    hdc_mem = hdc_screen.CreateCompatibleDC()
    hdc_mem.SelectObject(hbmp)
    hdc_mem.DrawIcon((0, 0), hicon)

    bmp_info = hbmp.GetInfo()
    bmp_bytes = hbmp.GetBitmapBits(True)

    img = Image.frombuffer(
        "RGBA",
        (bmp_info["bmWidth"], bmp_info["bmHeight"]),
        bmp_bytes,
        "raw",
        "BGRA",
        0,
        1
    )

    # 清理 GDI 资源
    try:
        del hdc_mem
        del hbmp
        del hdc_screen
    except Exception:
        pass

    return img

def _extract_icon_privateextracticons(exe_path: str, size: int = 256):
    # 使用 Win32 PrivateExtractIconsW 提取指定尺寸的图标
    shell32 = ctypes.WinDLL("shell32", use_last_error=True)
    user32 = ctypes.WinDLL("user32", use_last_error=True)

    PrivateExtractIconsW = shell32.PrivateExtractIconsW
    PrivateExtractIconsW.argtypes = [
        wintypes.LPCWSTR,  # szFileName
        ctypes.c_int,      # nIconIndex
        ctypes.c_int,      # cxIcon
        ctypes.c_int,      # cyIcon
        ctypes.POINTER(wintypes.HICON),  # phicon
        ctypes.POINTER(wintypes.UINT),   # piconid
        wintypes.UINT,     # nIcons
        wintypes.UINT      # flags
    ]
    PrivateExtractIconsW.restype = wintypes.UINT

    hicons = (wintypes.HICON * 1)()
    ids = (wintypes.UINT * 1)()

    # nIconIndex=0：通常取主图标
    n = PrivateExtractIconsW(exe_path, 0, size, size, hicons, ids, 1, 0)
    if n == 0 or not hicons[0]:
        return None

    hicon = hicons[0]
    try:
        img = _hicon_to_pil_image(hicon)
        return img
    finally:
        try:
            user32.DestroyIcon(hicon)
        except Exception:
            pass

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
            if range_time > 100:
                break
    if file_ok == False:
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
            if hasattr(img, "size") and img.size[0] > 0:
                png_path = os.path.splitext(file_path)[0] + ".webp"
                img.save(png_path, "WEBP")
                return png_path
            else:
                return "./resources/file_icos/exe.png"

def get_shortcut_icon_win32(lnk_path, name):
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(lnk_path)
        result = ""
        # 获取图标位置
        icon_location = shortcut.IconLocation
        if icon_location:
            if "," in icon_location:
                path_part, index_part = icon_location.rsplit(",", 1)
                result = path_part.strip()
            else:
                result = icon_location.strip()

        if result:
            if result.split(".")[-1] in ["ico", "png", "jpg", "jpeg"]:
                dir_name = os.path.dirname(lnk_path).replace("/", "-").replace(R"\\", "-").replace(":", "-")
                out_dir = os.path.join(cfg.DESKTOP_ICO_PATH, dir_name)
                _ensure_dir(out_dir)

                output_ico = os.path.join(out_dir, f"{name}.ico")
                relative_path = cfg.DESKTOP_ICO_RELATIVE_PATH + dir_name + "/" + name + ".webp"

                shutil.copyfile(result, output_ico)
                turn_png(output_ico)
                # 清理 ico（保持和 exe 逻辑一致）
                try:
                    if os.path.exists(output_ico):
                        os.remove(output_ico)
                except Exception:
                    pass
                return relative_path
            elif result.split(".")[-1] in ["exe", ".EXE"]:
                return get_icon(result, name)
            else:
                return None

        return None
    except Exception as e:
        print(f"处理快捷方式 {lnk_path} 时出错: {e}")
        return None

def get_icon(exe_path, name,temp=True):
    try:
        dir_name = os.path.dirname(exe_path).replace("/", "-").replace(R"\\", "-").replace(":", "-")
        out_dir = os.path.join(cfg.DESKTOP_ICO_PATH, dir_name)
        _ensure_dir(out_dir)

        webp_path = os.path.join(out_dir, f"{name}.webp")
        relative_path = cfg.DESKTOP_ICO_RELATIVE_PATH + dir_name + "/" + name + ".webp"

        # 缓存命中
        if temp == True and os.path.exists(webp_path):
            return relative_path

        # 检查 exe 文件是否存在
        if not os.path.exists(exe_path):
            # print(f"警告：EXE文件不存在 {exe_path}")
            return None

        # 1) 优先Win32提取图标
        try:
            img = _extract_icon_privateextracticons(exe_path, size=256)
            if img is not None:
                img.save(webp_path, "WEBP")
                try:
                    img.close()
                except Exception:
                    pass
                return relative_path
        except Exception as e:
            # Win32 失败 fallback（不要直接返回）
            # print(f"Win32 提取图标失败，准备 fallback: {e} - {exe_path}")
            pass

        # 2) fallback：复制到临时文件再用 icoextract（避免锁原 exe，且不吃大内存）
        ico_path = os.path.join(out_dir, f"{name}.ico")
        extractor = None
        try:
            extractor = IconExtractor(exe_path)
            extractor.export_icon(ico_path)

            out_webp = turn_png(ico_path)
            # 删除 ico
            try:
                if os.path.exists(ico_path):
                    os.remove(ico_path)
            except Exception:
                pass

            if out_webp and out_webp != "./resources/file_icos/exe.png":
                # turn_png 会输出 webp_path（同名），此处用实际缓存文件判断更稳
                if os.path.exists(webp_path):
                    return relative_path
                # 若 turn_png 保存到了别处（理论上不会），也兜底返回相对路径
                return relative_path

            # print(f"图标转换失败，使用默认图标: {exe_path}")
            return None

        except Exception as extract_error:
            # print(f"exe图标提取失败: {extract_error} - {exe_path}")
            return None
        finally:
            # 兜底释放 pefile 相关资源（若 icoextract 内部有）
            try:
                pe = getattr(extractor, "_pe", None)
                if pe is not None and hasattr(pe, "close"):
                    pe.close()
            except Exception:
                pass

    except Exception as e:
        # print(f"获取图标时发生未知错误: {e} - {exe_path}")
        return None

def get_url_icon(url_path):
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
        out_dir = os.path.join(cfg.DESKTOP_ICO_PATH, dir_name)
        _ensure_dir(out_dir)

        out_path = os.path.join(out_dir, os.path.basename(url_path) + ".webp")
        image.save(out_path)
        image.close()
        return cfg.DESKTOP_ICO_RELATIVE_PATH + dir_name + "/" + os.path.basename(url_path) + ".webp"
    except Exception as e:
        print(f"提取图标失败: {e}")
        return None

def get_shortcut_target(shortcut_path,sec=False):
    if not os.path.exists(shortcut_path):
        raise FileNotFoundError(f"快捷方式文件 {shortcut_path} 不存在")

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    target = shortcut.TargetPath
    if target == "" and sec==False:
        if not os.path.exists("temp"):
            os.makedirs("temp")
        shutil.copy(shortcut_path, "temp/temp.lnk")
        target = get_shortcut_target("temp/temp.lnk",True)
        os.remove("temp/temp.lnk")
    return target

def match_ico(file_name):
    print("match_ico " + file_name)
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
        command = win32api.RegQueryValue(win32con.HKEY_CLASSES_ROOT, extension)
        icon_path = win32api.RegQueryValue(
            win32con.HKEY_CLASSES_ROOT,
            f"{command}\\DefaultIcon"
        )
        if "," in icon_path:
            icon_path = icon_path.split(",")[0].strip()
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
        command = win32api.RegQueryValue(win32con.HKEY_CLASSES_ROOT, extension)
        icon_path = win32api.RegQueryValue(
            win32con.HKEY_CLASSES_ROOT,
            f"{command}\\DefaultIcon"
        )
        if "," in icon_path:
            icon_path = icon_path.split(",")[0].strip()
        return icon_path
    except Exception as e:
        print(f"获取图标失败: {e}")
        return None

def get_fileIcon(file_path):
    try:
        if file_path.split(".")[-1] in ["exe", "EXE"]:
            return "./resources/file_icos/exe.png"
        if file_path.split(".")[-1] in ["lnk", "LNK"]:
            return "./resources/file_icos/lnk.png"
        if file_path.split(".")[-1] in ["url", "URL"]:
            return "./resources/file_icos/url.png"
        if file_path.split(".")[-1] in ["ini", "INI"]:
            return "./resources/file_icos/ini.png"
        if file_path.split(".")[-1] in ["json", "JSON"]:
            return "./resources/file_icos/JSON.png"
        if file_path.split(".")[-1] in ["m4a", "M4A"]:
            return "./resources/file_icos/m4a.png"
        if file_path.split(".")[-1] in ["mp3", "MP3"]:
            return "./resources/file_icos/mp3.png"
        if file_path.split(".")[-1] in ["wav", "WAV"]:
            return "./resources/file_icos/wav.png"
        if file_path.split(".")[-1] in ["mp4", "MP4", "mkv", "MKV"]:
            return "./resources/file_icos/mp4.png"
        if file_path.split(".")[-1] in ["zip", "ZIP", "rar", "RAR", "7z", "7Z"]:
            return "./resources/file_icos/zip.png"
        if file_path.split(".")[-1] in ["png", "PNG", "jpg", "JPG", "jpeg", "JPEG", "gif", "GIF", "webp", "WEBP"]:
            return "./resources/file_icos/image.png"
        if file_path.split(".")[-1] in ["txt", "TXT"]:
            return "./resources/file_icos/txt.png"
        if file_path.split(".")[-1] in ["xls", "XLS", "xlsx", "XLSX"]:
            return "./resources/file_icos/xlsx.png"
        if file_path.split(".")[-1] in ["doc", "DOC", "docx", "DOCX"]:
            return "./resources/file_icos/docx.png"
        if file_path.split(".")[-1] in ["ppt", "PPT", "pptx", "PPTX"]:
            return "./resources/file_icos/pptx.png"
        if file_path.split(".")[-1] in ["pdf", "PDF"]:
            return "./resources/file_icos/pdf.png"
        if file_path.split(".")[-1] in ["html", "HTML", "htm", "HTM"]:
            return "./resources/file_icos/html.png"
        if file_path.split(".")[-1] in ["js", "JS"]:
            return "./resources/file_icos/js.png"
        if file_path.split(".")[-1] in ["css", "CSS"]:
            return "./resources/file_icos/css.png"
        if file_path.split(".")[-1] in ["bat", "BAT"]:
            return "./resources/file_icos/bat.png"
        if file_path.split(".")[-1] in ["py", "PY"]:
            return "./resources/file_icos/script.png"
        if file_path.split(".")[-1] in ["rbs", "RBS"]:
            return "./resources/file_icos/rbs.png"
        return "./resources/file_icos/unkonw.png"
    except:
        return "./resources/file_icos/unkonw.png"