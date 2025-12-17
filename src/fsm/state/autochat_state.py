from ..base_state import BaseState
from ..enums import AppState
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
        self.overlay = self.app.overlay
        self.text_recognizer = self.app.text_recognizer

    def enter(self):
        self.overlay.update_state(False)
        # 当刚进入AutoChat时，初始化last_ocr_text为当前的屏幕内容，
        try:
            red_box = self.overlay.get_region_rect("response_region")
            if red_box:
                self.last_ocr_text = self.text_recognizer.ocr_recognize_region(red_box, filter_right=True)
                console.print(f"[dim]初始化当前的屏幕内容 ({len(self.last_ocr_text) if self.last_ocr_text else 0} 字符)[/dim]")
        except Exception:
            pass

    def exit(self):
        self.overlay.update_state(False, visible_regions=[])

    def run(self):

        red_box = self.overlay.get_region_rect("response_region")
        blue_box = self.overlay.get_region_rect("input_box")

        if not red_box or not blue_box:
            console.print("[red]错误:[/red] 请使用覆盖层设置区域。")
            return False 

        # 1. OCR Step
        ocr_text = None
        try:
            ocr_text = self.text_recognizer.ocr_recognize_region(red_box, filter_right=True)
        except Exception as e:
            console.print(f"[red]OCR 出错: {e}[/red]")

        # 计算增量内容
        new_content = TextSimilarity.get_incremental_content(self.last_ocr_text, ocr_text)
        
        # 如果没有新内容，直接跳过
        if not new_content:
             # 如果整体有变化但没有提取出有效新行（可能是 OCR 抖动），更新 last_ocr_text 以便下次比较
             if ocr_text: 
                 self.last_ocr_text = ocr_text
             return True

        # 去重检查：防止识别到自己刚才发送的消息 (检查 new_content)
        if hasattr(self.app, 'last_sent_msg') and self.app.last_sent_msg:
            is_dup, reason = TextSimilarity.is_duplicate_message(new_content, self.app.last_sent_msg)
            
            if is_dup:
                console.print(f"[dim]跳过疑似重复/自身发送的内容 ({reason})[/dim]")
                self.last_ocr_text = ocr_text
                return True

        # 2. Process valid new content
        self.last_ocr_text = ocr_text 
        
        # 关键词过滤 (ROS)
        # 检查是否包含 ros 关键词 (模糊匹配，且不匹配 rose 等昵称)
        # clean_msg = new_content.strip()
        # if not TextSimilarity.has_trigger_keyword(clean_msg, "ros"):
        #     console.print(f"[dim]忽略: 内容未包含 'ros' 关键词前缀[/dim] {clean_msg}")
        #     return True
            
        console.print(Panel.fit(new_content, title="新增识别内容", border_style="dim"))
        
        # 3. AI Process
        ai_output = self.app.handle_chat_interaction(user_input=new_content, ocr_text=None)