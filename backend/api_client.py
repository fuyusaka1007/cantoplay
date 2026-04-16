"""
API客户端模块 - 处理与LLM的交互
"""
from openai import OpenAI
from backend.config import get_api_config

class LLMClient:
    """LLM API客户端封装"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式，确保只创建一个客户端实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_client()
        return cls._instance
    
    def _init_client(self):
        """初始化OpenAI客户端"""
        config = get_api_config()
        self.client = OpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"]
        )
        self.model_name = config["model_name"]
    
    def chat_completion(self, messages, temperature=0.7):
        """
        发送聊天请求到LLM
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            
        Returns:
            API响应对象
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature
            )
            return response
        except Exception as e:
            raise Exception(f"API调用失败: {str(e)}")
    
    def get_response_content(self, response):
        """从响应中提取内容"""
        return response.choices[0].message.content

# 全局客户端实例
def get_llm_client():
    """获取LLM客户端实例"""
    return LLMClient()
