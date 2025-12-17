from enum import Enum, auto

class AppState(Enum):
    IDLE_STATE = auto()               # 正常聊天（用户终端输入 -> AI -> 终端输出）
    OCR_STATE = auto()                # OCR 识别中 (红框输入 -> AI -> 终端输出)
    OUTPUT_STATE = auto()             # 输出模式 (用户终端输入 -> AI -> 蓝框输出)
    AUTOCHAT_STATE = auto()           # 自动聊天模式 (循环：红框输入 -> AI -> 蓝框输出)
    EDIT_STATE = auto()               # 编辑模式 (编辑每个框的大小)
    EXIT = auto()                     # 退出模式 (退出程序)

class FSMMode(Enum):
    NORMAL = auto()
    CHANGE = auto()
