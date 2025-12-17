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
        self.overlay.update_state(False, True, visible_regions=['input_box'])

    def exit(self):
        # Restore overlay
        self.overlay.update_state(False, self.app.ocr_enabled, visible_regions=None)

    def change(self):
        # Output is one-shot, always go back to IDLE_STATE
        return AppState.IDLE_STATE

    def run(self):
        content = self.app.context_data.get('ai_content')
        blue_box = self.overlay.get_region_rect("input_box")
        
        if content and blue_box:
            perform_blue_box_action(content, blue_box)
        elif not blue_box:
             console.print("[red]错误: 未找到蓝色输入区域 (input_box)[/red]")
        
        return True
