from ..base_state import BaseState
from ..enums import AppState
from src.utils.auto_paste import perform_blue_box_action
from rich.console import Console

console = Console()

class OutputProcessingState(BaseState):
    def __init__(self, app):
        super().__init__(app)
        self.overlay = self.app.overlay

    def enter(self):
        # Show Blue box (input_box)
        self.overlay.update_state(False, visible_regions=['input_box'])

    def exit(self):
        # Restore overlay
        self.overlay.update_state(False, visible_regions=None)

    def run(self):
        prompt_text = f"[green][{self.app.fsm_manager.current_state.name}][/green] User: "
        user_input = self.app._get_input(prompt_text)
        ai_output = self.app.handle_chat_interaction(user_input=user_input, ocr_text=None)
        blue_box = self.overlay.get_region_rect("input_box")
        
        if blue_box:
            perform_blue_box_action(ai_output, blue_box)
        elif not blue_box:
             console.print("[red]错误: 未找到蓝色输入区域 (input_box)[/red]")

