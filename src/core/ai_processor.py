import ollama
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from config import DEFAULT_MODEL, SYSTEM_PROMPT

console = Console()

def process_with_ai(user_prompt, ocr_text=None, console=None, model=DEFAULT_MODEL, history=None):
    """
    使用模型处理 (非流式输出)
    """
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

        # 关闭流式输出
        response = ollama.chat(
            model=model,
            messages=messages,
            stream=False
        )
        
        content = response['message']['content']

        console.print() # 空行，用于分隔“思考中”和结果
        console.print(Panel(Markdown(content), title="AI 回复", border_style="cyan"))
        
        return content
        
    except Exception as e:
        console.print(f"[bold red]Ollama 调用错误:[/bold red] {e}")
        return None
