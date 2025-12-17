from ..base_state import BaseState
from ..enums import AppState
from rich.console import Console

console = Console()

class IdleState(BaseState):
    def __init__(self, app):
        super().__init__(app)
        self.next_state = None

    def enter(self):
        self.next_state = None

    def exit(self):
        pass

    def change(self):
        cmd = self.app.context_data.get('user_input', '').strip().lower()
        if cmd == 'exit':
            self.next_state = AppState.EXIT
        elif cmd == 'edit':
            self.next_state = AppState.EDIT_STATE
        elif cmd == 'ocr':
            self.next_state = AppState.OCR_STATE
        elif cmd == 'autochat':
            self.next_state = AppState.AUTOCHAT_STATE
        elif cmd == 'output':
            self.next_state = AppState.OUTPUT_STATE  

        return self.next_state

    def run(self):
            status_text = f"[{self.fsm_manager.current_state_enum.name}]"
            prompt_text = f"[green]{status_text}[/green] User > "
            user_input = self._get_input(prompt_text)
            self.app.handle_chat_interaction(user_input=user_input, ocr_text=None)

        return 
