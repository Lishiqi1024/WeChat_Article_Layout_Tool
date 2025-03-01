import fitz  # PyMuPDF
import requests
import tempfile
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
from config import DOC_CONFIG

class DocumentProcessor:
    @staticmethod
    def is_allowed_file(filename):
        """检查文件类型是否允许"""
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in DOC_CONFIG['ALLOWED_EXTENSIONS']

    @staticmethod
    def extract_text_from_pdf(file_path):
        """从PDF提取文本"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            raise Exception(f"PDF文件处理失败: {str(e)}")

    @staticmethod
    def extract_text_from_url(url):
        """从URL提取文本内容"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 获取网页内容
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除脚本和样式元素
            for script in soup(["script", "style"]):
                script.decompose()
                
            # 获取正文内容
            # 常见的文章容器class名称
            article_classes = ['article', 'post', 'content', 'main-content', 'entry-content']
            article_content = None
            
            # 尝试找到文章主体
            for class_name in article_classes:
                article = soup.find(class_=class_name)
                if article:
                    article_content = article
                    break
            
            # 如果没找到特定容器，就获取body内容
            if not article_content:
                article_content = soup.body
                
            # 提取文本
            text = article_content.get_text(separator='\n', strip=True)
            return text
            
        except Exception as e:
            raise Exception(f"URL内容提取失败: {str(e)}")

    @staticmethod
    def process_uploaded_file(file):
        """处理上传的文件"""
        if not file:
            raise Exception("未收到文件")

        filename = secure_filename(file.filename)
        if not DocumentProcessor.is_allowed_file(filename):
            raise Exception("不支持的文件类型")

        # 检查文件大小
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        
        if size > DOC_CONFIG['MAX_FILE_SIZE']:
            raise Exception("文件大小超过限制")

        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1], delete=False) as tmp_file:
            file.save(tmp_file.name)
            tmp_path = tmp_file.name

        try:
            if filename.lower().endswith('.pdf'):
                text = DocumentProcessor.extract_text_from_pdf(tmp_path)
                # 返回文件名和提取的文本
                return {
                    'filename': filename,
                    'text': text,
                    'size': f"{size / 1024 / 1024:.2f}MB"
                }
            else:
                raise Exception("不支持的文件类型")
        finally:
            os.unlink(tmp_path)

    @staticmethod
    def download_and_process_file(url):
        """下载并处理URL文件"""
        parsed_url = urlparse(url)
        
        # 如果是PDF文件
        if parsed_url.path.lower().endswith('.pdf'):
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # 检查文件大小
                content_length = int(response.headers.get('content-length', 0))
                if content_length > DOC_CONFIG['MAX_FILE_SIZE']:
                    raise Exception("文件大小超过限制")

                # 创建临时文件
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    tmp_file.write(response.content)
                    tmp_path = tmp_file.name

                try:
                    text = DocumentProcessor.extract_text_from_pdf(tmp_path)
                    return {
                        'filename': os.path.basename(parsed_url.path),
                        'text': text,
                        'size': f"{content_length / 1024 / 1024:.2f}MB"
                    }
                finally:
                    os.unlink(tmp_path)
                    
            except requests.exceptions.RequestException as e:
                raise Exception(f"PDF下载失败: {str(e)}")
        else:
            # 如果是普通网页
            return {
                'url': url,
                'text': DocumentProcessor.extract_text_from_url(url)
            } 