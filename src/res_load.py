from src import getIcon # 本地模块源
from src.icon_mgr import iconMgr

import os
import json
from PIL import Image
from threading import Thread

import config as cfg
from src import group_mgr
import traceback

import base64
import io

import configparser
from src.windowMgr import windowMgr
from src import tool
from src.ucfg import ucfg
import time

TEMP_FILE="itemsTemp.json"
desktop_path = tool.get_desktop_path()
public_desktop = os.path.join(os.environ["PUBLIC"], "Desktop")



class resource_load:
    def __init__(self):
        self.last_update_time = 0
        self.temp = {}
    def read_full_temp(self):
        if os.path.exists(TEMP_FILE):
            try:
                with open(TEMP_FILE, "r",encoding="utf-8") as f:
                    temp_data = json.load(f)
                self.temp = temp_data
                return temp_data
            except Exception as e:
                return self.temp
        else:
            return {}
    def write_temp(self,dirPath,temp):
        data = self.read_full_temp()
        data[dirPath]=temp
        with open(TEMP_FILE, "w",encoding="utf-8") as f:
            json.dump(data, f,ensure_ascii=True, indent=4)
    def read_temp(self,dirPath):
        if os.path.exists(TEMP_FILE):
            data = self.read_full_temp()
            if dirPath in data:
                return data[dirPath]
            else:
                return None
        else:
            return None
    def check_recover(self,data, match):
        result = False
        for d in data:
            if d["filePath"] == match["filePath"] and d["fileName"] == match["fileName"]:
                result = True
                break
        return result
    def is_cl(self,file_path):
        try:
            cl_data = json.load(open(cfg.CL_DATA_FILE, "r"))
            if file_path in cl_data:
                return cl_data[file_path]
            else:
                return False
        except Exception as e:
            print(f"读取收藏数据失败: {e}")
            return False
        
    # 排序相关——————————————————
    def find_in_a(self,a,path):
        result = None
        for i in range(len(a)):
            item = a[i]
            if item["filePath"] == path:
                result = item
                break
        return result

    def merge_lists(self,a, b):
        # 查找新增项
        new_items = []
        for i in range(len(a)):
            item = a[i]
            if item["filePath"] not in b:
                new_items.append({"item":item,"pos":i/len(a)})

        # 删除排序引索不存在的path
        b[:] = [item for item in b if self.find_in_a(a, item) is not None]
        # for i in range(len(b)):
        #     item = b[i]
        #     if self.find_in_a(a,item)==None:
        #         del b[i]
        #         i -= 1
        #     if len(b)>=i+1:
        #         break

        # 开始排序
        new_order = []
        for i in range(len(b)):
            new_order.append(self.find_in_a(a,b[i]))
        
        # 插入新项
        for item in new_items:
            new_order.insert(int(item["pos"]*len(a)),item["item"])

        return new_order

    def get_url_from_url_file(self,file_path):
        """
        从.url文件中提取URL
        """
        config = configparser.ConfigParser()
        
        try:
            # 读取.url文件
            config.read(file_path)
            
            # 获取URL（通常在[InternetShortcut]部分的URL字段）
            url = config.get('InternetShortcut', 'URL')
            return url
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            print(f"解析文件时出错: {e}")
            return None
        except Exception as e:
            print(f"读取文件时出错: {e}")
            return None

    def mix_fileInfo(self,file_path,file_name,ico,ext,real_path=None):
        file = os.path.basename(file_path)
        if ext in [".exe",".EXE"]:
            if real_path!=None:
                file = os.path.basename(real_path)
            file_name=os.path.splitext(os.path.basename(file_path))[0]
        if real_path!=None:
            if os.path.isdir(real_path):
                ext = "文件夹"
                file_path=real_path
                real_path = None
        else:
            if os.path.isdir(file_path):
                ext = "文件夹"
        info = {
            "file": file,
            "filePath": file_path,
            "fileName": file_name,
            "ico": ico,
            "fileType": ext,
        }
        if file_path in ucfg.data["ico"]:
            info["edit_ico"]=True
        if real_path!=None:
            info["realPath"] = real_path
        if ext == ".url":
            try:
                print(file_path)
                url = self.get_url_from_url_file(file_path)
                if "steam://rungameid" in url:
                    info["fileType"] = "SteamGame"
            except:
                print("url解析失败")
                print(file_path)
        if ext in [".exe",".EXE",".url"]:
            # print(file_path)
            ft = "exe"
        elif ext in ["文件夹","dir"]:
            ft = "dir"
        else:
            ft = "file"
        return {"inf_type":ft,"inf":info}
    def load_items(self,dir_path):
        exe_data = []
        dir_data = []
        file_data = []

        if not dir_path in ["desktop",r"/\\","","/"]:
            if not os.path.exists(dir_path):
                dir_path = "desktop"
                ucfg.update_config("df_dir", dir_path)
                windowMgr.window.evaluate_js('UIUtils.showError("自定义目录不存在，已自动切换到桌面")')

        if dir_path == "desktop":
            get_count = 2
            path_list = [desktop_path, public_desktop]
        else:
            get_count = 1
            path_list = [dir_path]
        for i in range(get_count):
            current_dir = path_list[i]
            for item in os.listdir(current_dir):
                try:
                    if "desktop.ini" == item:
                        continue
                    filename, _ = os.path.splitext(item) # 文件名
                    full_path = os.path.join(current_dir, item) # 完整路径

                    ico = iconMgr.get_icon(full_path,filename)
                    if os.path.isfile(full_path):
                        ext = os.path.splitext(full_path)[1]
                    else:
                        ext = "dir"
                    if ext == ".lnk":
                        real_file = getIcon.get_shortcut_target(full_path)
                        if os.path.exists(real_file):
                            if os.path.isfile(real_file):
                                ext = os.path.splitext(real_file)[1]
                            else:
                                ext = "dir"
                        else:
                            real_file = full_path
                        info_data = self.mix_fileInfo(full_path,os.path.basename(real_file),ico,ext,real_file)
                    else:
                        info_data = self.mix_fileInfo(full_path,filename,ico,ext)

                    if info_data["inf_type"]=="exe":
                        exe_data.append(info_data["inf"])
                    elif info_data["inf_type"]=="dir":
                        dir_data.append(info_data["inf"])
                    elif info_data["inf_type"]=="file":
                        file_data.append(info_data["inf"])
                except:
                    tool.bugs_report(
                        "python-update_inf_item",
                        traceback.format_exc(),
                        False
                    )
        self.write_temp(
            dir_path,
            {
                "exe": exe_data,
                "dir": dir_data,
                "file": file_data
            }
        )
        self.last_update_time = time.time()
        return exe_data,dir_data,file_data
    def delay_update_action(self,dir_path):
        self.last_update_time = time.time()
        if dir_path == "/\\":
            dir_path = "desktop"
        exe_data,dir_data,file_data = self.load_items(dir_path)
        self.write_temp(dir_path,{"exe": exe_data,"dir": dir_data,"file": file_data})
        now_path = windowMgr.window.evaluate_js("AppState.currentPath")
        if now_path == dir_path:
            windowMgr.window.evaluate_js("NavigationManager.refreshCurrentPath(true,false)")
    def delay_update(self,dir_path):
        print(time.time()-self.last_update_time)
        if time.time()-self.last_update_time>2:
            print("update")
            Thread(target=self.delay_update_action,args=(dir_path,)).start()
        
    def get_items(self,dir_path,quick_update=True):
        if quick_update==False:
            print("及时更新")
            return self.load_items(dir_path)
        temp_data = self.read_temp(dir_path)
        if temp_data==None:
            return self.load_items(dir_path)
        else:
            self.delay_update(dir_path)
            return temp_data["exe"],temp_data["dir"],temp_data["file"]
        
    
    def order_items(self,dir_path,exe_data,dir_data,file_data):
        # if config["show_sysApp"]==True:
        out_data = []
        index = 0
        if ucfg.data["show_sysApp"] == True and (
            dir_path == "desktop"
            or dir_path == ""
            or dir_path == "/"
            or dir_path == desktop_path
            or dir_path == public_desktop
        ):
            for item in cfg.SYSTEM_APPS:
                # item["cl"]=False
                item["index"]= index
                index+=1
                out_data.append(item)

        # 应用组：组
        o_data = exe_data + dir_data + file_data
        all_groups = group_mgr.get_all_groups(dir_path)
        group_data = []
        for gid, ginfo in all_groups.items():
            # 校验组内文件是否仍有效
            valid_items = [p for p in ginfo.get("items", []) if os.path.exists(p)]
            if valid_items != ginfo.get("items", []):
                ginfo["items"] = valid_items
                _gdata = group_mgr._load_groups()
                _gdata[dir_path] = all_groups
                group_mgr._save_groups(_gdata)
            # 收集前4个子项图标
            group_icons = []
            for fp in valid_items[:4]:
                for it in o_data:
                    if it["filePath"] == fp:
                        group_icons.append(it.get("ico", ""))
                        break
                else:
                    fn = os.path.splitext(os.path.basename(fp))[0]
                    group_icons.append(iconMgr.get_icon(fp, fn))
            group_item = {
                "fileName": ginfo["name"],
                "filePath": "__group__:" + gid,
                "fileType": "应用组",
                "ico": "",
                "groupIcons": group_icons,
                "isGroup": True,
                "groupId": gid,
                "itemCount": len(valid_items),
                "f_type": "group",
                "file": "__group__"
            }
            group_item["index"] = index
            index += 1
            group_data.append(group_item)
        
        o_data = group_data + exe_data + dir_data + file_data
        # 应用组：过滤已编组文件，注入组项目
        grouped_paths = group_mgr.get_grouped_paths(dir_path)
        if grouped_paths:
            o_data = [item for item in o_data if item["filePath"] not in grouped_paths]
        for item in o_data:
            if self.check_recover(out_data, item) == True:
                continue

            # if item["cl"]==True:
            #     cl_list.append(item)
            #     continue
            item["index"]=index
            item["f_type"] = "exe"
            index+=1
            out_data.append(item)

        order_data = []
        if dir_path in ucfg.data["dir_order"]:
            this_order = ucfg.data["dir_order"][dir_path]
            # 先去从排序列表中删除无效项目
            r_index = 0
            while r_index < len(this_order):
                this_path = this_order[r_index]
                had_found = False
                for item in out_data:
                    if item["filePath"] == this_path:
                        had_found = True
                        break
                if had_found == False:
                    del this_order[r_index]
                else:
                    r_index += 1
        # 再插入排序
            order_data = this_order
            out_data = self.merge_lists(out_data, order_data)

        # 重复监测
        try:
            temp_list = []
            r_index = 0
            while r_index < len(out_data): 
                need_del = False
                for item in temp_list:
                    if item["filePath"] == out_data[r_index]["filePath"]:
                        need_del = True
                        break
                if need_del == True:
                    del out_data[r_index]
                else:
                    temp_list.append(out_data[r_index])
                    r_index += 1
            temp_list = []
        except:
            retry_count+=1
            if retry_count<=5:
                return self.update_inf(dir_path,retry_count)
            else:
                pass

        # 收藏排序
        out_with_cl = []
        for t in [True,False]:
            for i in range(len(out_data)):
                try:
                    out_data[i]["cl"] = self.is_cl(out_data[i]["filePath"])
                    if out_data[i]["cl"]==t:
                        out_with_cl.append(out_data[i])
                except:
                    break
        out_data = out_with_cl
        # 编号写入
        for i, item in enumerate(out_data):
            item['index'] = i
        return {"data":out_data}

    def update_inf(self,dir_path,quick_update=True):
        try:
            if dir_path == "/\\":
                dir_path = "desktop"

            # global config
            exe_data,dir_data,file_data = self.get_items(dir_path,quick_update)
            return self.order_items(dir_path,exe_data,dir_data,file_data)
            
            
        except:
            tool.bugs_report(
                "python-update_inf",
                traceback.format_exc()
            )

class imagePreview_main:
    def __init__(self):
        self.image_preview_cache = {}

    def get_imageBase64(self,file_path):
        if file_path in self.image_preview_cache:
            return self.image_preview_cache[file_path]
        max_size_kb = 200
        quality=85
        step=5
        # try:
        img = Image.open(file_path)
        
        # 保持原比例
        original_width, original_height = img.size
        
        # 转换为RGB模式（如果是RGBA或其他模式）
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 逐步降低质量直到满足大小要求
        output_buffer = io.BytesIO()
        current_quality = quality
        
        while current_quality > 10:  # 设置最低质量限制
            output_buffer.seek(0)
            output_buffer.truncate(0)
            
            # 保存图片到内存缓冲区
            img.save(output_buffer, format='JPEG', quality=current_quality, optimize=True)
            
            # 检查文件大小
            file_size_kb = len(output_buffer.getvalue()) / 1024
            
            if file_size_kb <= max_size_kb:
                break
            
            # 如果仍然太大，降低质量
            current_quality -= step
        
        # 如果仍然太大，尝试调整尺寸（保持比例）
        if len(output_buffer.getvalue()) / 1024 > max_size_kb:
            # 计算需要缩小的比例
            scale_factor = (max_size_kb * 1024 / len(output_buffer.getvalue())) ** 0.5
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            # 调整尺寸
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 重新压缩
            output_buffer.seek(0)
            output_buffer.truncate(0)
            img_resized.save(output_buffer, format='JPEG', quality=80, optimize=True)
        
        # 转换为base64字符串
        base64_string = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        blob_string = f"data:image/jpeg;base64,{base64_string}"

        self.image_preview_cache[file_path] = blob_string
        return blob_string
        # except:
        #     return None


itmeRes = resource_load()
imagePreView = imagePreview_main()