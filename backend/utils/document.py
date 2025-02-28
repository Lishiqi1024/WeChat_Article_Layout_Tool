import fitz  # PyMuPDF
import requests
import tempfile
import os
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
            else:
                raise Exception("不支持的文件类型")
            return text
        finally:
            os.unlink(tmp_path)

    @staticmethod
    def download_and_process_file(url):
        """下载并处理URL文件"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"文件下载失败: {str(e)}")

        # 检查文件大小
        content_length = int(response.headers.get('content-length', 0))
        if content_length > DOC_CONFIG['MAX_FILE_SIZE']:
            raise Exception("文件大小超过限制")

        # 获取文件扩展名
        content_type = response.headers.get('content-type', '')
        if 'pdf' not in content_type.lower():
            raise Exception("仅支持PDF文件")

        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name

        try:
            text = DocumentProcessor.extract_text_from_pdf(tmp_path)
            return text
        finally:
            os.unlink(tmp_path) 