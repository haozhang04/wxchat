import time
import queue
import msvcrt

from rich.console import Console
from rich.panel import Panel

from config import DEFAULT_MODEL
from src.utils.overlay import Overlay
from tools_pkg.RapidOCR import TextRecognizer
from src.utils.screen_region_config import ScreenRegionConfig
from src.fsm import AppState, FSMManager

console = Console()

class GeminiApp:
    def __init__(self):
        # 1. Initialize Components
        self.overlay_manager = Overlay()
        self.text_recognizer = TextRecognizer()
        
        # 2. Initialize Overlay Regions
        # 添加默认区域（如果配置文件中有记录，会自动使用配置文件的坐标）
        self.overlay_manager.add_region("input_box", "blue", "Input")
        self.overlay_manager.add_region("response_region", "red", "Response")

        # 3. Initialize State Variables
        self.ocr_enabled = False
        self.current_model = DEFAULT_MODEL
        self.autochat_running = False
        self.command_queue = queue.Queue()
        self.context_data = {}

        # 5. Initialize FSM Manager
        self.fsm_manager = FSMManager(self)


    # =========================================================================
    # State Management
    # =========================================================================
    # State management is delegated to self.fsm_manager

    def update_rects(self):
        """Update the region coordinates from the overlay manager."""
        # 仅从内存更新，不读取文件
        self.red_box = self.overlay_manager.get_region_rect("response_region")
        self.blue_box = self.overlay_manager.get_region_rect("input_box")

    def set_model(self, model_name):

        """Set the current AI model."""
        self.current_model = model_name
        console.print(f"[green]模型已切换为: {self.current_model}[/green]")

    def stop_autochat(self):
        """Stop the auto-chat loop."""
        self.autochat_running = False

    def _print_menu(self):
        """Print the operation menu."""
        menu_content = f"""模型: [bold]{DEFAULT_MODEL}[/bold]
  [bold yellow]Enter[/bold yellow] : 捕获并识别
  [bold cyan]edit[/bold cyan]  : 调整框位置
  [bold cyan]done[/bold cyan]  : 完成调整并锁定
  [bold red]exit[/bold red]  : 退出程序
  [bold magenta]Ctrl+C[/bold magenta]: 打断 AI 思考
  [bold magenta]Ctrl+D[/bold magenta]: 强制退出 (Windows 上可能需要 Ctrl+Z + Enter)"""
        console.print(Panel(menu_content, title="操作菜单", expand=False))

    # =========================================================================
    # Input Handling
    # =========================================================================
    def post_command(self, cmd):
        """Allow external sources (like UI) to post commands."""
        self.command_queue.put(cmd)

    def _get_input(self, prompt_text):
        """
        Custom input function that waits for either:
        1. Terminal input
        2. Queue command
        """
        console.print(prompt_text, end="")
        
        while True:
            # 1. Check Queue
            if not self.command_queue.empty():
                cmd = self.command_queue.get()
                console.print(f"{cmd} (from UI)")
                return cmd

            # 2. Check Terminal Input
            if msvcrt.kbhit():
                # If user starts typing, we fallback to standard input() to handle editing properly
                try:
                    return input()
                except EOFError:
                    return "exit"
            
            time.sleep(0.1)

    # =========================================================================
    # Main Loop
    # =========================================================================
    def run(self):
        """Start the application main loop."""
        console.print(Panel.fit("Ollama 智能助手", style="bold magenta"))
        self._print_menu()
        self.overlay_manager.start()
        
        try:
            # Ensure initial state is locked
            self.overlay_manager.update_state(False, self.ocr_enabled)
            
            # Initial rect update
            self.update_rects()

            # Start FSM
            self.fsm_manager.switch_state(AppState.IDLE)

            while True:
                # run current state logic
                if not self.fsm_manager.run_current_state():
                    break


        finally:
            self.overlay_manager.stop()
