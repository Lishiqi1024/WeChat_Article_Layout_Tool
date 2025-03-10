from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import json
import time
from config import API_KEY, API_URL,API_MODEL
import logging
from utils.wechat import WeChatAPI
from utils.document import DocumentProcessor
from utils.ai_generator import AIGenerator

app = Flask(__name__)

# 配置 CORS，允许所有来源
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化微信API
wechat_api = WeChatAPI()

def log_to_markdown(question, purpose):
    """记录操作日志到markdown文件"""
    with open("../log.md", "a", encoding="utf-8") as f:
        log_entry = f"""
**时间**：{time.strftime('%Y-%m-%d %H:%M:%S')}

**问题描述**：{question}

**目的**：{purpose}

---
"""
        f.write(log_entry)

def chunk_text(text, max_length=2000):
    """将长文本分块处理"""
    sentences = text.split('。')
    chunks = []
    current_chunk = ''
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + '。'
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + '。'
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

@app.route('/format', methods=['POST'])
def format_article():
    """处理文章排版请求"""
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({"error": "请求数据为空"}), 400
            
        content = data.get('content')
        if not content or not content.strip():
            return jsonify({"error": "请提供需要排版的文本"}), 400
            
        # 记录日志
        log_to_markdown(
            question="文章排版请求",
            purpose="将普通文本转换为微信公众号格式"
        )
        
        logger.info(f"接收到的内容: {content[:100]}...") # 记录前100个字符用于调试
        
        # 分块处理长文本
        chunks = chunk_text(content)
        formatted_chunks = []
        
        # 调用 DeepSeek API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        session = requests.Session()
        retries = requests.adapters.Retry(
            total=3,  # 最多重试3次
            backoff_factor=1,  # 重试间隔
            status_forcelist=[500, 502, 503, 504]  # 这些状态码会触发重试
        )
        session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))
        
        for i, chunk in enumerate(chunks):
            api_data = {
                "model": API_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": """你是一个专业的微信公众号排版专家。请按照以下规则对文章进行排版：
1. 标题层级：
   - 主标题使用24px，加粗，#333333
   - 二级标题使用18px，加粗，#666666
   - 三级标题使用16px，#888888
2. 正文：
   - 字体大小15px
   - 行高1.75
   - 颜色#333333
3. 段落间距：
   - 段落之间空一行
   - 标题与正文之间留适当间距
4. 特殊格式：
   - 重要内容使用加粗标签
   - 引用使用blockquote标签
   - 列表使用ul/ol和li标签
5. 图片：
   - 图片使用img标签，宽度自适应
   - 图片下方留适当的空白
6. 超链接：
   - 超链接使用a标签，颜色#1E9FFF
7. 代码：
   - 代码使用pre标签，字体大小14px，#888888
   - 代码块使用code标签，字体大小14px，#888888
8. 表格：
   - 表格使用table标签
   - 表头使用thead标签
   - 表体使用tbody标签
   - 单元格使用td标签
9. 其他：
   - 保持原文的意思，只对原文进行排版，不要添加任何新的内容
  

请将输入的文本转换为带有适当HTML标签和样式的格式。保持文章的整体结构清晰，视觉层次分明。

注意：这是文章的第 {current} 部分，共 {total} 部分。请保持格式一致性。""".format(
                            current=i+1, 
                            total=len(chunks)
                        )
                    },
                    {
                        "role": "user",
                        "content": chunk
                    }
                ],
                "temperature": 0.6
            }
            
            try:
                response = session.post(
                    API_URL,
                    headers=headers,
                    json=api_data,
                    timeout=(10, 120)
                )
                
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    formatted_chunks.append(result["choices"][0]["message"]["content"])
                else:
                    raise Exception("AI返回结果格式错误")
                    
            except Exception as e:
                logger.error(f"处理第{i+1}块文本时出错: {str(e)}")
                return jsonify({"error": f"处理第{i+1}块文本时出错"}), 500

        # 合并处理结果
        formatted_text = "\n".join(formatted_chunks)
        return jsonify(formatted_text)
        
    except Exception as e:
        logger.error(f"处理请求错误: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_document():
    """分析文档并生成文章"""
    try:
        if 'file' in request.files:
            # 处理文件上传
            file = request.files['file']
            result = DocumentProcessor.process_uploaded_file(file)
            
            # 记录日志
            log_to_markdown(
                question="PDF文件分析",
                purpose=f"分析文件：{result['filename']}（{result['size']}）"
            )
            
            # 调用AI生成文章摘要
            prompt = f"请分析以下PDF文档内容并生成一篇公众号文章：\n\n{result['text']}"
            summary = AIGenerator.generate_article(prompt)
            
            return jsonify({
                "success": True,
                "content": summary,
                "message": f"已成功分析文件：{result['filename']}（{result['size']}）"
            })
            
        else:
            # 处理URL
            data = request.get_json()
            if not data or 'url' not in data:
                return jsonify({"error": "请提供PDF文件或URL"}), 400
                
            result = DocumentProcessor.download_and_process_file(data['url'])
            
            # 记录日志
            log_to_markdown(
                question="URL内容分析",
                purpose=f"分析URL：{data['url']}"
            )
            
            # 调用AI生成文章摘要
            prompt = f"请分析以下内容并生成一篇公众号文章：\n\n{result['text']}"
            summary = AIGenerator.generate_article(prompt)
            
            return jsonify({
                "success": True,
                "content": summary,
                "message": f"已成功分析URL内容"
            })

    except Exception as e:
        logger.error(f"文档分析错误: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/generate', methods=['POST'])
def generate_article():
    """根据用户输入生成文章"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "请提供文章主题或关键词"}), 400

        prompt = data['prompt']
        content = AIGenerator.generate_article(prompt)
        return jsonify({"content": content})

    except Exception as e:
        logger.error(f"文章生成错误: {str(e)}")
        return jsonify({"error": str(e)}), 500
@app.route('/publish', methods=['POST'])
def publish_to_wechat():
    """发布到微信公众号草稿箱"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "请求数据为空"}), 400
            
        title = data.get('title')
        content = data.get('content')
        digest = data.get('digest')  # 获取用户提供的摘要

        if not title:
            return jsonify({"error": "文章标题不能为空"}), 400
        if not content:
            return jsonify({"error": "文章内容不能为空"}), 400

        # 记录日志
        log_to_markdown(
            question="发布文章到微信公众号",
            purpose=f"将文章《{title}》发布到微信公众号草稿箱"
        )

        try:
            # 发布到草稿箱，传递摘要参数
            media_id = wechat_api.add_draft(title, content, digest=digest)
            return jsonify({
                "success": True,
                "media_id": media_id,
                "message": "文章已成功保存到草稿箱"
            })
        except Exception as e:
            logger.error(f"发布到微信失败: {str(e)}")
            return jsonify({
                "success": False,
                "error": f"发布失败: {str(e)}"
            }), 500

    except Exception as e:
        logger.error(f"处理发布请求失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)