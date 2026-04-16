"""
前端工具函数模块
"""
import re

def format_jyutping(jp):
    """格式化粤拼显示"""
    if not jp:
        return ""
    return re.sub(r'([a-z]+)([1-9])', r'\1\2', jp)

def get_stage_display_name(stage, lang):
    """获取阶段的显示名称"""
    stage_names = {
        "greeting": "Greeting / 打招呼",
        "ordering": "Ordering / 点单",
        "chatting": "Chatting / 倾偈",
        "payment": "Payment / 埋单",
        "finished": "Finished / 已完成"
    }
    display_name = stage_names.get(stage)
    
    if display_name is None:
        # 非法阶段名（如"enjoy"、"next_stage"等AI返回的错误值）
        # 不原样输出，而是显示"已完成"
        if lang == 'zh':
            return "已完成"
        else:
            return "Completed"
    
    if lang == 'zh':
        return display_name.split("/")[-1].strip()
    else:
        return display_name.split("/")[0].strip()
