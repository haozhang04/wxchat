# Gemini AI Assistant
一个基于大语言模型的智能终端助手，集成了屏幕 OCR 识别、上下文记忆管理和多模态交互功能。它能够“看见”你的屏幕内容，并基于此进行智能对话。

## 🌟 核心特性

- **🤖 多模型支持**: 无缝集成 Ollama，支持 Qwen2.5, GLM-4, DeepSeek 等多种开源大模型，支持流式输出。
- **🧠 智能记忆管理**: 
  - **自动记录**: 完整记录对话历史。
  - **自动压缩**: 独创的记忆压缩算法，当对话过长时，自动调用 AI 生成**中文摘要**，在保留关键信息的同时无限延长对话轮次。
- **👁️ 屏幕 OCR**: 内置 RapidOCR，支持截取屏幕指定区域并提取文字，实现“所见即所问”。
- **🎮 状态机架构**: 基于 FSM (有限状态机) 设计，支持多种工作模式（闲置、编辑、OCR、自动对话等）的流畅切换。
- **🎨 沉浸式终端 UI**: 使用 `rich` 库打造的现代化终端界面，支持 markdown 渲染、加载动画和彩色日志。
- **⚡ 高效交互**: 支持全局覆盖层 (Overlay) 指示，提供快捷键操作。

## 🚀 快速开始

### 1. 环境准备

- **Python**: 3.8 或更高版本。
- **Ollama**: 请确保本地或远程服务器已安装并运行 [Ollama](https://ollama.com/)。

### 2. 安装

```bash
# 克隆项目
git clone <repository_url>
cd gemini

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置

项目根目录下的 `config.py` 是核心配置文件，你可以根据需要修改：

```python
# config.py

# Ollama 服务地址
BASE_URL = "http://localhost:11434"

# 默认使用的模型 (需确保 Ollama 已拉取该模型)
DEFAULT_MODEL = "qwen2.5-coder:14b"

# 系统提示词 (设定 AI 的人设)
SYSTEM_PROMPT = "..."
```

### 4. 运行

```bash
python main.py
```

## 📖 使用指南

程序启动后会进入 **IDLE (闲置)** 状态，终端会显示操作菜单。

### 常用指令

| 指令/按键 | 功能 | 说明 |
| :--- | :--- | :--- |
| **Enter** | **捕获并识别** | 截取当前蓝色框内的屏幕内容，进行 OCR 识别并发送给 AI。 |
| **edit** | **调整区域** | 进入编辑模式，调整屏幕截图区域的位置和大小。 |
| **autochat** | **自动对话** | 进入自动对话模式 (FSM 状态)。 |
| **exit** | **退出** | 退出程序。 |
| **Ctrl+C** | **中断** | 打断当前的 AI 生成或退出当前状态。 |

### 记忆管理系统详解

Gemini AI Assistant 并不是简单地丢弃旧消息，而是采用了一种更智能的策略：

1.  **阈值触发**: 当对话历史超过设定的阈值 (默认为 20 条) 时。
2.  **智能摘要**: 系统提取最早的一半历史记录，发送给 AI 要求生成一份**中文摘要**。
3.  **上下文注入**: 这份摘要会作为 System Prompt 的一部分注入到新的对话中。
4.  **无感体验**: 用户感知不到记忆的丢失，但 AI 却能一直保持对上下文的理解。

*调试提示: 当触发记忆压缩时，控制台会显示黄色的 "记忆压缩 Prompt" 面板。*

## 🛠️ 项目结构

```
gemini/
├── src/
│   ├── core/
│   │   ├── ai_processor_memory.py  # AI 交互核心 (含记忆逻辑)
│   │   ├── memory.py               # 记忆管理器 (实现自动压缩)
│   │   ├── app.py                  # 应用主逻辑
│   │   └── ...
│   ├── fsm/                        # 有限状态机
│   │   ├── fsm_manager.py          # 状态管理器
│   │   └── state/                  # 各个状态实现 (Idle, OCR, Edit 等)
│   ├── ui/                         # UI 组件
│   ├── utils/                      # 工具类 (Overlay 等)
│   └── text_processing/            # 文本处理
├── config.py                       # 配置文件
├── main.py                         # 程序入口
├── requirements.txt                # 依赖列表
└── README.md                       # 说明文档
```

## 🔧 常见问题

**Q: 报错 `ConnectionRefusedError`?**
A: 请检查 Ollama 服务是否已启动，且 `config.py` 中的 `BASE_URL` 配置正确。

**Q: OCR 识别率低?**
A: 请确保截取区域清晰，且文字大小适中。RapidOCR 对标准字体的识别效果最好。

**Q: 如何切换模型?**
A: 修改 `config.py` 中的 `DEFAULT_MODEL`，或者在代码中扩展模型切换逻辑。

## 📝 许可证

本项目采用 [MIT License](LICENSE) 许可证。

---
*Built with ❤️ by Gemini AI Assistant Team*
