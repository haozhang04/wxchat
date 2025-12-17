from rich.console import Console
from ..base_state import BaseState
from ..enums import AppState

console = Console()

class EditState(BaseState):
    def __init__(self, app):
        super().__init__(app)
        self.overlay = self.app.overlay

    def enter(self):
        self.overlay.update_state(True, self.app.ocr_enabled)

    def exit(self):
        # 退出编辑模式
        self.overlay.update_state(False, False)
        self.overlay.reload_config()

    def run(self):
        console.print("[yellow]进入编辑模式。请在覆盖层上拖动/调整区域。[/yellow]")        
        

