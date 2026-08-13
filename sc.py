
import sys
import json
from src import screenInfo

"""
参数说明：
    monitor_id: 屏幕ID 可以是整数或"active"（表示活动屏幕）
返回值：
    宽度, 高度, 缩放比例
"""

def get_monitor_info(monitor_id):
    """
    返回:
        width, height, scale
    """
    width, height, scale = screenInfo.get_monitor_info(monitor_id)
    return width, height, scale


if __name__ == "__main__":
    argv = sys.argv
    if len(argv)>1:
        screen = argv[1]
        if screen=="active":
            screen = screenInfo.get_active_monitor_id()
        else:
            try:
                screen = int(screen)
            except:
                print("Invalid screen id")
                sys.exit(1)
        w, h, s = get_monitor_info(screen)
        print(json.dumps({"w":w,"h":h,"s":s}))
    else:
        print(json.dumps({"error": "no args"}))

    # mid = get_active_monitor_id()
    # print("当前屏幕:", mid)

    # w, h, s = get_monitor_info(mid)
    # print(w, h, s)