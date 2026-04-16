"""
页面模块 - 主应用页面
"""
import streamlit as st
from backend.config import SCENARIOS, I18N
from backend.game_logic import get_ai_response, advance_to_next_scenario
from frontend.components import (
    render_sidebar, render_progress_bar, render_mission_info,
    render_chat_history, render_vocab_expander, render_stage_complete,
    render_celebration_modal
)
from tts.cantonese_tts import CantoneseTTS


def extract_vocab_for_tts(eval_data):
    """
    从AI响应的词汇数据中提取生词信息用于TTS朗读
    
    只朗读粤语词汇本身，不朗读粤拼注音（避免TTS将粤拼字母也读出来）
    
    Returns:
        str: 用于TTS朗读的文本，如 "你好。唔该。饮茶"
             如果没有词汇数据则返回None
    """
    if not eval_data or not eval_data.get("vocabulary"):
        return None
    
    vocab_items = eval_data["vocabulary"]
    if not vocab_items:
        return None
    
    # 只取前3个生词（避免TTS文本过长），只朗读词本身不读粤拼
    parts = []
    for word in vocab_items[:3]:
        word_text = word.get("word", "")
        if word_text:
            parts.append(word_text)
    
    return "。".join(parts) if parts else None


def render_main_app():
    """渲染主应用界面"""
    lang = st.session_state.game_state['language']
    t = I18N[lang]
    scenario_key = st.session_state.game_state['scenario']
    s_info = SCENARIOS[scenario_key]
    
    # 页面标题 - 茶楼沉浸式体验
    scenario_name = s_info[f"name_{lang}"]
    npc_name = s_info[f'npc_{lang}']
    if lang == 'zh':
        st.title(f"🥟 粤韵茶楼")
        st.subheader(f"同 **{npc_name}** 饮茶倾偈 💬")
    else:
        st.title(f"🥟 Cantonese Teahouse")
        st.subheader(f"Chat with **{npc_name}** 💬")
    
    # 渲染进度条和任务信息
    render_progress_bar(lang, t)
    render_mission_info(scenario_key, lang, t)
    
    # 渲染侧边栏
    render_sidebar()
    
    # 渲染聊天历史（含历史TTS音频播放器）
    render_chat_history()
    
    # 初始化TTS模块
    tts = CantoneseTTS()
    
    # 用户输入
    placeholder = t['input_placeholder_zh'] if lang == 'zh' else t['input_placeholder_en']
    prompt = st.chat_input(placeholder)
    
    # 处理用户输入
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown(f"*{s_info[f'npc_{lang}']} {t['thinking']}... {s_info['icon']}*")
            
            # 获取AI响应
            ai_text, tip_text, eval_data = get_ai_response(prompt, lang)
            thinking_placeholder.empty()
            
            # 显示AI回复
            st.markdown(ai_text)
            
            # TTS朗读 - 只朗读词汇本中的生词新词
            if tts.is_available() and eval_data:
                vocab_text = extract_vocab_for_tts(eval_data)
                if vocab_text:
                    with st.spinner("🔊 正在生成语音..."):
                        audio_bytes = tts.synthesize(vocab_text)
                        if audio_bytes:
                            # 渲染音频播放器
                            from frontend.components import render_audio_player
                            render_audio_player(audio_bytes, label="🔊 生词朗读:")
                            # 缓存到session_state，以便rerun后历史消息仍可播放
                            msg_idx = len(st.session_state.messages)
                            st.session_state[f"tts_audio_{msg_idx}"] = audio_bytes
            
            # 显示文化小贴士
            if tip_text:
                st.info(f"**{t['tip_label']}**: {tip_text}")
            
            # 显示词汇面板
            render_vocab_expander(eval_data, lang, t)
            
            # 保存消息
            st.session_state.messages.append({
                "role": "assistant",
                "content": ai_text,
                "data": eval_data
            })
        
        # 阶段切换后显示庆祝弹窗（在同一轮渲染中，不额外rerun）
        if st.session_state.game_state.get('show_celebration'):
            render_celebration_modal()
    
    # 阶段完成后的展示逻辑
    if st.session_state.game_state['stage'] == 'finished':
        render_stage_complete(scenario_key, scenario_name, lang, t)
