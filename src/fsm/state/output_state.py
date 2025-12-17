from ..base_state import BaseState
from ..fsm_manager import AppState
from src.utils.auto_paste import perform_blue_box_action
from rich.console import Console

console = Console()

class OutputProcessingState(BaseState):
    def enter(self):
        self.app.overlay_manager.update_state(False, True, visible_regions=['input_box'])

    def exit(self):
        pass

    def change(self):
        # Output is one-shot, always go back to IDLE
        return AppState.IDLE

    def run(self):
        content = self.app.context_data.get('ai_content')
        if content:
            perform_blue_box_action(content, self.app.blue_box)
        
        # Restore overlay and go back to IDLE
        self.app.overlay_manager.update_state(False, True, visible_regions=None)
        return True
