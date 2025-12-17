from typing import Dict, Optional
from .enums import AppState, FSMMode
from .base_state import BaseState
from .state.idle_state import IdleState
from .state.ocr_state import OcrProcessingState
from .state.output_state import OutputProcessingState
from .state.autochat_state import AutoChatState
from .state.edit_state import EditState


class FSMManager:
    def __init__(self, app):
        self.app = app
        self.states: Dict[AppState, BaseState] = {
            AppState.IDLE_STATE: IdleState(app),
            AppState.OCR_STATE: OcrProcessingState(app),
            AppState.OUTPUT_STATE: OutputProcessingState(app),
            AppState.AUTOCHAT_STATE: AutoChatState(app),
            AppState.EDIT_STATE: EditState(app)
        }
        self.current_state_handler: Optional[BaseState] = self.states[AppState.IDLE_STATE]
        self.current_state_enum: AppState = AppState.IDLE_STATE
        self.mode = FSMMode.NORMAL
        self.next_state_enum: Optional[AppState] = None

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
            
            if self.mode == FSMMode.NORMAL:
                # 1. Run Logic
                keep_running = self.current_state_handler.run()
                if not keep_running:
                    return False
                
                # 2. Check Transition
                next_state = self.current_state_handler.change()
                if next_state and next_state != self.current_state_enum:
                    self.mode = FSMMode.CHANGE
                    self.next_state_enum = next_state
                    # print(f"Switched from {self.current_state_enum.name} to {self.next_state_enum.name}")
            
            elif self.mode == FSMMode.CHANGE:
                if self.next_state_enum and self.next_state_enum in self.states:
                    if self.current_state_handler:
                        self.current_state_handler.exit()
                    
                    self.current_state_handler = self.states[self.next_state_enum]
                    self.current_state_enum = self.next_state_enum
                    self.current_state_handler.enter()
                    
                    self.mode = FSMMode.NORMAL
                    self.current_state_handler.run()
                else:
                    self.mode = FSMMode.NORMAL

            return True
        return False
