"""
配置模块 - 集中管理所有配置和常量
"""
import streamlit as st

# ==================== API 配置 ====================
def get_api_config():
    """获取API配置，支持从streamlit secrets读取"""
    if "qwen" not in st.secrets:
        st.error("❌ Configuration Error: Please configure [qwen] api_key and model_name in .streamlit/secrets.toml")
        st.stop()
    
    return {
        "api_key": st.secrets["qwen"]["api_key"],
        "model_name": st.secrets["qwen"]["model_name"],
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
    }

# ==================== 游戏配置 ====================
# 通关积分阈值配置 (保底机制)
# 优化后的单场景三阶段：降低阈值，让积分保底更容易触发
STAGE_SCORE_THRESHOLDS = {
    "greeting": 4,      # 打招呼只需少量互动即可通过
    "ordering": 6,      # 点单阶段适度降低
    "chatting": 5,      # 闲聊阶段新增，门槛较低
    "payment": 4        # 结账阶段容易完成
}

# 场景配置 - 只保留茶楼，深度优化体验
SCENARIOS = {
    "tea_house": {
        "name_zh": "茶楼",
        "name_en": "Teahouse",
        "npc_zh": "强哥",
        "npc_en": "Keung Gor",
        "icon": "🥟"
    }
}

# ==================== 多语言字典 (UI Texts) ====================
I18N = {
    "zh": {
        "title": "🥟 LinguaQuest: 粤韵茶楼",
        "start_title": "欢迎加入粤韵之旅！",
        "start_desc": "选择语言开始学习粤语和文化。",
        "btn_zh": "🇨🇳 普通话",
        "btn_en": "🇬🇧 English",
        "sidebar_status": "🎮 游戏状态",
        "sidebar_stage": "当前阶段",
        "sidebar_score": "总得分",
        "sidebar_stage_score": "本阶段进度分",
        "sidebar_vocab": "🎒 粤语笔记本",
        "sidebar_vocab_empty": "暂无词汇",
        "btn_reset": "🔄 重置游戏",
        "input_placeholder_zh": "输入粤语开始对话...",
        "input_placeholder_en": "Type in Cantonese...",
        "thinking": "正在思考...",
        "mission_label": "🎯 当前任务",
        "tip_label": "💡 文化小贴士",
        "vocab_label": "🎒 本轮秘籍",
        "success_msg": "🎉 恭喜完成 {scenario} 体验！",
        "next_level_btn": "再玩一次 🔄",
        "celebration_title": "🎉 阶段完成！",
        "celebration_desc": "太棒了！你已成功完成 **{stage_name}** 阶段！\n准备迎接新的挑战吧！",
        "celebration_btn": "继续旅程 🚀",
        "score_boost_hint": "💡 多互动自然推进，聊够了自动解锁下一阶段！",
        "tts_button": "🔊 朗读",
        "tts_loading": "生成语音中...",
        "tts_error": "语音生成失败",
        "missions": {
            "tea_house": {
                "greeting": "用粤语同强哥打招呼，入座茶楼。",
                "ordering": "点选经典点心，了解其寓意和粤语叫法。",
                "chatting": "同强哥倾下偈，了解茶楼文化。",
                "payment": "用「埋单」结账，用祝福语道别。",
                "finished": "任务完成！多谢嚟茶楼！"
            }
        }
    },
    "en": {
        "title": "🥟 LinguaQuest: Cantonese Teahouse",
        "start_title": "Welcome to the Cantonese Journey!",
        "start_desc": "Select your language to start learning.",
        "btn_zh": "🇨🇳 普通话",
        "btn_en": "🇬🇧 English",
        "sidebar_status": "🎮 Game Status",
        "sidebar_stage": "Current Stage",
        "sidebar_score": "Total Score",
        "sidebar_stage_score": "Stage Progress Score",
        "sidebar_vocab": "🎒 Cantonese Notebook",
        "sidebar_vocab_empty": "No vocabulary yet",
        "btn_reset": "🔄 Reset Game",
        "input_placeholder_zh": "输入粤语开始对话...",
        "input_placeholder_en": "Type in Cantonese...",
        "thinking": "Thinking...",
        "mission_label": "🎯 Current Mission",
        "tip_label": "💡 Cultural Tip",
        "vocab_label": "🎒 Vocabulary Learned",
        "success_msg": "🎉 Congratulations! You've completed the {scenario} experience!",
        "next_level_btn": "Play Again 🔄",
        "celebration_title": "🎉 Stage Completed!",
        "celebration_desc": "Awesome! You have successfully finished the **{stage_name}** stage!\nGet ready for the next challenge!",
        "celebration_btn": "Continue Journey 🚀",
        "score_boost_hint": "💡 Chat naturally to progress - the stage advances automatically as you interact!",
        "tts_button": "🔊 Speak",
        "tts_loading": "Generating audio...",
        "tts_error": "Audio generation failed",
        "missions": {
            "tea_house": {
                "greeting": "Greet Keung Gor in Cantonese and take a seat.",
                "ordering": "Order classic Dim Sum and learn their Cantonese names and meanings.",
                "chatting": "Chat with Keung Gor about teahouse culture.",
                "payment": "Ask for the bill ('Maai Daan') and say goodbye with a blessing.",
                "finished": "Mission Complete! Thanks for visiting!"
            }
        }
    }
}
