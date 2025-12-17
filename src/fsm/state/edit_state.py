from rich.console import Console
from ..base_state import BaseState
from ..enums import AppState

console = Console()

class EditState(BaseState):
    def __init__(self, app):
        super().__init__(app)
        self.overlay = self.app.overlay

    def enter(self):
        self.overlay.update_state(True)
        console.print("[yellow]进入编辑模式。请在覆盖层上拖动/调整区域。[/yellow]")   

    def exit(self):
        # 退出编辑模式
        self.overlay.update_state(False, visible_regions=[])
        self.overlay.reload_config()

    def run(self):
        pass