<template>
  <div class="app-container">
    <el-container>
      <el-header>
        <h1>微信公众号排版助手</h1>
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
                    style="height: 500px; overflow-y: hidden;"
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
import { ElMessage } from 'element-plus'

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
</style> 