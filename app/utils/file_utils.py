import os
import shutil
from typing import Optional

def get_project_root() -> str:
    """
    获取项目根目录（performance_gantt_generator）
    :return: 根目录绝对路径
    """
    # 当前文件路径（utils/file_utils.py）→ 父目录（utils）→ 再父目录（根目录）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    return project_root

def create_dir_if_not_exist(dir_path: str) -> None:
    """
    若目录不存在则创建
    :param dir_path: 目录路径
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)  # exist_ok=True避免多线程创建冲突
        print(f"[文件工具] 已创建目录：{dir_path}")

def delete_file_if_exist(file_path: str) -> None:
    """
    若文件存在则删除
    :param file_path: 文件路径
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"[文件工具] 已删除文件：{file_path}")

def delete_dir_contents(dir_path: str, keep_dir: bool = True) -> None:
    """
    删除目录下所有内容（可选保留目录本身）
    :param dir_path: 目录路径
    :param keep_dir: 是否保留目录本身（True=保留，False=删除整个目录）
    """
    if not os.path.exists(dir_path):
        return
    
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)
    
    if not keep_dir:
        os.rmdir(dir_path)
    print(f"[文件工具] 已清空目录内容：{dir_path}")

def get_file_name_without_ext(file_path: str) -> str:
    """
    获取文件名（不含扩展名）
    :param file_path: 文件路径
    :return: 无扩展名的文件名
    """
    return os.path.splitext(os.path.basename(file_path))[0]

# 初始化临时目录（程序启动时自动创建）
TEMP_DIR = os.path.join(get_project_root(), "resources", "temp")
create_dir_if_not_exist(TEMP_DIR)

# 初始化日志目录（程序启动时自动创建）
LOG_DIR = os.path.join(get_project_root(), "resources")
create_dir_if_not_exist(LOG_DIR)