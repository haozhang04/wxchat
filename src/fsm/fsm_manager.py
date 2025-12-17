from typing import Dict, Optional
from rich.console import Console
from .enums import AppState, FSMMode
from .base_state import BaseState
from .state.idle_state import IdleState
from .state.ocr_state import OcrProcessingState
from .state.output_state import OutputProcessingState
from .state.autochat_state import AutoChatState
from .state.edit_state import EditState

console = Console()

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
        self.current_state: AppState = AppState.IDLE_STATE
        self.next_state: Optional[AppState] = None
        self.mode = FSMMode.NORMAL

    def change(self):
        cmd = self.app._get_ui_cmd()
        if cmd == 'exit':
            return AppState.EXIT
        elif cmd == 'edit':
            return AppState.EDIT_STATE
        elif cmd == 'ocr':
            return AppState.OCR_STATE
        elif cmd == 'autochat':
            return AppState.AUTOCHAT_STATE
        elif cmd == 'output':
            return AppState.OUTPUT_STATE
        elif cmd == 'idle':
            return AppState.IDLE_STATE
        return None

    def run_current_state(self) -> bool:
        """run the logic of the current state."""
        if self.mode == FSMMode.NORMAL:
            # 1. Run Logic
            self.current_state_handler.run()
        
            # 2. Check Transition
            next_state = self.change()
            if next_state and next_state != self.current_state:
                self.mode = FSMMode.CHANGE
                self.next_state = next_state
                
        elif self.mode == FSMMode.CHANGE:
            console.print(f"[bold yellow][FSM] Switched from[/bold yellow] [bold magenta]{self.current_state.name}[/bold magenta] [bold yellow]to[/bold yellow] [bold magenta]{self.next_state.name}[/bold magenta]")
            self.current_state_handler.exit()
            if self.next_state == AppState.EXIT:
                return False
            self.current_state_handler = self.states[self.next_state]
            self.current_state = self.next_state
            self.current_state_handler.enter()
            self.mode = FSMMode.NORMAL

        return True