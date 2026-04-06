import json
from config import app_config as cfg
import os
from . import screen
import sys

# 打包后纠正工作目录
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(os.path.realpath(sys.executable))
    os.chdir(base_path)

class AppConfig:
    def __init__(self):
        # from . import tool
        screen_width, screen_height = screen.get_screen_size()
        width = int(screen_width * cfg.WINDOW_WIDTH_RATIO)
        height = int(screen_height * cfg.WINDOW_HEIGHT_RATIO)
        default_config = cfg.get_default_config(width, height)
        if os.path.exists(cfg.CONFIG_FILE):
            with open(cfg.CONFIG_FILE, "r",encoding="utf-8") as f:
                config = json.load(f)
                f.close()
            for c_item in default_config.keys():
                if c_item not in config.keys():
                    config[c_item] = default_config[c_item]
            config["version"] = cfg.APP_VERSION
            # json.dump(config, open(cfg.CONFIG_FILE, "w"))
            self.write_json(cfg.CONFIG_FILE,config)
        else:
            config = default_config
            # json.dump(config, open(cfg.CONFIG_FILE, "w"))
            self.write_json(cfg.CONFIG_FILE,config)

        self.data = config

        if not os.path.exists(cfg.CL_DATA_FILE):
            with open(cfg.CL_DATA_FILE, "w",encoding="utf-8") as f:
                json.dump({}, f)
                f.close()

        if not os.path.exists(cfg.USER_CLASS_FILE):
            itemClass = {self.data["df_dir"]:{}}
            with open(cfg.USER_CLASS_FILE, "w",encoding="utf-8") as f:
                json.dump(itemClass, f, ensure_ascii=True, indent=4)
                f.close()
        else:
            with open(cfg.USER_CLASS_FILE, "r",encoding="utf-8") as f:
                itemClass = json.load(f)
                f.close()

        if not os.path.exists(cfg.USER_GROUPS_FILE):
            with open(cfg.USER_GROUPS_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)
        self.itemClass = itemClass
    def get(self):
        return self.data
    def save_config(self):
        self.write_json(cfg.CONFIG_FILE,self.data)
    def write_json(self,file,data):
        with open(file, "w")as f:
            json.dump(data, f, ensure_ascii=True, indent=4)
            f.close()

    def update_config(self,part,data):
        self.data[part] = data
        self.write_json(cfg.CONFIG_FILE,self.data)
        # with open(cfg.CONFIG_FILE, "w")as f:
        #     json.dump(self.data, f)
        #     f.close()
        from .windowMgr import windowMgr
        windowMgr.update_state(part,data)
        

ucfg = AppConfig()