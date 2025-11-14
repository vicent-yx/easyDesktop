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
    global download_inf_bar,download_inf_var,progressbar,install_started,uninstall_btn,main_frame,install_type
    install_type = itype  # 保存操作类型
    install_started=True
    path_input_frame.destroy()
    start_btn.pack_forget()
    try:
        uninstall_btn.pack_forget()
    except:
        pass
    
    # 创建安装进度区域
    progress_frame = tkinter.Frame(main_frame, bg="white")
    progress_frame.pack(fill="both", expand=True, pady=20)
    
    progressbar=ttk.Progressbar(progress_frame, style="Custom.Horizontal.TProgressbar")
    progressbar.pack(pady=20)
    #设置进度条最大值为100
    progressbar['maximum']=100
    #设置进度条长度
    progressbar['length']=400
    
    download_inf_var = tkinter.StringVar()
    download_inf_bar = tkinter.Label(progress_frame, textvariable=download_inf_var, 
                                    bg="white", fg="#333333", font=("微软雅黑", 10))
    download_inf_bar.pack(pady=5)
    
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
    download_inf_var.set("检测进程...")
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
    try:
        if os.path.exists(os.path.join(install_path,"config.json")):
            user_config = json.load(open(os.path.join(install_path,"config.json"),"r",encoding="utf-8"))
        else:
            user_config = None
        if os.path.exists(os.path.join(install_path,"cl_data.json")):
            cl_data = json.load(open(os.path.join(install_path,"cl_data.json"),"r",encoding="utf-8"))
        else:
            cl_data = None
        if os.path.exists(os.path.join(install_path,"user_class.json")):
            user_class = json.load(open(os.path.join(install_path,"user_class.json"),"r",encoding="utf-8"))
        else:
            user_class = None
        copy_bg=False
        if user_config!=None:
            if user_config["use_bg"]==True:
                if os.path.exists(os.path.join(install_path,user_config["bg"])):
                    try:
                        shutil.copy2(os.path.join(install_path,user_config["bg"]),user_config["bg"])
                        copy_bg=True
                    except:
                        pass
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

        try:
            if user_config!=None:
                json.dump(user_config, open(os.path.join(install_path,"config.json"),"w",encoding="utf-8"))
            if cl_data!=None:
                json.dump(cl_data, open(os.path.join(install_path,"cl_data.json"),"w",encoding="utf-8"))
            if user_class!=None:
                json.dump(user_class, open(os.path.join(install_path,"user_class.json"),"w",encoding="utf-8"))
            if copy_bg==True:
                shutil.copy2(user_config["bg"],os.path.join(install_path,user_config["bg"]))
                os.remove(user_config["bg"])
        except Exception as e:
            print(e)

        download_inf_var.set("完成")
        install_started=False
        show_finish()
    except PermissionError:
        messagebox.showerror("EasyDesktop - 安装时出现错误","权限不足，无法在当前位置安装")
        install_started=False
    except Exception as e:
        messagebox.showerror("EasyDesktop - 安装时出现错误",e)
    install_started=False
def out():
    window.quit()
def out_and_open():
    os.startfile(os.path.join(install_path,"easyDesktop.exe"))
    while True:
        if judgeprocess("easyDesktop.exe")==True:
            break
        sleep(0.5)
    os.startfile(os.path.join(install_path,"easyDesktop.exe"))
    window.quit()
def show_finish():
    global install_path, main_frame, install_type
    
    # 清除进度相关组件
    for widget in main_frame.winfo_children():
        widget.destroy()
    
    # 创建完成界面
    finish_frame = tkinter.Frame(main_frame, bg="white")
    finish_frame.pack(fill="both", expand=True)
    
    # 根据操作类型显示不同的内容
    if install_type == "uninstall":
        # 卸载完成界面
        # 创建图标容器确保居中
        icon_frame = tkinter.Frame(finish_frame, bg="white")
        icon_frame.pack(fill="x", pady=(30, 0))
        success_label = tkinter.Label(icon_frame, text="    🗑️", font=("微软雅黑", 48), 
                                     fg="#FF6B6B", bg="white")
        success_label.pack(anchor="center")
        success_text = tkinter.Label(finish_frame, text="卸载完成！", 
                                    font=("微软雅黑", 16, "bold"), fg="#333333", bg="white")
        success_text.pack(pady=10)
        desc_text = tkinter.Label(finish_frame, text="EasyDesktop 已从您的计算机中移除", 
                                 font=("微软雅黑", 10), fg="#666666", bg="white")
        desc_text.pack(pady=5)
        # 按钮容器
        button_frame = tkinter.Frame(finish_frame, bg="white")
        button_frame.pack(fill="x", pady=40)

        inner_button_frame = tkinter.Frame(button_frame, bg="white")
        inner_button_frame.pack(anchor="center")
        tkinter.Button(inner_button_frame, text="完成", width=18, height=2, 
                      font=("微软雅黑", 11, "bold"), bg="#6C757D", fg="white", 
                      activebackground="#5A6268", relief="flat", 
                      cursor="hand2", command=out).pack()
        
    else:
        # 安装完成界面
        # 创建图标容器确保居中
        icon_frame = tkinter.Frame(finish_frame, bg="white")
        icon_frame.pack(fill="x", pady=(30, 0))
        success_label = tkinter.Label(icon_frame, text="🎉", font=("微软雅黑", 48), 
                                     fg="#4CAF50", bg="white")
        success_label.pack(anchor="center")  # 使用anchor="center"确保居中
        success_text = tkinter.Label(finish_frame, text="安装完成！", 
                                    font=("微软雅黑", 16, "bold"), fg="#333333", bg="white")
        success_text.pack(pady=10)
        desc_text = tkinter.Label(finish_frame, text="EasyDesktop 已成功安装到您的计算机", 
                                 font=("微软雅黑", 10), fg="#666666", bg="white")
        desc_text.pack(pady=5)
        # 按钮容器
        button_frame = tkinter.Frame(finish_frame, bg="white")
        button_frame.pack(fill="x", pady=30)
        
        # 创建内部按钮框架确保按钮居中
        inner_button_frame = tkinter.Frame(button_frame, bg="white")
        inner_button_frame.pack(anchor="center")
        
        # 水平排列按钮
        tkinter.Button(inner_button_frame, text="完成", width=12, height=2, 
                      font=("微软雅黑", 11, "bold"), bg="#6C757D", fg="white", 
                      activebackground="#5A6268", relief="flat", 
                      cursor="hand2", command=out).pack(side="left", padx=8)
        
        if os.path.exists(install_path):
            tkinter.Button(inner_button_frame, text="完成并打开", width=12, height=2, 
                          font=("微软雅黑", 11, "bold"), bg="#2196F3", fg="white", 
                          activebackground="#1976D2", relief="flat", 
                          cursor="hand2", command=out_and_open).pack(side="left", padx=8)

def closeWindow():
    if install_started == True:
        messagebox.showerror("警告","正在进行安装，请不要退出")
        return
    window.quit()

have_network=False
install_path = "D:/easydesktop"
install_started = False
install_type = "install"  # 默认操作类型

window = tkinter.Tk()
window.title("EasyDesktop - 安装")
window.geometry("600x400")
window.resizable(False,False)

# 设置样式
style = ttk.Style()
style.theme_use('clam')
style.configure("Custom.Horizontal.TProgressbar", 
                troughcolor='#f0f0f0',
                background='#4CAF50',
                bordercolor='#f0f0f0',
                lightcolor='#4CAF50',
                darkcolor='#4CAF50')

logo_img = tkinter.PhotoImage(file=resource_path(os.path.join("res","ed_logo.png"))) 
bg_img = tkinter.PhotoImage(file=resource_path(os.path.join("res","bg.png"))) 
background_label = tkinter.Label(window, image=bg_img)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# 创建主容器框架
main_frame = tkinter.Frame(window, bg="white", relief="flat", bd=1)
main_frame.place(relx=0.5, rely=0.5, anchor="center", width=550, height=350)

tkinter.Label(main_frame, image=logo_img, bg="white").pack(anchor="center", pady=20)

path_input_frame = tkinter.Frame(main_frame, bg="white")
path_v = tkinter.StringVar()
path_v.set(install_path)
tkinter.Label(path_input_frame, textvariable=path_v, width=40, height=1, 
              bg="#f8f9fa", fg="#333333", font=("微软雅黑", 10),
              relief="solid", bd=1, anchor="w", padx=10).pack(side="left", fill="both", expand=True)
tkinter.Button(path_input_frame, text="浏览", width=8, height=1, 
               command=select_dir, bg="#0078D7", fg="white", 
               font=("微软雅黑", 9, "bold"), relief="flat",
               activebackground="#106EBE").pack(side="right", padx=(10, 0))
path_input_frame.pack(pady=15, fill="x", padx=50)

start_btn=tkinter.Button(main_frame, text="开始安装", width=20, height=1, 
                        font=("微软雅黑", 12, "bold"), command=go_install,
                        bg="#0078D7", fg="white", relief="flat",
                        activebackground="#106EBE")
if check_registry_key()!=None:
    install_path=check_registry_key()
    path_v.set(install_path)
    start_btn=tkinter.Button(main_frame, text="更新程序", width=20, height=1,
                            font=("微软雅黑", 12, "bold"), command=go_install,
                            bg="#0078D7", fg="white", relief="flat",
                            activebackground="#106EBE")
    uninstall_btn=tkinter.Button(main_frame, text="卸载程序", width=20, height=1,
                                font=("微软雅黑", 12, "bold"), command=go_unsintall,
                                bg="#D83B01", fg="white", relief="flat",
                                activebackground="#C13501")
start_btn.pack(pady=5)
if check_registry_key()!=None:
    uninstall_btn.pack(pady=5)

# 添加底部版权信息
copyright_label = tkinter.Label(main_frame, text="EasyDesktop © 2025     Made by CodeVicent", 
                               bg="white", fg="#666666", font=("微软雅黑", 8))
copyright_label.pack(side="bottom", pady=10)

window.protocol('WM_DELETE_WINDOW', closeWindow)
window.mainloop()