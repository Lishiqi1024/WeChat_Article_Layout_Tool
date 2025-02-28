import requests
from config import API_KEY, API_URL, API_MODEL

class AIGenerator:
    @staticmethod
    def generate_article(prompt, max_tokens=2000):
        """使用AI生成文章内容"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        data = {
            "model": API_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": """你是一个专业的公众号文章写手，请根据用户的要求生成一篇内容丰富、结构清晰的文章。
要求：
1. 文章结构完整，包含标题、引言、主体和总结
2. 语言通俗易懂，适合大众阅读
3. 内容真实可靠，有数据支撑
4. 适当使用小标题划分段落
5. 字数控制在2000字以内"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": max_tokens
        }
        
        response = requests.post(API_URL, headers=headers, json=data)
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception("AI生成文章失败") 