# monitor.py
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
shcore = ctypes.windll.shcore

# 让程序 DPI Aware，避免拿到缩放后的坐标
try:
    shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
except Exception:
    try:
        user32.SetProcessDPIAware()
    except Exception:
        pass


MONITOR_DEFAULTTONEAREST = 2
MDT_EFFECTIVE_DPI = 0
MONITORINFOF_PRIMARY = 1


class POINT(ctypes.Structure):
    _fields_ = [
        ("x", wintypes.LONG),
        ("y", wintypes.LONG),
    ]


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


class MONITORINFOEX(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", wintypes.DWORD),
        ("szDevice", wintypes.WCHAR * 32),
    ]


MonitorEnumProc = ctypes.WINFUNCTYPE(
    wintypes.BOOL,
    wintypes.HMONITOR,
    wintypes.HDC,
    ctypes.POINTER(RECT),
    wintypes.LPARAM,
)


_enum_tmp = []
_monitors = []         # 按设备名排序后的 HMONITOR 列表（索引即屏幕ID）
_monitor_devices = []  # 与 _monitors 一一对应的设备名（如 \\.\DISPLAY1）
_monitor_infos = []    # 与 _monitors 一一对应的 MONITORINFOEX


def _enum_proc(hMonitor, hdc, lprc, lparam):
    _enum_tmp.append(hMonitor)
    return True


def _refresh_monitors():
    """
    枚举显示器并按 szDevice（设备名）排序后再建立索引。

    Windows 的 EnumDisplayMonitors 枚举顺序是未定义的，且会随睡眠唤醒/
    显示器重插/驱动重置等事件而翻转。若直接用枚举下标当屏幕ID，主进程与
    sc.py 子进程、以及显示器事件前后的两次枚举之间，可能把同一个ID解析
    到不同的物理显示器（表现为"屏幕认反"）。统一按设备名排序后，同一套
    显示器在任何进程、任何时刻都得到一致的ID顺序。
    """
    global _monitors, _monitor_devices, _monitor_infos
    _enum_tmp.clear()
    user32.EnumDisplayMonitors(
        0,
        0,
        MonitorEnumProc(_enum_proc),
        0,
    )
    pairs = []
    for h in _enum_tmp:
        info = MONITORINFOEX()
        info.cbSize = ctypes.sizeof(info)
        if user32.GetMonitorInfoW(h, ctypes.byref(info)):
            pairs.append((info.szDevice, h, info))
    pairs.sort(key=lambda p: p[0])
    _monitor_devices = [p[0] for p in pairs]
    _monitors = [p[1] for p in pairs]
    _monitor_infos = [p[2] for p in pairs]


def get_active_monitor_id():
    """
    获取当前鼠标所在屏幕ID
    """
    _refresh_monitors()

    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))

    hMonitor = user32.MonitorFromPoint(
        pt,
        MONITOR_DEFAULTTONEAREST,
    )

    for i, h in enumerate(_monitors):
        if h == hMonitor:
            return i

    return -1


def get_primary_monitor_id():
    """
    获取主显示器ID（依据 MONITORINFOF_PRIMARY 标志，不依赖索引位置）
    """
    _refresh_monitors()
    for i, info in enumerate(_monitor_infos):
        if info.dwFlags & MONITORINFOF_PRIMARY:
            return i
    return 0 if _monitors else -1


def is_primary_monitor_id(monitor_id):
    """
    判断指定屏幕ID是否为主显示器（依据 MONITORINFOF_PRIMARY 标志）
    """
    _refresh_monitors()
    if monitor_id is None or monitor_id < 0 or monitor_id >= len(_monitors):
        return False
    return bool(_monitor_infos[monitor_id].dwFlags & MONITORINFOF_PRIMARY)


def get_topology_signature():
    """
    返回当前显示器拓扑签名：(设备名, 区域, DPI) 的有序元组。
    显示器数量/设备名/分辨率/缩放发生变化时签名改变，
    可用于让"ID→屏幕信息"的缓存失效。
    """
    _refresh_monitors()
    sig = []
    for h, info in zip(_monitors, _monitor_infos):
        dpiX = wintypes.UINT()
        dpiY = wintypes.UINT()
        hr = shcore.GetDpiForMonitor(
            h,
            MDT_EFFECTIVE_DPI,
            ctypes.byref(dpiX),
            ctypes.byref(dpiY),
        )
        dpi = dpiX.value if hr == 0 else 96
        r = info.rcMonitor
        sig.append((info.szDevice, r.left, r.top, r.right, r.bottom, dpi))
    return tuple(sorted(sig))


def get_monitor_info(monitor_id):
    """
    返回:
        width, height, scale
    """
    _refresh_monitors()

    if monitor_id < 0 or monitor_id >= len(_monitors):
        raise IndexError("Invalid monitor id")

    info = _monitor_infos[monitor_id]

    width = info.rcMonitor.right - info.rcMonitor.left
    height = info.rcMonitor.bottom - info.rcMonitor.top

    dpiX = wintypes.UINT()
    dpiY = wintypes.UINT()

    hr = shcore.GetDpiForMonitor(
        _monitors[monitor_id],
        MDT_EFFECTIVE_DPI,
        ctypes.byref(dpiX),
        ctypes.byref(dpiY),
    )

    if hr == 0:
        scale = dpiX.value / 96.0
    else:
        scale = 1.0

    return width, height, scale
