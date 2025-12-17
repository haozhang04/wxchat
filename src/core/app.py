import time
import msvcrt

from rich.panel import Panel
from rich.console import Console

from config import DEFAULT_MODEL
from src.fsm import AppState, FSMManager
from src.utils.overlay import Overlay
from tools_pkg.RapidOCR import TextRecognizer
from src.core.ai_processor_memory import process_with_ai 

console = Console()

class App:
    def __init__(self):
        # 共享资源
        self.overlay = Overlay()
        self.text_recognizer = TextRecognizer()

        self.fsm_manager = FSMManager(self)

        # Initialize default regions
        self.overlay.add_region("response_region", "red", "Response Region")
        self.overlay.add_region("input_box", "blue", "Input Box")
        
        self.current_model = DEFAULT_MODEL
        self.ui_command = None

    def post_ui_command(self, cmd):
        self.ui_command = cmd

    def set_model(self, model_name):
        self.current_model = model_name
        console.print(f"\n[green][APP] Model switched to: {model_name}[/green]")

    def _get_ui_cmd(self):
        cmd = self.ui_command
        self.ui_command = None
        return cmd

    def _get_input(self, prompt_text):
        """
        自定义输入函数，用于同时等待：
        1. 终端键盘输入
        2. 状态切换（来自 UI）
        """
        console.print(prompt_text, end="")
        
        while True:
            # 1. Check UI command
            if self.ui_command:
                return None
            
            # 2. Check keyboard input
            if msvcrt.kbhit():
                return input()

            time.sleep(0.05)
                    
    def handle_chat_interaction(self, user_input=None, ocr_text=None):
        return process_with_ai(user_input, ocr_text, model=self.current_model)

    # =========================================================================
    # Main Loop
    # =========================================================================
    def run(self):
        """Start the application main loop."""
        menu_content = f"""
        [bold magenta][模型: {DEFAULT_MODEL}][/bold magenta]
        [bold yellow]Enter[/bold yellow] : 捕获并识别
        [bold cyan]edit[/bold cyan]  : 调整框位置
        [bold red]exit[/bold red]  : 退出程序
        [bold magenta]Ctrl+C[/bold magenta]: 打断 AI 思考
        [bold magenta]Ctrl+D[/bold magenta]: 强制退出
        """
        console.print(Panel(menu_content, title="AI", expand=False, border_style="bold magenta"))
        
        # Start global services
        self.overlay.start()
        
        try:
            while True:
                try:
                    # run current state logic
                    if not self.fsm_manager.run_current_state():
                        break
                except KeyboardInterrupt:
                    console.print("\n[bold yellow]操作已取消 (Ctrl+C)[/bold yellow]")
        finally:
            self.overlay.stop()
