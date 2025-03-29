# This Python file uses the following encoding: utf-8
import sys

from launcher_utils import launcher_utils

VERSION = "1.0"

if __name__ == "__main__":
    print(f"当前分支:{launcher_utils.current_branch}")
    print(f"当前python可执行路径：{launcher_utils.python_path}")
    choice = input("请选择操作:").strip().lower()
    '''
    1.升级bot(未实现)
    2.直接启动(并检查依赖)
    3.修改配置
    4.更新依赖
    5.切换分支
    6.重置分支
    7.学习新知识（等待LPMM适配）
    8.退出！
    '''
    if choice == "1":
        launcher_utils.update_bot()
    elif choice == "2":
        launcher_utils.start_bot()
    elif choice == "3":
        launcher_utils.modify_config()
    elif choice == "4":
        launcher_utils.update_dependency()
    elif choice == "5":
        # 由WebUI下拉框选择branch
        # 分支已经提前获取到launcher_utils.bot_branch
        launcher_utils.switch_branch("main")
    elif choice == "6":
        launcher_utils.reset_branch()
    elif choice == "7":
        pass
    elif choice == "8":
        sys.exit(0)
    