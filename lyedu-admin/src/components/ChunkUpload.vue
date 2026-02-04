<template>
  <div class="chunk-upload">
    <el-upload
      ref="uploadRef"
      :auto-upload="false"
      :on-change="handleFileChange"
      :show-file-list="false"
      :accept="accept"
      drag
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        将文件拖到此处，或<em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持大文件上传，自动分片上传，支持断点续传
        </div>
      </template>
    </el-upload>

    <div v-if="currentFile" class="upload-info">
      <div class="file-info">
        <span class="file-name">{{ currentFile.name }}</span>
        <span class="file-size">{{ formatFileSize(currentFile.size) }}</span>
      </div>
      
      <el-progress
        :percentage="uploadProgress"
        :status="uploadStatus"
        :stroke-width="8"
        style="margin-top: 10px"
      />
      
      <div v-if="uploadProgress < 100" class="upload-actions" style="margin-top: 10px">
        <el-button
          v-if="isUploading"
          type="warning"
          @click="pauseUpload"
        >
          暂停
        </el-button>
        <el-button
          v-if="!isUploading && uploadProgress > 0"
          type="primary"
          @click="resumeUpload"
        >
          继续上传
        </el-button>
        <el-button type="danger" @click="cancelUpload">
          取消
        </el-button>
      </div>
      
      <div v-if="uploadStatus === 'success'" class="upload-success">
        <el-icon><circle-check /></el-icon>
        <span>上传成功！</span>
        <span v-if="fileUrl" class="file-url">{{ fileUrl }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled, CircleCheck } from '@element-plus/icons-vue'
import type { UploadInstance, UploadFile } from 'element-plus'
import {
  initUpload,
  uploadChunk,
  mergeChunks,
  cancelUpload as cancelUploadApi,
  getUploadProgress,
  type InitUploadRequest
} from '@/api/upload'

const props = defineProps<{
  accept?: string
  chunkSize?: number // 分片大小（字节），默认 5MB
}>()

const emit = defineEmits<{
  (e: 'success', url: string): void
  (e: 'error', error: string): void
  (e: 'file-select', file: File): void
}>()

const uploadRef = ref<UploadInstance>()
const currentFile = ref<File | null>(null)
const fileId = ref<string>('')
const chunkSize = ref<number>(props.chunkSize || 5 * 1024 * 1024) // 默认 5MB
const totalChunks = ref<number>(0)
const uploadedChunks = ref<number[]>([])
const isUploading = ref<boolean>(false)
const uploadProgress = ref<number>(0)
const uploadStatus = ref<'success' | 'exception' | 'warning' | ''>('')
const fileUrl = ref<string>('')
const shouldPause = ref<boolean>(false)

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const handleFileChange = (file: UploadFile) => {
  if (file.raw) {
    currentFile.value = file.raw
    fileId.value = ''
    uploadProgress.value = 0
    uploadStatus.value = ''
    fileUrl.value = ''
    uploadedChunks.value = []
    shouldPause.value = false
    emit('file-select', file.raw)
    // 选择/拖入后自动开始上传
    startUpload()
  }
}

const generateFileId = (file: File): string => {
  // 使用文件名、大小和时间戳生成唯一ID
  return `${file.name}_${file.size}_${Date.now()}`
}

const startUpload = async () => {
  if (!currentFile.value) return
  
  try {
    isUploading.value = true
    shouldPause.value = false
    uploadStatus.value = ''
    
    // 初始化上传
    const initData: InitUploadRequest = {
      fileName: currentFile.value.name,
      fileSize: currentFile.value.size,
      fileType: currentFile.value.type || 'video/mp4',
      chunkSize: chunkSize.value
    }
    
    // 如果已有 fileId（断点续传），使用它
    if (fileId.value) {
      initData.fileId = fileId.value
    }
    
    const initRes = await initUpload(initData)
    fileId.value = initRes.fileId
    chunkSize.value = initRes.chunkSize
    totalChunks.value = initRes.totalChunks
    uploadedChunks.value = initRes.uploadedChunks || []
    
    // 开始上传分片
    await uploadAllChunks()
  } catch (error: any) {
    ElMessage.error('上传失败：' + (error?.response?.data?.message || error.message))
    uploadStatus.value = 'exception'
    isUploading.value = false
    emit('error', error.message)
  }
}

const uploadAllChunks = async () => {
  if (!currentFile.value || !fileId.value) return
  
  try {
    for (let i = 0; i < totalChunks.value; i++) {
      // 检查是否需要暂停
      if (shouldPause.value) {
        isUploading.value = false
        return
      }
      
      // 跳过已上传的分片
      if (uploadedChunks.value.includes(i)) {
        updateProgress()
        continue
      }
      
      // 读取分片
      const start = i * chunkSize.value
      const end = Math.min(start + chunkSize.value, currentFile.value.size)
      const chunkBlob = currentFile.value.slice(start, end)
      
      // 创建 File 对象用于上传
      const chunkFile = new File([chunkBlob], `${currentFile.value.name}.chunk${i}`, {
        type: currentFile.value.type || 'application/octet-stream'
      })
      
      // 上传分片
      await uploadChunk(fileId.value, i, chunkBlob.size, chunkFile)
      
      uploadedChunks.value.push(i)
      updateProgress()
    }
    
    // 所有分片上传完成，合并
    if (uploadedChunks.value.length === totalChunks.value) {
      const mergeRes = await mergeChunks(fileId.value)
      fileUrl.value = mergeRes.url
      uploadStatus.value = 'success'
      isUploading.value = false
      ElMessage.success('上传成功！')
      emit('success', mergeRes.url)
    }
  } catch (error: any) {
    ElMessage.error('上传失败：' + (error?.response?.data?.message || error.message))
    uploadStatus.value = 'exception'
    isUploading.value = false
    emit('error', error.message)
  }
}

const updateProgress = () => {
  uploadProgress.value = Math.round((uploadedChunks.value.length / totalChunks.value) * 100)
}

const pauseUpload = () => {
  shouldPause.value = true
  isUploading.value = false
  ElMessage.info('已暂停上传')
}

const resumeUpload = async () => {
  if (!fileId.value) {
    // 如果没有 fileId，重新开始
    await startUpload()
    return
  }
  
  try {
    // 获取当前进度
    const progressRes = await getUploadProgress(fileId.value)
    uploadedChunks.value = progressRes.uploadedChunkIndexes || []
    totalChunks.value = progressRes.totalChunks
    chunkSize.value = progressRes.fileSize / progressRes.totalChunks
    
    // 继续上传
    isUploading.value = true
    shouldPause.value = false
    await uploadAllChunks()
  } catch (error: any) {
    ElMessage.error('恢复上传失败：' + (error?.response?.data?.message || error.message))
  }
}

const cancelUpload = async () => {
  try {
    await ElMessageBox.confirm('确定要取消上传吗？', '提示', {
      type: 'warning'
    })
    
    if (fileId.value) {
      await cancelUploadApi(fileId.value)
    }
    
    currentFile.value = null
    fileId.value = ''
    uploadProgress.value = 0
    uploadStatus.value = ''
    fileUrl.value = ''
    uploadedChunks.value = []
    isUploading.value = false
    shouldPause.value = false
    
    ElMessage.info('已取消上传')
  } catch (error) {
    // 用户取消
  }
}
</script>

<style scoped lang="scss">
.chunk-upload {
  .upload-info {
    margin-top: 20px;
    padding: 15px;
    background: #f5f7fa;
    border-radius: 4px;
    
    .file-info {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .file-name {
        font-weight: 500;
        color: #303133;
      }
      
      .file-size {
        color: #909399;
        font-size: 12px;
      }
    }
    
    .upload-actions {
      display: flex;
      gap: 10px;
    }
    
    .upload-success {
      margin-top: 10px;
      padding: 10px;
      background: #f0f9ff;
      border-radius: 4px;
      display: flex;
      align-items: center;
      gap: 8px;
      color: #67c23a;
      
      .file-url {
        margin-left: auto;
        font-size: 12px;
        color: #409eff;
        word-break: break-all;
      }
    }
  }
}
</style>
