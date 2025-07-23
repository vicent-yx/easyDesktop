# -*- coding: utf-8 -*-
"""
EasyDesktop 配置文件
包含应用程序的所有配置常量和默认设置
"""

# ===== 应用程序基本信息 =====
APP_VERSION = "1.8.0"
APP_NAME = "EasyDesktop"
DEFAULT_WINDOW_TITLE = "EasyDesktop"

# ===== 路径配置 =====
DESKTOP_ICO_PATH = "./desktopICO/"
RESOURCES_PATH = "./resources/"
FILE_ICO_PATH = "./resources/file_icos/"
CONFIG_FILE = "config.json"
BUGS_REPORT_DIR = "bugs_report"
EMPTY_XLSX_TEMPLATE = "resources/empty.xlsx"

# ===== Windows API 常量 =====
SM_CXSCREEN = 0  # 屏幕宽度
SM_CYSCREEN = 1  # 屏幕高度
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000

# ===== 动画和界面常量 =====
ANIMATION_STEPS = 60
ANIMATION_DELAY = 0.003
WINDOW_WIDTH_RATIO = 0.65
WINDOW_HEIGHT_RATIO = 0.4
WINDOW_POSITION_RATIO = 0.1
TOLERANCE = 5  # 像素容差
CORNER_SIZE = 100  # 角落区域的边长
WAIT_TIMEOUT = 3  # 等待超时时间（秒）
SLEEP_INTERVAL = 0.4  # 循环间隔（秒）
MOUSE_CHECK_INTERVAL = 0.1  # 鼠标检查间隔（秒）

# ===== 支持的脚本文件类型 =====
SCRIPTS_TYPE = [
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

# ===== 文件图标映射 =====
FILE_ICO = {
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

# ===== 应用程序默认配置 =====
def get_default_config(width, height):
    """
    获取默认配置字典
    
    Args:
        width (int): 窗口宽度
        height (int): 窗口高度
    
    Returns:
        dict: 默认配置字典
    """
    return {
        "theme": "light",
        "language": "zh-CN",
        "follow_sys": True,
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

# ===== 系统应用程序配置 =====
SYSTEM_APPS = [
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

# ===== Windows 系统组件命令 =====
SYSTEM_COMMANDS = {
    "此电脑": r"explorer.exe shell:MyComputerFolder",
    "控制面板": r"explorer.exe shell:::{26EE0668-A00A-44D7-9371-BEB064C98683}",
    "回收站": r"explorer.exe shell:RecycleBinFolder",
}

# ===== 米哈游游戏图标映射 =====
MIHOYO_GAMES = {
    "原神": "./resources/file_icos/ys.ico",
    "Genshin Impact": "./resources/file_icos/ys.ico",
    "星穹铁道": "./resources/file_icos/sr.ico",
    "Star Rail": "./resources/file_icos/sr.ico",
    "绝区零": "./resources/file_icos/zzz.ico",
    "Zero": "./resources/file_icos/zzz.ico",
    "崩坏3": "./resources/file_icos/bh3.ico",
    "Honkai Impact 3": "./resources/file_icos/bh3.ico",
    "default": "./resources/file_icos/mhy_lancher.ico",
}