"""
LinguaQuest: 粤韵茶楼 - 模块化版本

基于Streamlit的粤语学习游戏应用
"""
import streamlit as st

# 页面配置（必须在其他st命令之前）
st.set_page_config(
    page_title="CANTOPLAY: 粤韵茶楼",
    page_icon="🥟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 导入后端模块
from backend.game_logic import init_session_state
from frontend.components import render_start_screen
from frontend.pages import render_main_app

# ==================== 主程序入口 ====================
if __name__ == "__main__":
    # 初始化session state
    init_session_state()
    
    # 根据状态渲染不同界面
    if st.session_state.show_start_screen:
        render_start_screen()
    else:
        render_main_app()
