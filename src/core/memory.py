import ollama
from config import DEFAULT_MODEL
from rich.console import Console
from rich.panel import Panel

console = Console()

class MemoryManager:
    def __init__(self, max_len=2):
        self.history = []  
        self.max_len = max_len
        self.summary = ""

    def _compress_memory(self):
        """如果记忆超过最大长度，则进行压缩。"""
        if len(self.history) <= self.max_len:
            return

        # 定义要总结的消息数量（例如，前半部分）
        num_to_summarize = len(self.history) // 2
        
        # 确保有内容可供总结
        if num_to_summarize == 0:
            return

        messages_to_summarize = self.history[:num_to_summarize]
        self.history = self.history[num_to_summarize:]

        # 构建用于 AI 的对话文本
        conversation_text = ""
        for msg in messages_to_summarize:
            role = "User" if msg['role'] == 'user' else "AI"
            conversation_text += f"{role}: {msg['content']}\n"

        prompt = f"""
        现有摘要: {self.summary}
        
        需要合并到摘要的新对话:
        {conversation_text}
        
        请提供一份更新后的、简洁的对话历史摘要。
        请注意：必须使用中文进行回答。
        """

        console.print(Panel(prompt, title="记忆压缩 Prompt", border_style="yellow"))

        try:
            # 调用 AI 生成摘要
            response = ollama.chat(model=DEFAULT_MODEL, messages=[{'role': 'user', 'content': prompt}])
            self.summary = response['message']['content']
        except Exception as e:
            print(f"记忆压缩失败: {e}")

    def add_user_message(self, message):
        """添加用户消息到记忆中。"""
        self.history.append({"role": "user", "content": message})

    def add_ai_message(self, message):
        """添加 AI 消息到记忆中。"""
        self.history.append({"role": "assistant", "content": message})
        self._compress_memory()

    def get_context(self):
        """获取包含摘要的完整对话历史。"""
        context = []
        if self.summary:
            context.append({"role": "system", "content": f"Previous conversation summary: {self.summary}"})
        context.extend(self.history)
        return context

    def clear(self):
        """清空记忆。"""
        self.history.clear()
        self.summary = ""
