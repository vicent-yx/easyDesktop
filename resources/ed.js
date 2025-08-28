// ========== 常量定义 ==========
const CONSTANTS = {
    SCRIPT_TYPES: [".py", ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".php", ".rb", ".go", ".swift", ".kt", ".m", ".pl", ".r", ".sh", ".bash", ".zsh", ".lua", ".scala", ".groovy", ".dart", ".rs", ".jl", ".hs", ".f", ".f90", ".f95", ".v", ".vhd", ".clj", ".ex", ".exs", ".elm", ".purs", ".erl", ".hrl", ".fs", ".fsx", ".fsi", ".ml", ".mli", ".pas", ".pp", ".d", ".nim", ".cr", ".cbl", ".cob", ".ada", ".adb", ".ads"],

    FILE_TYPES: {
        'docx': '文档', 'doc': '文档',
        'xlsx': '电子表格', 'xls': '电子表格',
        'pptx': '演示文稿', 'ppt': '演示文稿',
        'pdf': 'PDF文件',
        'jpg': '图片', 'png': '图片',
        'mp4': '视频', 'mp3': '音频',
        'psd': '设计稿', 'fig': '设计稿',
        'sql': '数据库', 'json': '配置文件',
        'zip': '压缩文件', 'exe': '应用程序'
    },

    THEME_PATHS: {
        "dark": "/theme/dark.css",
        "light": "/theme/light.css",
        "zzz": "/theme/zzz.css"
    },

    CLICK_DELAY: 200,
    REMIND_DURATION: 1000,
    ERROR_DISPLAY_TIME: 5000
};

// ========== 工具函数模块 ==========
const Utils = {
    /**
     * 获取文件类型显示名称
     */
    getFileType(fileName, fileType) {
        if (fileType === '文件夹') return '文件夹';

        const ext = fileName.split('.').pop().toLowerCase();
        if (CONSTANTS.SCRIPT_TYPES.includes(ext)) {
            return fileType.slice(1) + '脚本文件';
        }

        return CONSTANTS.FILE_TYPES[ext] || fileType.slice(1) + '文件';
    },

    /**
     * 生成文件DOM元素ID
     */
    generateFileId(filePath) {
        return filePath.replace(/[\\/:]/g, '-');
    },

    /**
     * 检查中文字符
     */
    checkChineseChars(str) {
        const chineseRegex = /[\u4e00-\u9fa5]/;
        const nonChineseRegex = /[^\u4e00-\u9fa5]/;
        const hasChinese = chineseRegex.test(str);
        const hasNonChinese = nonChineseRegex.test(str);

        if (!hasChinese) return { have_cn: false };

        if (hasChinese && !hasNonChinese) {
            return { have_cn: true, origin: str, fix: str };
        }

        const chineseOnly = str.split('').filter(c => chineseRegex.test(c)).join('');
        return { have_cn: true, origin: str, fix: chineseOnly };
    },

    /**
     * 字符串包含检查（忽略特殊字符）
     */
    contains(mainStr, searchStr) {
        const cleanMainStr = mainStr.replace(/[^\w\u4e00-\u9fa5]/g, '');
        const cleanSearchStr = searchStr.replace(/[^\w\u4e00-\u9fa5]/g, '');
        const regex = new RegExp(cleanSearchStr, 'i');
        return regex.test(cleanMainStr);
    },

    /**
     * 防抖函数
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// ========== 应用状态管理 ==========
const AppState = {
    files_data: [],
    selectedFile: null,
    contextMenu: null,
    dealing: false,
    currentPath: '',
    pathHistory: [],
    currentHistoryIndex: -1,
    timer: null,
    db_click_action: false,
    in_edit: false,

    reset() {
        this.files_data = [];
        this.selectedFile = null;
        this.dealing = false;
        this.db_click_action = false;
        this.in_edit = false;
        if (this.timer) {
            clearTimeout(this.timer);
            this.timer = null;
        }
    },

    setFiles(files) {
        this.files_data = files;
    },

    setSelectedFile(file) {
        this.selectedFile = file;
    },

    addToHistory(path) {
        this.pathHistory = this.pathHistory.slice(0, this.currentHistoryIndex + 1);
        this.pathHistory.push(path);
        this.currentHistoryIndex = this.pathHistory.length - 1;
        this.currentPath = path;
    }
};

// ========== DOM元素缓存 ==========
const DOMCache = {
    elements: {},

    get(id) {
        if (!this.elements[id]) {
            this.elements[id] = document.getElementById(id);
        }
        return this.elements[id];
    },

    getBySelector(selector) {
        return document.querySelector(selector);
    },

    getAllBySelector(selector) {
        return document.querySelectorAll(selector);
    }
};

// ========== API调用封装 ==========
const ApiHelper = {
    async call(method, ...args) {
        return await window.pywebview.api[method](...args);
    },

    async getConfig() {
        return await this.call('get_config');
    },

    async updateConfig(key, value) {
        return await this.call('update_config', key, value);
    },

    async getFileInfo(path) {
        return await this.call('get_fileinfo', path);
    },

    async openFile(filePath) {
        return await this.call('open_file', filePath);
    },

    async showFile(filePath) {
        return await this.call('show_file', filePath);
    },

    async copyFile(filePath) {
        return await this.call('copy_file', filePath);
    },

    async renameFile(filePath, newName) {
        return await this.call('rename_file', filePath, newName);
    },

    async removeFile(filePath, type = "remove") {
        return await this.call('remove_file', filePath, type);
    },

    async newFile(fileType, currentPath) {
        return await this.call('new_file', fileType, currentPath);
    },

    async putFile(targetPath) {
        return await this.call('put_file', targetPath);
    },

    async loadSearchIndex(data) {
        return await this.call('load_search_index', data);
    }
};

// ========== UI工具类 ==========
const UIUtils = {
    showError(message) {
        const errorBox = document.createElement('div');
        Object.assign(errorBox.style, {
            position: 'fixed',
            top: '-100px',
            left: '50%',
            transform: 'translateX(-50%)',
            padding: '20px 30px',
            backgroundColor: '#ff4d4d',
            color: 'white',
            fontSize: '16px',
            borderRadius: '12px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
            zIndex: '9999',
            opacity: '0',
            transition: 'opacity 0.5s ease, top 0.5s ease',
            textAlign: 'center'
        });

        const text = document.createElement('div');
        text.textContent = message;
        errorBox.appendChild(text);
        document.body.appendChild(errorBox);

        setTimeout(() => {
            errorBox.style.top = '20px';
            errorBox.style.opacity = '1';
        }, 100);

        setTimeout(() => {
            errorBox.style.opacity = '0';
            errorBox.style.top = '-100px';
            setTimeout(() => errorBox.remove(), 500);
        }, CONSTANTS.ERROR_DISPLAY_TIME);
    },

    remindFile(fileElement) {
        if (!fileElement) return;
        fileElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        fileElement.classList.add("file-item_hover");
        setTimeout(() => {
            fileElement.classList.remove("file-item_hover");
        }, CONSTANTS.REMIND_DURATION);
    },

    // 滚动控制相关的私有变量
    _scrollDisabled: false,
    _preventScrollHandler: null,
    _savedScrollPosition: { top: 0, left: 0 },
    _originalBodyStyles: null,

    disableScroll() {
        if (this._scrollDisabled) return; // 避免重复禁用

        this._scrollDisabled = true;

        // 保存当前滚动位置
        this._savedScrollPosition.top = window.pageYOffset || document.documentElement.scrollTop;
        this._savedScrollPosition.left = window.pageXOffset || document.documentElement.scrollLeft;

        const body = document.body;
        const html = document.documentElement;

        // 保存原始样式
        this._originalBodyStyles = {
            overflow: body.style.overflow,
            paddingRight: body.style.paddingRight
        };

        // 计算滚动条宽度，避免页面跳动
        const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;

        // 设置样式阻止滚动，但不改变定位
        body.style.overflow = "hidden";
        body.style.paddingRight = `${scrollbarWidth}px`; // 补偿滚动条宽度
        html.style.overflow = "hidden";

        // 创建统一的事件处理函数
        this._preventScrollHandler = (e) => {
            const settingsBox = DOMCache.get('themeSettings_box');
            // 只允许设置面板内的滚动
            if (!settingsBox || !settingsBox.contains(e.target)) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        };

        // 添加事件监听器
        const events = ['touchmove', 'mousewheel', 'wheel', 'DOMMouseScroll', 'keydown'];
        events.forEach(event => {
            document.addEventListener(event, this._preventScrollHandler, {
                passive: false,
                capture: true
            });
        });

        console.log('滚动已禁用');
    },

    enableScroll() {
        if (!this._scrollDisabled) return; // 避免重复启用

        this._scrollDisabled = false;

        if (this._preventScrollHandler) {
            const events = ['touchmove', 'mousewheel', 'wheel', 'DOMMouseScroll', 'keydown'];
            events.forEach(event => {
                document.removeEventListener(event, this._preventScrollHandler, {
                    passive: false,
                    capture: true
                });
            });
            this._preventScrollHandler = null;
        }

        const body = document.body;
        const html = document.documentElement;

        if (this._originalBodyStyles) {
            body.style.overflow = this._originalBodyStyles.overflow;
            body.style.paddingRight = this._originalBodyStyles.paddingRight;
            this._originalBodyStyles = null;
        } else {
            // 如果没有保存的样式，则清空
            body.style.overflow = "";
            body.style.paddingRight = "";
        }
        html.style.overflow = "";

        // 恢复滚动位置
        window.scrollTo(this._savedScrollPosition.left, this._savedScrollPosition.top);

        console.log('滚动已启用');
    },

    // 获取滚动状态
    isScrollDisabled() {
        return this._scrollDisabled;
    },

    // 调试函数：检查滚动状态
    debugScrollStatus() {
        console.log('=== 滚动状态调试信息 ===');
        console.log('滚动是否被禁用:', this._scrollDisabled);
        console.log('body.style.overflow:', document.body.style.overflow);
        console.log('body.style.position:', document.body.style.position);
        console.log('事件处理器是否存在:', !!this._preventScrollHandler);
        console.log('保存的滚动位置:', this._savedScrollPosition);
        console.log('========================');
    }
};

// ========== 文件渲染器 ==========
class FileRenderer {
    constructor() {
        this.gridContainer = DOMCache.get('filesContainer');
        this.listContainer = DOMCache.get('filesListContainer');
    }

    /**
     * 渲染文件列表
     */
    async render(files) {
        this.clearContainers();

        if (!files || files.length === 0) {
            this.setEmptyState();
            return;
        }

        files.forEach(file => {
            this.renderGridItem(file);
            this.renderListItem(file);
        });
    }

    clearContainers() {
        this.gridContainer.innerHTML = '';
        this.listContainer.innerHTML = '';
    }

    setEmptyState() {
        this.gridContainer.style.minHeight = "75vh";
        this.listContainer.style.minHeight = "75vh";
    }

    createFileElement(file, isGrid = true) {
        const element = document.createElement('div');
        element.className = isGrid ? 'file-item' : 'file-list-item';
        element.id = Utils.generateFileId(file.filePath);

        const fileType = Utils.getFileType(file.file, file.fileType);
        const iconClass = isGrid ? 'file-icon' : 'file-list-icon';
        const nameClass = isGrid ? 'file-name' : 'file-list-name';
        const typeClass = isGrid ? 'file-type' : 'file-list-type';

        element.innerHTML = `
            <img src="${file.ico}" alt="${file.fileName}" class="${iconClass}">
            <span class="${nameClass}">${file.fileName}</span>
            <span class="${typeClass}">${fileType}</span>
        `;
        const cl_e = document.createElement("div")
        
        cl_e.className = isGrid ? 'file-cl' : 'file-list-cl';;
        if(file.cl==false){
            if(document.getElementById("theme_css").href.includes("light")==true){
                cl_e.innerHTML="<img src='./resources/imgs/cl.png'>"
            }else{
                cl_e.innerHTML="<img src='./resources/imgs/cl_w.png'>"
            }
            
        }else{
            cl_e.innerHTML="<img src='./resources/imgs/cl-active.png'>"
            cl_e.style.display="block"
        }
        
        cl_e.onclick=(event) => {event.stopPropagation();change_cl_state(file.filePath, file.cl)};
        cl_e.ondblclick = (event) => {event.stopPropagation();}
        element.insertBefore(cl_e, element.firstChild);
        element.cl = cl_e;

        this.attachFileEvents(element, file);
        return element;
    }

    renderGridItem(file) {
        const element = this.createFileElement(file, true);
        this.gridContainer.appendChild(element);
    }

    renderListItem(file) {
        const element = this.createFileElement(file, false);
        this.listContainer.appendChild(element);
    }

    attachFileEvents(element, file) {
        // 双击事件
        element.addEventListener('dblclick', () => {
            AppState.db_click_action = true;
            clearTimeout(AppState.timer);
            this.handleFileAction(file, true);
        });

        // 单击事件
        element.addEventListener('click', () => {
            DOMCache.get("search_input").value = "";
            AppState.timer = setTimeout(async () => {
                if (AppState.db_click_action) {
                    AppState.db_click_action = false;
                    return;
                }
                this.handleFileAction(file, false);
            }, CONSTANTS.CLICK_DELAY);
        });

        // 右键菜单事件
        element.addEventListener('contextmenu', (e) => {
            MenuManager.showContextMenu(e, file);
        });
    }

    handleFileAction(file, isDoubleClick) {
        if (file.fileType === '文件夹') {
            if (isDoubleClick) {
                ApiHelper.openFile(file.filePath);
            } else {
                NavigationManager.navigateTo(file.filePath);
            }
        } else if (file.sysApp) {
            ApiHelper.call('open_sysApp', file.filePath);
        } else {
            if (isDoubleClick) {
                ApiHelper.showFile(file.filePath);
            } else {
                ApiHelper.openFile(file.filePath);
            }
        }
    }
}

// ========== 菜单管理器 ==========
const MenuManager = {
    async showContextMenu(e, file) {
        e.preventDefault();
        const config = await ApiHelper.getConfig();

        DOMCache.get('blankMenu').style.display = 'none';
        AppState.setSelectedFile(file);

        const contextMenu = DOMCache.get('contextMenu');
        contextMenu.style.display = 'block';
        contextMenu.style.left = `${e.pageX / (config["scale"] / 100)}px`;
        contextMenu.style.top = `${e.pageY / (config["scale"] / 100)}px`;

        this.adjustMenuPosition(contextMenu, e);
    },

    adjustMenuPosition(menu, e) {
        if (e.pageY + menu.offsetHeight > window.innerHeight) {
            window.scrollTo(0, document.documentElement.scrollHeight);
        }
        if (e.pageX + menu.offsetWidth > window.innerWidth) {
            window.scrollTo(document.body.scrollWidth, window.scrollY);
        }
    },

    hideContextMenu() {
        const contextMenu = DOMCache.get('contextMenu');
        if (contextMenu) {
            contextMenu.style.display = 'none';
        }
    },

    hideAllMenus() {
        this.hideContextMenu();
        DOMCache.get('blankMenu').style.display = 'none';
    }
};

// ========== 导航管理器 ==========
const NavigationManager = {
    async navigateTo(path) {
        DOMCache.get("content_box").scrollTo(0, 0);
        if(path=="/" || path=="" || path=="desktop" || path==document.getElementById("b2d").dataset.path){
            document.getElementById("box1").style.display="block"
        }else{
            document.getElementById("box1").style.display="none"
        }
        fit_btnBar()

        if (path === AppState.currentPath) {
            await this.refreshCurrentPath();
            return;
        }

        AppState.addToHistory(path);
        await this.updateBreadcrumb(path || '/');

        const result = await ApiHelper.getFileInfo(path);
        AppState.setFiles(result.data);
        await fileRenderer.render(result.data);

        window.scrollTo(0, 0);
    },

    async refreshCurrentPath() {
        const result = await ApiHelper.getFileInfo(AppState.currentPath);
        AppState.setFiles(result.data);
        await fileRenderer.render(result.data);
        if(last_group!="" || last_group!="全部"){
            change_class(last_group)
        }
    },

    async updateBreadcrumb(path) {
        console.log(path)
        const config = await ApiHelper.getConfig();
        const breadcrumb = DOMCache.get('breadcrumb');
        breadcrumb.innerHTML = '';

        const desktopPath = await ApiHelper.call('search_desktop_path');
        const basePath = config.df_dir === "desktop" ? desktopPath : config.df_dir;
        console.log(basePath)
        const parts = path.replace(basePath, "").split('\\').filter(part => part.length > 0);
        console.log(parts)

        // 添加根目录项
        const rootItem = document.createElement('span');
        rootItem.className = 'breadcrumb-item';
        rootItem.textContent = config.df_dir_name;
        rootItem.dataset.path = config.df_dir;
        rootItem.id = "b2d";
        breadcrumb.appendChild(rootItem);
        if (path.includes(basePath)){
            var currentPath = basePath+"\\";
        }else{
            var currentPath = ""
        }
        if(parts.length == 1 && parts[0] == "desktop")return
        parts.forEach((part, index) => {
            currentPath += part + "\\";
            
            console.log(part)

            if (index < parts.length - 1) {
                const separator = document.createElement('span');
                separator.className = 'breadcrumb-separator';
                separator.textContent = '›';
                breadcrumb.appendChild(separator);
            }

            const item = document.createElement('span');
            item.className = 'breadcrumb-item';
            item.textContent = part;
            item.dataset.path = currentPath;
            breadcrumb.appendChild(item);
        });
        console.log("______")
    }
};

// ========== 搜索管理器 ==========
const SearchManager = {
    async performSearch() {
        const key = DOMCache.get("search_input").value;

        if (key === "") {
            await fileRenderer.render(AppState.files_data);
            return;
        }

        const pyData = await ApiHelper.loadSearchIndex(AppState.files_data);
        const outData = [];
        const dealKey = Utils.checkChineseChars(key);

        if (dealKey.have_cn) {
            AppState.files_data.forEach(file => {
                if (Utils.contains(file.fileName, dealKey.origin) ||
                    Utils.contains(file.fileName, dealKey.fix)) {
                    outData.push(file);
                }
            });
        } else {
            AppState.files_data.forEach(file => {
                const fileData = pyData[file.fileName];
                if (fileData && (
                    Utils.contains(fileData.sxpy, key) ||
                    Utils.contains(fileData.py, key)
                )) {
                    outData.push(file);
                }
            });
        }

        await fileRenderer.render(outData);
    }
};

// ========== 主题管理器 ==========
const ThemeManager = {
    async applyBackgroundSettings(config) {
        const body = document.body;
        if (config.use_bg && config.bg) {
            Object.assign(body.style, {
                backgroundImage: `url("${config.bg}")`,
                backdropFilter: `blur(${config.ms_ef || 0}px)`,
                backgroundRepeat: "no-repeat",
                backgroundSize: "cover",
                backgroundPosition: "center"
            });
        } else {
            Object.assign(body.style, {
                backgroundImage: '',
                backdropFilter: ''
            });
        }
    }
};

// ========== 配置管理器 ==========
const ConfigManager = {
    async updateScale(value) {
        const realScale = value / 100;
        const container = DOMCache.get('content_box');
        container.style.height = (100 / realScale) + 'vh';
        document.body.style.zoom = realScale;
        await ApiHelper.updateConfig("scale", value);
    },

    async updateDefaultDirectory() {
        const config = await ApiHelper.getConfig();
        const settingBtns = DOMCache.get("dir_btn_box");

        document.getElementById("b2d").dataset.path = config.df_dir;// 此处DOM缓存项不起作用(似乎获取到的已经不是现在的b2d)，故用回getElementById
        document.getElementById("b2d").innerText = config.df_dir_name;
        navigateTo(config.df_dir);// 刷新主页
        DOMCache.get("defeat_dir_show").innerText = "当前选择：" + config.df_dir;

        if (config.df_dir === "desktop") {
            settingBtns.children[0].className = "dir_btn dir_btn_active";
            settingBtns.children[1].className = "dir_btn";
        } else {
            settingBtns.children[0].className = "dir_btn";
            settingBtns.children[1].className = "dir_btn dir_btn_active";
        }
    }
};

// ========== 文件操作管理器 ==========
const FileOperationManager = {
    async renameFile(filePath, newName) {
        const result = await ApiHelper.renameFile(filePath, newName);
        await this.refreshAndRemindFile(result);
        return result;
    },

    async removeFile(filePath, type = "remove") {
        const result = await ApiHelper.removeFile(filePath, type);
        await NavigationManager.refreshCurrentPath();
        return result;
    },

    async createNewFile(fileType) {
        const result = await ApiHelper.newFile(fileType, AppState.currentPath);
        await this.refreshAndRemindFile(result);
        return result;
    },

    async pasteFiles() {
        const result = await ApiHelper.putFile(AppState.currentPath);
        await NavigationManager.refreshCurrentPath();

        if (result.files) {
            setTimeout(() => {
                result.files.forEach(filePath => {
                    const fileId = Utils.generateFileId(filePath);
                    const element = DOMCache.get(fileId);
                    if (element) {
                        UIUtils.remindFile(element);
                    }
                });
            }, 200);
        }

        return result;
    },

    async refreshAndRemindFile(result) {
        await NavigationManager.refreshCurrentPath();

        if (result.file) {
            setTimeout(() => {
                const fileId = Utils.generateFileId(result.file);
                const element = DOMCache.get(fileId);
                if (element) {
                    UIUtils.remindFile(element);
                }
            }, 200);
        }
    }
};

// ========== 事件管理器 ==========
const EventManager = {
    init() {
        this.initTimeUpdate();
        this.initViewToggle();
        this.initSearchEvents();
        this.initMenuEvents();
        this.initDialogEvents();
        this.initSettingsEvents();
        this.initNavigationEvents();
        this.initKeyboardEvents();
        this.initClickEvents();
    },

    initTimeUpdate() {
        const updateTime = () => {
            const now = new Date();
            const options = {
                year: 'numeric', month: 'long', day: 'numeric',
                weekday: 'long', hour: '2-digit', minute: '2-digit',
                second: '2-digit', hour12: false
            };
            DOMCache.get('current-time').textContent = now.toLocaleDateString('zh-CN', options);
        };

        updateTime();
        setInterval(updateTime, 1000);
    },

    initViewToggle() {
        DOMCache.get('gridViewBtn').addEventListener('click', async () => {
            this.switchToGridView();
            await ApiHelper.updateConfig("view", "block");
        });

        DOMCache.get('listViewBtn').addEventListener('click', async () => {
            this.switchToListView();
            await ApiHelper.updateConfig("view", "list");
        });
    },

    switchToGridView() {
        DOMCache.get('filesContainer').style.display = 'grid';
        DOMCache.get('filesListContainer').style.display = 'none';
        DOMCache.get('gridViewBtn').classList.add('active');
        DOMCache.get('listViewBtn').classList.remove('active');
    },

    switchToListView() {
        DOMCache.get('filesContainer').style.display = 'none';
        DOMCache.get('filesListContainer').style.display = 'block';
        DOMCache.get('gridViewBtn').classList.remove('active');
        DOMCache.get('listViewBtn').classList.add('active');
    },

    initSearchEvents() {
        const debouncedSearch = Utils.debounce(() => {
            SearchManager.performSearch();
        }, 300);

        DOMCache.get("search_input").addEventListener('input', debouncedSearch);
    },

    initMenuEvents() {
        // 文件右键菜单
        DOMCache.get('menuOpen').addEventListener('click', () => {
            if (AppState.selectedFile.game) {
                ApiHelper.call('open_mhyGame', AppState.selectedFile.filePath, AppState.selectedFile.game);
            } else {
                ApiHelper.openFile(AppState.selectedFile.filePath);
            }
            MenuManager.hideContextMenu();
        });

        DOMCache.get('menuCopy').addEventListener('click', () => {
            ApiHelper.copyFile(AppState.selectedFile.filePath);
            MenuManager.hideContextMenu();
        });

        DOMCache.get('menuRename').addEventListener('click', this.showRenameDialog);
        DOMCache.get('menuDelete').addEventListener('click', this.showDeleteConfirm);

        // 空白区域右键菜单
        DOMCache.get('menuPaste').addEventListener('click', async () => {
            try {
                const result = await FileOperationManager.pasteFiles();
                if (result.success === false) {
                    UIUtils.showError(result.message);
                }
            } catch (error) {
                console.error('粘贴失败:', error);
            }
            DOMCache.get('blankMenu').style.display = 'none';
        });

        DOMCache.get('menuNew').addEventListener('click', () => {
            ApiHelper.call('lock_window_visibility');
            DOMCache.get('newFileOverlay').style.display = 'flex';
            DOMCache.get('blankMenu').style.display = 'none';
        });
    },

    initDialogEvents() {
        // 重命名对话框
        DOMCache.get('renameCancel').addEventListener('click', () => {
            if (AppState.dealing) return;
            AppState.dealing = true;
            ApiHelper.call('unlock_window_visibility');
            DOMCache.get('renameOverlay').style.display = 'none';
            AppState.dealing = false;
        });

        DOMCache.get('renameConfirm').addEventListener('click', async () => {
            if (AppState.dealing) return;
            AppState.dealing = true;
            ApiHelper.call('unlock_window_visibility');

            const newName = DOMCache.get('renameInput').value.trim();
            if (newName) {
                await FileOperationManager.renameFile(AppState.selectedFile.filePath, newName);
                DOMCache.get('renameOverlay').style.display = 'none';
            }
            AppState.dealing = false;
        });

        // 删除确认对话框
        DOMCache.get('deleteCancel').addEventListener('click', () => {
            DOMCache.get('deleteConfirm').style.display = 'none';
            AppState.dealing = false;
        });

        DOMCache.get('deleteConfirmBtn').addEventListener('click', async () => {
            AppState.dealing = true;
            const result = await FileOperationManager.removeFile(AppState.selectedFile.filePath);
            if (result.success === false) {
                UIUtils.showError(result.message);
            }
            DOMCache.get('deleteConfirm').style.display = 'none';
            AppState.dealing = false;
        });

        DOMCache.get('deleteConfirmBtn_r').addEventListener('click', async () => {
            AppState.dealing = true;
            const result = await FileOperationManager.removeFile(AppState.selectedFile.filePath, "rubbish");
            if (result.success === false) {
                UIUtils.showError(result.message);
            }
            DOMCache.get('deleteConfirm').style.display = 'none';
            AppState.dealing = false;
        });

        // 新建文件对话框
        DOMCache.get('newFileCancel').addEventListener('click', () => {
            ApiHelper.call('unlock_window_visibility');
            DOMCache.get('newFileOverlay').style.display = 'none';
        });

        DOMCache.get('newFileConfirm').addEventListener('click', async () => {
            ApiHelper.call('unlock_window_visibility');
            const selectedType = DOMCache.get('newFileTypeSelect').value;
            if (selectedType) {
                await FileOperationManager.createNewFile(selectedType);
                DOMCache.get('newFileOverlay').style.display = 'none';
            }
        });

        // 重命名输入框回车确认
        DOMCache.get('renameInput').addEventListener('keyup', (e) => {
            ApiHelper.call('unlock_window_visibility');
            if (e.key === 'Enter') {
                DOMCache.get('renameConfirm').click();
            }
        });
    },

    initSettingsEvents() {
        const settingsBtn = DOMCache.get('settingsBtn');
        const themePanel = DOMCache.get('themeSettingsPanel');
        const closeBtn = DOMCache.get('closeThemePanel');

        settingsBtn.addEventListener('click', () => {
            UIUtils.disableScroll();
            themePanel.style.display = themePanel.style.display === 'flex' ? 'none' : 'flex';
            ApiHelper.call("disable_autoClose")
        });

        closeBtn.addEventListener('click', () => {
            UIUtils.enableScroll();
            themePanel.style.display = 'none';
            ApiHelper.call("enable_autoClose")
        });

        this.initToggleSettings();
        this.initThemeSettings();
        this.initBackgroundSettings();
        this.initScaleSettings();
    },

    initToggleSettings() {
        const toggles = [
            'autoStartToggle', 'fullScreenToggle', 'fdrToggle',
            'of_sToggle', 'sysappToggle', 'followSystemTheme'
        ];

        const configKeys = [
            'auto_start', 'full_screen', 'fdr',
            'of_s', 'show_sysApp', 'follow_sys'
        ];

        toggles.forEach((toggleId, index) => {
            DOMCache.get(toggleId).addEventListener('change', function () {
                ApiHelper.updateConfig(configKeys[index], this.checked);
                if (toggleId === 'followSystemTheme') {
                    EventManager.updateThemeCardInteraction(this.checked);
                }
            });
        });

        // 选择器设置
        DOMCache.get('cf_type_toggle').addEventListener('change',async function () {
            try{
                if(this.value=="4"){
                    rs = await recordShortcut()
                    if(rs!=null){
                        await ApiHelper.updateConfig('cf_hotkey',rs);
                        ApiHelper.updateConfig('cf_type', this.value);
                        DOMCache.get("hotkey_show").innerText = "自定义："+rs
                        return
                    }else{
                        config = await ApiHelper.getConfig()
                        this.value = config.cf_type
                    }
                }
                ApiHelper.updateConfig('cf_type', this.value);
            }catch(e){
                config = await ApiHelper.getConfig()
                this.value = config.cf_type
            }
        });

        DOMCache.get('out_cf_type_toggle').addEventListener('change', function () {
            ApiHelper.updateConfig('out_cf_type', this.value);
        });
    },

    initThemeSettings() {
        const themeCards = DOMCache.getAllBySelector('.theme-card');
        const followSystemToggle = DOMCache.get('followSystemTheme');

        themeCards.forEach(card => {
            card.addEventListener('click', function () {
                if (followSystemToggle.checked) return;

                const theme = this.dataset.theme;
                ApiHelper.updateConfig("theme", theme);
                load_theme(theme);

                themeCards.forEach(c => c.classList.remove('active'));
                this.classList.add('active');
            });
        });

        // 监听系统主题变化
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', async (e) => {
            const config = await ApiHelper.getConfig();
            if (config.follow_sys) {
                const newTheme = e.matches ? 'dark' : 'light';
                load_theme(newTheme);
            }
        });
    },

    updateThemeCardInteraction(followSystem) {
        const themeCards = DOMCache.getAllBySelector('.theme-card');
        themeCards.forEach(card => {
            card.style.opacity = followSystem ? '0.5' : '1';
            card.style.pointerEvents = followSystem ? 'none' : 'auto';
        });
    },

    initBackgroundSettings() {
        const blurSlider = DOMCache.get('blurSlider');
        const blurValue = DOMCache.get('blurValue');

        if (blurSlider && blurValue) {
            blurSlider.addEventListener('input', async function () {
                blurValue.textContent = this.value;
                await ApiHelper.updateConfig("ms_ef", parseInt(this.value));
                const config = await ApiHelper.getConfig();
                ThemeManager.applyBackgroundSettings(config);
            });
        }

        DOMCache.get('bgResetBtn').addEventListener('click', async () => {
            await ApiHelper.updateConfig("use_bg", false);
            await ApiHelper.updateConfig("bg", "");
            await ApiHelper.updateConfig("ms_ef", 50);
            blurSlider.value = 50;
            blurValue.textContent = '50';
            const config = await ApiHelper.getConfig();
            ThemeManager.applyBackgroundSettings(config);
        });

        DOMCache.get('bgCustomBtn').addEventListener('click', async () => {
            try {
                const bgUrl = await ApiHelper.call('set_background');
                if (bgUrl) {
                    await ApiHelper.updateConfig("use_bg", true);
                    await ApiHelper.updateConfig("bg", bgUrl);
                    window.location.reload();
                }
            } catch (error) {
                console.error('设置背景图片失败:', error);
            }
        });
    },

    initScaleSettings() {
        const scaleSlider = DOMCache.get('sc_slider');
        scaleSlider.addEventListener('input', function () {
            const scaleValue = this.value;
            DOMCache.get("sc_input").innerText = `缩放比例：${scaleValue}%`;
            ConfigManager.updateScale(scaleValue);
        });
    },

    initNavigationEvents() {
        DOMCache.get('pathBackBtn').addEventListener('click', async () => {
            const parentPath = await ApiHelper.call('get_parent', AppState.currentPath);
            NavigationManager.navigateTo(parentPath);
            if(parentPath=="/" || parentPath=="" || parentPath=="desktop" || parentPath==document.getElementById("b2d").dataset.path){
                class_filter(last_group)
            }
        });

        DOMCache.get('breadcrumb').addEventListener('click', (e) => {
            if (e.target.classList.contains('breadcrumb-item')) {
                const path = e.target.dataset.path;
                NavigationManager.navigateTo(path);
            }
        });
    },

    initKeyboardEvents() {
        document.addEventListener('keydown', (event) => {
            if (document.activeElement.id !== 'search_input') {
                const searchInput = DOMCache.get('search_input');
                if (DOMCache.get("renameOverlay").style.display === "flex") return;
                if(document.activeElement.id == "categoryInput") return
                if(window_state==false)return

                if (searchInput && !event.ctrlKey && !event.altKey && !event.metaKey && event.key.length === 1) {
                    searchInput.focus();
                }
            }
        });
    },

    initClickEvents() {
        document.addEventListener('click', (event) => {
            MenuManager.hideAllMenus();

            if (["content_box", "main"].includes(event.target.id)) {
                ApiHelper.call('close_fullscreen_window');
            }
        });

        // 空白区域右键菜单
        DOMCache.getBySelector('.files-grid').addEventListener('contextmenu', (e) => {
            this.handleBlankContextMenu(e);
        });

        DOMCache.getBySelector('.files-list').addEventListener('contextmenu', (e) => {
            this.handleBlankContextMenu(e);
        });
    },

    handleBlankContextMenu(e) {
        if (e.target.classList.contains('files-grid') || e.target.classList.contains('files-list')) {
            e.preventDefault();
            MenuManager.hideContextMenu();
            const blankMenu = DOMCache.get('blankMenu');
            blankMenu.style.display = 'block';
            blankMenu.style.left = `${e.pageX}px`;
            blankMenu.style.top = `${e.pageY}px`;
        }
    },

    showRenameDialog() {
        ApiHelper.call('lock_window_visibility');
        const renameOverlay = DOMCache.get('renameOverlay');
        const renameInput = DOMCache.get('renameInput');

        renameInput.value = AppState.selectedFile.fileName;
        renameOverlay.style.display = 'flex';
        renameInput.focus();

        MenuManager.hideContextMenu();
    },

    showDeleteConfirm() {
        const deleteConfirm = DOMCache.get('deleteConfirm');
        const deleteFileName = DOMCache.get('deleteFileName');

        deleteFileName.textContent = AppState.selectedFile.fileName;
        deleteConfirm.style.display = 'flex';

        MenuManager.hideContextMenu();
    }
};

// ========== 全局变量 ==========
let files_data = [];
let selectedFile = null;
let contextMenu = null;
let dealing = false;
let currentPath = '';
let pathHistory = [];
let currentHistoryIndex = -1;
let timer = null;
let db_click_action = false;
let in_edit = false;
let window_state = false
const scripts_type = CONSTANTS.SCRIPT_TYPES;
const blankMenu = DOMCache.get('blankMenu');
const newFileOverlay = DOMCache.get('newFileOverlay');
const newFileTypeSelect = DOMCache.get('newFileTypeSelect');
const newFileCancel = DOMCache.get('newFileCancel');
const newFileConfirm = DOMCache.get('newFileConfirm');
const menuPaste = DOMCache.get('menuPaste');
const menuNew = DOMCache.get('menuNew');

// ========== 全局函数 ==========
function getFileType(fileName, fileType) {
    return Utils.getFileType(fileName, fileType);
}

/**
 * 显示文件选择对话框
 * @returns {Promise<Object>} 包含选中文件列表和分类名的对象
 */
async function showFileSelectionDialog(class_name=null) {
    return new Promise(async (resolve) => {
        setTimeout(enableScroll,200)
        ApiHelper.call("disable_autoClose")
        let del_btn = document.getElementById("fileSelectionDelete")
        let list_data = []
        if(class_name!=null){
            let class_data = await ApiHelper.call('read_class', class_name)
            for(item of class_data.files){
                list_data.push(Utils.generateFileId(item.filePath))
            }
            del_btn.style.display="block"
            del_btn.dataset.cid = class_name
        }else{
            document.getElementById("fileSelectionDelete").style.display="none"
        }
        // 获取对话框元素
        const dialogContainer = document.getElementById('fileSelectionDialog');
        const overlay = document.querySelector('.file-selection-overlay');
        const dialogContent = dialogContainer.querySelector('.file-selection-content');
        const fileSelectionList = document.getElementById('fileSelectionList');
        const categoryInput = document.getElementById('categoryInput');
        const categoryErrorMsg = document.getElementById('categoryErrorMsg');
        const cancelBtn = dialogContainer.querySelector('.file-selection-btn');
        const confirmBtn =document.getElementById("fileSelectionConfirm")
        const del_action = async function del_this_class(){
            delete_class(del_btn.dataset.cid)
            handleCancel()
        }
        // 重置对话框状态
        fileSelectionList.innerHTML = '<div class="loading-indicator">加载中...</div>';
        if(class_name!=null){
            categoryInput.value = class_name;
            del_btn.removeEventListener("click",del_action,false)
            del_btn.addEventListener("click",del_action,false)
        }else{
            categoryInput.value = '';
        }
        categoryErrorMsg.style.display = 'none';
        categoryErrorMsg.textContent = '';

        // 显示对话框
        dialogContainer.style.display = 'flex';

        // 禁用背景滚动
        UIUtils.disableScroll();

        // 初始化变量
        let selections = [];
        const checkedState = new Map();

        try {
            // 获取文件信息
            const result = await ApiHelper.getFileInfo(AppState.currentPath);
            selections = result.data;

            // 清空加载提示
            fileSelectionList.innerHTML = '';

            // 渲染每个项目
            selections.forEach(item => {
                const listItem = document.createElement('div');
                listItem.className = 'file-selection-item';

                // 复选框
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = item.filePath;
                checkbox.dataset.filePath = item.filePath;

                // 初始状态为未选中
                if(list_data.includes(Utils.generateFileId(item.filePath))){
                    checkedState.set(item.filePath, true);
                    checkbox.checked = true;
                    listItem.className = 'file-selection-item active';
                }else{
                    checkedState.set(item.filePath, false);
                }

                // 监听勾选状态变化
                checkbox.addEventListener('change', () => {
                    checkedState.set(item.filePath, checkbox.checked);
                });

                // 元素点击监听
                listItem.addEventListener('click', () => {
                    if (checkbox.checked==true) {
                        checkbox.checked = false;
                        listItem.classList.remove('active');
                    } else {
                        checkbox.checked = true;
                        listItem.classList.add('active');
                    }
                    checkedState.set(item.filePath, checkbox.checked);
                });

                // 图标
                const icon = document.createElement('img');
                icon.src = item.ico;
                icon.className = 'file-icon';

                // 文件名
                const fileName = document.createElement('div');
                fileName.className = 'file-name';
                fileName.textContent = item.fileName;

                // 文件类型
                const fileType = document.createElement('div');
                fileType.className = 'file-type';
                fileType.textContent = item.fileType === '文件夹' ? '文件夹' : item.fileType;

                // 组装列表项
                listItem.appendChild(checkbox);
                listItem.appendChild(icon);
                listItem.appendChild(fileName);
                listItem.appendChild(fileType);
                fileSelectionList.appendChild(listItem);
            });

        } catch (error) {
            console.error('获取文件信息失败:', error);
            fileSelectionList.innerHTML = '';

            const errorMsg = document.createElement('div');
            errorMsg.textContent = '获取文件信息失败: ' + error.message;
            errorMsg.className = 'error-message';

            fileSelectionList.appendChild(errorMsg);
        }

        // 取消按钮事件
        function handleCancel() {
            dialogContainer.style.display = 'none';
            UIUtils.enableScroll();
            resolve({files_data: [], title: ''});
            ApiHelper.call("enable_autoClose")
        }

        // 确定按钮事件
        function handleConfirm() {
            const selectedItems = [];
            checkedState.forEach((isChecked, filePath) => {
                if (isChecked) {
                    console.log("checked！")
                    const item = selections.find(item => item.filePath === filePath);
                    if (item) {
                        selectedItems.push(item);
                    }
                }
            });

            // 获取分类名
            const categoryTitle = categoryInput.value.trim();

            // 验证输入
            if (!categoryTitle) {
                categoryErrorMsg.textContent = '分类名不能为空';
                categoryErrorMsg.style.display = 'block';
                return;
            }

            if (selectedItems.length === 0) {
                categoryErrorMsg.textContent = '请选择至少一个文件或文件夹';
                categoryErrorMsg.style.display = 'block';
                return;
            }

            categoryErrorMsg.style.display = 'none';
            dialogContainer.style.display = 'none';
            UIUtils.enableScroll();
            resolve({files_data: selectedItems, title: categoryTitle});
            ApiHelper.call("enable_autoClose")
        }

        // 点击对话框外部关闭
        function handleOverlayClick(e) {
            if (e.target === overlay) {
                dialogContainer.style.display = 'none';
                UIUtils.enableScroll();
                resolve({files_data: [], title: ''});
                ApiHelper.call("enable_autoClose")
            }
        }

        // 绑定事件
        cancelBtn.addEventListener('click', handleCancel);
        confirmBtn.addEventListener('click', handleConfirm);
        overlay.addEventListener('click', handleOverlayClick);

        // 清理事件监听器
        function cleanup() {
            cancelBtn.removeEventListener('click', handleCancel);
            confirmBtn.removeEventListener('click', handleConfirm);
            overlay.removeEventListener('click', handleOverlayClick);
        }

        // 确保在对话框关闭时清理事件
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                if (mutation.attributeName === 'style' && dialogContainer.style.display === 'none') {
                    cleanup();
                    observer.disconnect();
                }
            });
        });

        observer.observe(dialogContainer, { attributes: true });
    });
}

function open_file(filePath) {
    window.pywebview.api.open_file(filePath);
}

function open_mhyGame(filePath, game) {
    window.pywebview.api.open_mhyGame(filePath, game);
}

function copy_file(filePath) {
    window.pywebview.api.copy_file(filePath);
}

async function rename_file(filePath, newName) {
    return await FileOperationManager.renameFile(filePath, newName);
}

async function remove_file(filePath) {
    return await FileOperationManager.removeFile(filePath);
}

async function remove_file_r(filePath) {
    return await FileOperationManager.removeFile(filePath, "rubbish");
}

async function showContextMenu(e, file) {
    await MenuManager.showContextMenu(e, file);
}

function hideContextMenu() {
    MenuManager.hideContextMenu();
}

function showRenameDialog() {
    EventManager.showRenameDialog();
}

function showDeleteConfirm() {
    EventManager.showDeleteConfirm();
}

async function push(fData = null, useLoadDir = false, path = '') {
    console.log("11")
    try {
        if (fData === null) {
            let result;
            if((useLoadDir==true && (path=="" || path=="desktop")) || fData==null){
                document.getElementById("box1").style.display = "block"
                class_filter(last_group)
            }else{
                document.getElementById("box1").style.display = "none"
            }
            render_class_btn()
            fit_btnBar()
            if (useLoadDir && path) {
                result = await ApiHelper.getFileInfo(path);
                AppState.currentPath = path;
                AppState.setFiles(result.data);
            } else {
                result = await ApiHelper.getFileInfo("desktop");
                AppState.setFiles(result.data);
            }
            fData = result.data;
        }

        // 同步全局变量
        files_data = fData;
        currentPath = AppState.currentPath;

        await fileRenderer.render(fData);
        AppState.contextMenu = DOMCache.get('contextMenu');

    } catch (error) {
        window.pywebview.api.bug_report("push", error.toString()+"\n"+error.stack.toString());
        console.error(error);
    }
}
async function change_cl_state(filePath, cl){
    await ApiHelper.call('change_cl_state', filePath, cl);
    NavigationManager.refreshCurrentPath();
}
async function grid_view() {
    EventManager.switchToGridView();
}

async function list_view() {
    EventManager.switchToListView();
}

async function set_scale(value) {
    await ConfigManager.updateScale(value);
}

async function pack_df_dir_settings() {
    await ConfigManager.updateDefaultDirectory();
}

function navigateTo(path) {
    NavigationManager.navigateTo(path);
}

async function updateBreadcrumb(path) {
    await NavigationManager.updateBreadcrumb(path);
}

function navigateBack() {
    if (AppState.currentHistoryIndex > 0) {
        AppState.currentHistoryIndex--;
        const path = AppState.pathHistory[AppState.currentHistoryIndex];
        AppState.currentPath = path;
        currentPath = path;
        NavigationManager.navigateTo(path);
    }
}

function navigateForward() {
    if (AppState.currentHistoryIndex < AppState.pathHistory.length - 1) {
        AppState.currentHistoryIndex++;
        const path = AppState.pathHistory[AppState.currentHistoryIndex];
        AppState.currentPath = path;
        currentPath = path;
        NavigationManager.navigateTo(path);
    }
}

async function loadDirectory(path) {
    try {
        const data = await ApiHelper.getFileInfo(path);
        return data.data;
    } catch (error) {
        console.error('Error loading directory:', error);
        return [];
    }
}

async function put_file() {
    return await FileOperationManager.pasteFiles();
}

async function new_file(fileType) {
    return await FileOperationManager.createNewFile(fileType);
}

function hideAllMenus() {
    MenuManager.hideAllMenus();
}

function applyBackgroundSettings(config) {
    ThemeManager.applyBackgroundSettings(config);
}

async function initBackgroundSettings() {
    const config = await ApiHelper.getConfig();
    const blurSlider = DOMCache.get('blurSlider');
    const blurValue = DOMCache.get('blurValue');

    if (blurSlider && blurValue) {
        blurSlider.value = config.ms_ef;
        blurValue.textContent = blurSlider.value;
    }

    ThemeManager.applyBackgroundSettings(config);
}

function showError(code) {
    UIUtils.showError(code);
}

function checkChineseChars(str) {
    return Utils.checkChineseChars(str);
}

function contains(mainStr, searchStr) {
    return Utils.contains(mainStr, searchStr);
}

async function load_search() {
    await SearchManager.performSearch();
}

async function load_theme(theme) {
    try {
        // 参数验证
        if (!theme) {
            console.warn('load_theme: 主题参数不能为空');
            return false;
        }

        // 验证主题是否存在
        if (!CONSTANTS.THEME_PATHS[theme]) {
            console.warn(`load_theme: 不支持的主题 "${theme}"`);
            return false;
        }

        // 获取主题CSS元素
        const themeCSS = DOMCache.get("theme_css");
        if (!themeCSS) {
            console.error('load_theme: 找不到主题CSS元素');
            return false;
        }

        // 加载主题
        themeCSS.href = CONSTANTS.THEME_PATHS[theme];
        NavigationManager.refreshCurrentPath();
        render_class_btn()
        console.log(`主题已切换到: ${theme}`);
        return true;
    } catch (error) {
        console.error('load_theme: 加载主题时发生错误', error);
        return false;
    }
}

async function fit_window() {
    await ApiHelper.call('fit_window_start');
}

async function disable_settings() {
    DOMCache.get("fit_btn").innerText = "点击完成调整";
    DOMCache.get("fit_btn").onclick = async function () {
        await ApiHelper.call('fit_window_end');
    };
    DOMCache.get("closeThemePanel").style.display = "none";
    DOMCache.getAllBySelector(".settings-section").forEach((item) => {
        item.style.display = "none";
    });
    DOMCache.getAllBySelector(".setting_note").forEach((item) => {
        item.style.display = "none";
    });
}

function disableScroll() {
    UIUtils.disableScroll();
}

function enableScroll() {
    UIUtils.enableScroll();
}

function preventDefault(e) {
    const box = DOMCache.get('themeSettings_box');
    const isInsideBox = box.contains(e.target);
    if (!isInsideBox) {
        e.preventDefault();
    }
}

async function remind_file(file_item) {
    UIUtils.remindFile(file_item);
}

// 调试函数：检查和测试滚动功能
function debugScrollFunction() {
    UIUtils.debugScrollStatus();

    // 提供手动测试接口
    console.log('测试滚动功能:');
    console.log('- 执行 UIUtils.disableScroll() 禁用滚动');
    console.log('- 执行 UIUtils.enableScroll() 启用滚动');
    console.log('- 执行 UIUtils.debugScrollStatus() 查看状态');

    return {
        disable: () => UIUtils.disableScroll(),
        enable: () => UIUtils.enableScroll(),
        status: () => UIUtils.debugScrollStatus(),
        isDisabled: () => UIUtils.isScrollDisabled()
    };
}

async function change_default_dir(path = null) {
    ApiHelper.call('lock_window_visibility');
    try {
        const oldPath = AppState.currentPath;
        const config = await ApiHelper.getConfig();
        const oldDfDir = config["df_dir"];
        const result = await ApiHelper.call('change_default_dir', path);

        ApiHelper.call('unlock_window_visibility');

        if (result["success"] === true) {
            DOMCache.get("b2d").dataset.path = result["data"];
            DOMCache.get("b2d").innerText = result["name"];

            await ConfigManager.updateDefaultDirectory();
            DOMCache.get("b2d").click();
            render_class_btn()
        }
    } catch (error) {
        ApiHelper.call('unlock_window_visibility');
        console.error('更改默认目录失败:', error);
    }
}
async function check_dirChange(){
    var now_data = JSON.stringify(files_data);
    var new_data = await ApiHelper.getFileInfo(AppState.currentPath).data
    var new_data = JSON.stringify(new_data.data)
    if(now_data!=new_data){
        NavigationManager.refreshCurrentPath()
    }
}
// ========== 应用初始化 ==========
const fileRenderer = new FileRenderer();

// 页面加载完成后执行
window.addEventListener('pywebviewready', async function () {
    try {
        // 初始化事件管理器
        EventManager.init();

        // 初始化设置
        await ConfigManager.updateDefaultDirectory();

        // 加载默认文件
        const config = await ApiHelper.getConfig();
        const thisDir = await ApiHelper.getFileInfo(config["df_dir"]);
        AppState.setFiles(thisDir.data);
        files_data = thisDir.data; // 同步全局变量
        await fileRenderer.render(thisDir.data);

        // 初始化UI状态
        const updateUIFromConfig = async (config) => {
            const followSystem = config.follow_sys || false;
            const currentTheme = config.theme || 'dark';

            // 更新切换开关状态
            const toggleConfigs = [
                ['followSystemTheme', 'follow_sys'],
                ['autoStartToggle', 'auto_start'],
                ['fullScreenToggle', 'full_screen'],
                ['fdrToggle', 'fdr'],
                ['of_sToggle', 'of_s'],
                ['sysappToggle', 'show_sysApp']
            ];

            toggleConfigs.forEach(([elementId, configKey]) => {
                const element = DOMCache.get(elementId);
                if (element) {
                    element.checked = config[configKey];
                }
            });

            // 更新选择器状态
            DOMCache.get('cf_type_toggle').value = config.cf_type;
            DOMCache.get('out_cf_type_toggle').value = config.out_cf_type;

            // 更新缩放
            const scSlider = DOMCache.get('sc_slider');
            scSlider.value = config.scale;
            DOMCache.get("sc_input").innerText = "缩放比例：" + config.scale + "%";
            await ConfigManager.updateScale(config.scale);

            // 更新主题卡片状态
            const themeCards = DOMCache.getAllBySelector('.theme-card');
            themeCards.forEach(card => card.classList.remove('active'));

            if (!followSystem) {
                const activeCard = DOMCache.getBySelector(`.theme-card[data-theme="${currentTheme}"]`);
                if (activeCard) {
                    activeCard.classList.add('active');
                }
            }

            EventManager.updateThemeCardInteraction(followSystem);

            // 加载主题
            if (followSystem) {
                const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
                await load_theme(systemTheme);
            } else {
                await load_theme(currentTheme);
            }

            // 更新背景设置
            const blurSlider = DOMCache.get('blurSlider');
            const blurValue = DOMCache.get('blurValue');
            if (blurSlider && blurValue) {
                blurSlider.value = config.ms_ef || 50;
                blurValue.textContent = blurSlider.value;
            }

            await ThemeManager.applyBackgroundSettings(config);
        };

        // 应用配置
        await updateUIFromConfig(config);

        // 初始化背景设置
        await initBackgroundSettings();

        // 不在应用启动时禁用滚动，保持正常滚动状态
        // 滚动禁用只在打开设置面板时触发
        console.log('应用初始化完成，滚动状态：正常');

        setTimeout(() => {
            document.getElementById("b2d").click(); // 自动点击默认目录按钮
        }, 100);
        // setInterval(check_dirChange,1000);

    } catch (error) {
        console.error('应用初始化失败:', error);
        ApiHelper.call('bug_report', 'init', error.toString());
    }
    render_class_btn()
});

// 监听系统主题变化
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', async (e) => {
    const config = await ApiHelper.getConfig();
    if (config.follow_sys) {
        const newTheme = e.matches ? 'dark' : 'light';
        await load_theme(newTheme);
    }
});

// 监听鼠标侧键
document.onmousedown = function(event){
    if(event.button == 3){
        DOMCache.get("pathBackBtn").click();
    }
}

// 分类相关
const class_btn_bar =  document.getElementById("class_bar")
async function add_class(){
    setTimeout(function () {
        enableScroll()
    }, 100);
    var rs = await showFileSelectionDialog()
    if(rs && rs.files_data.length > 0){
        await ApiHelper.call('add_class', rs.files_data ,rs.title);
    }
    render_class_btn()
}
async function class_filter(path){
    var ctn = document.getElementById("filesContainer")
    var list_ctn = document.getElementById("filesListContainer")
    if(path == "" || path == "全部"){
        for(file_item of [...ctn.children,...list_ctn.children]){
            file_item.style.display = "flex"
        }
        return
    }
    var classData =  await ApiHelper.call('read_class', path);
    var list_data = []
    for(item of classData.files){
        list_data.push(Utils.generateFileId(item.filePath))
    }
    console.log(list_data)
    for(file_item of [...ctn.children,...list_ctn.children]){
        console.log(file_item.id)
        if(list_data.includes(file_item.id)){
            file_item.style.display = "flex"
        }else{
            file_item.style.display = "none"
        }
    }
}
let last_group = "全部"
async function render_class_btn(){
    var classData =  await ApiHelper.call('read_class', '');
    class_btn_bar.innerHTML = '';
    var class_names = ["全部"]
    for(item in classData.data){
        class_names.push(item)
    }
    for(let index of class_names){
        let btn = document.createElement("button")
        btn.classList.add("class_bar_btn")
        if(index == last_group){
            btn.classList.add("active")
        }
        btn.innerHTML = `<span id="class_title">${index}</span>`
        btn.onclick = function(){ 
            change_class(index)
        }
        btn.addEventListener("contextmenu",async function(e) {
            e.preventDefault();
            var rs = await showFileSelectionDialog(index)
            if(rs && rs.files_data.length > 0){
                if(index!=rs.title){
                    await ApiHelper.call("remove_class",index)
                }
                await ApiHelper.call('add_class', rs.files_data ,rs.title);
                change_class(index)
            }
            render_class_btn()
        });
        btn.id = index;
        class_btn_bar.appendChild(btn);
    }
    let add_btn = document.createElement("button")
    add_btn.classList.add("class_bar_btn")
    add_btn.onclick = function(){ 
        add_class()
    }
    add_btn.innerHTML = `<span id="class_title">+新建分类</span>`
    add_btn.id = "class_bar_btn"
    class_btn_bar.appendChild(add_btn);
    fit_btnBar()
}
async function change_class(title){
    for(let e of class_btn_bar.children){
        if(e.id==title){
            e.className = "class_bar_btn active";
        }else{
            e.className = "class_bar_btn"
        }
    }
    class_filter(title);
    last_group = title;
}
async function delete_class(cid){
    await ApiHelper.call("remove_class",cid)
    render_class_btn()
    last_group = "全部"
    class_filter(last_group)
}
async function fit_btnBar() {
    const main = document.getElementById("main")
    const box1 = document.getElementById("box1")
    const box2 = document.getElementById("box2")
    const box3 = document.getElementById("class_bar")
    box1.style.height=main.offsetWidth+"px"
    box1.style.width = (box2.offsetHeight+20)+"px"
    box2.style.marginLeft = box2.offsetHeight+"px"
    box3.style.marginTop = box3.offsetHeight+"px"
    if(box1.style.display == "none"){
        document.getElementById("filesContainer").style.marginTop = "0px"
        document.getElementById("filesListContainer").style.marginTop = "0px"
    }else{
        document.getElementById("filesContainer").style.marginTop = -(main.offsetWidth-(box2.offsetHeight-20))+"px"
        document.getElementById("filesListContainer").style.marginTop = -(main.offsetWidth-(box2.offsetHeight-20))+"px"
    }
}
document.getElementById("class_bar_btn").addEventListener("click", add_class);

let enter_click = false;
window.addEventListener("keydown", function(event) {
    if (event.key === 'Enter') {
        for(let e of [...document.getElementById("filesContainer").children,...document.getElementById("filesListContainer").children]){
            if(e.style.display != "none" && enter_click==false){
                enter_click = true
                e.click()
                setTimeout(function () {
                    enter_click = false
                }, 3000);
                break
            }
        }
    }
});