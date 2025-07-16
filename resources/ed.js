const blankMenu = document.getElementById('blankMenu');
const newFileOverlay = document.getElementById('newFileOverlay');
const newFileTypeSelect = document.getElementById('newFileTypeSelect');
const newFileCancel = document.getElementById('newFileCancel');
const newFileConfirm = document.getElementById('newFileConfirm');
const menuPaste = document.getElementById('menuPaste');
const menuNew = document.getElementById('menuNew');
const scripts_type=[".py",".java",".c",".cpp",".h",".hpp",".cs",".php",".rb",".go",".swift",".kt",".m",".pl",".r",".sh",".bash",".zsh",".lua",".scala",".groovy",".dart",".rs",".jl",".hs",".f",".f90",".f95",".v",".vhd",".clj",".ex",".exs",".elm",".purs",".erl",".hrl",".fs",".fsx",".fsi",".ml",".mli",".pas",".pp",".d",".nim",".cr",".cbl",".cob",".ada",".adb",".ads"]
let files_data = []
let selectedFile = null;
let contextMenu = null;
let dealling = false;
let currentPath = ''; // 当前浏览路径
let pathHistory = []; // 路径历史记录
let currentHistoryIndex = -1; // 当前历史记录索引
let timer = null
let db_click_action = false

// 获取文件类型
function getFileType(fileName,fileType) {
    console.log('文件类型：',fileType);
    const ext = fileName.split('.').pop().toLowerCase();
    const types = {
        'docx': '文档',
        'doc': '文档',
        'xlsx': '电子表格',
        'xls': '电子表格',
        'pptx': '演示文稿',
        'ppt': '演示文稿',
        'pdf': 'PDF文件',
        'jpg': '图片',
        'png': '图片',
        'mp4': '视频',
        'mp3': '音频',
        'psd': '设计稿',
        'fig': '设计稿',
        'sql': '数据库',
        'json': '配置文件',
        'zip': '压缩文件',
        'exe': '应用程序',
    };
    if(scripts_type.includes(ext)){
        return fileType.slice(1)+'脚本文件';
    }
    if(ext in types){
        return types[ext];
    } else if(fileType == '文件夹'){
        return '文件夹';
    } else {
        console.log('未知文件类型：',fileType);
        return fileType.slice(1)+'文件';
    }
}

// 更新当前时间
function updateTime() {
    const now = new Date();
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        weekday: 'long',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    };
    document.getElementById('current-time').textContent = now.toLocaleDateString('zh-CN', options);
}
function open_file(filePath) {
    window.pywebview.api.open_file(filePath);
}
function open_mhyGame(filePath,game){
    window.pywebview.api.open_mhyGame(filePath,game);
}
function copy_file(filePath) {
    window.pywebview.api.copy_file(filePath);
}
function rename_file(filePath, newName) {
    window.pywebview.api.rename_file(filePath, newName);
    push()
}
async function remove_file(filePath) {
    var r = await window.pywebview.api.remove_file(filePath);
    push()
    return r
}

// 显示右键菜单
function showContextMenu(e, file) {
    e.preventDefault();
    blankMenu.style.display = 'none';
    selectedFile = file;
    
    contextMenu.style.display = 'block';
    contextMenu.style.left = `${e.pageX}px`;
    contextMenu.style.top = `${e.pageY}px`;
}

// 隐藏右键菜单
function hideContextMenu() {
    contextMenu.style.display = 'none';
}

// 显示重命名对话框
function showRenameDialog() {
    const renameOverlay = document.getElementById('renameOverlay');
    const renameInput = document.getElementById('renameInput');
    
    renameInput.value = selectedFile.fileName;
    renameOverlay.style.display = 'flex';
    renameInput.focus();
    
    hideContextMenu();
}

// 显示删除确认对话框
function showDeleteConfirm() {
    const deleteConfirm = document.getElementById('deleteConfirm');
    const deleteFileName = document.getElementById('deleteFileName');
    
    deleteFileName.textContent = selectedFile.fileName;
    deleteConfirm.style.display = 'flex';
    
    hideContextMenu();
}
async function push(fData = null,useLoadDir = false, path = ''){
    if(fData==null){
        if(useLoadDir && path) {
            files_data = await loadDirectory(path);
            currentPath = path;
        } else {
            files_data = await window.pywebview.api.get_inf("desktop");
            console.log(files_data);
            files_data = files_data["data"];
        }
        fData = files_data
    }
    
    const filesContainer = document.getElementById('filesContainer');
    const filesListContainer = document.getElementById('filesListContainer');
    filesContainer.innerHTML = '';
    filesListContainer.innerHTML = '';
    contextMenu = document.getElementById('contextMenu');
    
    // 渲染网格视图
    fData.forEach(file => {
        const fileElement = document.createElement('div');
        fileElement.className = 'file-item';
        
        const fileType = getFileType(file.file,file.fileType);
        
        fileElement.innerHTML = `
            <img src="${file.ico}" alt="${file.fileName}" class="file-icon">
            <span class="file-name">${file.fileName}</span>
            <span class="file-type">${fileType}</span>
        `;
        
        // 添加点击事件
        fileElement.addEventListener('dblclick', function() {
            db_click_action = true
            clearTimeout(timer)
            if (file.fileType === '文件夹') {
                open_file(file.filePath);
            } else if (file.game) {
                open_mhyGame(file.filePath, file.game);
            } else {
                window.pywebview.api.show_file(file.filePath);
            }
        });
        fileElement.addEventListener('click', function() {
            document.getElementById("search_input").value=""
            timer = setTimeout(async function(){
                if(db_click_action==true){
                    db_click_action = false
                    return
                }
                if (file.fileType === '文件夹') {
                    // 进入文件夹
                    navigateTo(file.filePath);
                } else if (file.game) {
                    open_mhyGame(file.filePath, file.game);
                } else {
                    open_file(file.filePath);
                }
            },200)
        });
        
        // 添加右键菜单事件
        fileElement.addEventListener('contextmenu', function(e) {
            showContextMenu(e, file);
        });
        
        filesContainer.appendChild(fileElement);
    });

    // 渲染列表视图
    fData.forEach(file => {
        const listItem = document.createElement('div');
        listItem.className = 'file-list-item';
        
        const fileType = getFileType(file.file,file.fileType);
        
        listItem.innerHTML = `
            <img src="${file.ico}" alt="${file.fileName}" class="file-list-icon">
            <span class="file-list-name">${file.fileName}</span>
            <span class="file-list-type">${fileType}</span>
        `;
        
        // 添加点击事件
        listItem.addEventListener('dblclick', function() {
            clearTimeout(timer)
            if (file.game) {
                open_mhyGame(file.filePath, file.game);
            } else {
                open_file(file.filePath);
            }
        });
        listItem.addEventListener('click', function() {
            document.getElementById("search_input").value=""
            timer = setTimeout(async function(){
                if (file.fileType === '文件夹') {
                    // 进入文件夹
                    navigateTo(file.filePath);
                } else if (file.game) {
                    open_mhyGame(file.filePath, file.game);
                } else {
                    open_file(file.filePath);
                }
            },200)
        });
        
        // 添加右键菜单事件
        listItem.addEventListener('contextmenu', function(e) {
            showContextMenu(e, file);
        });
        
        filesListContainer.appendChild(listItem);
    });
}
// 视图切换
async function grid_view() {
    document.getElementById('filesContainer').style.display = 'grid';
    document.getElementById('filesListContainer').style.display = 'none';
    document.getElementById('gridViewBtn').classList.add('active');
    document.getElementById('listViewBtn').classList.remove('active');
}
async function list_view() {
    document.getElementById('filesContainer').style.display = 'none';
    document.getElementById('filesListContainer').style.display = 'block';
    document.getElementById('gridViewBtn').classList.remove('active');
    document.getElementById('listViewBtn').classList.add('active');
}
document.getElementById('gridViewBtn').addEventListener('click', function() {
    grid_view()
    window.pywebview.api.update_config("view", "block");
});

document.getElementById('listViewBtn').addEventListener('click', function() {
    list_view()
    window.pywebview.api.update_config("view", "list");
});

// 页面加载完成后执行
window.addEventListener('pywebviewready',async function() {
    push(null);
    document.getElementById('pathBackBtn').addEventListener('click', async function(){
        parent_path = await window.pywebview.api.get_parent(currentPath)
        navigateTo(parent_path)
    });
    const settingsBtn = document.getElementById('settingsBtn');
    const themePanel = document.getElementById('themeSettingsPanel');
    const closeBtn = document.getElementById('closeThemePanel');
    const followSystemToggle = document.getElementById('followSystemTheme');
    const autoStartToggle = document.getElementById('autoStartToggle');
    const themeCards = document.querySelectorAll('.theme-card');
    
    // 切换设置面板显示
    settingsBtn.addEventListener('click', function() {
        disableScroll()
        themePanel.style.display = themePanel.style.display === 'flex' ? 'none' : 'flex';
    });
    
    // 关闭设置面板
    closeBtn.addEventListener('click', function() {
        enableScroll()
        themePanel.style.display = 'none';
    });
    
    // 初始化面板状态
    async function updateUIFromConfig(config) {
        // 处理跟随系统主题
        const followSystem = config.follow_sys || false;
        followSystemToggle.checked = followSystem;
        
        // 处理主题选择
        const currentTheme = config.theme || 'dark';

        // pack自启动
        autoStartToggle.checked = config.auto_start;
        
        // 清除所有主题卡片的active状态
        themeCards.forEach(card => card.classList.remove('active'));
        
        // 设置当前主题的active状态
        if (!followSystem) {
            document.querySelector(`.theme-card[data-theme="${currentTheme}"]`).classList.add('active');
        }
        
        // 更新主题卡片交互状态
        themeCards.forEach(card => {
            card.style.opacity = followSystem ? '0.5' : '1';
            card.style.pointerEvents = followSystem ? 'none' : 'auto';
        });
        
        // 如果跟随系统主题，加载系统主题
        if (followSystem) {
            const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            load_theme(systemTheme);
        } else {
            // 否则加载配置中的主题
            load_theme(currentTheme);
        }
        
        // 更新背景设置
        const blurSlider = document.getElementById('blurSlider');
        const blurValue = document.getElementById('blurValue');
        if (blurSlider && blurValue) {
            blurSlider.value = config.ms_ef || 50;
            blurValue.textContent = blurSlider.value;
        }
        applyBackgroundSettings(await window.pywebview.api.get_config())
    }

    // 监听系统主题变化
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        window.pywebview.api.get_config().then(config => {
            if (config.follow_sys) {
                const newTheme = e.matches ? 'dark' : 'light';
                load_theme(newTheme);
            }
        });
    });

    // 初始化配置
    window.pywebview.api.get_config().then(updateUIFromConfig);

    // 跟随系统主题切换
    followSystemToggle.addEventListener('change', function() {
        const followSystem = this.checked;
        window.pywebview.api.update_config("follow_sys",followSystem);
        
        // 禁用主题选择
        themeCards.forEach(card => {
            card.style.opacity = followSystem ? '0.5' : '1';
            card.style.pointerEvents = followSystem ? 'none' : 'auto';
        });
    });
    // 自启动设置
    autoStartToggle.addEventListener('change', function() {
        const auto_start_result = this.checked;
        window.pywebview.api.update_config("auto_start",auto_start_result);
    });
    
    // 主题卡片点击事件
    themeCards.forEach(card => {
        card.addEventListener('click', function() {
            if (followSystemToggle.checked) return;
            
            const theme = this.dataset.theme;
            window.pywebview.api.update_config("theme",theme);
            load_theme(theme);
            
            // 更新选中状态
            themeCards.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
        });
    });
});

async function updateBreadcrumb(path) {
    const breadcrumb = document.getElementById('breadcrumb');
    breadcrumb.innerHTML = '';
    desktop_path = await window.pywebview.api.where_d()
    
    const parts = path.replace(desktop_path,"").split('\\').filter(part => part.length > 0);
    let currentPath = '';
    
    // 添加桌面项
    const rootItem = document.createElement('span');
    rootItem.className = 'breadcrumb-item';
    rootItem.textContent = '桌面';
    rootItem.dataset.path = "\\";
    rootItem.id = "b2d"
    breadcrumb.appendChild(rootItem);
    
    // 添加路径各部分
    parts.forEach((part, index) => {
        currentPath += part+"\\";
        
        // 添加分隔符
        if (index < parts.length - 1) {
            const separator = document.createElement('span');
            separator.className = 'breadcrumb-separator';
            separator.textContent = '›';
            breadcrumb.appendChild(separator);
        }
        
        // 添加路径项
        const item = document.createElement('span');
        item.className = 'breadcrumb-item';
        item.textContent = part;
        item.dataset.path = currentPath;
        breadcrumb.appendChild(item);
    });
}

function navigateTo(path) {
    if (path === currentPath){
        push(null,true, path);
        window.scrollTo(0, 0);
        return
    }
    
    // 添加到历史记录
    pathHistory = pathHistory.slice(0, currentHistoryIndex + 1);
    pathHistory.push(path);
    currentHistoryIndex = pathHistory.length - 1;
    
    // 更新当前路径
    currentPath = path;
    updateBreadcrumb(path || '/');
    
    // 加载新路径内容
    push(null,true, path);
    window.scrollTo(0, 0);
}

// 绑定面包屑点击事件
document.getElementById('breadcrumb').addEventListener('click', function(e) {
    if (e.target.classList.contains('breadcrumb-item')) {
        const path = e.target.dataset.path;
        navigateTo(path);
    }
});

function navigateBack() {
    if (currentHistoryIndex > 0) {
        currentHistoryIndex--;
        const path = pathHistory[currentHistoryIndex];
        currentPath = path;
        document.getElementById('currentPathDisplay').textContent = path || '/';
        push(null,true, path);
    }
}

function navigateForward() {
    if (currentHistoryIndex < pathHistory.length - 1) {
        currentHistoryIndex++;
        const path = pathHistory[currentHistoryIndex];
        currentPath = path;
        document.getElementById('currentPathDisplay').textContent = path || '/';
        push(null,true, path);
    }
}

async function loadDirector(path) {
    try {
        const response = await window.pywebview.api.get_inf(path);
        response = response["data"]
        console.log(response);
        if (response && response.data) {
            return response.data.map(item => ({
                ico: item.is_dir ? '/resources/folder.png' : getFileIcon(item.name),
                fileName: item.name,
                filePath: item.path,
                fileType: item.is_dir ? '文件夹' : getFileType(item.name),
                game: item.is_game ? true : undefined
            }));
        }
        return [];
    } catch (error) {
        console.error('加载目录失败:', error);
        return [];
    }
}

function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    // 可以根据不同文件类型返回不同图标
    return '/resources/file.png';
}

// 加载目录内容
async function loadDirectory(path) {
    try {
        data = await window.pywebview.api.get_inf(path);
        data = data["data"]
        return data;
    } catch (error) {
        console.error('Error loading directory:', error);
        return [];
    }
}

// 监听空白区域右键点击（网格视图）
document.querySelector('.files-grid').addEventListener('contextmenu', function(e) {
    if (e.target === this) {
        e.preventDefault();
        hideContextMenu();
        blankMenu.style.display = 'block';
        blankMenu.style.left = `${e.pageX}px`;
        blankMenu.style.top = `${e.pageY}px`;
    } else if (e.target.classList.contains('file') || e.target.classList.contains('file-name')) {
        const fileElement = e.target.classList.contains('file') ? e.target : e.target.parentElement;
        const fileName = fileElement.querySelector('.file-name').textContent;
        selectedFile = files_data.find(file => file.fileName === fileName);
        
        if (selectedFile) {
            const openItem = document.getElementById('menuOpen');
            if (selectedFile.fileType === '文件夹') {
                openItem.textContent = '打开文件夹';
            } else {
                openItem.textContent = '打开文件';
            }
            
            contextMenu.style.display = 'block';
            contextMenu.style.left = `${e.pageX}px`;
            contextMenu.style.top = `${e.pageY}px`;
            e.preventDefault();
        }
    }
});

// 监听空白区域右键点击（列表视图）
document.querySelector('.files-list').addEventListener('contextmenu', function(e) {
    if (e.target === this) {
        e.preventDefault();
        hideContextMenu();
        blankMenu.style.display = 'block';
        blankMenu.style.left = `${e.pageX}px`;
        blankMenu.style.top = `${e.pageY}px`;
    } else if (e.target.classList.contains('file-list-item') || e.target.classList.contains('file-list-name')) {
        const fileElement = e.target.classList.contains('file-list-item') ? e.target : e.target.parentElement;
        const fileName = fileElement.querySelector('.file-list-name').textContent;
        selectedFile = files_data.find(file => file.fileName === fileName);
        
        if (selectedFile) {
            const openItem = document.getElementById('menuOpen');
            if (selectedFile.fileType === '文件夹') {
                openItem.textContent = '打开文件夹';
            } else {
                openItem.textContent = '打开文件';
            }
            
            contextMenu.style.display = 'block';
            contextMenu.style.left = `${e.pageX}px`;
            contextMenu.style.top = `${e.pageY}px`;
            e.preventDefault();
        }
    }
});

// 点击空白处隐藏菜单
document.addEventListener('click', function() {
    blankMenu.style.display = 'none';
});

// 确保右键菜单在两种视图下都能工作
function hideAllMenus() {
    hideContextMenu();         // 隐藏文件菜单
    blankMenu.style.display = 'none';  // 隐藏空白菜单
}

document.addEventListener('click', hideAllMenus);
// 模拟的put_file函数
async function put_file() {
    await window.pywebview.api.put_file();
    push(null);
}

// 模拟的new_file函数
async function new_file(fileType) {
    await window.pywebview.api.new_file(fileType);
    push(null); // 刷新界面
}

// 粘贴按钮事件
menuPaste.addEventListener('click',async function() {
    try{
        r = await put_file();
        try{
            if(r["success"]==false){
                showError(r["message"]);
            }
        }catch{}
        blankMenu.style.display = 'none';
    }catch{}
});

// 新建按钮事件
menuNew.addEventListener('click', function() {
    newFileOverlay.style.display = 'flex';
    blankMenu.style.display = 'none';
});

// 取消新建
newFileCancel.addEventListener('click', function() {
    newFileOverlay.style.display = 'none';
});

// 确认新建
newFileConfirm.addEventListener('click',async function() {
    const selectedType = newFileTypeSelect.value;
    if (selectedType) {
        await new_file(selectedType);
        newFileOverlay.style.display = 'none';
        push(null);
    }
});
function hideAllMenus() {
    hideContextMenu();         // 隐藏文件菜单
    blankMenu.style.display = 'none';  // 隐藏空白菜单
}

document.addEventListener('click', hideAllMenus);

// 应用背景设置
function applyBackgroundSettings(config) {
    const body = document.body;
    if (config.use_bg && config.bg) {
        body.style.backgroundImage = `url("${config.bg}")`;
        body.style.backdropFilter = `blur(${config.ms_ef || 0}px)`;
        body.style.backgroundRepeat="no-repeat"
        body.style.backgroundSize="cover"
        body.style.backgroundPosition="center"
    } else {
        body.style.backgroundImage = '';
        body.style.backdropFilter = '';
    }
}

// 初始化背景设置
async function initBackgroundSettings() {
    const config = await window.pywebview.api.get_config();
    const blurSlider = document.getElementById('blurSlider');
    const blurValue = document.getElementById('blurValue');
    
    // 设置滑块初始值
    blurSlider.value = config.ms_ef;
    blurValue.textContent = blurSlider.value;
    
    // 滑块事件
    blurSlider.addEventListener('input',async function() {
        blurValue.textContent = this.value;
        window.pywebview.api.update_config("ms_ef", parseInt(this.value));
        applyBackgroundSettings(await window.pywebview.api.get_config())
    });
    
    // 恢复默认按钮
    document.getElementById('bgResetBtn').addEventListener('click', async function() {
        await window.pywebview.api.update_config("use_bg", false);
        await window.pywebview.api.update_config("bg", "");
        await window.pywebview.api.update_config("ms_ef", 50);
        blurSlider.value = 50;
        blurValue.textContent = '50';
        applyBackgroundSettings(await window.pywebview.api.get_config())
    });
    
    
    // 选择图片按钮
    document.getElementById('bgCustomBtn').addEventListener('click', async function() {
        try {
            const bgUrl = await window.pywebview.api.set_bg();
            if (bgUrl) {
                await window.pywebview.api.update_config("use_bg", true);
                await window.pywebview.api.update_config("bg", bgUrl);
                window.location.reload();
            }
        } catch (error) {
            console.error('设置背景图片失败:', error);
        }
    });
    
    // 应用初始设置
    applyBackgroundSettings(await window.pywebview.api.get_config())
}

window.addEventListener('pywebviewready',async function() {
    // 更新时间
    updateTime();
    setInterval(updateTime, 1000);
    
    // 初始化背景设置
    initBackgroundSettings();
    
    // 右键菜单项事件z
    document.getElementById('menuOpen').addEventListener('click', function() {
        if(selectedFile['game']){
            open_mhyGame(selectedFile.filePath,selectedFile.game);
        }else{
            open_file(selectedFile.filePath);
        }
        hideContextMenu();
    });
    
    document.getElementById('menuCopy').addEventListener('click', function() {
        copy_file(selectedFile.filePath);
        hideContextMenu();
    });
    
    document.getElementById('menuRename').addEventListener('click', showRenameDialog);
    document.getElementById('menuDelete').addEventListener('click', showDeleteConfirm);
    
    // 重命名相关事件
    document.getElementById('renameCancel').addEventListener('click', function() {
        if(dealling)return
        dealling = true
        document.getElementById('renameOverlay').style.display = 'none';
        dealling = false
    });
    
    document.getElementById('renameConfirm').addEventListener('click', function() {
        if(dealling)return
        dealling = true
        const newName = document.getElementById('renameInput').value.trim();
        if (newName) {
            rename_file(selectedFile.filePath, newName);
            document.getElementById('renameOverlay').style.display = 'none';
        }
        dealing = false
    });
    
    // 删除相关事件
    document.getElementById('deleteCancel').addEventListener('click', function() {
        document.getElementById('deleteConfirm').style.display = 'none';
        dealing = false
    });
    
    document.getElementById('deleteConfirmBtn').addEventListener('click',async function() {
        dealling = true
        var r = await remove_file(selectedFile.filePath);
        if(r["success"]==false){
            showError(r["message"])
        }
        document.getElementById('deleteConfirm').style.display = 'none';
        dealling = false
    });
    
    // 点击页面其他位置关闭右键菜单
    document.addEventListener('click', hideContextMenu);
    
    // 重命名输入框按回车确认
    document.getElementById('renameInput').addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            document.getElementById('renameConfirm').click();
        }
    });
})

function showError(code) {
    // 创建外层提示框
    const errorBox = document.createElement('div');
    errorBox.style.position = 'fixed';
    errorBox.style.top = '-100px';
    errorBox.style.left = '50%';
    errorBox.style.transform = 'translateX(-50%)';
    errorBox.style.padding = '20px 30px';
    errorBox.style.backgroundColor = '#ff4d4d';
    errorBox.style.color = 'white';
    errorBox.style.fontSize = '16px';
    errorBox.style.borderRadius = '12px';
    errorBox.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
    errorBox.style.zIndex = '9999';
    errorBox.style.opacity = '0';
    errorBox.style.transition = 'opacity 0.5s ease, top 0.5s ease';
    errorBox.style.textAlign = 'center';

    // 创建文字内容
    const text = document.createElement('div');
    text.textContent = code;
    errorBox.appendChild(text);

    // 添加到 body
    document.body.appendChild(errorBox);

    // 触发动画显示
    setTimeout(() => {
        errorBox.style.top = '20px';
        errorBox.style.opacity = '1';
    }, 100);

    // 5秒后自动消失（淡出）
    setTimeout(() => {
        errorBox.style.opacity = '0';
        errorBox.style.top = '-100px';

        // 完全隐藏后移除元素
        setTimeout(() => {
            if (errorBox.parentNode) {
                errorBox.remove();
            }
        }, 500);
    }, 5000);
}
function contains(mainStr, searchStr) {
    const cleanMainStr = mainStr.replace(/[^\w]/g, '');
    const cleanSearchStr = searchStr.replace(/[^\w]/g, '');
    const regex = new RegExp(cleanSearchStr, 'i');
    return regex.test(cleanMainStr);
}
async function load_search(){
    const key = document.getElementById("search_input").value
    if(key==""){
        push(files_data)
        return
    }
    py_data = await window.pywebview.api.load_search_index(files_data)
    out_data = []
    for(var i=0;i<files_data.length;i++){
        if(contains(py_data[files_data[i]["fileName"]]["sxpy"],key)==true){
            out_data.push(files_data[i])
            continue
        }
        if(contains(py_data[files_data[i]["fileName"]]["py"],key)==true){
            out_data.push(files_data[i])
            continue
        }
    }
    push(out_data)
}
async function load_theme(theme){
    const theme_inf = {
        "dark":"/theme/dark.css",
        "light":"/theme/light.css",
        "zzz":"/theme/zzz.css"
    }
    document.getElementById("theme_css").href = theme_inf[theme]
}
document.addEventListener('keydown', function(event) {
    if (document.activeElement.id !== 'search_input') {
        const searchInput = document.getElementById('search_input');
        if (searchInput) {
            if (!event.ctrlKey && !event.altKey && !event.metaKey && event.key.length === 1) {
            searchInput.focus();
            }
        }
    }
});
function disableScroll() {
    document.body.style.overflow = "hidden"
    document.addEventListener('touchmove', preventDefault, { passive: false });
    document.addEventListener('mousewheel', preventDefault, { passive: false });
    document.addEventListener('wheel', preventDefault, { passive: false });
    document.addEventListener('DOMMouseScroll', preventDefault, { passive: false });
}
function enableScroll() {
    document.body.style.overflow = "scroll"
    document.removeEventListener('touchmove', preventDefault, { passive: false });
    document.removeEventListener('mousewheel', preventDefault, { passive: false });
    document.removeEventListener('wheel', preventDefault, { passive: false });
    document.removeEventListener('DOMMouseScroll', preventDefault, { passive: false });
}
function preventDefault(e) {
    const box = document.getElementById('themeSettings_box');
    const isInsideBox = box.contains(e.target);
    if (!isInsideBox) {
        e.preventDefault();
    }
}
disableScroll()