"""
UI组件模块 - 各种可复用的UI组件
"""
import streamlit as st
import base64
from frontend.utils import format_jyutping, get_stage_display_name
from backend.config import I18N, SCENARIOS, STAGE_SCORE_THRESHOLDS


def render_audio_player(audio_bytes: bytes, label: str = "🔊"):
    """
    渲染音频播放器 - 使用HTML5 audio标签确保兼容性
    
    Streamlit自带的st.audio在某些浏览器/WAV格式下有兼容性问题，
    使用HTML5 <audio>标签嵌入base64音频是最可靠的方案。
    """
    audio_b64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
    <div style="margin: 8px 0; display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 1.1rem;">{label}</span>
        <audio controls preload="auto" style="height: 36px;">
            <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
            您的浏览器不支持音频播放。
        </audio>
    </div>
    """
    st.markdown(audio_html, unsafe_allow_html=True)


def render_start_screen():
    """渲染开始界面"""
    st.markdown("""
    <style>
    .start-container {
        text-align: center;
        padding: 3rem 1rem;
    }
    .start-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .start-desc {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    lang = st.session_state.game_state['language'] or 'zh'
    t = I18N[lang]
    
    with st.container():
        st.markdown(f"""
        <div class="start-container">
            <div class="start-title">{t['start_title']}</div>
            <div class="start-desc">{t['start_desc']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t['btn_zh'], use_container_width=True, key="btn_start_zh"):
                st.session_state.game_state['language'] = 'zh'
                st.session_state.show_start_screen = False
                st.rerun()
        with col2:
            if st.button(t['btn_en'], use_container_width=True, key="btn_start_en"):
                st.session_state.game_state['language'] = 'en'
                st.session_state.show_start_screen = False
                st.rerun()

def render_celebration_modal():
    """
    渲染庆祝弹窗 - 纯HTML/JS实现，3秒后自动淡出消失
    
    不使用time.sleep阻塞，不影响用户输入和页面交互
    """
    import uuid
    
    lang = st.session_state.game_state['language']
    t = I18N[lang]
    completed_stage = st.session_state.game_state.get('last_completed_stage', '')
    display_name = get_stage_display_name(completed_stage, lang)
    
    # 生成唯一ID避免冲突
    modal_id = f"celebration_{uuid.uuid4().hex[:8]}"
    
    celebration_html = f"""
    <div id="{modal_id}" style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        color: white;
        margin: 1rem 0;
        transition: opacity 0.5s ease-out;
    ">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🎉🎈🥳</div>
        <div style="font-size: 1.8rem; font-weight: bold; margin-bottom: 1rem;">{t['celebration_title']}</div>
        <div style="font-size: 1.1rem; margin-bottom: 1.5rem;">{t['celebration_desc'].format(stage_name=display_name)}</div>
    </div>
    <script>
    (function() {{
        var modal = document.getElementById('{modal_id}');
        if (modal) {{
            setTimeout(function() {{
                modal.style.opacity = '0';
                setTimeout(function() {{
                    modal.style.display = 'none';
                }}, 500);
            }}, 3000);
        }}
    }})();
    </script>
    """
    st.markdown(celebration_html, unsafe_allow_html=True)
    
    # 自动清除庆祝状态（不用sleep，用一个标记让下次rerun时清除）
    if not st.session_state.game_state.get('_celebration_shown', False):
        st.session_state.game_state['_celebration_shown'] = True
        # 用一次性的rerun来清除状态
        # 不直接在这里rerun，而是等用户下一次交互时自然清除
    
    # 标记庆祝已显示，下次rerun时自动清除
    st.session_state.game_state['show_celebration'] = False
    st.session_state.game_state['last_completed_stage'] = None

def render_sidebar():
    """渲染侧边栏"""
    lang = st.session_state.game_state['language']
    t = I18N[lang]
    
    current_stage = st.session_state.game_state['stage']
    threshold = STAGE_SCORE_THRESHOLDS.get(current_stage, 10)
    current_stage_score = st.session_state.game_state.get('stage_score', 0)
    
    with st.sidebar:
        st.header(t['sidebar_status'])
        st.metric(t['sidebar_stage'], get_stage_display_name(current_stage, lang))
        st.metric(t['sidebar_score'], st.session_state.game_state['total_score'])
        st.divider()
        
        st.header(t['sidebar_vocab'])
        vocab_list = st.session_state.game_state['learned_vocabulary']
        if vocab_list:
            for idx, word in enumerate(vocab_list[-5:]):
                st.markdown(f"**{word['word']}**")
                st.markdown(f"<small>{format_jyutping(word['jyutping'])}</small>", unsafe_allow_html=True)
                st.caption(f"{word['meaning']}")
                
                # TTS朗读按钮（词汇本中的生词）- 只朗读词本身，不朗读粤拼
                word_key = f"tts_vocab_{idx}_{word['word']}"
                if st.button(f"🔊", key=word_key):
                    from tts.cantonese_tts import CantoneseTTS
                    tts = CantoneseTTS()
                    if tts.is_available():
                        audio_bytes = tts.synthesize(word['word'])
                        if audio_bytes:
                            render_audio_player(audio_bytes, label=f"{word['word']}")
                
                st.divider()
        else:
            st.caption(t['sidebar_vocab_empty'])
        
        st.divider()
        
        if st.button(t['btn_reset']):
            from backend.game_logic import reset_game
            reset_game(lang)
            st.rerun()

def render_progress_bar(lang, t):
    """渲染进度条"""
    current_stage = st.session_state.game_state['stage']
    threshold = STAGE_SCORE_THRESHOLDS.get(current_stage, 10)
    current_stage_score = st.session_state.game_state.get('stage_score', 0)
    stage_rounds = st.session_state.game_state.get('stage_rounds', 0)
    MAX_ROUNDS = 4
    progress_pct = min(100, int((current_stage_score / threshold) * 100))
    
    st.progress(progress_pct)
    
    # 显示积分和轮数提示
    if lang == 'zh':
        rounds_hint = f" | 本阶段已聊 {stage_rounds}/{MAX_ROUNDS} 轮"
    else:
        rounds_hint = f" | {stage_rounds}/{MAX_ROUNDS} rounds this stage"
    
    st.caption(f"{t['sidebar_stage_score']}: {current_stage_score} / {threshold}{rounds_hint}")

def render_mission_info(scenario_key, lang, t):
    """渲染任务信息"""
    current_stage = st.session_state.game_state['stage']
    mission_text = t['missions'][scenario_key].get(current_stage, "")
    st.info(f"**{t['mission_label']}**: {mission_text}", icon="🎯")

def render_chat_history():
    """渲染聊天历史（包含TTS音频播放器）"""
    chat_container = st.container()
    with chat_container:
        for i, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                # 如果是assistant消息且有缓存的音频，渲染播放器
                if msg["role"] == "assistant":
                    cached_audio = st.session_state.get(f"tts_audio_{i}")
                    if cached_audio:
                        render_audio_player(cached_audio, label="🔊 生词朗读:")

def render_vocab_expander(eval_data, lang, t):
    """渲染词汇扩展面板"""
    if eval_data and eval_data.get("vocabulary"):
        with st.expander(f"🎒 {t['vocab_label']}", expanded=False):
            for word in eval_data["vocabulary"]:
                c1, c2, c3 = st.columns([1.5, 1.5, 3])
                with c1:
                    st.markdown(f"**{word['word']}**")
                with c2:
                    st.markdown(f"<small>{format_jyutping(word['jyutping'])}</small>", unsafe_allow_html=True)
                with c3:
                    st.caption(word['meaning'])
                if 'example' in word:
                    st.markdown(f"*Ex:* {word['example']}")
                    st.markdown(f"<small>{format_jyutping(word.get('example_jyutping',''))}</small>", unsafe_allow_html=True)

def render_stage_complete(scenario_key, scenario_name, lang, t):
    """渲染阶段完成界面（单场景：提供再玩一次按钮）"""
    st.success(t['success_msg'].format(scenario=scenario_name))
    st.balloons()
    
    if st.button(t['next_level_btn']):
        from backend.game_logic import advance_to_next_scenario
        if advance_to_next_scenario():
            st.rerun()
