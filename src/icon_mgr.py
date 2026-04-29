import os
from src import getIcon # 本地模块源
import config as cfg
import subprocess
from src.ucfg import ucfg
import json
from .appAction.report import bugs_report
import traceback
class icon_mgr():
    def __init__(self):
        self.icon_cache = {}

    def save_cache(self,file_path,icon_path):
        self.icon_cache[file_path] = icon_path
        
    def call_iconGetter(self,path,temp=True):
        print("调用图标获取器: ", path)
        result = subprocess.run(
            cfg.iconGetter({"path": path,"temp":temp}),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            last_line = lines[-1]
            try:
                data = json.loads(last_line)
            except Exception as e:
                bugs_report("python-iconGetter_parse", f"图标获取器返回数据解析失败: {traceback.format_exc()}",True,result.stdout.strip())
        else:
            data = None
        return data
    def update(self,path,temp=True):
        # 先验证有无exe图标
        r = False
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isfile(full_path):
                if item.endswith(".exe") or item.endswith(".EXE"):
                    r=True
                    break
                if item.endswith(".lnk"):
                    full_path = getIcon.get_shortcut_target(full_path)
                    if full_path!=None and os.path.exists(full_path):
                        if os.path.isfile(full_path) and (full_path.endswith(".exe") or full_path.endswith(".EXE")):
                            r=True
                            break
        if r==False:
            return None

        result = self.call_iconGetter(path,temp)
        if result!=None:
            data = result
            if not "error" in data:
                for item in data:
                    if data[item]==None:
                        data[item] = "/resources/file_icos/exe.png"
                    self.save_cache(item, data[item])
                    print(f"已更新图标缓存: {item} -> {data[item]}")
            else:
                print(f"错误: {data['error']}")
        else:
            print(f"错误: {result.stderr}")
            return f"错误: {result.stderr}"
    def icon_file(self,file_path):
        # return getIcon.match_ico(file_name)
        return getIcon.get_fileIcon(file_path)
    def icon_dir(self):

        return cfg.DEFAULT_DIR_ICON
    def icon_exe(self,file_path,file_name=""):
        if file_path in self.icon_cache:
            return self.icon_cache[file_path]
        icon_r = self.call_iconGetter(file_path)
        if icon_r!=None:
            icon_r = icon_r[file_path]
            self.save_cache(file_path,icon_r)
            return icon_r
        else:
            return cfg.DEFAULT_EXE_ICON
    def icon_url(self,file_path,file_name):
        icon_r = getIcon.get_url_icon(file_path)
        if icon_r!=None:
            self.save_cache(file_path,icon_r)
            return icon_r
        else:
            print(f"无法获取URL图标，使用默认图标: {file_path}")
            return cfg.DEFAULT_UNKONW_ICON

    def get_icon(self,file_path,file_name):
        # 从缓存中获取
        if file_path in self.icon_cache:
            return self.icon_cache[file_path]
        # 自定义图标返回
        if file_path in ucfg.data["ico"]:
            return ucfg.data["ico"][file_path]
        
        if os.path.isdir(file_path):
            return self.icon_dir()

        extension = os.path.splitext(file_path)[1]
        # 快捷方式解析
        if extension == ".lnk":
            # 直接从快捷方式获取
            icon_r = getIcon.get_shortcut_icon_win32(file_path,file_name)
            if icon_r!=None:
                self.save_cache(file_path,icon_r)
            else:
                # 从快捷方式指向的文件获取
                target_path = getIcon.get_shortcut_target(file_path)
                if not os.path.exists(target_path):
                    return self.icon_file(file_path)
                ltExt = os.path.splitext(target_path)[1]
                if os.path.isfile(target_path):
                    if ltExt in [".exe",".EXE"]:
                        icon_r = self.icon_exe(target_path,file_name)
                    else:
                        icon_r = self.icon_file(target_path)
                else:
                    icon_r = self.icon_dir()
        # 链接解析
        elif extension == ".url":
            icon_r = self.icon_url(file_path,file_name)
        # 文件解析
        else:
            if extension in [".exe",".EXE"]:
                icon_r = self.icon_exe(file_path,file_name)
            else:
                icon_r = self.icon_file(file_path)
        return icon_r


# 创建单例实例
iconMgr = icon_mgr()
__all__ = ['iconMgr']