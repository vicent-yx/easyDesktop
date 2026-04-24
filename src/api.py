from src import getIcon # 本地模块源
from src.icon_mgr import iconMgr
import os
import win32gui
import win32api
import time
import webview
import subprocess
from pypinyin import pinyin, Style, lazy_pinyin
import shutil
import json
import sys
from easygui import msgbox
import send2trash
import config as cfg
from src import group_mgr
from src.windowMgr import windowMgr,resize_win
from src import tool
from src.ucfg import ucfg
from src.res_load import itmeRes,imagePreView
from .appAction.report import bugs_report

SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004

desktop_path = tool.get_desktop_path()
public_desktop = os.path.join(os.environ["PUBLIC"], "Desktop")


def get_initials(text):
    initials = pinyin(text, style=Style.FIRST_LETTER, errors="default")
    return "".join([item[0] for item in initials])


def getPinyin(text):
    result = "".join(lazy_pinyin(text, style=Style.NORMAL, errors="default"))
    return result
def open_sysApp_action(component_name):
    if component_name not in cfg.SYSTEM_COMMANDS:
        return False
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        subprocess.Popen(cfg.SYSTEM_COMMANDS[component_name], startupinfo=startupinfo, shell=True)
        return True
    except Exception as e:
        print(f"打开 {component_name} 时出错: {str(e)}")
        return False

class AppAPI:
    file_info_temp = [],
    def bug_report(self, part, data):
        bugs_report(
            part,
            data
        )
    def is_path_abs(self,path):
        return os.path.isabs(path)
    def change_cl_state(self,filePath, state):
        cl_data = json.load(open(cfg.CL_DATA_FILE,"r"))
        cl_data[filePath] = not state
        json.dump(cl_data,open(cfg.CL_DATA_FILE,"w"))
    def set_background(self):
        # global ignore_action
        file_types = ("Image Files (*.bmp;*.jpg;*.gif;*.png;*.jpeg)", "All files (*.*)")
        windowMgr.disable_autoClose()
        bg_file = windowMgr.window.create_file_dialog(file_types=file_types, allow_multiple=False)
        windowMgr.enable_autoClose()
        bg_file = bg_file[0]
        if bg_file:
            bg_config_path = "bg." + str(bg_file).split(".")[-1]
            if getattr(sys, 'frozen', False):
                file_path = "_internal/bg." + str(bg_file).split(".")[-1]
            else:
                file_path = "bg." + str(bg_file).split(".")[-1]
            if os.path.exists(ucfg.data["bg"]):
                os.remove(ucfg.data["bg"])
            shutil.copy(bg_file, file_path)
            return bg_config_path
        return None

    def get_config(self):
        return_config = ucfg.data.copy()
        del return_config["dir_order"]
        return return_config

    def update_config(self, part, data):
        ucfg.update_config(part, data)

    def update_config_order(self,path,order):

        path_order = []
        for item in order:
            path_order.append(item["filePath"])
        ucfg.data["dir_order"][path]=path_order
        # json.dump(ucfg.data, open("ucfg.data.json", "w"))
        ucfg.save_config()


    def search_desktop_path(self):
        return desktop_path

    def get_parent(self, path):
        pr_path = os.path.dirname(path)
        if pr_path == desktop_path or pr_path == public_desktop:
            return "desktop"
        return pr_path

    def load_search_index(self, data):
        outData = {}
        for f in data:
            outData[f["fileName"]] = {"sxpy": get_initials(f["fileName"]), "py": getPinyin(f["fileName"])}
        return outData

    def fit_window_start(self):
        resize_win.fit_window_start()
    #     # global ignore_action, ucfg.data, resize_window, hwnd, has_cleared_fit,fit_hwnd
    #     if ucfg.data["full_screen"] == True:
    #         return
    #     windowMgr.disable_autoClose()
    #     width, height, end_x, end_y = tool.get_window_inf()
    #     windowMgr.window.hide()
    #     resize_window = webview.create_window(
    #         "easyDesktop-fit",
    #         "easyFileDesk.html",
    #         x=end_x,
    #         y=end_y,
    #         js_api=AppAPI(),
    #         confirm_close=False,
    #         shadow=True,
    #         on_top=True,
    #         resizable=True,
    #         draggable=False,
    #     )
    #     has_cleared_fit = False
    #     resize_window.resize(ucfg.data["width"], ucfg.data["height"])
    #     resize_window.evaluate_js("disable_settings()")
    #     fit_hwnd = win32gui.FindWindow(None, "easyDesktop-fit")
    #     win32gui.MoveWindow(fit_hwnd, end_x, end_y, width, height, True)
    #     remove_title_bar(fit_hwnd)
    #     print("ucfg.data:", ucfg.data["width"], ucfg.data["height"])
    #     print("window: ", width, height)
    #     # print("webview:", window.width, window.height)
    #     time.sleep(3)
    #     while True:
    #         try:
    #             resize_window.get_cookies()
    #             active_hwnd = tool.get_active_window()
    #             if not active_hwnd:
    #                 break
    #             window_title = win32gui.GetWindowText(active_hwnd)
    #             if window_title != "easyDesktop-fit":
    #                 break
    #         except:
    #             break
    #         time.sleep(cfg.MOUSE_CHECK_INTERVAL)
    #     if has_cleared_fit == False:
    #         self.fit_window_end()

    # def fit_window_end(self):
    #     # global ignore_action, ucfg.data, resize_window, has_cleared_fit
    #     has_cleared_fit = True
    #     try:
    #         width, height, end_x, end_y = tool.get_window_inf(resize_window.title)
    #     except:
    #         windowMgr.window.show()
    #         return
    #     flags = SWP_NOMOVE | SWP_NOZORDER | 0x0008 # 组合标志位
    #     endx,endy = tool.get_targetPos(width, height)
    #     win32gui.MoveWindow(hwnd, endx, endy, width, height, True)
    #     ucfg.update_ucfg.data("width", width)
    #     ucfg.update_ucfg.data("height", height)
    #     resize_window.destroy()
    #     windowMgr.window.show()
    #     if ucfg.data['blur_bg']==True:
    #         windowMgr.fit_blur_effect()
    #     time.sleep(1)
    #     ignore_action = False

    def change_default_dir(self, path):
        if path == None:
            path = windowMgr.window.create_file_dialog(dialog_type=webview.FOLDER_DIALOG)
            if path != None:
                path = path[0]
                ucfg.update_config("df_dir", path)
                name = os.path.basename(path)
                if name == "":
                    name = path.split("\\")[-2]
                ucfg.update_config("df_dir_name", name)
                return {"success": True, "data": path, "name": name}
            else:
                return {"success": True, "data": ucfg.data["df_dir"], "name": ucfg.data["df_dir_name"]}
        else:
            ucfg.update_config("df_dir", "desktop")
            ucfg.update_config("df_dir_name", "桌面")
            return {"success": True, "data": path, "name": "桌面"}

    def get_fileinfo(self, path,quck=True):
        if path == "desktop" or path == "" or path == "\\":
            path = "desktop"
        data = itmeRes.update_inf(path,quck)
        r_data = {"success": True, "data": data["data"],"same":self.file_info_temp==data}
        self.file_info_temp = data
        return r_data

    def close_fullscreen_window(self):
        # global fullscreen_close, ucfg.data
        if ucfg.data["full_screen"] == True:
            windowMgr.fullscreen_close = True

    def open_file(self, file_path):
        # global fullscreen_close, ucfg.data
        os.startfile(file_path)
        if ucfg.data["of_s"] == True:
            windowMgr.fullscreen_close = True
        return {"success": True}

    def show_file(self, file_path):
        # global fullscreen_close
        file = os.path.realpath(file_path)
        subprocess.Popen(
            f"explorer /select, {file}", shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8"
        )
        windowMgr.fullscreen_close = True
        return {"success": True}

    def copy_file(self, file_path):
        subprocess.run(
            ["powershell", "-Command", f"Get-Item {file_path} | Set-Clipboard"],
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return {"success": True}

    def rename_file(self, file_path, new_name):
        if os.path.isfile(file_path):
            new_path = os.path.join(os.path.dirname(file_path), new_name + os.path.splitext(file_path)[1])
        else:
            new_path = os.path.join(os.path.dirname(file_path), new_name)
        os.rename(file_path, os.path.join(os.path.dirname(file_path), new_path))
        return {"success": True, "file": new_path}

    def remove_file(self, file_path, del_type="remove"):
        try:
            if del_type == "rubbish":
                send2trash.send2trash(file_path)
                return {"success": True}
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except:
            return {"success": False, "message": "拒绝访问（无权限）"}
        finally:
            return {"success": True}

    def new_file(self, suffix, current_path):
        if current_path == "desktop" or current_path == "" or current_path == "\\":
            current_path = desktop_path
        try:
            if suffix == "folder":
                base_name = "新建文件夹"
            else:
                base_name = f"新建文档.{suffix}"
            file_path = os.path.join(current_path, base_name)
            if not os.path.exists(file_path):
                if suffix == "folder":
                    os.mkdir(file_path)
                elif suffix == "xlsx":
                    print("创建表格：", file_path)
                    shutil.copy(cfg.EMPTY_XLSX_TEMPLATE, file_path)
                else:
                    with open(file_path, "w") as f:
                        f.write("")
                print(f"已创建: {file_path}")
                return {"success": True, "file": file_path}
            count = 1
            while True:
                if suffix == "folder":
                    new_name = f"新建文件夹{count}"
                else:
                    new_name = f"新建文档{count}.{suffix}"
                new_path = os.path.join(current_path, new_name)
                if not os.path.exists(new_path):
                    if suffix == "folder":
                        os.mkdir(new_path)
                    elif suffix == "xlsx":
                        print("创建表格：", new_path)
                        shutil.copy(cfg.EMPTY_XLSX_TEMPLATE, new_path)
                    else:
                        with open(new_path, "w") as f:
                            f.write("")
                    print(f"已创建: {new_path}")
                    return {"success": True, "file": new_path}
                count += 1
        except:
            return {"success": False, "message": "拒绝访问"}

    def lock_window_visibility(self):
        """锁定窗口可见性（不自动隐藏）"""
        windowMgr.disable_autoClose()

    def unlock_window_visibility(self):
        """解锁窗口可见性（恢复自动隐藏）"""
        windowMgr.enable_autoClose()

    def open_sysApp(self,app_name):
        open_sysApp_action(app_name)
    def put_file(self, target_path):
        if target_path == "desktop" or target_path == "" or target_path == "\\":
            target_path = desktop_path
        saved_files = []
        command = [
            "powershell",
            "-Command",
            "$files = Get-Clipboard -Format FileDropList; "
            "if ($files) { $files | ForEach-Object { $_.FullName } }",
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        output = result.stdout.strip()
        if not output:
            return {"success": True}
        file_paths = [path.strip() for path in output.splitlines() if path.strip()]

        # 验证所有文件路径是否有效
        valid_paths = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                valid_paths.append(file_path)
            else:
                return {"success": False, "message": "剪切板中没有有效的文件"}

        if not valid_paths:
            return {"success": False, "message": "剪切板中没有有效的文件"}
        for src_path in valid_paths:
            filename = os.path.basename(src_path)
            dest_path = os.path.join(target_path, filename)
            # 处理文件名冲突
            counter = 1
            base_name, extension = os.path.splitext(filename)
            while os.path.exists(dest_path):
                new_filename = f"{base_name}_{counter}{extension}"
                dest_path = os.path.join(target_path, new_filename)
                counter += 1
            shutil.copy2(src_path, dest_path)
            saved_files.append(os.path.abspath(dest_path))
        return {"success": True, "files": saved_files}
    def add_class(self,files,key):
        # global ucfg.itemClass,ucfg.data
        ucfg.itemClass[ucfg.data["df_dir"]][key] = files
        with open(cfg.USER_CLASS_FILE,"w",encoding="utf-8") as f:
            json.dump(ucfg.itemClass,f,ensure_ascii=False)
        return {"success":True}
    def read_class(self,key):
        # global ucfg.itemClass,ucfg.data
        if key=="" or key=="all" or key=="全部":
            if not ucfg.data["df_dir"] in ucfg.itemClass:
                ucfg.itemClass[ucfg.data["df_dir"]]={}
            # 排序
            class_order_inf = ucfg.data["class_order"]
            if len(class_order_inf)==0:
                class_order_inf = list(ucfg.itemClass[ucfg.data["df_dir"]].keys())
            outputData = {}
            index = 0
            while True:
                if index>=len(class_order_inf):
                    break
                key = class_order_inf[index]
                if key in ucfg.itemClass[ucfg.data["df_dir"]]:
                    outputData[key] = ucfg.itemClass[ucfg.data["df_dir"]][key]
                    index += 1
                else:
                    del class_order_inf[index]
                    # json.dump(ucfg.data,open("ucfg.data.json","w"),ensure_ascii=False)
                    ucfg.save_config()

            return {"success":True,"data":outputData}
        if key in ucfg.itemClass[ucfg.data["df_dir"]]:
            return {"success":True,"files":ucfg.itemClass[ucfg.data["df_dir"]][key]}
        else:
            return {"success":False,"files":[],"message":"没有找到该分类的文件"}

    def save_classOrder(self,order):
        # global ucfg.data
        ucfg.data["class_order"] = order
        # json.dump(ucfg.data,open("ucfg.data.json","w"),ensure_ascii=False)
        ucfg.save_config()
        return {"success":True}

    def remove_class(self,key):
        # global ucfg.itemClass
        if key in ucfg.itemClass[ucfg.data["df_dir"]]:
            del ucfg.itemClass[ucfg.data["df_dir"]][key]
            with open(cfg.USER_CLASS_FILE,"w",encoding="utf-8") as f:
                json.dump(ucfg.itemClass,f,ensure_ascii=False)
        return {"success":True}

    # ===== 应用组 API =====
    def create_group(self, name):
        # global ucfg.data
        gid = group_mgr.create_group(ucfg.data["df_dir"], name)
        return {"success": True, "groupId": gid}

    def rename_group(self, group_id, new_name):
        # global ucfg.data
        ok = group_mgr.rename_group(ucfg.data["df_dir"], group_id, new_name)
        return {"success": ok}

    def delete_group(self, group_id):
        # global ucfg.data
        ok = group_mgr.delete_group(ucfg.data["df_dir"], group_id)
        return {"success": ok}

    def add_to_group(self, group_id, file_paths):
        # global ucfg.data
        ok = group_mgr.add_items(ucfg.data["df_dir"], group_id, file_paths)
        return {"success": ok}

    def remove_from_group(self, group_id, file_path):
        # global ucfg.data
        ok = group_mgr.remove_item(ucfg.data["df_dir"], group_id, file_path)
        return {"success": ok}

    def get_group_contents(self, group_id):
        # global ucfg.data
        items = group_mgr.get_group_items(ucfg.data["df_dir"], group_id)
        result = []
        for fp in items:
            if not os.path.exists(fp):
                continue
            fn = os.path.splitext(os.path.basename(fp))[0]
            ico = iconMgr.get_icon(fp, fn)
            if os.path.isfile(fp):
                ext = os.path.splitext(fp)[1]
            else:
                ext = "dir"
            if ext == ".lnk":
                real_file = getIcon.get_shortcut_target(fp)
                if os.path.isfile(real_file):
                    ext = os.path.splitext(real_file)[1]
                else:
                    ext = "dir"
                info_data = itmeRes.mix_fileInfo(fp, os.path.basename(real_file), ico, ext, real_file)
            else:
                info_data = itmeRes.mix_fileInfo(fp, fn, ico, ext)
            info = info_data["inf"]
            info["f_type"] = info_data["inf_type"]
            info["cl"] = itmeRes.is_cl(fp)
            result.append(info)
        return {"success": True, "data": result}

    def get_groups(self):
        # global ucfg.data
        groups = group_mgr.get_all_groups(ucfg.data["df_dir"])
        return {"success": True, "data": groups}

    def save_group_order(self, ordered_ids):
        # global ucfg.data
        ucfg.data["dir_order"]["__groups__:" + ucfg.data["df_dir"]] = ordered_ids
        # json.dump(ucfg.data, open("ucfg.data.json", "w"), ensure_ascii=False)
        ucfg.save_config()
        return {"success": True}
    
    def edit_group_order(self, group_id, ordered_paths):
        if isinstance(ordered_paths,list)==False:
            return {"success": False, "message": "参数错误"}
        # global ucfg.data
        now_dir = ucfg.data["df_dir"]
        data = group_mgr._load_groups()
        data[now_dir][group_id]["items"]=ordered_paths
        group_mgr._save_groups(data)
        return {"success": True}
    def get_imageBase64(self,file_path):
        return imagePreView.get_imageBase64(file_path)

    def set_blur_effect(self,open_state,real_theme=None):
        windowMgr.set_blur(open_state,real_theme)

    def load_blur_effect(self,b_type='Acrylic'):
        windowMgr.load_blur_effect(b_type)
        # global hwnd,ucfg.data
        # if ucfg.data['blur_bg']==False:
        #     return
        # WindowEffect().resetEffect(hwnd)
        # print("from lbe")
        # if b_type=='Acrylic':
        #     WindowEffect().setAcrylicEffect(hwnd)
        # else:
        #     WindowEffect().setAeroEffect(hwnd)

    def fit_resize(self):
        # global fit_hwnd
        width, height, end_x, end_y = tool.get_window_inf("easyDesktop-fit")
        win32gui.MoveWindow(resize_win.fit_hwnd, end_x, end_y, width, height, True)

    def drag_posMoveAction(self):
        # global hwnd
        while True:
            try:
                left, top, right, bottom = win32gui.GetWindowRect(windowMgr.hwnd)
                point = win32api.GetCursorPos()
                break
            except:
                time.sleep(0.5)
        in_window = (left <= point[0] <= right) and (top <= point[1] <= bottom)
        if in_window == True:
            pos_percent = (bottom-point[1])/(bottom-top)
            if pos_percent < 0.2:
                move_type = "bottom"
            elif pos_percent > 0.8:
                move_type = "top"
            else:
                move_type = "none"
        else:
            move_type = "none"
        return move_type
    def get_version(self):
        return {"success":True,"version":cfg.APP_VERSION}

    def select_image(self):
        # global ignore_action
        windowMgr.disable_autoClose()
        file_types = ('Image Files (*.png;*.jpg;*.gif;*.jpeg;*.webp)', 'All files (*.*)')

        result = windowMgr.window.create_file_dialog(
            webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types
        )
        if result !=None:
            ext = os.path.splitext(result[0])[1]
            if ext.lower() not in ['.png', '.jpg', '.jpeg', '.gif', '.webp','.ico','.PNG','.JPG','.JPEG','.GIF','.WEBP']:
                result = None
                msgbox("请选择图片文件！", "文件类型错误")
        windowMgr.enable_autoClose()
        return result
    
    def setIcon(self,file_path,icon_select=False):
        # global ucfg.data
        if icon_select==False:
            if file_path in ucfg.data["ico"]:
                if os.path.exists(ucfg.data["ico"][file_path]):
                    os.remove(ucfg.data["ico"][file_path])
                del ucfg.data["ico"][file_path]
                # json.dump(ucfg.data,open("ucfg.data.json","w")
                ucfg.save_config()
            return {"success":True}
        else:
            icon_path = self.select_image()
            if icon_path == None:
                return {"success":False,"message":"未选择图标"}
            icon_path = icon_path[0]
            if not os.path.exists(icon_path):
                return {"success":False,"message":"图标文件不存在"}
            if not os.path.exists(cfg.ICON_SET_PATH):
                os.mkdir(cfg.ICON_SET_PATH)
            new_iconPath = os.path.join(cfg.ICON_SET_PATH,os.path.basename(icon_path))
            shutil.copy(icon_path, new_iconPath)
            # 删除旧图标
            if file_path in ucfg.data["ico"]:
                if os.path.exists(ucfg.data["ico"][file_path]):
                    os.remove(ucfg.data["ico"][file_path])
            # 保存新图标
            ucfg.data["ico"][file_path] = os.path.join("icon_set",os.path.basename(icon_path))
            json.dump(ucfg.data,open("ucfg.data.json","w"))
            return {"success":True}
        
    def clean_temp(self):
        if os.path.exists("desktopICO"):
            shutil.rmtree("desktopICO")
        if os.path.exists("itemsTemp.json"):
            os.remove("itemsTemp.json")
        from src.res_load import itmeRes
        itmeRes.temp={}