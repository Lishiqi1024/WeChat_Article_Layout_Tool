# 微信公众号排版助手

一个基于 AI 的智能排版工具，可以一键将普通文本转换为微信公众号格式。

## 功能特点

- 智能排版：自动识别文章结构，应用微信公众号风格
- 长文本支持：自动分块处理长文本，避免 API 超时
- 实时预览：所见即所得的编辑体验
- 一键复制：快速复制排版后的内容
- 导出功能：支持导出为 HTML 文件

## 技术栈

### 前端
- Vue 3
- Element Plus
- WangEditor
- Axios
- SCSS

### 后端
- Flask
- Flask-CORS
- DeepSeek AI API

## 安装说明

### 环境要求
- Python 3.8+
- Node.js 16+
- NPM 8+

### 后端安装
进入后端目录
cd backend

安装依赖
pip install -r requirements.txt

启动服务
python app.py

### 前端安装
进入前端目录
cd frontend

安装依赖
npm install

启动服务
npm run dev

## 使用说明

1. 在左侧编辑器中输入或粘贴需要排版的文本
2. 点击"一键排版"按钮
3. 等待 AI 处理完成
4. 在右侧预览排版效果
5. 使用"复制内容"或"下载文档"按钮导出结果

## 排版规范

### 标题层级
- 主标题：24px，加粗，#333333
- 二级标题：18px，加粗，#666666
- 三级标题：16px，#888888

### 正文样式
- 字体大小：15px
- 行高：1.75
- 文字颜色：#333333

### 特殊格式
- 重要内容：使用加粗标签
- 引用：使用灰色背景块
- 列表：规范的符号和缩进

## 项目结构

```
wechat-formatter/
├── backend/              # Python后端
│   ├── app.py           # Flask主程序
│   ├── config.py        # 配置文件
│   └── requirements.txt # Python依赖
├── frontend/            # Vue前端
│   ├── src/            # 源代码目录
│   ├── public/         # 静态资源
│   └── package.json    # 项目配置
├── log.md              # 日志文件
└── README.md           # 项目说明
```

## 配置说明

### 后端配置
在 `backend/config.py` 中配置：
1. 复制 config.template.py 为 config.py
2. 在 config.py 中填入实际的 API 密钥和 URL
- DeepSeek API Key
- API URL
- 样式配置

### 前端配置
在 `frontend/vite.config.js` 中配置：
- 开发服务器端口
- API 代理设置
- CORS 配置

## 注意事项

1. 文本长度限制
   - 单次处理建议不超过 10000 字
   - 超长文本会自动分块处理

2. API 限制
   - API 请求超时时间为 120 秒
   - 建议控制单次请求的文本长度

3. 浏览器支持
   - 推荐使用 Chrome、Firefox 等现代浏览器
   - 确保浏览器已启用 JavaScript

## 错误处理

常见错误及解决方案：
- API 超时：尝试减少文本长度或分段处理
- 格式错误：检查输入文本是否包含特殊字符
- 网络问题：检查网络连接和 API 服务状态

## 开发计划

- [ ] 添加更多排版模板
- [ ] 支持自定义样式配置
- [ ] 添加批量处理功能
- [ ] 优化长文本处理性能
- [ ] 添加更多导出格式支持

## 贡献指南

欢迎提交 Issue 和 Pull Request。在提交代码前，请确保：
1. 代码符合项目规范
2. 添加必要的注释和文档
3. 通过所有测试

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或联系开发团队。




