import requests
import json
import time
from config import WECHAT_CONFIG

class WeChatAPI:
    def __init__(self):
        self.access_token = None
        self.token_expires = 0
        self.appid = WECHAT_CONFIG['APPID']
        self.secret = WECHAT_CONFIG['SECRET']

    def get_access_token(self):
        if self.access_token and time.time() < self.token_expires:
            return self.access_token

        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.appid}&secret={self.secret}"
        response = requests.get(url)
        result = response.json()

        if 'access_token' in result:
            self.access_token = result['access_token']
            self.token_expires = time.time() + 7000  # Token有效期7200秒，预留200秒
            return self.access_token
        else:
            raise Exception(f"获取access_token失败: {result}")

    def add_draft(self, title, content, thumb_media_id=None, digest=None):
        """添加到草稿箱"""
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
        
        # 检查是否提供了有效的thumb_media_id
        if not thumb_media_id:
            thumb_media_id = WECHAT_CONFIG['DEFAULT_THUMB_MEDIA_ID']
            
        # 如果DEFAULT_THUMB_MEDIA_ID为空或无效，则不使用thumb_media_id参数

        # 处理内容长度限制
        max_content_length = WECHAT_CONFIG['MAX_CONTENT_LENGTH']
        if len(content) > max_content_length:
            # 在合适的句子结束处截断
            content = content[:max_content_length]
            last_period = content.rfind('。')
            if last_period > 0:
                content = content[:last_period + 1]
            content += "\n...(由于内容长度限制，部分内容已省略)"

        # 处理摘要长度限制
        # 微信公众号摘要(description)长度限制为120字符
        max_digest_length = 120
        
        # 如果没有提供摘要，则自动生成
        if digest is None:
            # 清理HTML标签，只保留纯文本
            import re
            clean_content = re.sub(r'<[^>]+>', '', content)
            
            # 提取纯文本摘要
            digest = clean_content[:max_digest_length].strip()
            if len(digest) >= max_digest_length:
                digest = digest[:max_digest_length-3] + "..."
        else:
            # 确保提供的摘要不超过长度限制
            if len(digest) > max_digest_length:
                digest = digest[:max_digest_length-3] + "..."

        # 确保所有文本内容都被正确解码
        try:
            if isinstance(title, str):
                title = title.encode('utf-8').decode('unicode_escape')
            if isinstance(content, str):
                content = content.encode('utf-8').decode('unicode_escape')
            if isinstance(digest, str):
                digest = digest.encode('utf-8').decode('unicode_escape')
        except Exception as e:
            print(f"Unicode解码警告: {str(e)}")

        article = {
            "title": title[:64],  # 标题长度限制
            "author": "Lxz",
            "digest": ' ',  # 使用处理后的摘要
            "content": content,
            "need_open_comment": 0,
            "only_fans_can_comment": 0,
            "content_source_url": ""
        }
        
        # 只有当thumb_media_id有效时才添加到请求中
        if thumb_media_id and thumb_media_id != "":
            article["thumb_media_id"] = thumb_media_id

        data = {
            "articles": [article]
        }

        try:
            response = requests.post(url, json=data)
            result = response.json()
            
            if 'media_id' in result:
                return result['media_id']
            else:
                error_msg = result.get('errmsg', '未知错误')
                raise Exception(f"添加草稿失败: {error_msg}")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败: {str(e)}")