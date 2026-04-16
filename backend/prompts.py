"""
Prompt工程模块 - 管理系统提示词和响应解析
"""
import re
import json
from backend.config import SCENARIOS, STAGE_SCORE_THRESHOLDS

def get_system_prompt(scenario, stage, lang, tracker, stage_score):
    """
    生成系统提示词
    
    保持与原始代码完全一致的prompt逻辑
    """
    s_info = SCENARIOS[scenario]
    npc_name = s_info[f"npc_{lang}"]
    threshold = STAGE_SCORE_THRESHOLDS.get(stage, 10)
    
    hint = ""
    if stage_score >= threshold - 2 and stage != "finished":
        hint = f"User is close to unlocking the next stage by points (Current: {stage_score}, Threshold: {threshold}). Gently guide them to wrap up and transition naturally."

    progress_hint = ""
    if scenario == "tea_house" and stage == "ordering":
        if tracker.get("items_ordered", 0) < 2:
            progress_hint = "User hasn't ordered 2 items yet. Actively recommend dishes and make it easy for them to order."
        elif not tracker.get("meanings_discussed"):
            progress_hint = "User ordered items but didn't discuss meanings. Explain meanings naturally in conversation."
    elif scenario == "tea_house" and stage == "chatting":
        progress_hint = "This is a relaxed chatting stage. Be conversational, share cultural stories, and make the user feel comfortable. No strict requirements - just enjoy the conversation."
    elif scenario == "tea_house" and stage == "payment":
        progress_hint = "Help the user wrap up naturally. Guide them toward asking for the bill and saying goodbye. Once they've said goodbye or paid, set next_stage to 'finished'."
    
    if lang == 'en':
        lang_instr = "Explain in English. Speak Cantonese in dialogue."
        role_desc = f"You are {npc_name}. Guide the user warmly."
    else:
        lang_instr = "使用中文解释。对话用粤语。"
        role_desc = f"你是{npc_name}。热情引导用户。"
    
    return f"""{role_desc}
Scenario: {s_info['name_zh']} | Stage: {stage}

Score Info: Current Stage Score = {stage_score}, Threshold to pass = {threshold}.
{hint}

Progress Info: {progress_hint}

【Rules】
1. Speak authentic **Cantonese**. {lang_instr}
2. Use **Standard Jyutping** (e.g., nei5hou2) for all pinyin.
3. If the user interacts well, give high fluency/accuracy scores.
4. **Transition Logic**:
   - If (Task Conditions Met) OR (Stage Score >= {threshold}), set "next_stage" to the next phase.
   - If transitioning due to score, say something like "You've chatted enough! Let's move on!"

【Output Format】
1. Dialogue.
2. `[Tip]` section.
3. JSON block wrapped in ```json ... ```.

JSON Structure:
{{
    "fluency": 1-5,
    "accuracy": 1-5,
    "next_stage": "next_stage_name",
    "cultural_point": "Tip text",
    "vocabulary": [{{"word": "...", "jyutping": "...", "meaning": "...", "example": "...", "example_jyutping": "..."}}],
    "game_update": {{
        "items_ordered_increment": 0 or 1,
        "meanings_discussed_flag": true or false
    }}
}}
"""

def parse_ai_response(text):
    """
    解析AI响应，提取JSON数据和清理后的文本
    
    保持与原始代码完全一致的解析逻辑
    """
    # 尝试匹配 ```json ... ``` 格式
    match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            clean_text = text.replace(match.group(0), "").strip()
            return clean_text, data
        except:
            pass
    
    # 尝试匹配 ``` ... ``` 格式（不带json标记）
    match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            clean_text = text.replace(match.group(0), "").strip()
            return clean_text, data
        except:
            pass
    
    # 尝试匹配 { ... } 格式
    match = re.search(r'(\{.*\})', text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            clean_text = text.replace(match.group(0), "").strip()
            return clean_text, data
        except:
            pass
    
    return text, {}

def extract_tip(text):
    """提取[Tip]部分的内容"""
    if "[Tip]" in text:
        parts = text.split("[Tip]", 1)
        clean_text = parts[0].strip()
        tip_content = parts[1].strip() if len(parts) > 1 else ""
        return clean_text, tip_content
    return text, None
