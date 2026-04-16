# Cantoplay: 粤韵茶楼

基于Streamlit的粤语学习游戏应用 - 模块化重构版本

## 🎯 项目简介

这是一个通过游戏化方式学习粤语的Web应用。用户可以在不同的场景（茶楼、花市、骑楼、大排档）中与AI NPC进行粤语对话，学习粤语词汇和文化知识。

## 🏗️ 项目结构

```
cantoplayv2/
├── main.py                 # 应用入口
├── requirements.txt        # 依赖列表
├── README.md              # 项目说明
├── .streamlit/
│   └── secrets.toml.example  # 配置文件示例
│
├── backend/               # 后端模块
│   ├── __init__.py
│   ├── config.py          # 配置和常量
│   ├── api_client.py      # LLM API客户端
│   ├── prompts.py         # Prompt工程
│   └── game_logic.py      # 游戏逻辑
│
├── frontend/              # 前端模块
│   ├── __init__.py
│   ├── utils.py           # 工具函数
│   ├── components.py      # UI组件
│   └── pages.py           # 页面逻辑
│
└── tts/                   # TTS模块（独立功能）
    ├── __init__.py
    └── cantonese_tts.py   # 粤语语音合成
```

## ✨ 新增功能

### 1. 代码模块化
- **backend/**: 后端逻辑分离，包含配置、API调用、游戏逻辑
- **frontend/**: 前端UI组件化，便于维护和扩展
- **tts/**: 独立的粤语TTS模块

### 2. 粤语朗读功能
- 使用小米MiMo V2 TTS模型（OpenAI兼容接口）
- 支持`<style>粤语</style>`风格标签控制方言输出
- 内置音色：mimo_default（中性）、default_zh（中文女声）、default_en（英文女声）
- AI回复后自动生成粤语语音，内嵌HTML5播放器
- 自动提取粤语内容进行朗读
- 音频缓存在session_state中，rerun后仍可播放

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# 编辑 secrets.toml 填入你的API密钥
```

### 3. 运行应用

```bash
streamlit run main.py
```

## ⚙️ 配置说明

在 `.streamlit/secrets.toml` 中配置：

```toml
[qwen]
api_key = "your-dashscope-api-key"
model_name = "qwen-max"

[mimo]
api_key = "your-mimo-api-key"  # 用于TTS粤语语音合成，申请地址：https://platform.xiaomimimo.com
```

## 🎮 游戏玩法

1. **选择语言**: 中文或英文界面
2. **场景探索**: 茶楼、花市、骑楼、大排档
3. **阶段任务**: 
   - Greeting: 打招呼
   - Ordering: 点单/购物
   - Payment: 结账
4. **通关方式**:
   - 完成任务条件（AI判断）
   - 积累足够积分
5. **粤语朗读**: AI回复后自动生成粤语语音，点击播放器听取发音

## 📝 开发说明

### 添加新场景

在 `backend/config.py` 的 `SCENARIOS` 中添加：

```python
"new_scene": {
    "name_zh": "新场景",
    "name_en": "New Scene",
    "npc_zh": "NPC名",
    "npc_en": "NPC Name",
    "icon": "🎭"
}
```

在 `I18N` 中添加对应的任务描述。

### 修改TTS音色

在 `tts/cantonese_tts.py` 中修改：

```python
DEFAULT_VOICE = "default_zh"  # 中文女声（默认）
# 或 "mimo_default"  # 中性音色
# 或 "default_en"   # 英文女声
```

### TTS模块说明

TTS模块使用小米MiMo V2 TTS模型，通过OpenAI兼容接口调用：
- 接口地址：`https://api.xiaomimimo.com/v1`
- 模型名称：`mimo-v2-tts`
- 输出格式：WAV
- 支持粤语风格：自动添加`<style>粤语</style>`标签
- 文档参考：https://platform.xiaomimimo.com/#/docs/usage-guide/speech-synthesis

## 📄 许可证

MIT License

## 🙏 致谢

- 阿里云DashScope提供的大模型API（LLM对话）
- 小米MiMo平台提供的TTS语音合成API
- Streamlit团队提供的优秀框架
