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

    def add_draft(self, title, content, thumb_media_id=None):
        """添加到草稿箱"""
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
        
        if not thumb_media_id:
            thumb_media_id = WECHAT_CONFIG['DEFAULT_THUMB_MEDIA_ID']

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
        digest = content[:120].strip()
        if len(digest) >= 120:
            digest = digest[:117] + "..."

        data = {
            "articles": [{
                "title": title[:64],  # 标题长度限制
                "author": "AI助手",
                "digest": digest,
                "content": content,
                "thumb_media_id": thumb_media_id,
                "need_open_comment": 0,
                "only_fans_can_comment": 0,
                "content_source_url": ""
            }]
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