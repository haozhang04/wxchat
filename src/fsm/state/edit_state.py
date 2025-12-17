from rich.console import Console
from ..base_state import BaseState
from ..enums import AppState

console = Console()

class EditState(BaseState):
    def __init__(self, app):
        super().__init__(app)
        self.overlay = self.app.overlay
        self.next_state = None

    def enter(self):
        self.overlay.update_state(True, self.app.ocr_enabled)
        self.next_state = None

    def exit(self):
        # 退出编辑模式
        self.overlay.update_state(False, False)
        # 刷新配置
        self.overlay.reload_config()
        # self.app.update_rects() # Removed: State fetches directly

    def change(self):
        return self.next_state

    def run(self):
        try:
            prompt_text = "[yellow][EDIT_STATE][/yellow] 输入 'done' 或 'lock' 结束 > "
            user_input = self.app._get_input(prompt_text)
        except KeyboardInterrupt:
            return True
        except EOFError:
            return False

        if user_input is None:
            return True

        cmd = user_input.strip().lower()

        if cmd == 'done' or cmd == 'lock' or cmd == 'chat':
            self.next_state = AppState.IDLE_STATE
            return True
        elif cmd == 'autochat':
            self.next_state = AppState.AUTOCHAT_STATE
            return True
        elif cmd == 'ocr_processing':
            self.next_state = AppState.OCR_STATE
            return True
        elif cmd == 'output':
            self.app.post_command('output') # Re-queue
            self.next_state = AppState.IDLE_STATE
            return True
        
        return True
