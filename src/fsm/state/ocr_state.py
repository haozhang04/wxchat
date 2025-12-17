from ..base_state import BaseState
from ..enums import AppState
from src.core.ai_processor import process_with_ai
from rich.console import Console

console = Console()

class OcrProcessingState(BaseState):
    def __init__(self, app):
        super().__init__(app)
        self.next_state = None
        self.overlay = self.app.overlay
        self.text_recognizer = self.app.text_recognizer

    def enter(self):
        self.overlay.update_state(False, True, visible_regions=['response_region', 'input_box'])
        self.next_state = None

    def exit(self):
        # Hide boxes when leaving
        self.overlay.update_state(False, False, visible_regions=None)

    def change(self):
        return self.next_state

    def run(self):
        ocr_text = None
        red_box = self.overlay.get_region_rect("response_region")
        
        with console.status("[bold red]正在捕获屏幕并识别文本...[/bold red]"):
            try:
                if red_box:
                    img = self.text_recognizer.capture_region(red_box)
                    ocr_text = self.text_recognizer.extract_text(img)
                else:
                    console.print("[red]错误: 未找到红色识别区域 (response_region)[/red]")
                    ocr_text = None
                
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
                    self.next_state = AppState.OUTPUT_STATE
                else:
                    self.next_state = AppState.IDLE_STATE
                    
        except KeyboardInterrupt:
            console.print("\n[bold yellow]AI 思考已打断[/bold yellow]")
            self.next_state = AppState.IDLE_STATE

        return True
