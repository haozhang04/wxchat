import ollama
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from config import DEFAULT_MODEL, SYSTEM_PROMPT
from src.core.memory import MemoryManager
import json

console = Console()
memory_manager = MemoryManager()
def process_with_ai(user_prompt, ocr_text=None, model=DEFAULT_MODEL):
    """
    使用模型处理 (流式输出)
    """

    # 检查输入
    if not user_prompt or not user_prompt.strip():
        if not ocr_text: 
            return None

    try:
        #1. 构建消息列表
        messages = [
            {'role': 'system', 'content': SYSTEM_PROMPT}
        ]
        
        #2. 扩展历史消息
        if memory_manager:
             messages.extend(memory_manager.get_context())
        
        #3. 构建当前用户消息
        user_msg = f"用户输入: {user_prompt}"

        #4. 添加OCR识别内容
        if ocr_text:
            user_msg += f"\n\n[OCR 识别到的屏幕内容]:\n{ocr_text}"
            
        messages.append({'role': 'user', 'content': user_msg})

        #打印总消息
        console.print(Panel(json.dumps(messages, indent=2, ensure_ascii=False), title="总消息", border_style="green"))

        full_content = ""
        
        # 使用 Live 进行流式显示
        with Live(Panel(Spinner("dots", text="思考中...", style="cyan"), title="AI 回复", border_style="cyan"), console=console, refresh_per_second=12) as live:
            response = ollama.chat(model=model, messages=messages, stream=True)
            
            for chunk in response:
                content = chunk['message']['content']
                full_content += content
                live.update(Panel(Markdown(full_content), title="AI 回复", border_style="cyan"))
        
        # 5. 更新记忆
        if memory_manager:
            memory_manager.add_user_message(user_msg)
            memory_manager.add_ai_message(full_content)
            
        return full_content
        
    except Exception as e:
        console.print(f"[bold red]Ollama 调用错误:[/bold red] {e}")
        return None
