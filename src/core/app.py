import time
import queue
import msvcrt

from rich.panel import Panel
from rich.console import Console

from config import DEFAULT_MODEL
from src.utils.screen_region_config import ScreenRegionConfig
from src.fsm import AppState, FSMManager
from src.utils.overlay import Overlay
from tools_pkg.RapidOCR import TextRecognizer
from src.core.ai_processor import process_with_ai

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
        self.ocr_enabled = False

    def post_ui_command(self, cmd):
        self.ui_command = cmd

    def _get_ui_cmd(self):
        cmd = self.ui_command
        self.ui_command = None
        return cmd

    def _get_input(self, prompt_text, expected_state=None):
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

            # 2. Check terminal input
            if msvcrt.kbhit():
                try:
                    return input()
                except EOFError:
                    return "exit"

            time.sleep(0.05)
                    
    def handle_chat_interaction(self, user_input=None, ocr_text=None):
        """
        Handle chat interaction:
        1. Get user input
        2. Process with AI (allow Ctrl+C interruption)
        """
        # Process with AI
        try:
            ai_output = process_with_ai(user_input, ocr_text, model=self.current_model)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]AI 思考已打断[/bold yellow]")
        return ai_output

    # =========================================================================
    # Main Loop
    # =========================================================================
    def run(self):
        """Start the application main loop."""
        menu_content = f"""模型: [bold]{DEFAULT_MODEL}[/bold]
        [bold yellow]Enter[/bold yellow] : 捕获并识别
        [bold cyan]edit[/bold cyan]  : 调整框位置
        [bold red]exit[/bold red]  : 退出程序
        [bold magenta]Ctrl+C[/bold magenta]: 打断 AI 思考
        [bold magenta]Ctrl+D[/bold magenta]: 强制退出 (Windows 上可能需要 Ctrl+Z + Enter)"""
        console.print(Panel(menu_content, title="AI", expand=False, border_style="bold magenta"))
        
        # Start global services
        self.overlay.start()
        
        try:
            while True:
                # run current state logic
                if not self.fsm_manager.run_current_state():
                    break
        finally:
            self.overlay.stop()
