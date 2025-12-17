from ..base_state import BaseState
from ..fsm_manager import AppState
from src.core.ai_processor import process_with_ai
from src.core.memory import ChatMemory
from src.utils.auto_paste import perform_blue_box_action
from src.text_processing.similarity import TextSimilarity
from rich.console import Console
import time
import difflib

from rich.panel import Panel

console = Console()

class AutoChatState(BaseState):
    def __init__(self, app):
        super().__init__(app)
        self.last_ocr_text = None
        self.memory = ChatMemory()

    def enter(self):
        # self.app.current_state_enum is already updated
        self.app.autochat_running = True
        self.last_ocr_text = None
        # 当刚进入AutoChat时，初始化last_ocr_text为当前的屏幕内容，
        # 这样可以避免一开始就处理屏幕上已有的内容。
        try:
            if self.app.red_box:
                img = self.app.text_recognizer.capture_region(self.app.red_box)
                self.last_ocr_text = self.app.text_recognizer.extract_text(img, filter_right=True)
                console.print(f"[dim]初始化基准内容 ({len(self.last_ocr_text) if self.last_ocr_text else 0} 字符)[/dim]")
        except Exception:
            pass
            
        console.print("[bold yellow]进入 AutoChat 模式 [/bold yellow]")

    def exit(self):
        self.app.overlay_manager.update_state(False, self.app.ocr_enabled, visible_regions=None)

    def change(self):
        if not self.app.autochat_running:
            return AppState.IDLE
        return None

    def run(self):
        # Check if stopped externally
        if not self.app.autochat_running:
            return True

        # Reload config
        self.app.overlay_manager.reload_config()
        self.app.update_rects()
        if not self.app.red_box or not self.app.blue_box:
            console.print("[red]错误:[/red] 请使用覆盖层设置区域。")
            self.app.autochat_running = False
            return True

        # 1. OCR Step
        # Update overlay to show only red box
        self.app.overlay_manager.update_state(False, True, visible_regions=['response_region'])
        
        ocr_text = None
        try:
            img = self.app.text_recognizer.capture_region(self.app.red_box)
            ocr_text = self.app.text_recognizer.extract_text(img, filter_right=True)
        except Exception as e:
            console.print(f"[red]OCR 出错: {e}[/red]")

        # 计算增量内容
        new_content = TextSimilarity.get_incremental_content(self.last_ocr_text, ocr_text)
        
        # 如果没有新内容，直接跳过
        if not new_content:
             # 如果整体有变化但没有提取出有效新行（可能是 OCR 抖动），更新 last_ocr_text 以便下次比较
             if ocr_text: 
                 self.last_ocr_text = ocr_text
             time.sleep(0.1)
             return True

        # 去重检查：防止识别到自己刚才发送的消息 (检查 new_content)
        if hasattr(self.app, 'last_sent_msg') and self.app.last_sent_msg:
            is_dup, reason = TextSimilarity.is_duplicate_message(new_content, self.app.last_sent_msg)
            
            if is_dup:
                console.print(f"[dim]跳过疑似重复/自身发送的内容 ({reason})[/dim]")
                # 即使跳过了，也要更新 last_ocr_text，因为屏幕确实变了（变成了机器人的回复）
                self.last_ocr_text = ocr_text
                return True

        # 2. Process valid new content
        self.last_ocr_text = ocr_text # 更新基准
        
        # 关键词过滤 (ROS)
        # 检查是否包含 ros 关键词 (模糊匹配，且不匹配 rose 等昵称)
        # clean_msg = new_content.strip()
        # if not TextSimilarity.has_trigger_keyword(clean_msg, "ros"):
        #     console.print(f"[dim]忽略: 内容未包含 'ros' 关键词前缀[/dim] {clean_msg}")
        #     return True
            
        console.print(f"[bold green]发现新内容 (包含关键词)，开始处理...[/bold green]")
        console.print(Panel.fit(new_content, title="新增识别内容", border_style="dim"))
        
        # 3. AI Process
        try:
            # 获取上下文 (不包含当前消息)
            history = self.memory.get_context()
            
            # 打印当前记忆 (Debug)
            console.print(Panel(
                "\n".join([f"[bold {'green' if m['role']=='user' else 'cyan'}]{m['role']}:[/] {m['content']}" for m in history]),
                title="当前对话记忆 (Context)",
                border_style="yellow",
                expand=False
            ))

            content = process_with_ai("请根据屏幕内容进行回复", new_content, console, model=self.app.current_model, history=history)
            
            if content:
                    # 存入用户消息 (完成对话后才存入记忆)
                    self.memory.add_user_message(new_content)
                    # 存入AI回复
                    self.memory.add_ai_message(content)

                    # 4. Output
                    # Show blue box
                    self.app.overlay_manager.update_state(False, True, visible_regions=['input_box'])
                    perform_blue_box_action(content, self.app.blue_box)
                    
                    # 保存发送的内容用于去重
                    if hasattr(self.app, 'last_sent_msg'):
                        self.app.last_sent_msg = content

        except Exception as e:
            console.print(f"[red]AI 处理出错: {e}[/red]")

        # Sleep
        try:
            time.sleep(0.2)
        except KeyboardInterrupt:
            # Catch Ctrl+C inside the loop and exit cleanly
            console.print("\n[bold yellow]AutoChat 循环已停止 (Ctrl+C)[/bold yellow]")
            self.app.autochat_running = False
            self.app.fsm_manager.switch_state(AppState.IDLE)
        
        return True

