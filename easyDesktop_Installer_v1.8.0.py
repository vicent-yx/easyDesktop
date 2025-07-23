from win32com.client import Dispatch
import pythoncom
import zipfile
import tkinter
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
import os
import sys
import shutil
import _thread
import winreg
from time import sleep
import psutil
from ctypes import windll
import json
import win32com
progressbar=""

def get_desktop_path():
    shell = win32com.client.Dispatch("WScript.Shell")
    return shell.SpecialFolders("Desktop")
def create_shortcut(target_path, shorcut_path,install_path):
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortcut(shorcut_path)
    shortcut.TargetPath = target_path
    shortcut.WorkingDirectory=install_path
    shortcut.Save()
def resource_path(relative_path):
    if getattr(sys, 'frozen', False): #是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def is_wpp_dir(check_path):
    file_c = ["easyDesktop.exe","easyFileDesk.html","favicon.ico","base_library.zip","theme"]
    is_n = 0
    for exe_c in file_c:
        if os.path.exists(os.path.join(check_path,exe_c)):
            is_n+=1
    if is_n >= len(file_c)/2:
        return True
    else:
        return False

def select_dir():
    global install_path,path_v
    install_path_input = filedialog.askdirectory()
    if os.path.exists(install_path_input):
        if os.listdir(install_path_input)==[] or is_wpp_dir(install_path_input)==True:
            install_path = install_path_input
            path_v.set(install_path)
            print("1")
            return
    if install_path_input[-1] == "/":
        dir_name = "easydesktop"
    else:
        dir_name = "/easydesktop"
    install_path = install_path_input+dir_name
    print(install_path)
    print("2")
    if not os.path.exists(install_path):
        os.makedirs(install_path)
    path_v.set(install_path)
def start_install(itype="install"):
    global download_inf_bar,download_inf_var,progressbar,install_started,uninstall_btn
    install_started=True
    path_input_frame.destroy()
    start_btn.pack_forget()
    try:
        uninstall_btn.pack_forget()
    except:
        pass
    progressbar=ttk.Progressbar(window)
    progressbar.pack()
    #设置进度条最大值为100
    progressbar['maximum']=100
    #设置进度条长度
    progressbar['length']=500
    download_inf_var = tkinter.StringVar()
    download_inf_bar = tkinter.Label(window,textvariable=download_inf_var)
    download_inf_bar.place(x=50,y=290)
    text_json = os.path.join(install_path,"text.json")
    if not os.path.exists(install_path):
        try:
            os.mkdir(install_path)
        except PermissionError as e:
            messagebox.showerror("EasyDesktop - 安装时出现错误","请以管理员身份运行安装程序！如果安装在此处，若想体验完整功能，需要常驻给EasyDesktop开管理员权限。")
            print(e)
            os._exit(0)
    try:
        json.dump("",open(text_json,"w",encoding="utf-8"))
    except PermissionError as e:
        messagebox.showerror("EasyDesktop - 安装时出现错误","请以管理员身份运行安装程序！如果安装在此处，若想体验完整功能，需要常驻给EasyDesktop开管理员权限。")
        print(e)
        os._exit(0)
    finally:
        if os.path.exists(text_json):
            os.remove(text_json)
    if itype=="uninstall":
        download_inf_var.set("准备开始卸载...")
        window.update()
        _thread.start_new_thread(un_install,())
    else:
        download_inf_var.set("准备开始安装...")
        window.update()
        _thread.start_new_thread(install,())

def go_install():
    start_install("install")
def go_unsintall():
    start_install("uninstall")
def check_registry_key():
    try:
        # 打开HKEY_CURRENT_USER下的Software\easydesktop项
        key_path = r"Software\easydesktop"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            
            # 尝试读取InstallPath的值
            value, reg_type = winreg.QueryValueEx(key, "InstallPath")
            print(f"找到InstallPath: {value}")
            return value
    
    except FileNotFoundError:
        print("注册表路径或键值不存在")
    except PermissionError:
        print("权限不足，无法访问注册表")
    except Exception as e:
        print(f"发生错误: {str(e)}")
    return None
def judgeprocess(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            return True
    return False
def un_install():
    global download_inf_var,install_started,progressbar,install_path
    # try:
    progressbar["mode"]="indeterminate"
    progressbar["orient"]=tkinter.HORIZONTAL
    download_inf_var.set("正在删除文件")
    exe_list = ["easyDesktop.exe"]
    for exe in exe_list:
        if judgeprocess(exe)==True:
            os.popen("taskkill /F /im "+exe)
            download_inf_var.set("正在删除文件 停止进程"+exe)
            while True:
                if judgeprocess(exe)==False:
                    break
                sleep(0.5)
    download_inf_var.set("正在删除文件")
    shutil.rmtree(check_registry_key())
    pythoncom.CoInitialize()
    if os.path.exists(os.path.join(os.path.expanduser("~"), "Desktop","EasyDesktop.lnk")):
        os.remove(os.path.join(os.path.expanduser("~"), "Desktop","EasyDesktop.lnk"))
    pythoncom.CoUninitialize()
    download_inf_var.set("正在删除注册表项:")
    try:
        # 打开父键（HKEY_CURRENT_USER\Software）
        parent_path = r"Software"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, parent_path, 0, winreg.KEY_WRITE) as parent_key:
            # 删除目标键（easydesktop）
            winreg.DeleteKey(parent_key, "easydesktop")
            print("注册表项已成功删除")
    except:
        print("注册表项删除失败")

    download_inf_var.set("卸载完成")
    install_started=False
    show_finish()
    # except Exception:
    #     download_inf_var.set("卸载失败")
def install():
    global download_inf_var,install_started,progressbar
    if os.path.exists(os.path.join(install_path,"config.json")):
        user_config = json.load(open(os.path.join(install_path,"config.json"),"r",encoding="utf-8"))
    else:
        user_config = None
    # try:
    progressbar["mode"]="indeterminate"
    progressbar["orient"]=tkinter.HORIZONTAL
    if os.listdir(install_path)!=[]:
        download_inf_var.set("正在删除文件")
        exe_list = ["easyDesktop.exe"]
        for exe in exe_list:
            if judgeprocess(exe)==True:
                os.popen("taskkill /F /im "+exe)
                download_inf_var.set("正在删除文件 停止进程"+exe)
                while True:
                    if judgeprocess(exe)==False:
                        break
                    sleep(0.5)
            
        download_inf_var.set("正在删除文件")
        un_delDir_list=["wallpaper","plug","char"]
        for filename in os.listdir(install_path):
            file_path = os.path.join(install_path, filename)
            if os.path.isfile(file_path):
                if not ".json" in file_path:
                    os.remove(file_path)
                    download_inf_var.set("正在删除: "+file_path)
            else:
                can_del_s = False
                for dir in un_delDir_list:
                    if dir in file_path:
                        can_del_s=True
                        break
                if can_del_s==True:
                    shutil.rmtree(file_path)
                    download_inf_var.set("正在删除文件夹: "+file_path)
        # shutil.rmtree(install_path)
        # print("正在删除目录："+install_path)
        # os.makedirs(install_path)

    progressbar["mode"]="determinate"
    filename = resource_path(os.path.join("res","easydesktop.zip"))
    download_inf_var.set("正在解压文件")
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        total_files = len(zip_ref.infolist())
        extracted_files = 0
        for file in zip_ref.infolist():
            extracted_files += 1
            if not os.path.exists(file.filename):
                zip_ref.extract(file, install_path)
            progress = (extracted_files / total_files) * 100
            progress_num = int(progress)
            progressbar['value']=int(progress_num)
            download_inf_var.set("正在解压文件 "+str('[解压进度]: '+str(progress_num)+"%"))
            # print(f"Extracting: {file.filename} - Progress: {progress:.2f}%")
        # zip_ref.extractall(install_path)

    download_inf_var.set("正在写入注册表")
    # Windows 注册表
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\easydesktop") as key:
        winreg.SetValueEx(key, "InstallPath", 0, winreg.REG_SZ, install_path)
    download_inf_var.set("正在创建快捷方式")

    pythoncom.CoInitialize()
    if os.path.exists(os.path.join(os.path.expanduser("~"), "Desktop","EasyDesktop.lnk")):
        os.remove(os.path.join(os.path.expanduser("~"), "Desktop","EasyDesktop.lnk"))
    desktop_path = get_desktop_path()
    target_path = os.path.join(install_path,"easyDesktop.exe")
    shortcut_path = os.path.join(desktop_path, 'EasyDesktop.lnk')
    create_shortcut(target_path, shortcut_path,install_path)
    pythoncom.CoUninitialize()

    if user_config!=None:
        json.dump(user_config, open(os.path.join(install_path,"config.json"),"w",encoding="utf-8"))

    download_inf_var.set("完成")
    install_started=False
    show_finish()
    # except PermissionError:
    #     messagebox.showerror("EasyDesktop - 安装时出现错误","此窗口无权限，如果你已经点击允许给了权限，请在新窗口进行安装")
    #     install_started=False
    # except Exception as e:
    #     messagebox.showerror("EasyDesktop - 安装时出现错误",e)
    install_started=False
def out():
    window.quit()
def show_finish():
    progressbar.pack_forget()
    download_inf_bar.place_forget()
    tkinter.Button(window,text="完成",width=20,height=2,font=("微软雅黑", 20),command=out).pack()
def closeWindow():
    if install_started == True:
        messagebox.showerror("警告","正在进行安装，请不要退出")
        return
    window.quit()
have_network=False
install_path = "D:/easydesktop"

install_started = False
window = tkinter.Tk()
window.title("EasyDesktop - 安装")
window.geometry("600x400")
window.resizable(False,False)
logo_img = tkinter.PhotoImage(file=resource_path(os.path.join("res","ed_logo.png"))) 
tkinter.Label(window, image=logo_img).pack(anchor="center")
path_input_frame = tkinter.Frame(window)
path_v = tkinter.StringVar()
path_v.set(install_path)
tkinter.Label(path_input_frame,textvariable=path_v,width=50,height=2,bg="white").pack(side="left")
tkinter.Button(path_input_frame,text="浏览",width=5,height=2,command=select_dir).pack(side="right")
path_input_frame.pack()
start_btn=tkinter.Button(window,text="开始安装",width=20,height=1,font=("微软雅黑", 20),command=go_install)
if check_registry_key()!=None:
    install_path=check_registry_key()
    path_v.set(install_path)
    start_btn=tkinter.Button(window,text="更新程序",width=20,height=1,font=("微软雅黑", 20),command=go_install)
    uninstall_btn=tkinter.Button(window,text="卸载程序",width=20,height=1,font=("微软雅黑", 20),command=go_unsintall)
start_btn.pack()
if check_registry_key()!=None:
    uninstall_btn.pack()
window.protocol('WM_DELETE_WINDOW', closeWindow)
window.mainloop() 