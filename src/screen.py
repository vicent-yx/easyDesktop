import win32api
import win32gui
import win32con
import win32print
import time

def get_screen_size():
    r1_width,r1_height = get_active_screen_size()
    return r1_width,r1_height

def get_sfb():
    hdc = win32gui.GetDC(0)
    # 获取物理分辨率
    physical_width = win32print.GetDeviceCaps(hdc, win32con.DESKTOPHORZRES)
    # 获取逻辑分辨率（受缩放影响）
    logical_width = win32print.GetDeviceCaps(hdc, win32con.HORZRES)
    
    # 计算缩放比例
    scale_factor = round(physical_width / logical_width, 2)
    return scale_factor
def get_active_screen_size(with_origin=False,with_work_area=False):
    """
    获取当前活动屏幕的宽高（包含鼠标光标的屏幕）
    返回: (width, height)
    """
    sfb = get_sfb()
    while True:
        try:
            # 获取鼠标位置
            mouse_x, mouse_y = win32api.GetCursorPos()
            
            # 获取包含该点的显示器信息
            monitor = win32api.MonitorFromPoint((mouse_x, mouse_y), win32con.MONITOR_DEFAULTTONEAREST)
            monitor_info = win32api.GetMonitorInfo(monitor)
            
            # 获取工作区域
            work_area = monitor_info['Monitor']
            # print("work_area =",work_area)
            # os._exit(0)
            work_area = list(work_area)
            for i in range(len(work_area)):
                num = work_area[i]
                if str(num)[-1]!="0":
                    work_area[i] = int(round(num*sfb))
            width = work_area[2] - work_area[0]  # right - left
            height = work_area[3] - work_area[1] # bottom - top
            
            if with_origin==True and with_work_area==True:
                return width, height,work_area[0],work_area[1],work_area[2],work_area[3]
            elif with_origin==True and with_work_area==False:
                return width, height,work_area[0],work_area[1]
            else:
                return width, height
        except:
            time.sleep(0.5)