import os

# API 配置
BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")

# 模型列表配置
TARGET_MODELS = [
    "glm-4.6:cloud",
    "qwen2.5-coder:14b",
    "deepseek-v3.1:671b-cloud",    
    "gpt-oss:120b-cloud",    
    "gpt-oss:20b-cloud",         
    "qwen2.5-coder:14b",         
]

# 默认使用的文本模型
DEFAULT_MODEL = "qwen2.5-coder:14b"

# 系统提示词
SYSTEM_PROMPT = """
你现在的设定是一个无所不知、严谨专业的智能助手。
采用微信能接受的格式输出，这很重要
你的任务是：
1. 基于OCR上下文，输出准确、严谨、有理有据的中文回答。
2. 直接输出最终结果，严禁包含客套话或解释性前缀。
3. 回复简炼，简炼，简炼，精准，直击要害。
"""
