from typing import Dict, Optional
from enum import Enum, auto
from .base_state import BaseState
from .state.idle_state import IdleState
from .state.ocr_state import OcrProcessingState
from .state.output_state import OutputProcessingState
from .state.autochat_state import AutoChatState

class AppState(Enum):
    IDLE = auto()               # 正常聊天/等待输入
    OCR_PROCESSING = auto()     # OCR 识别中 (只显示红色框)
    OUTPUT_PROCESSING = auto()  # 输出模式 (只显示蓝色框，点击获焦输入)
    AUTO_CHAT = auto()          # 自动聊天模式 (循环：红框输入 -> AI -> 蓝框输出)

class FSMManager:
    def __init__(self, app):
        self.app = app
        self.states: Dict[AppState, BaseState] = {
            AppState.IDLE: IdleState(app),
            AppState.OCR_PROCESSING: OcrProcessingState(app),
            AppState.OUTPUT_PROCESSING: OutputProcessingState(app),
            AppState.AUTO_CHAT: AutoChatState(app)
        }
        self.current_state_handler: Optional[BaseState] = self.states[AppState.IDLE]
        self.current_state_enum: AppState = AppState.IDLE

    def switch_state(self, new_state_enum: AppState):
        """Switch the application state."""
        if new_state_enum in self.states:
            if self.current_state_handler:
                self.current_state_handler.exit()
            
            self.current_state_handler = self.states[new_state_enum]
            self.current_state_enum = new_state_enum
            self.current_state_handler.enter()

    def run_current_state(self) -> bool:
        """run the logic of the current state."""
        if self.current_state_handler:
            # 1. Run Logic
            keep_running = self.current_state_handler.run()
            if not keep_running:
                return False
            
            # 2. Check Transition
            next_state = self.current_state_handler.change()
            if next_state:
                self.switch_state(next_state)
            
            return True
        return False
