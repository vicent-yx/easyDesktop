
import json
import requests
import config as cfg
from easygui import buttonbox,msgbox
from src.appAction.fgp import get_machine_fingerprint
import os
import time

# apiHost = "https://api.codevicent.xyz/"
apiHost = cfg.API_URL
window = None

class BugsReportMgr():
    def __init__(self):
        pass
    def add_bug(self,part,data,note=True,with_data=None):
        # bug汇报操作
        # ..........
        pass

bugs_report_mgr = BugsReportMgr()

def bugs_report(part,data,note=True,with_data=None):
    bugs_report_mgr.add_bug(part,data,note,with_data)
