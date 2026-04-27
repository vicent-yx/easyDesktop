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
        'zip': '压缩文件', 'exe': '应用程序',
        'SteamGame':"Steam游戏",
        'lnk': "快捷方式",
    },

    THEME_PATHS: {
        "dark": "/theme/dark.css",
        "light": "/theme/light.css",
        "zzz": "/theme/zzz.css"
    },

    CLICK_DELAY: 100,
    REMIND_DURATION: 1000,
    ERROR_DISPLAY_TIME: 5000
};
const block="block"
// ========== 显示模式管理 ==========
const DisplayModeManager = {
    mode:"grid",
    btn:document.getElementById("displayToggleBtn"),
    async toggleDisplayMode(){
        if (this.mode == "grid") {
            this.list_view()
            await ApiHelper.updateConfig("view", "list");
        } else {
            this.grid_view()
            await ApiHelper.updateConfig("view", "block");
        }
    },
    async list_view(){
        this.mode = "list";
        this.btn.innerHTML = '<i class="fas fa-list"></i>';
        EventManager.switchToListView();
    },
    async grid_view(){
        this.mode = "grid";
        this.btn.innerHTML = '<i class="fas fa-th-large"></i>';
        EventManager.switchToGridView()
    }
}

// ========== 工具函数模块 ==========
const Utils = {
    /**
     * UIBox Display Change
     */
    async uiBoxDisplayChange(uiBox, display,ani=true) {
        if (uiBox) {
            
            if (ani) {
                if(['block','flex'].includes(display))uiBox.style.display = display
                if(uiBox.children.length==1){
                    uiBox = uiBox.children[0]
                }
                uiBox.classList.add(['block','flex'].includes(display) ? 'fade-in-up' : 'fade-out-up');
                await new Promise(resolve => setTimeout(resolve, 300));
                uiBox.classList.remove(['block','flex'].includes(display) ? 'fade-in-up' : 'fade-out-up');
                if(['none'].includes(display))uiBox.style.display = display
            }else{
                uiBox.style.display = display;

            }
        }
    },
    /**
     * 获取文件类型显示名称
     */
    getFileType(fileName, fileType) {
        if (fileType == '文件夹') return '文件夹';
        if (fileType == 'SteamGame') return 'Steam游戏';
        // console.log(fileType)

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
    filter_data:[],
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
        var result = await window.pywebview.api[method](...args);
        return result;
    },

    async getConfig() {
        return await this.call('get_config');
    },

    async updateConfig(key, value) {
        return await this.call('update_config', key, value);
    },

    async getFileInfo(path,quick=true) {
        var data = await this.call('get_fileinfo', path,quick);
        AppState.filter_data = data["filter_data"];
        return data;
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
    },

    async cleanTemp() {
        await this.call('clean_temp');
        UIUtils.showMessage("缓存清理完成",false)
    },
};

// ========== UI工具类 ==========
const loadingUI = {
    wait:{},
    closeList:[],
    closeAll(){
        for(var i of this.closeList){
            i()
        }
    },
    showLoading(container){
        var wid = setTimeout(()=>{
            var close_func = this.loading_action(container)
            this.closeList.push(close_func);
        },500)
        this.wait[container.id] = wid;
    },
    sets(area,view){
        if(area=="items_ctn"){
            if(view==true){
                this.showLoading(DOMCache.get("filesContainer"))
                this.showLoading(DOMCache.get("filesListContainer"))
            }else{
                this.clearLoading(DOMCache.get("filesContainer"))
                this.clearLoading(DOMCache.get("filesListContainer"))
            }
        }
    },
    loading_action(container) {
        if(container.children.length>0){
            return function hideLoading() {};
        }
        // 确保容器有定位上下文，以便内部绝对定位生效
        if (getComputedStyle(container).position === 'static') {
            container.style.position = 'relative';
        }
        container.style.minHeight = `${window.innerHeight-container.getBoundingClientRect().top}px`;
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        `;
        // 创建内容包裹层（用于转圈和文字）
        const content = document.createElement('div');
        content.style.cssText = `
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: system-ui, -apple-system, sans-serif;
            color: #2196F3;
        `;

        // 创建转圈元素（使用CSS动画）
        const spinner = document.createElement('div');
        spinner.style.cssText = `
            width: 40px;
            height: 40px;
            border: 4px solid rgba(0, 0, 0, 0.1);
            border-left-color: #007bff;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-bottom: 12px;
        `;

        // 创建文字元素
        const text = document.createElement('div');
        text.textContent = '加载中...';
        text.style.cssText = `
            font-size: 14px;
            font-weight: 500;
            letter-spacing: 0.5px;
        `;

        // 组装结构
        content.appendChild(spinner);
        content.appendChild(text);
        overlay.appendChild(content);
        container.appendChild(overlay);

        // 注入旋转动画的keyframes（仅注入一次）
        if (!document.getElementById('loading-spinner-style')) {
            const style = document.createElement('style');
            style.id = 'loading-spinner-style';
            style.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            `;
            document.head.appendChild(style);
        }

        // 返回一个移除加载提示的函数，方便调用者控制隐藏
        return function hideLoading() {
            if (overlay.parentNode === container) {
            container.removeChild(overlay);
            }
        };
    },
    clearLoading(container){
        container.style.minHeight = ""
        clearTimeout(this.wait[container.id])
        this.closeAll()
    },
}
const UIUtils = {
    showMessage(message,isErr=true) {
        const errorBox = document.createElement('div');
        Object.assign(errorBox.style, {
            position: 'fixed',
            top: '-100px',
            left: '50%',
            transform: 'translateX(-50%)',
            padding: '20px 30px',
            backgroundColor: isErr?'#ff4d4d':'#2196F3',
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
const DialogManager = {
    unlockTimer: null,
    unlockDelay: 150,

    lockWindowVisibility() {
        if (this.unlockTimer !== null) {
            clearTimeout(this.unlockTimer);
            this.unlockTimer = null;
        }
        ApiHelper.call('lock_window_visibility');
    },

    releaseWindowVisibility(delay = this.unlockDelay) {
        if (this.unlockTimer !== null) {
            clearTimeout(this.unlockTimer);
        }
        this.unlockTimer = setTimeout(() => {
            this.unlockTimer = null;
            ApiHelper.call('unlock_window_visibility');
        }, delay);
    }
};

class FileRenderer {
    constructor() {
        this.gridContainer = DOMCache.get('filesContainer');
        this.listContainer = DOMCache.get('filesListContainer');
    }
    async changeClass_ani_state(t,class_name){
        if(t==true){
            this.gridContainer.classList.add(class_name);
            this.listContainer.classList.add(class_name);
        }else{
            this.gridContainer.classList.remove(class_name);
            this.listContainer.classList.remove(class_name);
        }
    }

    /**
     * 渲染文件列表
     */
    async render(files,target_ctn=null,ani=true) {
        this.clearContainers(target_ctn);

        // if (!files || files.length === 0) {
        //     this.setEmptyState();
        //     return;
        // }
        for(var file of files){
            if(target_ctn=="grid" || target_ctn==null)await this.renderGridItem(file);
            if(target_ctn=="list" || target_ctn==null)await this.renderListItem(file);
        }
        if(ani==true)this.changeClass_ani_state(true,"fade-in-up")
        if(ani==true)await new Promise(resolve => setTimeout(resolve, 300));
        if(ani==true)this.changeClass_ani_state(false,"fade-in-up")
        image_preview()
        loadingUI.sets("items_ctn",false)
    }

    clearContainers(target_ctn) {
        if(target_ctn=="grid" || target_ctn==null)this.gridContainer.innerHTML = '';
        if(target_ctn=="list" || target_ctn==null)this.listContainer.innerHTML = '';
    }

    // setEmptyState() {
    //     this.gridContainer.style.minHeight = "75vh";
    //     this.listContainer.style.minHeight = "75vh";
    // }
    renderGroupIcon(isGrid,file){
        // 2x2 宫格图标
        let gridHtml = `<div class="group-icon-grid" ${isGrid?'':'style="width: 40px;height: 40px;margin-bottom: 0px;margin-left:1.5%"'}>`;
        for (let i = 0; i < 4; i++) {
            if (file.groupIcons && file.groupIcons[i]) {
                gridHtml += `<img draggable="false" src="${file.groupIcons[i]}" alt="">`;
            } else {
                gridHtml += '<div class="group-icon-empty"></div>';
            }
        }
        gridHtml += '</div>';
        return gridHtml;
    }

    createFileElement = async function(file, isGrid = true) {
        const element = document.createElement('div');
        element.draggable = true;
        element.dataset.is_cl = file.cl;
        element.id = Utils.generateFileId(file.filePath);
        element.dataset.list_index = file.index;

        // 组项目特殊渲染
        if (file.isGroup) {
            element.className = isGrid ? 'file-item file-group-item' : 'file-list-item file-group-item';
            element.dataset.group_id = file.groupId;
            const nameClass = isGrid ? 'file-name' : 'file-list-name';
            const typeClass = isGrid ? 'file-type' : 'file-list-type';

            let gridHtml = this.renderGroupIcon(isGrid,file);
            element.innerHTML = `
                ${gridHtml}
                <span draggable="false" ${isGrid==true?'':'style="margin-left:12px;"'} class="${nameClass}">${file.fileName}</span>
                <span draggable="false" class="${typeClass}">应用组</span>
                ${isGrid==false?'':`<div class="group-badge">${file.itemCount}</div>`}
            `;
            this.attachGroupEvents(element, file);
            return element;
        }

        element.className = isGrid ? 'file-item' : 'file-list-item';

        const fileType = Utils.getFileType(file.file, file.fileType);
        const iconClass = isGrid ? 'file-icon' : 'file-list-icon';
        const nameClass = isGrid ? 'file-name' : 'file-list-name';
        const typeClass = isGrid ? 'file-type' : 'file-list-type';

        element.innerHTML = `
            <img draggable = false src="${file.ico}" alt="${file.fileName}" class="${iconClass}">
            <span draggable = false class="${nameClass}">${file.fileName}</span>
            <span draggable = false class="${typeClass}">${fileType}</span>
        `;
        const cl_e = document.createElement("div")

        cl_e.className = isGrid ? 'file-cl' : 'file-list-cl';;
        if(file.cl==false){
            if(document.getElementById("theme_css").href.includes("light")==true){
                cl_e.innerHTML="<img draggable = false src='./resources/imgs/cl.png'>"
            }else{
                cl_e.innerHTML="<img draggable = false src='./resources/imgs/cl_w.png'>"
            }

        }else{
            cl_e.innerHTML="<img draggable = false src='./resources/imgs/cl-active.png'>"
            cl_e.style.display="block"
        }

        cl_e.onclick=(event) => {event.stopPropagation();change_cl_state(file.filePath, file.cl)};
        cl_e.ondblclick = (event) => {event.stopPropagation();}
        element.insertBefore(cl_e, element.firstChild);
        element.cl = cl_e;

        this.attachFileEvents(element, file);
        return element;
    }

    async renderGridItem(file) {
        const element = await this.createFileElement(file, true);
        this.gridContainer.appendChild(element);
    }

    async renderListItem(file) {
        const element = await this.createFileElement(file, false);
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
            e.preventDefault();
            if(file.sysApp!=undefined)return
            // 组视图内由 showGroupItemContextMenu 接管，跳过普通菜单
            if (GroupManager.currentOpenGroup !== null) return;
            MenuManager.showContextMenu(e, file);
        });
    }

    handleFileAction(file, isDoubleClick) {
        if (file.isGroup) {
            GroupManager.openGroup(file.groupId, file.fileName);
            return;
        }
        // 从组视图内打开文件时，先关闭组视图（恢复 autoClose）
        if (GroupManager.currentOpenGroup !== null) {
            GroupManager.closeGroup();
        }
        if (file.fileType === '文件夹') {
            if (isDoubleClick) {
                if(config["dbc_action"]=="1"){
                    ApiHelper.openFile(file.filePath);
                }else{
                    NavigationManager.navigateTo(file.filePath);
                }
            } else {
                NavigationManager.navigateTo(file.filePath);
            }
        } else if (file.sysApp) {
            ApiHelper.call('open_sysApp', file.filePath);
        } else {
            if (isDoubleClick) {
                if(config["dbc_action"]=="1"){
                    ApiHelper.showFile(file.filePath);
                }else{
                    ApiHelper.openFile(file.filePath);
                }
            } else {
                ApiHelper.openFile(file.filePath);
            }
        }
    }

    attachGroupEvents(element, file) {
        // 单击打开组视图
        element.addEventListener('click', () => {
            DOMCache.get("search_input").value = "";
            AppState.timer = setTimeout(() => {
                if (AppState.db_click_action) {
                    AppState.db_click_action = false;
                    return;
                }
                GroupManager.openGroup(file.groupId, file.fileName);
            }, CONSTANTS.CLICK_DELAY);
        });

        // 双击也打开组
        element.addEventListener('dblclick', () => {
            AppState.db_click_action = true;
            clearTimeout(AppState.timer);
            GroupManager.openGroup(file.groupId, file.fileName);
        });

        // 右键菜单
        element.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            GroupManager.showGroupContextMenu(e, file);
        });
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
        // contextMenu.style.display = 'block';
        Utils.uiBoxDisplayChange(contextMenu,block,true)
        var scale_rate = config["scale"] / 100
        console.log(e.pageX / scale_rate)
        console.log((window.innerWidth-contextMenu.offsetWidth)/scale_rate)
        if((e.pageX / scale_rate)>((window.innerWidth-contextMenu.offsetWidth)/scale_rate)){
            contextMenu.style.left = `${(window.innerWidth - contextMenu.offsetWidth) / scale_rate}px`;
        }else{
            contextMenu.style.left = `${e.pageX / scale_rate}px`;
        }
        if((e.pageY / scale_rate)>((window.innerHeight-contextMenu.offsetHeight)/scale_rate)){
            contextMenu.style.top = `${(window.innerHeight - contextMenu.offsetHeight) / scale_rate}px`;
        }else{
            contextMenu.style.top = `${e.pageY / scale_rate}px`;
        }

        this.adjustMenuPosition(contextMenu, e);

        if(file.edit_ico!=undefined){
            DOMCache.get("edit_icon_btn").innerText="恢复默认图标"
        }else{
            DOMCache.get("edit_icon_btn").innerText="自定义图标"
        }
        // 在普通文件右键菜单中显示"添加到组"，隐藏"从组中移除"
        if(config["df_dir"]==AppState.currentPath){
            const addToGroupItem = DOMCache.get('menuAddToGroup');
            if (addToGroupItem) addToGroupItem.style.display = 'flex';
            const removeItem = document.getElementById('menuGroupRemoveItem');
            if (removeItem) removeItem.style.display = 'none';
        }else{
            addToGroupItem.style.display = 'none'
            removeItem.style.display = 'none'
        }
        
        disableScroll();
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
            contextMenu.style.zIndex = '';  // 恢复默认 z-index
        }
        enableScroll();
    },

    hideAllMenus() {
        this.hideContextMenu();
        DOMCache.get('blankMenu').style.display = 'none';
        const groupMenu = DOMCache.get('groupContextMenu');
        if (groupMenu) groupMenu.style.display = 'none';
        const groupSubMenu = DOMCache.get('groupSubMenu');
        if (groupSubMenu) groupSubMenu.style.display = 'none';
        // 隐藏"从组中移除"菜单项
        const removeItem = document.getElementById('menuGroupRemoveItem');
        if (removeItem) removeItem.style.display = 'none';
        enableScroll();
    }
};

// ========== 导航管理器 ==========
const NavigationManager = {
    async navigateTo(path) {
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
        DOMCache.get("filesContainer").innerHTML = '';
        DOMCache.get("filesListContainer").innerHTML = '';
        loadingUI.sets("items_ctn",true)
        AppState.addToHistory(path);
        await this.updateBreadcrumb(path || '/');

        const result = await ApiHelper.getFileInfo(path);
        AppState.setFiles(result.data);
        DOMCache.get("content_box").scrollTo({
            top: 0,
            behavior: 'smooth',
        })
        await fileRenderer.render(result.data);
        window.scrollTo(0, 0);
        loadingUI.sets("items_ctn",false)
    },

    async refreshCurrentPath(quick_update=true,ani=true) {
        return new Promise(async (resolve) => { 
            console.log(quick_update)
            loadingUI.sets("items_ctn",true)
            const result = await ApiHelper.getFileInfo(AppState.currentPath,quick_update);
            // if(result.same==true)return;
            DOMCache.get("search_input").value=""
            AppState.setFiles(result.data);
            loadingUI.sets("items_ctn",false)

            await fileRenderer.render(result.data,null,ani);
            if(last_group!="" || last_group!="全部"){
                change_class(last_group)
            }

            console.log(result)
            resolve(true);
        });
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
    async performSearch(searchKey=null,render=true) {
        let key = ""
        if(searchKey==null){
            key = DOMCache.get("search_input").value;
        }else{
            key = searchKey;
        }

        if (key === "") {
            await fileRenderer.render(AppState.files_data,null,false);
            return;
        }

        const groups = AppState.files_data.filter(f => f.isGroup);
        let group_data = []
        for (const group of groups) {
            try {
                const contents = await ApiHelper.call('get_group_contents', group.groupId);
                if (contents.data) {
                    contents.data.forEach(file => {
                        group_data.push(file);
                    });
                }
            } catch (e) { /* 忽略 */ }
        }
        const pyData = await ApiHelper.loadSearchIndex([...AppState.files_data,...group_data]);
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

        // 同时搜索组内文件
        for (const group of groups) {
            if (outData.find(f => f.filePath === group.filePath)) continue;
            try {
                const contents = await ApiHelper.call('get_group_contents', group.groupId);
                if (contents.data) {
                    contents.data.forEach(file => {
                        if(dealKey.have_cn){
                            // console.log(file)
                            if (Utils.contains(file.fileName, dealKey.origin) ||
                                Utils.contains(file.fileName, dealKey.fix)) {
                                outData.push(file);
                            }
                        }else{
                            const fileData = pyData[file.fileName];
                            if (fileData && (
                                Utils.contains(fileData.sxpy, key) ||
                                Utils.contains(fileData.py, key)
                            )) {
                                outData.push(file);
                            }
                        }
                        
                    });
                }
            } catch (e) { /* 忽略 */ }
        }

        if(render==true)await fileRenderer.render(outData,null,false);
        return outData;
    }
};

// ========== 主题管理器 ==========
const ThemeManager = {
    now_theme: 'light',
    async applyBackgroundSettings(config) {
        if(config.bgType!="1")return;
        console.log("applyBackgroundSettings")
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
        console.log(result)
        await NavigationManager.refreshCurrentPath(false,false);

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

// ========== 应用组管理器 ==========
const groupContainer = document.querySelector('.group-view-container');
const GroupManager = {
    currentOpenGroup: null,
    currentGroupName: '',
    isDialogActive: false,  // 标记组对话框是否活跃，防止原始重命名逻辑触发

    async openGroup(groupId, groupName) {
        this.currentOpenGroup = groupId;
        this.currentGroupName = groupName || '';
        const overlay = DOMCache.get('groupViewOverlay');
        const title = DOMCache.get('groupViewTitle');
        const container = DOMCache.get('groupFilesContainer');

        title.textContent = groupName || '应用组';
        container.innerHTML = '<div class="loading-indicator">加载中...</div>';
        // overlay.style.display = 'flex';
        Utils.uiBoxDisplayChange(overlay, "flex",true)
        // UIUtils.disableScroll();

        try {
            const result = await ApiHelper.call('get_group_contents', groupId);
            container.innerHTML = '';
            if (result.data && result.data.length > 0) {
                for (const file of result.data) {
                    file.index = 0;
                    const el = await fileRenderer.createFileElement(file, true);
                    el.dataset.file_path = file.filePath;
                    el.dataset.gid = groupId;
                    // 为组内文件添加"从组中移除"的右键菜单
                    el.addEventListener('contextmenu', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        this.showGroupItemContextMenu(e, file, groupId);
                    });
                    // 拖拽到组窗口外 = 移出组
                    // el.addEventListener('dragend', (e) => {
                    //     const rect = groupContainer.getBoundingClientRect();
                    //     if (e.clientX < rect.left || e.clientX > rect.right ||
                    //         e.clientY < rect.top || e.clientY > rect.bottom) {
                    //         const fp = el.dataset.file_path;
                    //         if (fp) this.removeFromGroup(groupId, fp);
                    //     }
                    // });
                    container.appendChild(el);
                }
            } else {
                container.innerHTML = '<div class="loading-indicator">组内没有文件</div>';
            }
        } catch (err) {
            console.error('加载组内容失败:', err);
            container.innerHTML = '<div class="loading-indicator">加载失败</div>';
        }
    },

    closeGroup() {
        const overlay = DOMCache.get('groupViewOverlay');
        overlay.style.display = 'none';
        this.currentOpenGroup = null;
        UIUtils.enableScroll();
    },

    async createGroup() {
        this.isDialogActive = true;
        DialogManager.lockWindowVisibility();
        const renameOverlay = DOMCache.get('renameOverlay');
        const renameInput = DOMCache.get('renameInput');
        const h3 = renameOverlay.querySelector('h3');
        const origTitle = h3.textContent;
        h3.textContent = '新建组';
        renameInput.value = '';
        // renameOverlay.style.display = 'flex';
        Utils.uiBoxDisplayChange(renameOverlay, "flex",true)
        renameInput.focus();

        const confirmBtn = DOMCache.get('renameConfirm');
        const handler = async () => {
            const name = renameInput.value.trim();
            if (!name) return;
            var r = await ApiHelper.call('create_group', name);
            renameOverlay.style.display = 'none';
            h3.textContent = origTitle;
            confirmBtn.removeEventListener('click', handler);
            cancelBtn.removeEventListener('click', cancelHandler);
            this.isDialogActive = false;
            DialogManager.releaseWindowVisibility();
            FileOperationManager.refreshAndRemindFile({file:"__group__:"+r.groupId})
        };
        confirmBtn.addEventListener('click', handler);

        const cancelBtn = DOMCache.get('renameCancel');
        const cancelHandler = () => {
            h3.textContent = origTitle;
            confirmBtn.removeEventListener('click', handler);
            cancelBtn.removeEventListener('click', cancelHandler);
            this.isDialogActive = false;
        };
        cancelBtn.addEventListener('click', cancelHandler);
    },

    async editGroupOrder() {
        const ctn = DOMCache.get('groupFilesContainer');
        var paths = [];
        for(let p of ctn.children){
            paths.push(p.dataset.file_path)
        }
        await ApiHelper.call('edit_group_order', this.currentOpenGroup, paths);
        NavigationManager.refreshCurrentPath();
    },

    async renameGroup(groupId) {
        this.isDialogActive = true;
        DialogManager.lockWindowVisibility();
        const renameOverlay = DOMCache.get('renameOverlay');
        const renameInput = DOMCache.get('renameInput');
        const h3 = renameOverlay.querySelector('h3');
        const origTitle = h3.textContent;
        h3.textContent = '重命名组';
        renameInput.value = this.currentGroupName;
        // renameOverlay.style.display = 'flex';
        Utils.uiBoxDisplayChange(renameOverlay, "flex",true)
        renameInput.focus();

        const confirmBtn = DOMCache.get('renameConfirm');
        const handler = async () => {
            const name = renameInput.value.trim();
            if (!name) return;
            await ApiHelper.call('rename_group', groupId, name);
            renameOverlay.style.display = 'none';
            h3.textContent = origTitle;
            confirmBtn.removeEventListener('click', handler);
            cancelBtn.removeEventListener('click', cancelHandler);
            this.isDialogActive = false;
            DialogManager.releaseWindowVisibility();
            NavigationManager.refreshCurrentPath();
        };
        confirmBtn.addEventListener('click', handler);

        const cancelBtn = DOMCache.get('renameCancel');
        const cancelHandler = () => {
            h3.textContent = origTitle;
            confirmBtn.removeEventListener('click', handler);
            cancelBtn.removeEventListener('click', cancelHandler);
            this.isDialogActive = false;
        };
        cancelBtn.addEventListener('click', cancelHandler);
    },

    async deleteGroup(groupId) {
        return this.confirmAndDeleteGroup(groupId, this.currentGroupName);
    },

    async confirmAndDeleteGroup(groupId, groupName = '') {
        const overlay = DOMCache.get('groupDeleteConfirm');
        const groupDeleteName = DOMCache.get('groupDeleteName');
        const cancelBtn = DOMCache.get('groupDeleteCancel');
        const confirmBtn = DOMCache.get('groupDeleteConfirmBtn');

        groupDeleteName.textContent = groupName || this.currentGroupName || '未命名应用组';
        // overlay.style.display = 'flex';
        Utils.uiBoxDisplayChange(overlay, "flex",true)
        UIUtils.disableScroll();
        DialogManager.lockWindowVisibility();

        const confirmed = await new Promise((resolve) => {
            let settled = false;

            const cleanup = (result) => {
                if (settled) return;
                settled = true;
                overlay.style.display = 'none';
                cancelBtn.removeEventListener('click', handleCancel);
                confirmBtn.removeEventListener('click', handleConfirm);
                overlay.removeEventListener('click', handleOverlayClick);
                document.removeEventListener('keydown', handleKeyDown, true);
                if (DOMCache.get('groupViewOverlay').style.display !== 'flex') {
                    UIUtils.enableScroll();
                }
                DialogManager.releaseWindowVisibility();
                resolve(result);
            };

            const handleCancel = () => cleanup(false);
            const handleConfirm = () => cleanup(true);
            const handleOverlayClick = (e) => {
                if (e.target.id === 'groupDeleteConfirm') {
                    cleanup(false);
                }
            };
            const handleKeyDown = (e) => {
                if (overlay.style.display !== 'flex') return;
                if (e.key === 'Enter') {
                    e.preventDefault();
                    e.stopImmediatePropagation();
                    cleanup(true);
                    return;
                }
                if (e.key === 'Escape') {
                    e.preventDefault();
                    e.stopImmediatePropagation();
                    cleanup(false);
                }
            };

            cancelBtn.addEventListener('click', handleCancel);
            confirmBtn.addEventListener('click', handleConfirm);
            overlay.addEventListener('click', handleOverlayClick);
            document.addEventListener('keydown', handleKeyDown, true);
            confirmBtn.focus();
        });

        if (!confirmed) return;
        await ApiHelper.call('delete_group', groupId);
        this.closeGroup();
        NavigationManager.refreshCurrentPath();
    },

    async addToGroup(groupId, filePaths) {
        await ApiHelper.call('add_to_group', groupId, filePaths);
        await NavigationManager.refreshCurrentPath();
        UIUtils.showMessage("已添加到组",false)
    },

    async removeFromGroup(groupId, filePath) {
        await ApiHelper.call('remove_from_group', groupId, filePath);
        // 如果组视图是打开的，刷新组视图
        if (this.currentOpenGroup === groupId) {
            this.openGroup(groupId, this.currentGroupName);
        }
        NavigationManager.refreshCurrentPath();
    },

    showGroupContextMenu(e, file) {
        MenuManager.hideAllMenus();
        const menu = DOMCache.get('groupContextMenu');
        // menu.style.display = 'block';
        Utils.uiBoxDisplayChange(menu,block,true)
        menu.style.left = `${e.pageX}px`;
        menu.style.top = `${e.pageY}px`;

        // 绑定事件
        DOMCache.get('menuGroupOpen').onclick = () => {
            menu.style.display = 'none';
            this.openGroup(file.groupId, file.fileName);
        };
        DOMCache.get('menuGroupRename').onclick = () => {
            menu.style.display = 'none';
            this.currentGroupName = file.fileName;
            this.renameGroup(file.groupId);
        };
        DOMCache.get('menuGroupDelete').onclick = () => {
            menu.style.display = 'none';
            this.currentGroupName = file.fileName;
            this.confirmAndDeleteGroup(file.groupId, file.fileName);
        };

        disableScroll();
    },

    showGroupItemContextMenu(e, file, groupId) {
        // 复用主右键菜单但添加"从组中移除"选项
        MenuManager.hideAllMenus();
        AppState.setSelectedFile(file);

        const contextMenu = DOMCache.get('contextMenu');
        // contextMenu.style.display = 'block';
        Utils.uiBoxDisplayChange(contextMenu,block,true)
        // 提升 z-index 使右键菜单显示在组视图 overlay 之上
        contextMenu.style.zIndex = '4000';

        // 缩放感知定位 + 边界检测
        const scale = document.body.style.zoom ? parseFloat(document.body.style.zoom) : 1;
        let posX = e.pageX / scale;
        let posY = e.pageY / scale;
        if (posX > (window.innerWidth - contextMenu.offsetWidth) / scale) {
            posX = (window.innerWidth - contextMenu.offsetWidth) / scale;
        }
        if (posY > (window.innerHeight - contextMenu.offsetHeight) / scale) {
            posY = (window.innerHeight - contextMenu.offsetHeight) / scale;
        }
        contextMenu.style.left = `${posX}px`;
        contextMenu.style.top = `${posY}px`;

        // 隐藏"添加到组"，显示"从组中移除"
        const addToGroupItem = DOMCache.get('menuAddToGroup');
        if (addToGroupItem) addToGroupItem.style.display = 'none';

        // 临时添加"从组中移除"菜单项
        let removeItem = document.getElementById('menuGroupRemoveItem');
        if (!removeItem) {
            removeItem = document.createElement('div');
            removeItem.className = 'context-menu-item group-remove';
            removeItem.id = 'menuGroupRemoveItem';
            removeItem.innerHTML = '<i class="fas fa-minus-circle"></i><span>从组中移除</span>';
            contextMenu.appendChild(removeItem);
        }
        // removeItem.style.display = 'flex';
        Utils.uiBoxDisplayChange(removeItem,"flex",false)
        removeItem.onclick = () => {
            this.removeFromGroup(groupId, file.filePath);
            MenuManager.hideContextMenu();
        };

        disableScroll();
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
        DOMCache.get('displayToggleBtn').addEventListener('click', async () => {
            DisplayModeManager.toggleDisplayMode();
        });

        // DOMCache.get('listViewBtn').addEventListener('click', async () => {
        //     this.switchToListView();
        //     await ApiHelper.updateConfig("view", "list");
        // });
    },

    switchToGridView() {
        DOMCache.get('filesContainer').style.display = 'grid';
        DOMCache.get('filesListContainer').style.display = 'none';
        // DOMCache.get('gridViewBtn').classList.add('active');
        // DOMCache.get('listViewBtn').classList.remove('active');
    },

    switchToListView() {
        DOMCache.get('filesContainer').style.display = 'none';
        DOMCache.get('filesListContainer').style.display = 'block';
        // DOMCache.get('gridViewBtn').classList.remove('active');
        // DOMCache.get('listViewBtn').classList.add('active');
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
            // 从组视图内通过右键菜单打开文件时，先关闭组视图
            if (GroupManager.currentOpenGroup !== null) {
                GroupManager.closeGroup();
            }
            if (AppState.selectedFile.game) {
                ApiHelper.call('open_mhyGame', AppState.selectedFile.filePath, AppState.selectedFile.game);
            } else {
                ApiHelper.openFile(AppState.selectedFile.filePath);
            }
            MenuManager.hideContextMenu();
        });
        DOMCache.get('menuOpenLocation').addEventListener('click',async () => {
            if (AppState.selectedFile.realPath!== undefined) {
                ApiHelper.showFile(AppState.selectedFile.realPath);
            } else {
                ApiHelper.showFile(AppState.selectedFile.filePath);
            }
            MenuManager.hideContextMenu();
        });

        DOMCache.get('menuCopy').addEventListener('click', () => {
            ApiHelper.copyFile(AppState.selectedFile.filePath);
            MenuManager.hideContextMenu();
        });

        DOMCache.get('menuRename').addEventListener('click', this.showRenameDialog);
        DOMCache.get('menuDelete').addEventListener('click', this.showDeleteConfirm);
        DOMCache.get("menuCustomIcon").addEventListener('click',this.setIcon)

        // 添加到组 - 鼠标悬停时展示子菜单
        DOMCache.get('menuAddToGroup').addEventListener('mouseenter', async function() {
            const subMenu = DOMCache.get('groupSubMenu');
            const result = await ApiHelper.call('get_groups');
            const groups = result.data || {};
            const keys = Object.keys(groups);

            subMenu.innerHTML = '';
            if (keys.length === 0) {
                const emptyItem = document.createElement('div');
                emptyItem.className = 'context-menu-item';
                emptyItem.innerHTML = '<span style="color:#999">暂无组，请先新建</span>';
                subMenu.appendChild(emptyItem);
            } else {
                keys.forEach(gid => {
                    const item = document.createElement('div');
                    item.className = 'context-menu-item';
                    item.innerHTML = `<i class="fas fa-layer-group"></i><span>${groups[gid].name}</span>`;
                    item.addEventListener('click', async () => {
                        await GroupManager.addToGroup(gid, [AppState.selectedFile.filePath]);
                        MenuManager.hideAllMenus();
                    });
                    subMenu.appendChild(item);
                });
            }

            // 定位子菜单到"添加到组"右侧，若超出窗口则放左侧
            const parentRect = DOMCache.get('menuAddToGroup').getBoundingClientRect();
            const contextMenuRect = DOMCache.get('contextMenu').getBoundingClientRect();
            const scale = document.body.style.zoom ? parseFloat(document.body.style.zoom) : 1;
            subMenu.style.display = 'block';
            const subMenuWidth = subMenu.offsetWidth;
            if ((parentRect.right + subMenuWidth) > window.innerWidth) {
                subMenu.style.left = ((contextMenuRect.left - subMenuWidth) / scale) + 'px';
            } else {
                subMenu.style.left = (parentRect.right / scale) + 'px';
            }
            subMenu.style.top = (parentRect.top / scale) + 'px';
        });
        DOMCache.get('menuAddToGroup').addEventListener('mouseleave', function(e) {
            // 延迟隐藏，允许鼠标移到子菜单上
            setTimeout(() => {
                const subMenu = DOMCache.get('groupSubMenu');
                if (!subMenu.matches(':hover')) {
                    subMenu.style.display = 'none';
                }
            }, 200);
        });

        // 空白区域右键菜单
        DOMCache.get('menuPaste').addEventListener('click', async () => {
            try {
                const result = await FileOperationManager.pasteFiles();
                if (result.success === false) {
                    UIUtils.showMessage(result.message);
                }
            } catch (error) {
                console.error('粘贴失败:', error);
            }
            DOMCache.get('blankMenu').style.display = 'none';
        });

        DOMCache.get('menuNew').addEventListener('click', () => {
            DialogManager.lockWindowVisibility();
            // DOMCache.get('newFileOverlay').style.display = 'flex';
            Utils.uiBoxDisplayChange(DOMCache.get('newFileOverlay'), 'flex',true);
            // DOMCache.get('blankMenu').style.display = 'none';
            Utils.uiBoxDisplayChange(DOMCache.get('blankMenu'),"none", false);
        });

        DOMCache.get('menuNewGroup').addEventListener('click', () => {
            // DOMCache.get('blankMenu').style.display = 'none';
            Utils.uiBoxDisplayChange(DOMCache.get('blankMenu'),"none", false);
            GroupManager.createGroup();
        });

        // 组视图关闭
        DOMCache.get('closeGroupView').addEventListener('click', () => {
            GroupManager.closeGroup();
        });
        DOMCache.get('groupViewOverlay').addEventListener('click', (e) => {
            if (e.target.id === 'groupViewOverlay') {
                GroupManager.closeGroup();
            }
        });
    },

    initDialogEvents() {
        // 重命名对话框
        DOMCache.get('renameCancel').addEventListener('click', () => {
            DialogManager.releaseWindowVisibility();
            DOMCache.get('renameOverlay').style.display = 'none';
            AppState.dealing = false;
        });

        DOMCache.get('renameConfirm').addEventListener('click', async () => {
            // 组操作使用对话框时跳过文件重命名逻辑
            if (GroupManager.isDialogActive) return;
            if (AppState.dealing) return;
            AppState.dealing = true;
            try{
                const newName = DOMCache.get('renameInput').value.trim();
                if (newName) {
                    try{
                        await FileOperationManager.renameFile(AppState.selectedFile.filePath, newName);
                        DOMCache.get('renameOverlay').style.display = 'none';
                        DialogManager.releaseWindowVisibility();
                    }catch(e){
                        UIUtils.showMessage(e);
                    }
                }
            }catch(e){}
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
                UIUtils.showMessage(result.message);
            }
            DOMCache.get('deleteConfirm').style.display = 'none';
            AppState.dealing = false;
        });

        DOMCache.get('deleteConfirmBtn_r').addEventListener('click', async () => {
            AppState.dealing = true;
            const result = await FileOperationManager.removeFile(AppState.selectedFile.filePath, "rubbish");
            if (result.success === false) {
                UIUtils.showMessage(result.message);
            }
            DOMCache.get('deleteConfirm').style.display = 'none';
            AppState.dealing = false;
        });

        // 新建文件对话框
        DOMCache.get('newFileCancel').addEventListener('click', () => {
            DialogManager.releaseWindowVisibility();
            DOMCache.get('newFileOverlay').style.display = 'none';
        });

        DOMCache.get('newFileConfirm').addEventListener('click', async () => {
            const selectedType = DOMCache.get('newFileTypeSelect').value;
            if (selectedType) {
                await FileOperationManager.createNewFile(selectedType);
                DOMCache.get('newFileOverlay').style.display = 'none';
                DialogManager.releaseWindowVisibility();
            }
        });

        // 重命名输入框回车确认
        DOMCache.get('renameInput').addEventListener('keydown', (e) => {
            e.stopPropagation();
            if (e.key === 'Enter') {
                e.preventDefault();
                DOMCache.get('renameConfirm').click();
                return;
            }
            if (e.key === 'Escape') {
                e.preventDefault();
                DOMCache.get('renameCancel').click();
            }
        });
    },

    initSettingsEvents() {
        const settingsBtn = DOMCache.get('settingsBtn');
        const themePanel = DOMCache.get('themeSettingsPanel');
        const closeBtn = DOMCache.get('closeThemePanel');

        settingsBtn.addEventListener('click', () => {

            // themePanel.style.display = themePanel.style.display === 'flex' ? 'none' : 'flex';
            Utils.uiBoxDisplayChange(themePanel, themePanel.style.display === 'flex' ? 'none' : 'flex',true);
            ApiHelper.call("lock_window_visibility")
        });

        closeBtn.addEventListener('click', () => {
            UIUtils.enableScroll();
            themePanel.style.display = 'none';
            ApiHelper.call("unlock_window_visibility")
        });

        this.initToggleSettings();
        this.initThemeSettings();
        this.initBackgroundSettings();
        this.initScaleSettings();
    },

    initToggleSettings() {
        const toggles = [
            'autoStartToggle', 'fullScreenToggle', 'fdrToggle',
            'of_sToggle', 'sysappToggle',/* 'followSystemTheme',*/'imgpreToggle','blurToggle'
        ];

        const configKeys = [
            'auto_start', 'full_screen', 'fdr',
            'of_s', 'show_sysApp',/* 'follow_sys',*/'imgpre','blur_bg'
        ];

        toggles.forEach((toggleId, index) => {
            DOMCache.get(toggleId).addEventListener('change', function () {
                ApiHelper.updateConfig(configKeys[index], this.checked);
                // if (toggleId === 'themeChangeType_toggle') {
                //     EventManager.updateThemeCardInteraction(this.value == "1");
                // }
                if(toggleId === "imgpreToggle"){
                    if(this.checked==true){
                        image_preview()
                    }else{
                        preview_runing = false
                    }
                }else if(toggleId === "blurToggle"){
                    ApiHelper.call('set_blur_effect', this.checked,ThemeManager.now_theme);
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
        DOMCache.get("outPos_toggle").addEventListener('change', function () {
            ApiHelper.updateConfig('outPos', this.value);
        });
        DOMCache.get("corner_size_toggle").addEventListener('change', function () {
            ApiHelper.updateConfig('corner_size', this.value);
        });
        DOMCache.get("dbc_action_toggle").addEventListener('change', function () {
            ApiHelper.updateConfig('dbc_action', this.value);
        });
        DOMCache.get("bgType_toggle").addEventListener('change', function () {
            ApiHelper.updateConfig('bgType', this.value);
            load_bgType(this.value)
            EventManager.updateBGInteraction(this.value != "1");
        });
        DOMCache.get("themeChangeType_toggle").addEventListener('change', function () {
            ApiHelper.updateConfig('themeChangeType', this.value);
            // EventManager.updateThemeCardInteraction();
        });
    },

    initThemeSettings() {
        const themeCards = DOMCache.getAllBySelector('.theme-card');
        const followSystemToggle = DOMCache.get('followSystemTheme');

        themeCards.forEach(card => {
            card.addEventListener('click', function () {
                // if (followSystemToggle.checked) return;

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
            if (config.themeChangeType == "1") {
                const newTheme = e.matches ? 'dark' : 'light';
                load_theme(newTheme);
            }
        });
    },

    async updateThemeCardInteraction() {
        var now_config = await ApiHelper.getConfig()
        let bgState = now_config.bgType != "1";
        const themeCards = DOMCache.getAllBySelector('.theme-card');
        themeCards.forEach(card => {
            card.style.opacity = bgState ? '0.5' : '1';
            card.style.pointerEvents = bgState ? 'none' : 'auto';
        });
    },
    updateBGInteraction(state) {
        const bgtCards = DOMCache.get('bg_setting');
        for(let card of bgtCards.children){
            card.style.opacity = state ? '0.5' : '1';
            card.style.pointerEvents = state ? 'none' : 'auto';
        };
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
                    config = await ApiHelper.getConfig();
                    setTimeout(() => {
                        window.location.reload();
                        // ThemeManager.applyBackgroundSettings(config);
                    }, 500);
                }
            } catch (error) {
                console.error('设置背景图片失败:', error);
            }
            // setTimeout(() => {
            //     window.location.reload();
            // }, 500);
        });
    },

    initScaleSettings() {
        const scaleSlider = DOMCache.get('sc_slider');
        scaleSlider.addEventListener('input', function () {
            const scaleValue = this.value;
            DOMCache.get("sc_input").innerText = `缩放比例：${scaleValue}%`;
            ConfigManager.updateScale(scaleValue);
        });
        const blur_ef_input = DOMCache.get('blur_ef_input');
        blur_ef_input.addEventListener('input', function () {
            var value = this.value;
            DOMCache.get("blur_ef_input_show").innerText = `毛玻璃效果强度：${value}%`;
            ApiHelper.updateConfig("blur_effect", Math.floor(100-value));
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
                DOMCache.get("search_input").value = "";
            }
        });
    },

    initKeyboardEvents() {
        document.addEventListener('keydown', (event) => {
            if (document.activeElement.id !== 'search_input') {
                const searchInput = DOMCache.get('search_input');
                if (DOMCache.get("renameOverlay").style.display === "flex") return;
                if (DOMCache.get("groupDeleteConfirm").style.display === "flex") return;
                if(document.activeElement.id == "categoryInput") return
                if(document.getElementById("fileSelectionDialog").style.display!="none")return;
                if(window_state==false)return

                if (searchInput && !event.ctrlKey && !event.altKey && !event.metaKey && event.key.length === 1) {
                    searchInput.focus();
                }
            }
        });
    },

    initClickEvents() {
        document.addEventListener('click', (event) => {
            if(event.target.id=="menuAddToGroup")return
            try{if(event.target.parentNode.id=="menuAddToGroup")return}catch(e){}
            MenuManager.hideAllMenus();

            if (["content_box", "main"].includes(event.target.id)) {
                ApiHelper.call('close_fullscreen_window');
            }
        });
        document.addEventListener('contextmenu', (e) => {
            // this.handleBlankContextMenu(e);
            console.log(e.target)
            if(config.df_dir==AppState.currentPath){
                console.log("当前目录")
                // document.getElementById("menuNewGroup").style.display="block"
                // document.getElementById("menuAddToGroup").style.display="block"
                Utils.uiBoxDisplayChange(document.getElementById("menuNewGroup"),block,true)
                Utils.uiBoxDisplayChange(document.getElementById("menuAddToGroup"),block,false)
            }else{
                console.log("非当前目录")
                // document.getElementById("menuNewGroup").style.display="none"
                // document.getElementById("menuAddToGroup").style.display="none"
                Utils.uiBoxDisplayChange(document.getElementById("menuNewGroup"),none,true)
                Utils.uiBoxDisplayChange(document.getElementById("menuAddToGroup"),none,false)
            }
        });
        // 空白区域右键菜单
        DOMCache.getBySelector('.content_box').addEventListener('contextmenu', (e) => {
            this.handleBlankContextMenu(e);
        });

        // DOMCache.getBySelector('.content_box').addEventListener('contextmenu', (e) => {
        //     this.handleBlankContextMenu(e);
        // });
    },

    handleBlankContextMenu(e) {
        if (e.target.classList.contains('files-grid') || e.target.classList.contains('files-list') || e.target.classList.contains('content_box')) {
            e.preventDefault();
            MenuManager.hideContextMenu();
            const blankMenu = DOMCache.get('blankMenu');
            // blankMenu.style.display = 'block';
            Utils.uiBoxDisplayChange(blankMenu,block,true)
            blankMenu.style.left = `${e.pageX}px`;
            blankMenu.style.top = `${e.pageY}px`;
        }
    },

    showRenameDialog() {
        DialogManager.lockWindowVisibility();
        const renameOverlay = DOMCache.get('renameOverlay');
        const renameInput = DOMCache.get('renameInput');

        renameInput.value = AppState.selectedFile.fileName;
        // renameOverlay.style.display = 'flex';
        Utils.uiBoxDisplayChange(renameOverlay,"flex",true)
        renameInput.focus();

        MenuManager.hideContextMenu();
    },

    showDeleteConfirm() {
        const deleteConfirm = DOMCache.get('deleteConfirm');
        const deleteFileName = DOMCache.get('deleteFileName');

        deleteFileName.textContent = AppState.selectedFile.fileName;
        // deleteConfirm.style.display = 'flex';
        Utils.uiBoxDisplayChange(deleteConfirm,"flex",true)

        MenuManager.hideContextMenu();
    },
 
    async setIcon(){
        await ApiHelper.call("setIcon", AppState.selectedFile.filePath,AppState.selectedFile.edit_ico==undefined)
        NavigationManager.refreshCurrentPath()
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
        ApiHelper.call("unlock_window_visibility")
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
        // dialogContainer.style.display = 'flex';
        Utils.uiBoxDisplayChange(dialogContainer,"flex",true)

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
                icon = document.createElement('img');
                icon.src = item.fileType=="应用组"?"./resources/imgs/group.png":item.ico;
                

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
                listItem.dataset.filePath = item.filePath;
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
            ApiHelper.call("unlock_window_visibility")
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
            ApiHelper.call("unlock_window_visibility")
        }

        // 点击对话框外部关闭
        function handleOverlayClick(e) {
            if (e.target === overlay) {
                dialogContainer.style.display = 'none';
                UIUtils.enableScroll();
                resolve({files_data: [], title: ''});
                ApiHelper.call("unlock_window_visibility")
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
async function run_fileSelector_search(){
    const fileSelectionList = document.getElementById('fileSelectionList');
    const input_box = document.getElementById('cs_search_box');
    if(input_box.value==""){
        for(let c of fileSelectionList.children){
            c.style.display = "flex";
        }
    }else{
        let result =  await SearchManager.performSearch(input_box.value,false)
        // 转为列表
        result_list = []
        for(let i of result){
            result_list.push(i.filePath)
        }
        for(let c of fileSelectionList.children){
            if(result_list.includes(c.dataset.filePath)){
                c.style.display = "flex";
            }else{
                c.style.display = "none";
            }
        }
    }
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
let preview_runing = false
async function image_preview() {
    console.log("image_preview")
    try{
        if(preview_runing) return;
        let config = await ApiHelper.getConfig()
        if(config["imgpre"]==false)return
        preview_runing = true;
        for(let file of AppState.files_data){
            if([".png",".jpg",".jpeg",".bmp",".gif"].includes(file.fileType)){
                var view_img = await ApiHelper.call("get_imageBase64", file.filePath);
                if(view_img){
                    console.log("预览图片："+file.fileName)
                    te = document.getElementById(Utils.generateFileId(file.filePath))
                    te.children[1].src = view_img
                }
            }
            if(preview_runing==false) break;
        }
        preview_runing = false;
    }catch{
        console.log("image_preview error")
        preview_runing = false
    }
}
async function change_cl_state(filePath, cl){
    await ApiHelper.call('change_cl_state', filePath, cl);
    NavigationManager.refreshCurrentPath();
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
    UIUtils.showMessage(code);
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

async function load_theme(theme,from_fit) {

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
        if(from_fit==true){
            if(theme=="dark"){
                let setting_theme = await ApiHelper.getConfig()
                setting_theme = setting_theme["theme"]
                if(setting_theme!="light"){
                    console.log(setting_theme)
                    load_theme(setting_theme)
                    return 
                }
            }
        }
        // 加载主题
        themeCSS.href = CONSTANTS.THEME_PATHS[theme];
        NavigationManager.refreshCurrentPath();
        render_class_btn()
        console.log(`主题已切换到: ${theme}`);
        if(theme=="light"){
            await ApiHelper.call('load_blur_effect', 'Acrylic');
        }else{
            await ApiHelper.call('load_blur_effect', 'Aero');
        }
        ThemeManager.now_theme = theme;
        config = await ApiHelper.getConfig();
        if(config["bgType"]=="3")load_bgType(config["bgType"])
        ThemeManager.applyBackgroundSettings(config);
        return true;

}
async function load_bgType(tid){
    if(tid=="1"){
        document.body.style.background = ""
        document.body.style.backgroundColor = "unset"
    }else if(tid=="2"){
        document.body.style.background = "unset"
        document.body.style.backgroundColor = "rgba(0,0,0,0)"
        document.body.style.backdropFilter = "blur(10px)"
    }else{
        document.body.style.background = "unset"
        if(ThemeManager.now_theme=='light'){
            document.body.style.backgroundColor = "rgba(255,255,255,0.3)"
        }else{
            document.body.style.backgroundColor = "rgba(0,0,0,0.3)"
        }
    }
    var config = await ApiHelper.getConfig();
    if(config['use_bg']==true && config['bgType']==1){
        ThemeManager.applyBackgroundSettings(config);
    }
}
async function fit_window() {
    await ApiHelper.call('fit_window_start');
}
let setting_mode = false
async function disable_settings() {
    setting_mode = true
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
    window.addEventListener("resize",async function(event) {
        await ApiHelper.call('fit_resize');
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
        let version = await ApiHelper.call('get_version')
        document.getElementById("v_note").innerText = "v"+version["version"]

        // 初始化UI状态
        const updateUIFromConfig = async (config) => {
            const followSystem = config.themeChangeType != "0";
            const currentTheme = config.theme || 'dark';
            load_bgType(config.bgType)

            // 更新切换开关状态
            const toggleConfigs = [
                // ['followSystemTheme', 'follow_sys'],
                ['autoStartToggle', 'auto_start'],
                ['fullScreenToggle', 'full_screen'],
                ['fdrToggle', 'fdr'],
                ['of_sToggle', 'of_s'],
                ['sysappToggle', 'show_sysApp'],
                ['imgpreToggle', 'imgpre'],
                ['blurToggle','blur_bg']
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
            DOMCache.get('corner_size_toggle').value = config.corner_size;
            DOMCache.get('outPos_toggle').value = config.outPos;
            DOMCache.get('dbc_action_toggle').value = config.dbc_action;
            DOMCache.get("bgType_toggle").value = config.bgType;
            DOMCache.get("themeChangeType_toggle").value = config.themeChangeType;
            // EventManager.updateThemeCardInteraction();


            // 更新缩放
            const scSlider = DOMCache.get('sc_slider');
            scSlider.value = config.scale;
            const blur_ef_input = DOMCache.get('blur_ef_input');
            blur_ef_input.value = Math.floor(100-config.blur_effect);
            DOMCache.get("sc_input").innerText = "缩放比例：" + config.scale + "%";
            DOMCache.get("blur_ef_input_show").innerText = "毛玻璃效果强度：" + Math.floor(100-config.blur_effect) + "%";
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

            // EventManager.updateThemeCardInteraction(followSystem);
            EventManager.updateBGInteraction();

            // 加载主题
            if (followSystem) {
                const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
                await load_theme(systemTheme);
            } else {
                await load_theme(currentTheme);
            }
            if(config.bgType != "0"){
                setTimeout(function(){
                    load_bgType(config.bgType)
                },100)
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

    render_class_btn()
});

// 监听系统主题变化
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', async (e) => {
    const config = await ApiHelper.getConfig();
    if (config.themeChangeType=="!") {
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
        if(index!="全部"){
            btn.draggable = true
        }
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
setInterval(fit_btnBar,200)
document.getElementById("class_bar_btn").addEventListener("click", add_class);

let enter_click = false;
window.addEventListener("keydown", function(event) {
    if (event.key === 'Enter') {
        // 输入框活跃或对话框打开时不触发文件点击
        // if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') return;
        if (DOMCache.get("renameOverlay").style.display === "flex") return;
        if (DOMCache.get("groupDeleteConfirm").style.display === "flex") return;
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


let dragging = false
boxs = [
    document.getElementById("filesContainer"),
    document.getElementById("filesListContainer"),
    document.getElementById("class_bar"),
    document.getElementById("groupFilesContainer")
]
content_box = document.getElementById("content_box")
boxs[0].dataset.other = "list"
boxs[1].dataset.other = "grid"
pos_move_dt = null
pos_move_pc = null
const drag_move = {
    last_time : null,
    move_ctn:async function(num){
        // 防过高频触发
        if(this.last_time!=null){
            if (Date.now() - this.last_time < 50) {
                return;
            }
        }

        content_box.scrollTo({
            top: content_box.scrollTop + num,
            behavior: 'smooth',
        })
        this.last_time = Date.now()
    }
}
async function detect_posMove(){
    r = await ApiHelper.call("drag_posMoveAction")
    ms = await ApiHelper.call("mouse_state")
    if(ms==false){
        try{clearInterval(pos_move_pc)}catch(e){}
        return
    }
    if(r!="none"){
        if(r=="bottom"){
            if(pos_move_pc!=null)return
            pos_move_pc = setInterval(async function(){
                drag_move.move_ctn(50)
            },50)
        }else if(r=="top"){
            if(pos_move_pc!=null)return
            pos_move_pc = setInterval(async function(){
                drag_move.move_ctn(-50)
            },50)
        }
    }else{ 
        if(pos_move_pc!=null){
            clearInterval(pos_move_pc)
            pos_move_pc = null
        }
    }
}
async function stop_moveAction(){
    if(pos_move_pc!=null){
        clearInterval(pos_move_pc)
        pos_move_pc = null
    }
    if(pos_move_dt!=null){
        clearInterval(pos_move_dt)
        pos_move_dt = null
    }
}
for(let list of boxs){
    // let list = document.querySelector('.list')
    let currentLi
    list.addEventListener('dragstart',(e)=>{
        e.dataTransfer.effectAllowed = 'move'
        dragging = true
        currentLi = e.target
        setTimeout(()=>{
            currentLi.classList.add('moving')
        })
        stop_moveAction()
        pos_move_dt = setInterval(async function(){
            detect_posMove()
        },100)
        ApiHelper.call("lock_window_visibility")
    })
    list.addEventListener('dragenter',(e)=>{
        e.preventDefault()
        dragging = true
        if(e.target === currentLi||e.target === list){
            return
        }

        // 拖拽到组项目上：高亮但不排序
        let targetEl = e.target.closest('.file-group-item');
        if (targetEl && !currentLi.classList.contains('file-group-item')) {
            targetEl.classList.add('drag-over-group');
            return;
        }
        // 移出组项目时移除高亮
        list.querySelectorAll('.drag-over-group').forEach(el => el.classList.remove('drag-over-group'));

        try{
            if(currentLi.classList.contains("class_bar_btn")){
                if(e.target.classList.contains("class_bar_btn")==false || e.target.draggable!=true){
                    return
                }
            }
            if(e.target.dataset.is_cl!=currentLi.dataset.is_cl)return
        }catch(e){return}
        let liArray = Array.from(list.childNodes)
        let currentIndex = liArray.indexOf(currentLi)
        let targetindex = liArray.indexOf(e.target)

        try{
            if(currentIndex<targetindex){
                list.insertBefore(currentLi,e.target.nextElementSibling)
            }else{
                list.insertBefore(currentLi,e.target)
            }
        }catch(e){}
    })
    list.addEventListener('dragover',(e)=>{
        e.preventDefault()
        dragging = true
        // 持续检测组目标，确保拖拽到组上时高亮稳定
        if (currentLi && !currentLi.classList.contains('file-group-item')) {
            let targetEl = e.target.closest('.file-group-item');
            if (targetEl) {
                list.querySelectorAll('.drag-over-group').forEach(el => {
                    if (el !== targetEl) el.classList.remove('drag-over-group');
                });
                targetEl.classList.add('drag-over-group');
            } else {
                list.querySelectorAll('.drag-over-group').forEach(el => el.classList.remove('drag-over-group'));
            }
        }
    })
    list.addEventListener('dragleave',(e)=>{
        let targetEl = e.target.closest('.file-group-item');
        if (targetEl) {
            // 仅在鼠标真正离开组项目时移除高亮（排除子元素间的切换）
            if (!e.relatedTarget || !targetEl.contains(e.relatedTarget)) {
                targetEl.classList.remove('drag-over-group');
            }
        }
    })
    list.addEventListener('dragend',async(e)=>{
        ApiHelper.call("unlock_window_visibility")
        currentLi.classList.remove('moving')
        dragging = false
        stop_moveAction()

        // 检查是否拖入了组
        const groupTarget = list.querySelector('.drag-over-group');
        if (groupTarget && currentLi && !currentLi.classList.contains('file-group-item')) {
            groupTarget.classList.remove('drag-over-group');
            const groupId = groupTarget.dataset.group_id;
            const fileIndex = currentLi.dataset.list_index;
            const fileData = AppState.files_data[fileIndex];
            if (groupId && fileData && fileData.filePath) {
                await GroupManager.addToGroup(groupId, [fileData.filePath]);
                return;
            }
        }
        // 清除所有高亮
        list.querySelectorAll('.drag-over-group').forEach(el => el.classList.remove('drag-over-group'));
        if(e.target.classList.contains("class_bar_btn")){
            var order = []
            for(let item of boxs[2].children){
                if(item.draggable!=true)continue
                order.push(item.id)
            }
            await ApiHelper.call("save_classOrder",order)
        }else if(e.target.parentNode.id=="groupFilesContainer"){
            const rect = groupContainer.getBoundingClientRect();
            if (e.clientX < rect.left || e.clientX > rect.right ||
                e.clientY < rect.top || e.clientY > rect.bottom) {
                const fp = currentLi.dataset.file_path;
                if (fp) GroupManager.removeFromGroup(currentLi.dataset.gid, fp);
            }else{
                await GroupManager.editGroupOrder()
            }
        }else{
            await save_new_order(list.dataset.other)
        }
    })
}

async function save_new_order(reload_part){
    if(boxs[0].style.display!="none"){
        target_box = boxs[0]
    }else{
        target_box = boxs[1]
    }
    let new_order = []
    for(let item of target_box.children){
        new_order.push(AppState.files_data[item.dataset.list_index])
    }
    console.log(new_order)
    await ApiHelper.call("update_config_order",AppState.currentPath,new_order)
    console.log(reload_part)
    // NavigationManager.refreshCurrentPath()
    // fileRenderer.render(new_order,reload_part)
}
loadingUI.sets("items_ctn",true);
