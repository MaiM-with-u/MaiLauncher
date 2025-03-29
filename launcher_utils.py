import os
import subprocess
import shutil
import sys


class LauncherUtils:
    def __init__(self):
        self.root_path: str = LauncherUtils.get_current_path()
        self.python_path: str = None
        self.git_path: str = None
        self.conda_path: str = None

        self.MongoDB_enable: bool = False
        self.git_enable: bool = False
        self.conda_enable: bool = False

        self.bot_branch: list = {}
        self.current_branch: str = None

        self.search_python()
        self.search_git()
        self.search_conda()

        self._validate_mongodb()

    @staticmethod
    def get_current_path() -> str:
        """
        获取当前路径
        """
        file_absolute_path = os.path.abspath(__file__)
        root_path = os.path.dirname(file_absolute_path)
        return root_path

    @staticmethod
    def run_command(command, shell=False) -> tuple[int, str]:
        """
        运行系统命令并返回结果
        """
        try:
            result = subprocess.run(
                command, shell=shell, text=True, capture_output=True
            )
            return result.returncode, result.stdout.strip()
        except Exception as e:
            print(f"Error running command: {command}\n{e}")
            return 1, ""

    def search_python(self):
        """
        检测并获取python路径
        """
        if os.path.exists(os.path.join(self.root_path, "venv")):
            self.python_path = os.path.join(
                self.root_path, "venv", "Scripts", "python.exe"
            )
            self._validate_python()
        else:
            # -------------------------------------------------------------------- 输出需要更改
            print("正在寻找python解释器")
            system_python_path = shutil.which("python")
            if system_python_path:
                print(f"找到Python解释器：{system_python_path}")
                self.python_path = system_python_path
                self._validate_python()
            else:
                print("Python解释器解析失败")
                sys.exit(1)

    def search_git(self):
        """
        搜索git路径
        """
        print("正在自动查找Git...")
        git_path = shutil.which("git")
        if git_path:
            print(f"找到Git：{git_path}")
            self.git_path = git_path
            self.git_enable = True
        else:
            print("请手动安装git并添加到系统PATH来启用分支切换功能")
            self.git_enable = False

    def search_conda(self):
        """
        搜索conda路径
        """
        conda_path = shutil.which("conda")
        if conda_path:
            print(f"找到Conda：{conda_path}")
            self.conda_path = conda_path
            self.conda_enable = True
        else:
            print("未检测到conda")
            self.conda_enable = False

    def _validate_python(self) -> bool:
        if self.python_path:
            code, ret = self.run_command(f"{self.python_path} --version")
            if code != 0:
                print("Python解释器无效")
            else:
                python_version = ret.split(" ")[1].split(".")
                if int(python_version[0]) < 3:
                    print("获取到的Python版本过低")
                elif int(python_version[1]) < 10:
                    print("获取到的Python版本过低")
                else:
                    print("Python解释器验证通过")
        else:
            print("Python解释器验证失败")

    def _validate_mongodb(self):
        """
        检查MongoDB服务
        """
        code, ret = self.run_command("sc query")
        if code != 0:
            print("系统错误，无法查询服务")
        else:
            if "MongoDB" not in ret:
                print("MongoDB服务未启动")
                print("MongoDB服务未运行，是否尝试运行服务？")
                confirm = input("是否启动？(Y/n): ").strip().lower()
                if confirm == "y":
                    print("正在尝试启动MongoDB服务...")
                    code, ret = self.run_command(
                        "powershell -Command \"Start-Process -Verb RunAs cmd -ArgumentList '/c net start MongoDB'\""
                    )
                    if code == 0:
                        code, ret = self.run_command("sc query")
                        if "MongoDB" not in ret:
                            print("MongoDB服务启动失败，请检查安装")
                            self.MongoDB_enable = False
                    else:
                        print("MongoDB服务启动失败，请检查安装")
                        self.MongoDB_enable = False
                else:
                    print("警告：MongoDB服务未运行，将导致MaiMBot无法访问数据库！")
                    self.MongoDB_enable = False
            else:
                self.MongoDB_enable = True

    def _get_branch(self):
        """
        获取全部分支
        """
        if not self.git_enable:
            return
        else:
            code, ret = self.run_command("git branch -a")
            if code == 0:
                branch_list = ret.split("\n")
                for i in branch_list:
                    if i.startswith("*"):
                        branch = i.split(" ")[1]
                        self.bot_branch.append(branch)
                        self.current_branch = branch
                        print(f"当前分支：{branch}")
                    else:
                        branch = i.split(" ")[-1]
                        self.bot_branch.append(branch)
            else:
                print("获取当前分支失败")

    def update_dependency(self):
        """
        更新依赖
        """
        code, _ = self.run_command(
            f"{self.python_path} -m pip install -r requirements.txt --upgrade pip"
        )
        if code == 0:
            print("环境依赖更新成功")
        else:
            print("依赖更新出现错误，请手动重试")

    def switch_branch(self, target_branch: str):
        """
        切换分支
        """
        if not self.git_enable:
            print("没有可用git，无法使用分支切换功能")
            return
        else:
            print("正在切换分支...")
            code, _ = self.run_command(f"git checkout -b {target_branch}")
            if code == 0:
                print(f"切换分支成功，当前分支{target_branch}")
            else:
                print("切换分支失败")

    def reset_branch(self):
        """
        重置分支
        """
        if not self.git_enable:
            return
        else:
            print("正在重置分支...")
            code, _ = self.run_command(f"git reset --hard {self.current_branch}")
            if code == 0:
                print("重置分支成功")
            else:
                print("重置分支失败")

    def update_config(self):
        """
        自动更新配置文件
        """
        print("请确保已备份重要数据，继续将修改当前配置文件。")
        confirm = input("继续？(Y/n): ").strip().lower()
        if confirm == "y":
            print("正在更新配置文件...")
            code, _ = self.run_command(
                f'"{self.python_path} {os.path.join(self.root_path, "config", "auto_update.py")}"'
            )
            if code == 0:
                print("配置文件更新成功")
            else:
                print("配置文件更新失败")
        else:
            print("取消更新配置文件")

    def update_bot(self):
        """
        自动升级MaiBot
        """
        pass

    def start_bot_venv(self):
        """
        venv启动MaiBot
        """
        print("正在更新依赖")
        self.update_dependency()
        print("正在启动MaiMBot...")
        os.system(f"{self.python_path} {os.path.join(self.root_path, 'test.py')}")
        print("MaiBot已关闭，系统退出")
        sys.exit(0)

    def start_bot_conda(self):
        """
        conda启动MaiBot
        """
        pass

    def start_bot(self):
        # if self.conda_enable:
        #     self.start_bot_conda()
        # else:
        #     self.start_bot_venv()
        self.start_bot_venv()

    def modify_config(self):
        config_path = os.path.join(self.root_path, "config")
        if not os.path.exists(os.path.join(config_path, "bot_config.toml")):
            shutil.copy(
                os.path.join(self.root_path, "template", "bot_config_template.toml"),
                os.path.join(config_path, "bot_config.toml"),
            )
        # 此处待定，等待配置文件拆分
        pass
        # 进入WebUI模式修改配置

launcher_utils = LauncherUtils()
