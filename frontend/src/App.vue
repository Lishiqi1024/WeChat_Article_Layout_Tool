<template>
  <div class="app-container">
    <el-container>
      <el-header>
        <h1>微信公众号排版助手</h1>
        <div class="header-actions">
          <el-tabs v-model="activeTab" class="demo-tabs">
            <el-tab-pane label="URL分析" name="url">
              <el-input
                v-model="documentUrl"
                placeholder="输入PDF文档URL"
                style="width: 300px; margin-right: 10px;"
              />
              <el-button type="primary" @click="analyzeUrl" :loading="analyzing">
                分析文档
              </el-button>
            </el-tab-pane>
            
            <el-tab-pane label="本地PDF" name="file">
              <el-upload
                class="upload-demo"
                :action="'/api/analyze'"
                :on-success="handleUploadSuccess"
                :on-error="handleUploadError"
                :before-upload="beforeUpload"
                :show-file-list="false"
                accept=".pdf"
              >
                <el-button type="primary">选择PDF文件</el-button>
              </el-upload>
            </el-tab-pane>
            
            <el-tab-pane label="AI生成" name="generate">
              <el-input
                v-model="generatePrompt"
                placeholder="输入文章主题或关键词"
                style="width: 300px; margin-right: 10px;"
              />
              <el-button type="primary" @click="generateArticle" :loading="generating">
                生成文章
              </el-button>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-header>
      
      <el-main>
        <el-row :gutter="20">
          <!-- 左侧编辑区 -->
          <el-col :span="12">
            <div class="editor-container">
              <div class="editor-header">
                <el-button 
                  type="primary" 
                  @click="formatContent" 
                  :loading="loading"
                >
                  {{ loading ? '正在排版...' : '一键排版' }}
                </el-button>
                <el-button @click="clearContent">清空内容</el-button>
              </div>
              <div class="editor-body">
                <div style="border: 1px solid #ccc">
                  <Toolbar
                    style="border-bottom: 1px solid #ccc"
                    :editor="editor"
                    :defaultConfig="toolbarConfig"
                    :mode="mode"
                  />
                  <Editor
                    style="height: 780px; overflow-y: auto;"
                    v-model="html"
                    :defaultConfig="editorConfig"
                    :mode="mode"
                    @onCreated="handleCreated"
                  />
                </div>
              </div>
            </div>
          </el-col>
          
          <!-- 右侧预览区 -->
          <el-col :span="12">
            <div class="preview-container">
              <div class="preview-header">
                <el-button type="success" @click="copyContent">复制内容</el-button>
                <el-button @click="downloadContent">下载文档</el-button>
                <el-button type="primary" @click="publishToWechat" :loading="publishing">
                  发布到草稿箱
                </el-button>
              </div>
              <div class="preview-body" v-html="formattedContent"></div>
            </div>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, shallowRef, onBeforeUnmount } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

// 编辑器实例，必须用 shallowRef
const editor = shallowRef(null)

// 内容 HTML
const html = ref('')
const formattedContent = ref('')

// 模式
const mode = ref('default')

// 工具栏配置
const toolbarConfig = {
  excludeKeys: [
    'uploadImage',
    'uploadVideo',
    'insertTable',
    'group-video',
    'group-image',
    'group-more-style'
  ],
  insertKeys: {
    index: 0,
    keys: ['headerSelect', 'blockquote', '|']
  }
}

// 编辑器配置
const editorConfig = {
  placeholder: '请输入内容...',
  MENU_CONF: {},
  autoFocus: false,
  readOnly: false,
  customAlert: (s, t) => {
    ElMessage({
      message: s,
      type: t === 'success' ? 'success' : 'error',
    })
  }
}

// 组件销毁时，也及时销毁编辑器
onBeforeUnmount(() => {
  const editorInstance = editor.value
  if (editorInstance == null) return
  editorInstance.destroy()
})

const handleCreated = (e) => {
  editor.value = e
}

// 在 formatContent 函数中添加加载状态
const loading = ref(false)

const formatContent = async () => {
  try {
    const content = editor.value.getText()
    
    if (!content || content.trim() === '') {
      ElMessage.warning('请先输入内容')
      return
    }

    loading.value = true
    ElMessage.info('正在处理长文本，请耐心等待...')

    const response = await axios.post('/api/format', {
      content: content
    }, {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      withCredentials: false,
      timeout: 180000  // 3分钟超时
    })
    
    if (response.data && response.data.error) {
      throw new Error(response.data.error)
    }
    
    formattedContent.value = response.data
    ElMessage.success('排版完成！')
  } catch (error) {
    console.error('排版错误:', error)
    ElMessage.error('排版失败：' + (error.response?.data?.error || error.message))
  } finally {
    loading.value = false
  }
}

// 清空内容
const clearContent = () => {
  html.value = ''
  formattedContent.value = ''
  if (editor.value) {
    editor.value.clear()
  }
}

// 复制内容
const copyContent = () => {
  if (!formattedContent.value) {
    ElMessage.warning('没有可复制的内容')
    return
  }
  
  navigator.clipboard.writeText(formattedContent.value)
    .then(() => ElMessage.success('复制成功！'))
    .catch(() => ElMessage.error('复制失败！'))
}

// 下载文档
const downloadContent = () => {
  if (!formattedContent.value) {
    ElMessage.warning('没有可下载的内容')
    return
  }

  const blob = new Blob([formattedContent.value], { type: 'text/html' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = '微信文章.html'
  a.click()
  URL.revokeObjectURL(url)
}

// 添加新的响应式变量
const documentUrl = ref('')
const analyzing = ref(false)
const publishing = ref(false)
const articleTitle = ref('')
const activeTab = ref('url')
const generatePrompt = ref('')
const generating = ref(false)

// 处理文件上传
const beforeUpload = (file) => {
  const isPDF = file.type === 'application/pdf'
  if (!isPDF) {
    ElMessage.error('只能上传PDF文件!')
    return false
  }
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  return true
}

const handleUploadSuccess = (response) => {
  if (response.success) {
    editor.value.setHtml(response.content)
    ElMessage({
      type: 'success',
      message: response.message,
      duration: 5000
    })
  } else {
    ElMessage.error(response.error || '文档分析失败')
  }
}

const handleUploadError = (error) => {
  ElMessage.error('文件上传失败：' + error.message)
}

// URL分析
const analyzeUrl = async () => {
  if (!documentUrl.value) {
    ElMessage.warning('请输入文档URL')
    return
  }

  try {
    analyzing.value = true
    const response = await axios.post('/api/analyze', {
      url: documentUrl.value
    })
    
    if (response.data.success) {
      editor.value.setHtml(response.data.content)
      ElMessage({
        type: 'success',
        message: response.data.message,
        duration: 5000
      })
    } else {
      throw new Error(response.data.error)
    }
  } catch (error) {
    ElMessage.error('文档分析失败：' + (error.response?.data?.error || error.message))
  } finally {
    analyzing.value = false
  }
}

// AI生成文章
const generateArticle = async () => {
  if (!generatePrompt.value) {
    ElMessage.warning('请输入文章主题或关键词')
    return
  }

  try {
    generating.value = true
    const response = await axios.post('/api/generate', {
      prompt: generatePrompt.value
    })
    
    editor.value.setHtml(response.data.content)
    ElMessage.success('文章生成完成')
  } catch (error) {
    ElMessage.error('文章生成失败：' + error.message)
  } finally {
    generating.value = false
  }
}

// 发布到微信草稿箱
const publishToWechat = async () => {
  if (!formattedContent.value) {
    ElMessage.warning('请先生成排版内容')
    return
  }

  try {
    // 弹出输入标题对话框
    const { value: title } = await ElMessageBox.prompt('请输入文章标题', '发布到草稿箱', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: articleTitle.value,
      inputValidator: (value) => {
        if (!value) {
          return '标题不能为空'
        }
        if (value.length > 64) {
          return '标题长度不能超过64个字符'
        }
        return true
      }
    })

    articleTitle.value = title
    publishing.value = true

    const response = await axios.post('/api/publish', {
      title: title,
      content: formattedContent.value
    })

    if (response.data.success) {
      ElMessage.success('发布成功！请在公众号后台查看草稿')
    } else {
      throw new Error(response.data.error || '发布失败')
    }

  } catch (error) {
    if (error.message !== 'cancel') {  // 忽略用户取消的情况
      ElMessage.error(error.response?.data?.error || error.message || '发布失败')
    }
  } finally {
    publishing.value = false
  }
}
</script>

<style src="@wangeditor/editor/dist/css/style.css"></style>

<style lang="scss" scoped>
.app-container {
  height: 100vh;
  
  :deep(.el-container) {
    height: 100%;
  }
  
  :deep(.el-header) {
    background: #fff;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    h1 {
      margin: 0;
      font-size: 20px;
    }
  }
  
  .editor-container,
  .preview-container {
    height: calc(100vh - 120px);
    min-height: 500px;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    
    .editor-header,
    .preview-header {
      padding: 10px;
      border-bottom: 1px solid #dcdfe6;
    }
    
    .editor-body,
    .preview-body {
      height: calc(100% - 60px);
      padding: 20px;
      overflow-y: auto;
    }
  }
}

.preview-body {
  background: #fff;
  font-size: 15px;
  line-height: 1.75;
  color: #333;
  
  :deep(h1) { font-size: 24px; color: #333; font-weight: bold; }
  :deep(h2) { font-size: 18px; color: #666; font-weight: bold; }
  :deep(h3) { font-size: 16px; color: #888; }
  
  :deep(p) { margin: 1em 0; }
  
  :deep(blockquote) {
    background: #f4f4f4;
    border-left: 4px solid #ddd;
    padding: 15px;
    margin: 1em 0;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  margin-left: auto;
  
  .el-tabs {
    margin-right: 20px;
  }
  
  .upload-demo {
    display: inline-block;
  }
}
</style>