"""
粤语TTS模块 - 使用小米MiMo V2 TTS模型进行粤语语音合成

此模块独立于原有功能，通过OpenAI兼容接口调用小米MiMo V2 TTS模型
支持粤语风格语音合成，使用style标签控制方言输出

关键注意：
- 合成文本必须放在 role=assistant 的消息中
- 使用openai Python SDK调用（requests有SSL兼容问题）
- 非流式调用返回完整WAV音频
"""
import os
import base64
import streamlit as st
from typing import Optional


class CantoneseTTS:
    """
    粤语语音合成器
    
    使用小米MiMo V2 TTS模型，支持粤语风格语音合成
    通过OpenAI兼容接口调用
    """
    
    # mimo-v2-tts支持的音色列表
    CANTONESE_VOICES = {
        "mimo_default": "MiMo默认 - 中性音色",
        "default_zh": "MiMo中文女声 - 适合中文/粤语",
        "default_en": "MiMo英文女声 - 适合混合场景"
    }
    
    # 默认使用中文女声（更适合粤语）
    DEFAULT_VOICE = "default_zh"
    
    def __init__(self, voice: str = None):
        """
        初始化TTS模块
        
        Args:
            voice: 音色名称，可选 mimo_default / default_zh / default_en
        """
        self.voice = voice or self.DEFAULT_VOICE
        self.api_key = self._get_api_key()
        self.base_url = "https://api.xiaomimimo.com/v1"
        self.model = "mimo-v2-tts"
    
    def _get_api_key(self) -> str:
        try:
            # 优先使用mimo配置
            if "mimo" in st.secrets:
                return st.secrets["mimo"]["api_key"]
            # 回退到qwen配置（同一平台可能有通用key）
            elif "qwen" in st.secrets:
                return st.secrets["qwen"]["api_key"]
            else:
                return ""
        except Exception:
            return ""
    
    def is_available(self) -> bool:
        """检查TTS功能是否可用（是否有配置API key）"""
        return bool(self.api_key)
    
    def synthesize(self, text: str) -> Optional[bytes]:
        """
        合成粤语语音，返回音频字节数据
        
        Args:
            text: 要合成的文本（粤语）
            
        Returns:
            WAV格式的音频字节数据，失败返回None
        """
        if not self.api_key:
            print("TTS: API key未配置")
            return None
        
        if not text or len(text.strip()) == 0:
            print("TTS: 文本为空")
            return None
        
        # 限制文本长度（MiMo TTS有字数限制）
        text = text.strip()[:500]
        
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            # 在文本开头添加风格标签（官方文档语法）：
            # <|粤语|> 确保粤语发音
            # <|减速|> 降低语速，方便学习者跟读
            # 注意：MiMo TTS使用<|...|>格式的style标签，
            # 不是<style>...</style>或<slow down>等格式
            styled_text = f"<|粤语|><|减速|>{text}"
            
            # 调用mimo-v2-tts模型
            # 关键：目标文本必须放在role=assistant的消息中
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user", 
                        "content": "请用粤语朗读以下内容"
                    },
                    {
                        "role": "assistant", 
                        "content": styled_text
                    }
                ],
                audio={
                    "format": "wav",
                    "voice": self.voice
                }
            )
            
            # 解析响应
            message = completion.choices[0].message
            audio_attr = getattr(message, "audio", None)
            
            if audio_attr is not None:
                # audio属性包含id和data字段
                audio_base64 = getattr(audio_attr, "data", None)
                if audio_base64:
                    audio_bytes = base64.b64decode(audio_base64)
                    return audio_bytes
            
            print("TTS: 响应中未包含音频数据")
            return None
                
        except ImportError:
            print("TTS: 需要安装openai库，请运行: pip install openai")
            return None
        except Exception as e:
            print(f"TTS合成失败: {str(e)}")
            return None


def get_tts_engine() -> CantoneseTTS:
    """
    获取TTS引擎实例
    
    Returns:
        TTS引擎实例
    """
    return CantoneseTTS()
