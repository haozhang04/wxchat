import ollama
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from config import DEFAULT_MODEL, SYSTEM_PROMPT

console = Console()

def process_with_ai(user_prompt, ocr_text=None, model=DEFAULT_MODEL, history=None):
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
        if history:
             messages.extend(history)
        
        #3. 构建当前用户消息
        user_msg = f"用户输入: {user_prompt}"

        #4. 添加OCR识别内容
        if ocr_text:
            user_msg += f"\n\n[OCR 识别到的屏幕内容]:\n{ocr_text}"
            
        messages.append({'role': 'user', 'content': user_msg})

        full_content = ""
        
        # 使用 Live 进行流式显示
        with Live(Panel("...", title="AI 回复", border_style="cyan"), console=console, refresh_per_second=12) as live:
            response = ollama.chat(model=model, messages=messages, stream=True)
            
            for chunk in response:
                content = chunk['message']['content']
                full_content += content
                live.update(Panel(Markdown(full_content), title="AI 回复", border_style="cyan"))
        
        return full_content
        
    except Exception as e:
        console.print(f"[bold red]Ollama 调用错误:[/bold red] {e}")
        return None
