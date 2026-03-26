# -*- coding: utf-8 -*-
"""
应用组管理模块
封装组数据的持久化逻辑（创建、重命名、删除、添加/移除项目）
"""
import json
import time
import os
import config as cfg


def _load_groups():
    """加载组数据"""
    if os.path.exists(cfg.USER_GROUPS_FILE):
        with open(cfg.USER_GROUPS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_groups(data):
    """保存组数据"""
    with open(cfg.USER_GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def create_group(dir_key, name):
    """创建新组，返回 group_id"""
    data = _load_groups()
    if dir_key not in data:
        data[dir_key] = {}
    group_id = "grp_" + str(int(time.time() * 1000))
    data[dir_key][group_id] = {
        "name": name,
        "items": [],
        "order": len(data[dir_key])
    }
    _save_groups(data)
    return group_id


def rename_group(dir_key, group_id, new_name):
    """重命名组"""
    data = _load_groups()
    if dir_key in data and group_id in data[dir_key]:
        data[dir_key][group_id]["name"] = new_name
        _save_groups(data)
        return True
    return False


def delete_group(dir_key, group_id):
    """解散组（文件回到主视图）"""
    data = _load_groups()
    if dir_key in data and group_id in data[dir_key]:
        del data[dir_key][group_id]
        _save_groups(data)
        return True
    return False


def add_items(dir_key, group_id, file_paths):
    """添加文件到组"""
    data = _load_groups()
    if dir_key not in data or group_id not in data[dir_key]:
        return False
    group = data[dir_key][group_id]
    for fp in file_paths:
        if fp not in group["items"]:
            group["items"].append(fp)
    _save_groups(data)
    return True


def remove_item(dir_key, group_id, file_path):
    """从组中移除文件"""
    data = _load_groups()
    if dir_key not in data or group_id not in data[dir_key]:
        return False
    items = data[dir_key][group_id]["items"]
    if file_path in items:
        items.remove(file_path)
        _save_groups(data)
        return True
    return False


def get_group_items(dir_key, group_id):
    """获取组内文件路径列表"""
    data = _load_groups()
    if dir_key in data and group_id in data[dir_key]:
        return data[dir_key][group_id]["items"]
    return []


def get_all_groups(dir_key):
    """获取目录下所有组"""
    data = _load_groups()
    return data.get(dir_key, {})


def get_grouped_paths(dir_key):
    """获取所有已被编组的文件路径"""
    data = _load_groups()
    paths = set()
    for group in data.get(dir_key, {}).values():
        for p in group.get("items", []):
            paths.add(p)
    return paths
