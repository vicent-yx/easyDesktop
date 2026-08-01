import win32api
import win32con
import config as cfg
import subprocess
import json
import traceback
from .appAction.report import bugs_report
from src import screenInfo

class ScreenInf:
    def __init__(self):
        self.temp_data = {}
    def getInfo(self, sc_id):
        if sc_id in self.temp_data:
            return self.temp_data[sc_id]

        result = subprocess.run(
            cfg.scInfoGetter(sc_id),
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            last_line = lines[-1]
            try:
                data = json.loads(last_line)
            except Exception as e:
                bugs_report("python-iconGetter_parse", f"屏幕数据返回数据解析失败: {traceback.format_exc()}",True,result.stdout.strip())
            else:
                self.temp_data[sc_id] = data
        else:
            data = None
            try:
                err_info = result.stderr.strip()
            except:
                err_info = "获取失败"
            bugs_report("python-iconGetter_parse", f"屏幕数据获取失败: {err_info}",True)
        return data

    def clearCache(self):
        self.temp_data = {}

screen_info = ScreenInf()

def get_screen_size():
    r1_width,r1_height = get_active_screen_size()
    return r1_width,r1_height

def get_sfb(screen_id=None):
    if screen_id is None:
        screen_id = active_screen.getActive()
    return screen_info.getInfo(screen_id)['s']

def _get_monitor_info_by_point(x, y):
    """
    根据坐标点获取显示器信息
    返回: (monitor_handle, monitor_info)
    """
    monitor = win32api.MonitorFromPoint((x, y), win32con.MONITOR_DEFAULTTONEAREST)
    monitor_info = win32api.GetMonitorInfo(monitor)
    return monitor, monitor_info

def _get_monitor_by_screen_id(screen_id):
    """
    根据屏幕ID获取显示器句柄
    
    参数:
        screen_id: 0=主屏幕, 1/2/3...=副屏幕
    返回:
        monitor_handle: 显示器句柄
    """
    screenInfo._refresh_monitors()
    try:
        return screenInfo._monitors[screen_id]
    except KeyError:
        return None

def get_active_screen_size(with_origin=False, with_work_area=False):
    """
    获取屏幕的宽高
    
    参数:
        with_origin: 是否返回原点坐标
        with_work_area: 是否返回工作区域完整信息
        screen_id: 屏幕ID（0=主屏幕，1/2/3...=副屏幕），
                  如果为None，则获取鼠标所在的活动屏幕
    返回: (width, height) 或 (width, height, left, top) 或 (width, height, left, top, right, bottom)
    """
    screen_id = active_screen.getActive()
    
    # 确定要获取的显示器
    if screen_id is not None:
        monitor = _get_monitor_by_screen_id(screen_id)
        if monitor is None:
            # 如果指定的ID无效，回退到鼠标所在的屏幕
            mouse_x, mouse_y = win32api.GetCursorPos()
            monitor, monitor_info = _get_monitor_info_by_point(mouse_x, mouse_y)
        else:
            monitor_info = win32api.GetMonitorInfo(monitor)
    else:
        # 获取鼠标位置所在的屏幕
        mouse_x, mouse_y = win32api.GetCursorPos()
        monitor, monitor_info = _get_monitor_info_by_point(mouse_x, mouse_y)
    
    # 获取当前屏幕在虚拟桌面中的逻辑坐标 (left, top, right, bottom)
    rect = monitor_info['Monitor']
    left, top, right, bottom = rect
    
    # 逻辑宽高（受 DPI 缩放影响），用逻辑坐标计算确保多屏幕定位正确
    width = right - left
    height = bottom - top
    
    if with_origin and with_work_area:
        return width, height, left, top, right, bottom
    elif with_origin and not with_work_area:
        return width, height, left, top
    else:
        return width, height

def get_info_str():
    """
    获取当前活跃屏幕的真实物理分辨率字符串（用于窗口尺寸配置索引）
    通过 EnumDisplaySettings 直接查询显示器当前分辨率，避免坐标系统 DPI 混乱
    """
    data = screen_info.getInfo(active_screen.getActive())
    return f"{data['w']}x{data['h']} {int(data['s']*100)}%"

class activeScreen:
    def __init__(self):
        self.now_active = 0
    def markActive(self):
        self.now_active = screenInfo.get_active_monitor_id()
    def getActive(self):
        return self.now_active

active_screen = activeScreen()