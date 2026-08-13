import win32api
import win32con
import os
import winreg

def set_shutdown_registry():
    """设置注册表以在关机时自动结束进程，避免.NET Framework阻止关机提示"""
    settings = {
        # 自动结束无响应任务，不弹出"等待程序关闭"对话框
        (winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop"): {
            "AutoEndTasks": "1",
            "WaitToKillAppTimeout": "2000",
        },
    }

    for (hkey, subkey), values in settings.items():
        try:
            key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_SET_VALUE)
            for name, data in values.items():
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, data)
            winreg.CloseKey(key)
            print(f"[注册表] 已设置 {subkey}: {values}")
        except PermissionError:
            print(f"[注册表] 权限不足，跳过 {subkey}")
        except Exception as e:
            print(f"[注册表] 设置 {subkey} 失败: {e}")

    # WaitToKillServiceTimeout 位于 HKLM，需要管理员权限
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "WaitToKillServiceTimeout", 0, winreg.REG_SZ, "2000")
        winreg.CloseKey(key)
        print("[注册表] 已设置 HKLM\\WaitToKillServiceTimeout = 2000")
    except PermissionError:
        print("[注册表] 权限不足，跳过 HKLM\\WaitToKillServiceTimeout（需管理员）")
    except Exception as e:
        print(f"[注册表] 设置 WaitToKillServiceTimeout 失败: {e}")


class ShutdownHandler:
    """处理Windows关机信号的类"""
    def __init__(self, window):
        self.window = window
        self.shutdown_occurred = False
        # 注册关机回调
        self._register_handler()
    
    def _register_handler(self):
        """注册控制台控制处理器"""
        # 设置回调函数，返回True表示消息已被处理
        win32api.SetConsoleCtrlHandler(self._console_handler, True)
    
    def _console_handler(self, ctrl_type):
        if ctrl_type == win32con.CTRL_SHUTDOWN_EVENT:
            print("检测到系统关机信号，正在清理资源...")
            self._cleanup_and_exit()
            return True  # 表示消息已被处理
        elif ctrl_type == win32con.CTRL_CLOSE_EVENT:
            print("检测到控制台关闭信号，正在清理资源...")
            self._cleanup_and_exit()
            return True
        elif ctrl_type in (win32con.CTRL_LOGOFF_EVENT,):
            print("检测到用户注销信号，正在清理资源...")
            self._cleanup_and_exit()
            return True
        return False  # 未处理，交给系统默认处理
    
    def _cleanup_and_exit(self):
        """执行清理工作并退出"""
        if self.shutdown_occurred:
            return  # 避免重复执行
        
        self.shutdown_occurred = True
        # 系统关机/注销时不调用 window.destroy()，因为此时窗口句柄已
        # 被系统销毁，触发 FormClosed 事件链会导致 Control.Invoke()
        # 在无效句柄上抛出 System.ArgumentException
        print("检测到系统关机/注销信号，直接退出")
        os._exit(0)