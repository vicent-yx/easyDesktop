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
        self._topo_signature = None
    def getInfo(self, sc_id):
        # 显示器拓扑（数量/设备名/分辨率/DPI）变化时清空缓存，
        # 防止旧的"ID→屏幕信息"映射在拓扑变化后张冠李戴（屏幕认反）
        signature = screenInfo.get_topology_signature()
        if signature != self._topo_signature:
            self.temp_data = {}
            self._topo_signature = signature
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
        self._topo_signature = None

screen_info = ScreenInf()

def get_screen_size():
    r1_width,r1_height = get_active_screen_size()
    return r1_width,r1_height

def get_sfb(screen_id=None):
    screen_id = _resolve_screen_id(screen_id)
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
        screen_id: 屏幕ID（screenInfo 中按设备名排序后的索引）
    返回:
        monitor_handle: 显示器句柄，ID 无效时返回 None
    """
    screenInfo._refresh_monitors()
    if screen_id is None or screen_id < 0 or screen_id >= len(screenInfo._monitors):
        return None
    return screenInfo._monitors[screen_id]


def _resolve_screen_id(screen_id=None):
    """
    解析出有效的屏幕ID：优先用传入值，其次用 active_screen 记录的值，
    都无效时（如 markActive 检测失败返回 -1）实时按鼠标位置检测。
    """
    if screen_id is None:
        screen_id = active_screen.getActive()
    if screen_id is None or screen_id < 0:
        screen_id = screenInfo.get_active_monitor_id()
    return screen_id

def get_screen_id_by_point(x, y):
    """
    根据坐标获取所在屏幕的ID
    
    参数:
        x, y: 坐标点
    返回:
        screen_id: 屏幕ID（0=主屏幕，1/2/3...=副屏幕），找不到返回 -1
    """
    screenInfo._refresh_monitors()
    monitor, _ = _get_monitor_info_by_point(x, y)
    for i, h in enumerate(screenInfo._monitors):
        if h == monitor:
            return i
    return -1


def is_point_on_other_screen(x, y):
    """
    判断指定坐标是否在非当前活跃屏幕上

    参数:
        x, y: 坐标点
    返回:
        True: 坐标所在的屏幕与 active_screen.getActive() 不一致
        False: 坐标在活跃屏幕上
    """
    point_screen_id = get_screen_id_by_point(x, y)
    return point_screen_id != active_screen.getActive()


def get_active_screen_size(with_origin=False, with_work_area=False):
    """
    获取屏幕的宽高

    参数:
        with_origin: 是否返回原点坐标
        with_work_area: 是否返回工作区域完整信息
    返回: (width, height) 或 (width, height, left, top) 或 (width, height, left, top, right, bottom)
    """
    screen_id = _resolve_screen_id()

    # 确定要获取的显示器：ID 无效时回退到鼠标所在的屏幕
    monitor = _get_monitor_by_screen_id(screen_id)
    if monitor is None:
        mouse_x, mouse_y = win32api.GetCursorPos()
        monitor, monitor_info = _get_monitor_info_by_point(mouse_x, mouse_y)
    else:
        monitor_info = win32api.GetMonitorInfo(monitor)
    
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
    data = screen_info.getInfo(_resolve_screen_id())
    return f"{data['w']}x{data['h']} {int(data['s']*100)}%"

def is_active_screen_primary():
    """
    判断当前活动屏幕是否为主显示器（依据 MONITORINFOF_PRIMARY 标志，不依赖ID数值）
    """
    return screenInfo.is_primary_monitor_id(_resolve_screen_id())

class activeScreen:
    def __init__(self):
        # 初始值取真实主屏，而不是假定索引0=主屏
        try:
            self.now_active = screenInfo.get_primary_monitor_id()
        except Exception:
            self.now_active = 0
    def markActive(self):
        self.now_active = screenInfo.get_active_monitor_id()
    def getActive(self):
        return self.now_active

active_screen = activeScreen()