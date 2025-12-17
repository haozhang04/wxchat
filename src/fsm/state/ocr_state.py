from ..base_state import BaseState
from ..fsm_manager import AppState
from src.core.ai_processor import process_with_ai
from rich.console import Console

console = Console()

class OcrProcessingState(BaseState):
    def __init__(self, app):
        super().__init__(app)
        self.next_state = None

    def enter(self):
        # self.app.current_state_enum is already updated
        self.app.overlay_manager.update_state(False, True, visible_regions=['response_region'])
        self.next_state = None

    def exit(self):
        pass

    def change(self):
        return self.next_state

    def run(self):
        ocr_text = None
        with console.status("[bold red]正在捕获屏幕并识别文本...[/bold red]"):
            try:
                img = self.app.text_recognizer.capture_region(self.app.red_box)
                ocr_text = self.app.text_recognizer.extract_text(img)
                
                if ocr_text:
                    self.app.context_data['ocr_text'] = ocr_text
                else:
                    self.app.context_data['ocr_text'] = None
                    
            except Exception as e:
                console.print(f"[red]OCR 过程出错: {e}[/red]")
                self.app.context_data['ocr_text'] = None
        
        # AI Processing
        user_input = self.app.context_data.get('user_input', '')
        
        try:
            with console.status(f"[bold cyan]思考中 ({self.app.current_model}) - 按 Ctrl+C 打断...[/bold cyan]"):
                content = process_with_ai(user_input, ocr_text, console, model=self.app.current_model)
                
                if content:
                    self.app.context_data['ai_content'] = content
                    self.next_state = AppState.OUTPUT_PROCESSING
                else:
                    self.next_state = AppState.IDLE
                    
        except KeyboardInterrupt:
            console.print("\n[bold yellow]AI 思考已打断[/bold yellow]")
            self.next_state = AppState.IDLE

        return True
