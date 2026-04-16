"""
游戏逻辑模块 - 处理游戏状态管理和进度计算
"""
import streamlit as st
from backend.config import STAGE_SCORE_THRESHOLDS, SCENARIOS
from backend.prompts import get_system_prompt, parse_ai_response, extract_tip
from backend.api_client import get_llm_client

def init_session_state():
    """初始化session state"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'game_state' not in st.session_state:
        st.session_state.game_state = {
            "scenario": "tea_house",
            "stage": "greeting",
            "total_score": 0,
            "stage_score": 0,
            "learned_vocabulary": [],
            "current_npc": "Keung Gor",
            "language": None,
            "progress_tracker": {"items_ordered": 0, "meanings_discussed": False},
            "show_celebration": False,
            "last_completed_stage": None,
            "stage_rounds": 0  # 追踪当前阶段的对话轮数
        }
    if 'show_start_screen' not in st.session_state:
        st.session_state.show_start_screen = True

def reset_game(lang=None):
    """重置游戏状态"""
    scenario_key = "tea_house"
    s_info = SCENARIOS[scenario_key]
    
    st.session_state.messages = []
    # 清除TTS音频缓存
    keys_to_remove = [k for k in st.session_state.keys() if k.startswith("tts_audio_")]
    for k in keys_to_remove:
        del st.session_state[k]
    
    st.session_state.game_state = {
        "scenario": scenario_key,
        "stage": "greeting",
        "total_score": 0,
        "stage_score": 0,
        "learned_vocabulary": [],
        "current_npc": s_info[f'npc_{lang}'] if lang else "Keung Gor",
        "language": lang,
        "progress_tracker": {"items_ordered": 0, "meanings_discussed": False},
        "show_celebration": False,
        "last_completed_stage": None,
        "stage_rounds": 0
    }

def get_current_scenario_info():
    """获取当前场景信息"""
    scenario_key = st.session_state.game_state['scenario']
    return SCENARIOS.get(scenario_key, SCENARIOS["tea_house"])

def get_stage_threshold(stage):
    """获取阶段通关阈值"""
    return STAGE_SCORE_THRESHOLDS.get(stage, 10)

# 严格阶段顺序 - AI不可随意跳转，只能按序推进
STAGE_ORDER = ["greeting", "ordering", "chatting", "payment", "finished"]

def _get_next_stage(current_stage):
    """获取当前阶段的下一个阶段（严格按序）"""
    if current_stage in STAGE_ORDER:
        next_idx = STAGE_ORDER.index(current_stage) + 1
        if next_idx < len(STAGE_ORDER):
            return STAGE_ORDER[next_idx]
    return None

def should_advance_stage(eval_data, current_stage, stage_score):
    """
    判断是否应该进入下一阶段
    
    支持多种通关方式（按优先级）：
    1. 任务条件达成（AI判断） - 但必须校验目标阶段合法性
    2. 积分达到阈值
    3. 对话轮数保底（每阶段最多4轮自动推进，防止"无话可聊"）
    
    重要：阶段只能严格按顺序推进，不可回退或跳跃
    """
    # finished阶段不再推进
    if current_stage == "finished":
        return False, None
    
    # 只接受STAGE_ORDER中的合法阶段名
    VALID_STAGES = set(STAGE_ORDER)
    
    threshold = get_stage_threshold(current_stage)
    
    # 方式1：AI判断任务完成 - 校验next_stage合法性
    ai_next = eval_data.get("next_stage")
    if ai_next and ai_next in VALID_STAGES and ai_next != current_stage:
        # 只有当AI指定的阶段是当前阶段的"下一个"时才接受
        expected_next = _get_next_stage(current_stage)
        if ai_next == expected_next:
            return True, expected_next
        # AI返回了非法跳跃（如从greeting跳到payment），忽略，继续检查积分
    
    # 方式2：积分达到阈值
    if stage_score >= threshold:
        expected_next = _get_next_stage(current_stage)
        if expected_next:
            return True, expected_next
    
    return False, None

def update_game_state(eval_data):
    """
    根据AI响应更新游戏状态
    
    Returns:
        should_advance: 是否进入了下一阶段
    """
    if not eval_data:
        return False
    
    # 更新分数
    round_score = eval_data.get('fluency', 0) + eval_data.get('accuracy', 0)
    st.session_state.game_state['total_score'] += round_score
    st.session_state.game_state['stage_score'] += round_score
    
    # 增加阶段对话轮数
    st.session_state.game_state['stage_rounds'] += 1
    
    current_stage = st.session_state.game_state['stage']
    stage_score = st.session_state.game_state['stage_score']
    stage_rounds = st.session_state.game_state['stage_rounds']
    
    # 对话轮数保底机制：每阶段最多4轮对话，自动推进
    # 防止用户"无话可聊"卡关
    # payment阶段特殊：2轮即可推进（结账场景不宜拖太久）
    if current_stage == "payment":
        MAX_ROUNDS_PER_STAGE = 2
    else:
        MAX_ROUNDS_PER_STAGE = 4
    rounds_auto_advance = False
    
    if stage_rounds >= MAX_ROUNDS_PER_STAGE and current_stage != "finished":
        next_stage = _get_next_stage(current_stage)
        if next_stage:
            # 轮数保底触发，使用严格有序的下一阶段
            eval_data["next_stage"] = next_stage
            rounds_auto_advance = True
    
    # 检查是否应该进入下一阶段
    should_advance, next_stage = should_advance_stage(eval_data, current_stage, stage_score)
    
    if should_advance and next_stage:
        # 标记需要显示庆祝弹窗
        if next_stage != current_stage:
            st.session_state.game_state['last_completed_stage'] = current_stage
            st.session_state.game_state['show_celebration'] = True
            st.session_state.game_state['stage'] = next_stage
            st.session_state.game_state['stage_score'] = 0
            st.session_state.game_state['stage_rounds'] = 0  # 重置轮数
            st.session_state.game_state['progress_tracker'] = {
                "items_ordered": 0,
                "meanings_discussed": False
            }
    
    # 更新进度追踪器
    game_update = eval_data.get("game_update", {})
    curr_tracker = st.session_state.game_state['progress_tracker']
    
    if "items_ordered_increment" in game_update:
        curr_tracker["items_ordered"] += game_update["items_ordered_increment"]
    
    if "meanings_discussed_flag" in game_update:
        if game_update["meanings_discussed_flag"]:
            curr_tracker["meanings_discussed"] = True
    
    st.session_state.game_state['progress_tracker'] = curr_tracker
    
    # 更新词汇表
    for word in eval_data.get('vocabulary', []):
        if word not in st.session_state.game_state['learned_vocabulary']:
            st.session_state.game_state['learned_vocabulary'].append(word)
    
    return should_advance

def get_ai_response(user_input, lang):
    """
    获取AI响应
    
    这是核心函数，保持与原始代码一致的API调用方式
    """
    scenario = st.session_state.game_state['scenario']
    stage = st.session_state.game_state['stage']
    tracker = st.session_state.game_state.get('progress_tracker', {})
    stage_score = st.session_state.game_state.get('stage_score', 0)
    
    # 构建系统提示词
    sys_prompt = get_system_prompt(scenario, stage, lang, tracker, stage_score)
    
    # 构建消息列表
    messages = [{"role": "system", "content": sys_prompt}]
    for msg in st.session_state.messages:
        if msg["role"] in ["user", "assistant"]:
            messages.append(msg)
    
    try:
        # 调用API（保持原有调用方式）
        client = get_llm_client()
        response = client.chat_completion(messages, temperature=0.7)
        raw_content = client.get_response_content(response)
        
        # 解析响应
        clean_reply, eval_data = parse_ai_response(raw_content)
        clean_reply, tip_content = extract_tip(clean_reply)
        
        # 更新游戏状态
        if eval_data:
            should_advance = update_game_state(eval_data)
            
            # 如果通过积分通关或轮数保底，添加提示
            if should_advance:
                if lang == 'zh':
                    clean_reply += "\n\n*(系统提示：对话推进自然，解锁下一阶段！)*"
                else:
                    clean_reply += "\n\n*(System: Conversation progressing naturally, unlocking next stage!)*"
        
        return clean_reply, tip_content, eval_data
        
    except Exception as e:
        return f"Error: {str(e)}", None, None

def advance_to_next_scenario():
    """重新开始茶楼体验（单场景循环）"""
    lang = st.session_state.game_state['language']
    reset_game(lang)
    return True
