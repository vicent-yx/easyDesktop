const recordBtn = document.getElementById('recordBtn');
const modalOverlay = document.getElementById('modalOverlay');
const keyDisplay = document.getElementById('keyDisplay');
const confirmBtn = document.getElementById('confirmBtn');
const cancelBtn = document.getElementById('cancelBtn');
const shortcutDisplay = document.getElementById('shortcutDisplay');
const currentKeysElement = document.getElementById('currentKeys');

// 特殊键的映射
const keyMap = {
    ' ': 'space',
    'Control': 'ctrl',
    'ArrowUp': 'up',
    'ArrowDown': 'down',
    'ArrowLeft': 'left',
    'ArrowRight': 'right',
    'Escape': 'esc',
    'Enter': 'enter',
    'Shift': 'shift',
    'Alt': 'alt',
    'Meta': 'windows',
    'Tab': 'tab',
    'CapsLock': 'caps lock',
    'Backspace': 'backspace',
    'Delete': '	delete'
};

// 封装记录快捷键的函数，返回Promise
function recordShortcut() {
    return new Promise((resolve, reject) => {
        // 显示模态框
        modalOverlay.classList.add('active');
        
        // 初始化按键数组
        const pressedKeys = [];
        
        // 更新按键显示
        function updateKeyDisplay() {
            currentKeysElement.textContent = pressedKeys.length;
            
            if (pressedKeys.length === 0) {
                keyDisplay.textContent = '等待按键输入...';
            } else {
                keyDisplay.textContent = pressedKeys.join(' + ');
            }
        }
        
        // 键盘事件处理
        const handleKeyDown = (e) => {
            // 防止重复记录
            if (pressedKeys.includes(getKeyName(e))) return;
            
            // 最多记录3个键
            if (pressedKeys.length >= 3) return;
            
            // 获取键名
            const keyName = getKeyName(e);
            
            // 添加按键到数组
            pressedKeys.push(keyName);
            updateKeyDisplay();
            
            // 阻止默认行为
            e.preventDefault();
        };
        
        // 添加键盘事件监听
        document.addEventListener('keydown', handleKeyDown);
        
        // 确认按钮点击事件
        const handleConfirm = () => {
            cleanup();
            resolve(pressedKeys.join('+'));
        };
        
        // 取消按钮点击事件
        const handleCancel = () => {
            cleanup();
            reject(null);
        };
        
        // 模态框外部点击事件
        const handleOverlayClick = (e) => {
            if (e.target === modalOverlay) {
                handleCancel();
            }
        };
        
        // 清理函数
        function cleanup() {
            modalOverlay.classList.remove('active');
            document.removeEventListener('keydown', handleKeyDown);
            confirmBtn.removeEventListener('click', handleConfirm);
            cancelBtn.removeEventListener('click', handleCancel);
            modalOverlay.removeEventListener('click', handleOverlayClick);
        }
        
        // 添加事件监听
        confirmBtn.addEventListener('click', handleConfirm);
        cancelBtn.addEventListener('click', handleCancel);
        modalOverlay.addEventListener('click', handleOverlayClick);
        
        // 初始化显示
        updateKeyDisplay();
    });
}

// 获取标准键名
function getKeyName(event) {
    // 特殊键优先处理
    if (keyMap[event.key]) {
        return keyMap[event.key];
    }
    
    // 处理修饰键
    if (event.key === 'Control' || event.key === 'Shift' || 
        event.key === 'Alt' || event.key === 'Meta') {
        return keyMap[event.key] || event.key;
    }
    
    // 返回原键名（首字母大写）
    return event.key.length === 1 ? event.key.toUpperCase() : event.key;
}

// // 主按钮点击事件
// recordBtn.addEventListener('click', async function() {
//     try {
//         const shortcut = await recordShortcut();
//         shortcutDisplay.textContent = shortcut;
//     } catch (error) {
//         if (error === null) {
//             console.log("用户取消了快捷键记录");
//         } else {
//             console.error("记录快捷键时出错:", error);
//         }
//     }
// });