from ..base_state import BaseState
from ..enums import AppState
from src.core.ai_processor import process_with_ai
from rich.console import Console

console = Console()

class OcrProcessingState(BaseState):
    def __init__(self, app):
        super().__init__(app)
        self.overlay = self.app.overlay
        self.text_recognizer = self.app.text_recognizer

    def enter(self):
        self.overlay.update_state(False, True, visible_regions=['response_region', 'input_box'])

    def exit(self):
        # Hide boxes when leaving
        self.overlay.update_state(False, False, visible_regions=None)

    def run(self):
        ocr_text = None
        red_box = self.overlay.get_region_rect("response_region")
        with console.status("[bold red]正在捕获屏幕并识别文本...[/bold red]"):
            try:
                if red_box:
                    ocr_text = self.text_recognizer.ocr_recognize_region(red_box)
                else:
                    console.print("[red]错误: 未找到红色识别区域 (response_region)[/red]")
                    ocr_text = None
            except Exception as e:
                console.print(f"[red]OCR 过程出错: {e}[/red]")
                ocr_text = None
        
        # AI Processing
        prompt_text = f"[green][{self.app.fsm_manager.current_state.name}][/green] User: "
        user_input = self.app._get_input(prompt_text)
        ai_output = self.app.handle_chat_interaction(user_input=user_input, ocr_text=ocr_text)
