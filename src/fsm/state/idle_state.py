from ..base_state import BaseState
from ..enums import AppState
from rich.console import Console

console = Console()

class IdleState(BaseState):
    def __init__(self, app):
        super().__init__(app)

    def enter(self):
        pass

    def exit(self):
        pass

    def run(self):
        prompt_text = f"[green][{self.app.fsm_manager.current_state.name}][/green] User: "
        user_input = self.app._get_input(prompt_text)
        ai_output = self.app.handle_chat_interaction(user_input=user_input, ocr_text=None)
