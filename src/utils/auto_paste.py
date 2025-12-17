import time
import pyautogui
import pyperclip
import random
from rich.console import Console

console = Console()
def random_sleep(min_time=0.05, max_time=0.1):
    """生成一个指定范围内的随机浮点数延时"""
    time.sleep(random.uniform(min_time, max_time))

def perform_blue_box_action(text, region):
    """
    在蓝色框区域执行操作：点击 -> 粘贴 -> 回车
    """
    offset = random.uniform(-10, 10)

    # 计算中心点
    cx = region[0] + region[2] // 2 + offset
    cy = region[1] + region[3] // 2 + offset

    # 确保cx和cy在region范围内
    if cx < region[0] or cx > region[0] + region[2]:
        cx = region[0] + region[2] // 2

    if cy < region[1] or cy > region[1] + region[3]:
        cy = region[1] + region[3] // 2

    # 复制文本
    pyperclip.copy(text)

    # 移动到位置
    pyautogui.moveTo(cx, cy)
    
    # 点击
    pyautogui.click()

    # 粘贴文本
    pyautogui.hotkey('ctrl', 'v')
    random_sleep()
    
    # 按下回车键
    pyautogui.press('enter')
    console.log(f"[blue]动作: 输入成功[/blue] ")
