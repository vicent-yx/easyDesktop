# EasyDesktop - 您的桌面伴侣

✨ **让整洁桌面与高效操作完美共存** ✨  


**隐藏桌面图标，但不隐藏便捷性！** EasyDesktop 是一款创新的桌面增强工具，让您在保持桌面整洁美观的同时，快速访问桌面文件。只需将鼠标移至屏幕左下角，即可呼出智能文件面板！

![主界面](https://gitee.com/codevicent/easy-desktop/raw/main/README_RES/main_show.jpg)

## 🔧 开发信息
 软件使用pywebview开发，界面使用html+css+js实现，实际操作（如打开文件、新建文件等）由python实现（js通过pywebview调用）


## ✨ 核心功能

### 🖥️ 智能呼出与布局
- **角落触发**：鼠标移至左下角即可呼出面板
- **双视图模式**：网格布局（默认）与列表布局自由切换
- **深度文件操作**：
  - 新建文件（docx/xlsx/pptx/txt/文件夹）
  - 重命名/删除文件
  - 粘贴剪切板文件（支持资源管理器复制内容）
  - 单击打开文件，双击在资源管理器显示
  - 单击进入文件夹，双击在资源管理器打开

### 🔍 闪电搜索
- **智能过滤**：输入文件名、拼音首字母或全拼实时搜索
- **模糊匹配**：忽略大小写和标点符号
- **快速搜索**：在当前目录进行快速搜索

![文件搜索](https://gitee.com/codevicent/easy-desktop/raw/main/README_RES/search_show.gif)

### 🎨 个性化主题
- **多主题支持**：浅色/深色/3Z 三种精美主题
- **系统跟随**：自动匹配系统主题切换
- **高级自定义**：
  - 自定义背景图片
  - 磨砂效果强度调节
  - 透明度控制

| 自定义背景及磨砂 | 跟随系统主题切换深浅色主题 |
|-----|------|
![自定义背景](https://gitee.com/codevicent/easy-desktop/raw/main/README_RES/bg_set.gif)|![主题切换](https://gitee.com/codevicent/easy-desktop/raw/main/README_RES/sys_theme.gif)

### ⚙️ 便捷设置
- **开机自启**：一次设置，永久自动运行
- **零配置使用**：下载即用，无需复杂安装

## 🖼️ 界面展示

### 多主题预览
| 效果展示 | theme |
|----------|----------|
| ![浅色主题](https://gitee.com/codevicent/easy-desktop/raw/main/README_RES/main.jpg) | 浅色主题 |
| ![深色主题](https://gitee.com/codevicent/easy-desktop/raw/main/README_RES/dark_theme.jpg) | 深色主题 |
| ![3Z主题](https://gitee.com/codevicent/easy-desktop/raw/main/README_RES/3z_theme.jpg) | 3Z主题 |
注意：本软件不自带桌面壁纸，请自行下载壁纸并设置背景。

### 操作界面
| 右键菜单 | 新建文件 |
|----------|----------|
| ![右键菜单](https://gitee.com/codevicent/easy-desktop/raw/main/README_RES/menu.jpg) | ![新建文件](https://gitee.com/codevicent/easy-desktop/raw/main/README_RES/new_file.jpg)

| 文件粘贴 | 主题设置 |
|----------|----------|
| ![文件粘贴](https://gitee.com/codevicent/easy-desktop/raw/main/README_RES/put_file.jpg) | ![主题设置](https://gitee.com/codevicent/easy-desktop/raw/main/README_RES/theme_settings.jpg) |

## 🚀 快速开始

1. **下载软件**：请在右侧的发行版中获取最新版软件！
2. **运行程序**：解压后双击 `easyDesktop.exe` 即可启动
3. **基本操作**：
   - 鼠标移至左下角呼出面板
   - 右键菜单进行文件操作
   - 右上角设置按钮进行个性化配置
4. **设置自启**：设置中勾选"开机自启动"

## 🤝 贡献指南

我们欢迎各种形式的贡献！如果您想：
- 报告问题或建议新功能
- 提交代码改进
- 完善文档

欢迎提交 Pull Request！喵。

---

**如果喜欢这个项目，请点个 Star 支持一下呀！** 