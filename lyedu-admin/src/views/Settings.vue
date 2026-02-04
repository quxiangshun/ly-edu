<template>
  <div class="settings-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统配置</span>
          <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="网站设置" name="site">
          <el-form label-width="140px" class="settings-form">
            <el-form-item label="公司 Logo">
              <div class="logo-row">
                <el-image :src="logoPreviewSrc" fit="contain" class="logo-preview" />
                <el-upload
                  :show-file-list="false"
                  :before-upload="beforeLogoUpload"
                  :http-request="handleLogoUpload"
                  accept=".jpg,.jpeg,.png,.gif,.webp"
                >
                  <el-button type="primary">上传 Logo</el-button>
                </el-upload>
                <el-button v-if="form.site_logo" type="default" @click="form.site_logo = ''">恢复默认</el-button>
              </div>
              <div class="logo-tip">默认显示系统图标，上传后会覆盖。建议比例 1:1（系统会压缩为 256×256 PNG），支持 jpg/png/gif/webp</div>
            </el-form-item>
            <el-form-item label="网站标题">
              <el-input v-model="form.site_title" placeholder="如：LyEdu 学习平台" />
            </el-form-item>
            <el-form-item label="SEO 关键词">
              <el-input v-model="form.site_keywords" placeholder="逗号分隔" />
            </el-form-item>
            <el-form-item label="网站描述">
              <el-input v-model="form.site_description" type="textarea" :rows="2" placeholder="网站描述" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="播放器设置" name="player">
          <el-form label-width="140px" class="settings-form">
            <el-form-item label="允许下载视频">
              <el-radio-group v-model="form.player_allow_download">
                <el-radio label="0">否</el-radio>
                <el-radio label="1">是</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="禁止拖拽进度条">
              <el-radio-group v-model="form.player_disable_seek">
                <el-radio label="0">否（允许拖拽）</el-radio>
                <el-radio label="1">是（防拖拽）</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="禁止倍速播放">
              <el-radio-group v-model="form.player_disable_speed">
                <el-radio label="0">否（允许倍速）</el-radio>
                <el-radio label="1">是（仅 1x）</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="学员端设置" name="student">
          <el-form label-width="140px" class="settings-form">
            <el-form-item label="列表每页条数">
              <el-input-number v-model="form.student_default_page_size" :min="5" :max="100" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getConfigAll, batchSetConfig, type ConfigItem } from '@/api/config'
import { uploadImage } from '@/api/image'

const activeTab = ref('site')
const saving = ref(false)
const form = reactive({
  site_logo: '',
  site_title: '',
  site_keywords: '',
  site_description: '',
  player_allow_download: '0',
  player_disable_seek: '0',
  player_disable_speed: '0',
  student_default_page_size: 20
})

const keyToForm: Record<string, string> = {
  'site.logo': 'site_logo',
  'site.title': 'site_title',
  'site.keywords': 'site_keywords',
  'site.description': 'site_description',
  'player.allow_download': 'player_allow_download',
  'student.default_page_size': 'student_default_page_size'
}

function toAbsUrl(url?: string) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  return window.location.origin + url
}

const logoPreviewSrc = computed(() => {
  // 预览区：默认展示系统图标；上传后展示上传的
  const raw = form.site_logo || '/icon-192.png'
  return toAbsUrl(raw)
})

function beforeLogoUpload(file: File) {
  const ok = /\.(jpe?g|png|gif|webp)$/i.test(file.name)
  if (!ok) {
    ElMessage.error('仅支持 jpg/png/gif/webp')
    return false
  }
  return true
}

function loadImageFromFile(file: File): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file)
    const img = new Image()
    img.onload = () => {
      URL.revokeObjectURL(url)
      resolve(img)
    }
    img.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error('load image failed'))
    }
    img.src = url
  })
}

async function compressToLogoFile(file: File, sizePx = 256): Promise<File> {
  const img = await loadImageFromFile(file)
  const canvas = document.createElement('canvas')
  canvas.width = sizePx
  canvas.height = sizePx
  const ctx = canvas.getContext('2d')
  if (!ctx) return file

  // 清空为透明背景（png/webp 保持透明；jpg 则会变黑，这里统一输出 png）
  ctx.clearRect(0, 0, sizePx, sizePx)

  // 保持比例居中绘制（不裁剪）
  const iw = img.naturalWidth || img.width
  const ih = img.naturalHeight || img.height
  const scale = Math.min(sizePx / iw, sizePx / ih)
  const w = Math.round(iw * scale)
  const h = Math.round(ih * scale)
  const x = Math.round((sizePx - w) / 2)
  const y = Math.round((sizePx - h) / 2)

  ctx.imageSmoothingEnabled = true
  // @ts-expect-error: safari fallback
  ctx.imageSmoothingQuality = 'high'
  ctx.drawImage(img, x, y, w, h)

  const blob: Blob = await new Promise((resolve) => {
    canvas.toBlob((b) => resolve(b || new Blob()), 'image/png')
  })

  const base = (file.name || 'logo').replace(/\.[^.]+$/, '')
  return new File([blob], `${base}-logo.png`, { type: 'image/png' })
}

async function handleLogoUpload({ file }: { file: File }) {
  try {
    const logoFile = await compressToLogoFile(file, 256)
    const res = await uploadImage(logoFile)
    const url = (res as any)?.url
    if (url) {
      form.site_logo = url
      ElMessage.success('上传成功')
    } else {
      ElMessage.error('上传失败：未返回 URL')
    }
  } catch (_e) {
    ElMessage.error('上传失败')
  }
}

async function loadConfig() {
  try {
    const res = await getConfigAll()
    const list = (res as unknown as { data?: ConfigItem[] })?.data ?? res ?? []
    if (Array.isArray(list)) {
      list.forEach((c: ConfigItem) => {
        const key = c.configKey
        const formKey = keyToForm[key]
        if (formKey && form.hasOwnProperty(formKey)) {
          ;(form as Record<string, unknown>)[formKey] = c.configValue ?? ''
        }
      })
      if (typeof form.student_default_page_size === 'string') {
        form.student_default_page_size = parseInt(form.student_default_page_size, 10) || 20
      }
    }
  } catch (_e) {
    ElMessage.error('加载配置失败')
  }
}

async function handleSave() {
  saving.value = true
  try {
    await batchSetConfig({
      'site.logo': form.site_logo,
      'site.title': form.site_title,
      'site.keywords': form.site_keywords,
      'site.description': form.site_description,
      'player.allow_download': String(form.player_allow_download),
      'player.disable_seek': String(form.player_disable_seek),
      'player.disable_speed': String(form.player_disable_speed),
      'student.default_page_size': String(form.student_default_page_size)
    })
    ElMessage.success('保存成功')
  } catch (_e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => loadConfig())
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.settings-form {
  max-width: 560px;
}
.logo-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.logo-preview {
  width: 48px;
  height: 48px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background: #fff;
}
.logo-tip {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
}
</style>
