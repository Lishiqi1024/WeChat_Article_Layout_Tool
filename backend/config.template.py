# DeepSeek API配置
import os
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "your_api_key_here")  
API_URL = os.environ.get("DEEPSEEK_API_URL", "your_api_url_here")  
API_MODEL = os.environ.get("DEEPSEEK_API_MODEL", "your_model_here")  

# 排版样式配置
STYLE_CONFIG = {
    "title": {
        "size": "24px",
        "color": "#333333",
        "weight": "bold"
    },
    "subtitle": {
        "size": "18px",
        "color": "#666666",
        "weight": "bold"
    },
    "text": {
        "size": "15px",
        "color": "#333333",
        "lineHeight": "1.75"
    }
}

# 微信公众号配置
WECHAT_CONFIG = {
    "APPID": os.environ.get("WECHAT_APPID", "your_appid_here"),
    "SECRET": os.environ.get("WECHAT_SECRET", "your_secret_here"),
    "DEFAULT_THUMB_MEDIA_ID": os.environ.get("DEFAULT_THUMB_MEDIA_ID", "your_media_id_here"),
    "MAX_CONTENT_LENGTH": 20000  # 微信图文内容字数限制
}

# 文档处理配置
DOC_CONFIG = {
    "ALLOWED_EXTENSIONS": ['pdf', 'doc', 'docx'],
    "MAX_FILE_SIZE": 10 * 1024 * 1024  # 10MB
}