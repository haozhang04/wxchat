# 水下机器人GUI控制系统 (UWBot GUI)

一个基于PyQt5开发的水下机器人控制界面系统，提供实时监控、运动控制、摄像头管理和数据可视化功能。

2025年12月15日 初始版本发布。

## 功能特性

- 🎮 **运动控制**: 实时控制水下机器人的运动状态
- 📹 **摄像头管理**: 支持多摄像头实时预览、录制和截图
- 📊 **数据可视化**: 实时显示机器人状态数据和传感器信息
- 📝 **日志系统**: 完整的系统日志记录和查看
- ⚙️ **参数配置**: 灵活的系统参数设置和管理
- 🔄 **实时通信**: 与水下机器人的低延迟数据通信
- 🌐 **LCM通信**: 基于LCM(Lightweight Communications and Marshalling)的实时通信
- 🎯 **多模式控制**: 支持简单模式和控制模式切换
- 📐 **3D可视化**: URDF机器人模型的3D显示

## 环境要求

- **操作系统**: Windows 10/11 或 Linux
- **Python 版本**: 3.9 (推荐)
- **依赖管理**: 推荐使用 Anaconda 或 Miniconda

## 安装与运行

### 1. 克隆项目

```bash
git clone https://gitee.com/haozhang04/uwbot_gui.git
cd uwbot_gui
```

### 2. 环境配置 (推荐使用 Conda)

由于项目依赖对版本有特定要求（如 `networkx`, `PyOpenGL`, `numpy` 等），强烈建议使用 Conda 创建隔离环境。

```bash
# 创建名为 ui 的环境，指定 python 3.9
conda create -n ui python=3.9 -y

# 激活环境
conda activate ui
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

> **注意**: 
> - `requirements.txt` 中已锁定关键库的版本（如 `networkx==2.2`, `PyOpenGL==3.1.0`, `numpy<2.0`），请勿随意升级，否则可能导致 URDF 可视化功能失效。
> - LCM 通信库已包含在依赖列表中。

### 4. 运行程序

```bash
python main.py
```

### 5. 打包程序 (可选)

如果需要将程序打包为独立可执行文件，请使用 `PyInstaller`。

首先安装 PyInstaller：
```bash
pip install pyinstaller
```

**Windows 系统:**
```bash
pyinstaller --noconfirm --clean --onefile --windowed --name uwrobot_gui --add-data "resource;resource" --hidden-import PyQt5.QtSvg --hidden-import lcm main.py
```

**Linux 系统:**
```bash
pyinstaller --noconfirm --clean --onefile --windowed --name uwrobot_gui --add-data "resource:resource" --hidden-import PyQt5.QtSvg --hidden-import lcm main.py
```

## 项目结构

```
uwbot_gui/
├── main.py                 # 主程序入口：负责初始化主窗口、LCM通信、定时器等
├── requirements.txt        # 项目依赖清单
├── config/                 # 配置模块
│   └── uwbot_config.py     # 核心配置文件（网络、相机、运动参数等）
├── ui_modules/             # UI界面模块
│   ├── bar/                # 顶部状态栏（显示电池、连接状态、模式等）
│   ├── camera/             # 摄像头显示组件（支持RTSP流、录制、截图）
│   ├── log_mode/           # 日志查看界面
│   ├── simple_mode/        # 简易模式主界面
│   │   ├── motion/         # 运动控制组件（浮游/轮式控制、清洗功能）
│   │   └── status/         # 状态显示组件（姿态、深度、速度等）
│   └── viewer_mode/        # 3D可视化界面（基于OpenGL显示URDF模型）
├── messages/               # 数据结构定义
│   ├── LowlevelCmd.py      # 下发指令数据类
│   ├── LowlevelState.py    # 反馈状态数据类
│   └── robot_data.py       # 全局机器人数据模型
├── input_dev/              # 输入设备驱动
│   ├── camera/             # 摄像头后台采集线程与视频录制
│   ├── keyboard/           # 键盘事件处理
│   ├── Joystick/           # 游戏手柄驱动（支持双摇杆）
│   └── button/             # 外部物理按钮驱动（串口通信）
├── LCM/                    # 通信模块
│   ├── lcm.py              # LCM通信接口封装（收发线程管理）
│   └── lcm_type/           # 自动生成的LCM消息类型定义
├── utils/                  # 通用工具库
│   ├── urdf_loader/        # URDF模型加载与3D渲染引擎
│   └── math_tool.py        # 数学工具（四元数/欧拉角转换等）
├── resource/               # 静态资源
│   ├── images/             # UI图标和图片资源
│   ├── material/           # 说明文档与辅助脚本
│   └── robot_description/  # 机器人URDF描述文件与STL模型
└── .gitignore              # Git忽略配置
```

## 分支说明

- `1080p_real`: 开发分支
- `1080p稳定`: 主线分支，稳定版本（推荐）
- `1080p_max`、`1080p_old`、`2k`: 历史或其他显示配置

## 开发说明

### 代码规范
- 使用 Python PEP 8 代码规范
- 所有函数和类都应包含详细的中文注释
- 提交代码前请运行测试确保功能正常

### 贡献指南
1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证

## 联系方式

- 项目维护者: HAO ZHANG
- 项目链接: [https://gitee.com/haozhang04/uwbot_gui](https://gitee.com/haozhang04/uwbot_gui)
