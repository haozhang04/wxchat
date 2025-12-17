import os
import json
import termcolor

class ScreenRegionConfig:
    def __init__(self):
        self.DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        self.CONFIG_FILE = os.path.join(self.DATA_DIR, "screen_config.json")

    def load(self):
        """加载屏幕区域配置"""
        if not os.path.exists(self.CONFIG_FILE):
            termcolor.cprint(f"警告: 配置文件 {self.CONFIG_FILE} 不存在", 'yellow')
            return {}
        try:
            with open(self.CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            termcolor.cprint(f"警告: 配置文件 {self.CONFIG_FILE} 格式错误", 'yellow')
            return {}

    def save(self, config):
        """写入屏幕区域配置"""
        try:
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
        except:
            termcolor.cprint(f"警告: 无法写入配置文件 {self.CONFIG_FILE}", 'yellow')