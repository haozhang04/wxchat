from rich.prompt import Prompt
from ..base_state import BaseState
from ..fsm_manager import AppState
from src.core.ai_processor import process_with_ai
from rich.console import Console

console = Console()

class IdleState(BaseState):
    def __init__(self, app):
        super().__init__(app)
        self.next_state = None

    def enter(self):
        # self.app.current_state_enum is already updated in switch_state
        self.app.overlay_manager.update_state(False, self.app.ocr_enabled)
        self.next_state = None

    def exit(self):
        pass

    def change(self):
        return self.next_state

    def run(self):
        try:
            # status_text = "[OCR开启]" if self.app.ocr_enabled else "[OCR关闭]"
            status_text = f"[{self.app.fsm_manager.current_state_enum.name}]"
            color = "green" if self.app.ocr_enabled else "dim white"
            prompt_text = f"[{color}]{status_text}[/{color}] 用户输入 > "
            
            # Use the app's custom input method that supports queue
            user_input = self.app._get_input(prompt_text)
            
        except KeyboardInterrupt:
            console.print()
            return True
        except EOFError:
            console.print("\n[bold red]强制退出...[/bold red]")
            return False

        if user_input is None: # Should not happen with _get_input loop but safety check
            return True

        cmd = user_input.strip().lower()

        if cmd == 'exit':
            return False
        elif cmd == 'edit':
            self.app.overlay_manager.update_state(True, self.app.ocr_enabled)
            console.print("[yellow]已进入编辑模式 (在 UI 中点击 Lock 结束)[/yellow]")
            return True
        elif cmd == 'done' or cmd == 'lock':
            self.app.overlay_manager.update_state(False, self.app.ocr_enabled)
            # 用户可能调整了位置，手动刷新一次
            self.app.overlay_manager.reload_config()
            self.app.update_rects()
            return True
        elif cmd == 'ocr':
            self.app.ocr_enabled = not self.app.ocr_enabled
            state = "开启" if self.app.ocr_enabled else "关闭"
            console.print(f"[yellow]OCR 功能已{state}[/yellow]")
            self.app.overlay_manager.update_state(False, self.app.ocr_enabled)
            return True
        elif cmd == 'autochat':
            self.next_state = AppState.AUTO_CHAT
            return True
        elif cmd == 'output':
             # Prompt for user input
             user_prompt = self.app._get_input("[cyan]请输入发送给 AI 的内容 > [/cyan]")
             if not user_prompt or not user_prompt.strip():
                 return True

             self.app.context_data['user_input'] = user_prompt
             self.app.context_data['force_paste'] = True
             
             try:
                 with console.status(f"[bold cyan]思考中 ({self.app.current_model}) - 按 Ctrl+C 打断...[/bold cyan]"):
                    content = process_with_ai(user_prompt, None, console, model=self.app.current_model)
                    
                    if content:
                        self.app.context_data['ai_content'] = content
                        self.next_state = AppState.OUTPUT_PROCESSING
                        
             except KeyboardInterrupt:
                console.print("\n[bold yellow]AI 思考已打断[/bold yellow]")

             return True
        elif cmd == 'chat':
             user_input = "" 
        
        # Only skip if input is empty AND OCR is OFF (no text to process)
        if not user_input.strip() and not self.app.ocr_enabled:
            return True

        self.app.update_rects()
        
        if not self.app.red_box or not self.app.blue_box:
            console.print("[red]错误:[/red] 请使用覆盖层设置区域。")
            return True

        # Store user input for next states
        self.app.context_data['user_input'] = user_input
        
        # Decide next state
        if self.app.ocr_enabled:
            self.next_state = AppState.OCR_PROCESSING
        else:
             try:
                 with console.status(f"[bold cyan]思考中 ({self.app.current_model}) - 按 Ctrl+C 打断...[/bold cyan]"):
                    process_with_ai(user_input, None, console, model=self.app.current_model)
             except KeyboardInterrupt:
                console.print("\n[bold yellow]AI 思考已打断[/bold yellow]")
            
        return True
