from ast import If
import json
import requests
import config as cfg
from src.ucfg import ucfg
import shutil
import sys
# from easygui import buttonbox,msgbox
from src.appAction.fgp import get_machine_fingerprint
from ..appAction import report
import os
import subprocess
from src.windowMgr import windowMgr

def check_update():
    # 更新检查操作
    # ..........
    pass
def main():
    print("EasyDesktop backend action")
    check_update()
    