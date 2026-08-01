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


_monitors = []


def _enum_proc(hMonitor, hdc, lprc, lparam):
    _monitors.append(hMonitor)
    return True


def _refresh_monitors():
    _monitors.clear()
    user32.EnumDisplayMonitors(
        0,
        0,
        MonitorEnumProc(_enum_proc),
        0,
    )


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


def get_monitor_info(monitor_id):
    """
    返回:
        width, height, scale
    """
    _refresh_monitors()

    if monitor_id < 0 or monitor_id >= len(_monitors):
        raise IndexError("Invalid monitor id")

    hMonitor = _monitors[monitor_id]

    info = MONITORINFOEX()
    info.cbSize = ctypes.sizeof(info)

    user32.GetMonitorInfoW(
        hMonitor,
        ctypes.byref(info),
    )

    width = info.rcMonitor.right - info.rcMonitor.left
    height = info.rcMonitor.bottom - info.rcMonitor.top

    dpiX = wintypes.UINT()
    dpiY = wintypes.UINT()

    hr = shcore.GetDpiForMonitor(
        hMonitor,
        MDT_EFFECTIVE_DPI,
        ctypes.byref(dpiX),
        ctypes.byref(dpiY),
    )

    if hr == 0:
        scale = dpiX.value / 96.0
    else:
        scale = 1.0

    return width, height, scale