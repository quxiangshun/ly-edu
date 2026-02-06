<template>
  <div class="settings-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="card-header-left">
            <span>系统配置</span>
            <el-tooltip content="查看本模块使用说明" placement="right">
              <el-icon class="card-help-icon" @click="openPageHelp('settings')">
                <QuestionFilled />
              </el-icon>
            </el-tooltip>
          </div>
          <div class="card-actions">
            <el-button type="default" @click="handleRestoreTheme">恢复默认</el-button>
            <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
          </div>
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
            <el-form-item label="主题色">
              <el-radio-group v-model="form.site_theme_mode">
                <el-radio label="auto">自适应</el-radio>
                <el-radio label="default">默认</el-radio>
                <el-radio label="custom">自定义</el-radio>
              </el-radio-group>
              <div v-if="form.site_theme_mode === 'custom'" class="theme-color-row">
                <el-color-picker v-model="form.site_theme_color" />
                <span class="theme-color-value">{{ form.site_theme_color || '#409eff' }}</span>
              </div>
              <div class="logo-tip">更改选项或 Logo/颜色会立即预览主题；“恢复默认”还原为已保存的样式。</div>
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
        <el-tab-pane label="飞书应用" name="feishu">
          <div class="feishu-tip">
            <p><strong>飞书同步功能</strong>：可将飞书企业通讯录中的机构（部门）和用户同步至本系统，不存在则创建、存在则更新。支持手动触发与定时更新。</p>
            <p>请先在飞书开放平台创建自建应用，并完成以下配置：</p>
            <ul>
              <li>在<strong>后端环境变量</strong>中设置：在 <code>lyedu-api-python/.env</code> 文件中添加：
                <pre style="background: #f5f7fa; padding: 6px 8px; border-radius: 4px; font-size: 12px; margin: 4px 0; display: inline-block;">FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret</pre>
                （如果 <code>.env</code> 不存在，可复制 <code>.env.example</code> 为 <code>.env</code> 后修改。配置后需重启后端服务。）
              </li>
              <li>在飞书开放平台该应用的<strong>权限管理</strong>中，申请并启用：<strong>通讯录 - 部门信息（只读）</strong>、<strong>通讯录 - 用户信息（只读）</strong>。</li>
            </ul>
            <p>配置完成后，可在「员工管理」页点击「从第三方同步」→「飞书」进行手动同步；定时同步可由后端配置定时任务调用 <code>POST /api/feishu/sync</code>。</p>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import { getConfigAll, batchSetConfig, getConfigByKey, type ConfigItem } from '@/api/config'
import { uploadImage } from '@/api/image'
import { applyThemeFromConfig, applyDefaultTheme, applyCustomTheme, applyThemeFromLogoUrl } from '@/utils/theme'
import { useHelp } from '@/hooks/useHelp'

const activeTab = ref('site')
const saving = ref(false)
const form = reactive({
  site_logo: '',
  site_theme_mode: 'auto' as 'auto' | 'default' | 'custom',
  site_theme_color: '#409eff',
  site_title: '',
  site_keywords: '',
  site_description: '',
  player_allow_download: '0',
  player_disable_seek: '0',
  player_disable_speed: '0',
  student_default_page_size: 20
})

const { openPageHelp } = useHelp()

const keyToForm: Record<string, string> = {
  'site.logo': 'site_logo',
  'site.theme_mode': 'site_theme_mode',
  'site.theme_color': 'site_theme_color',
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
      if (form.site_theme_mode === 'auto') {
        await applyThemeFromLogoUrl(toAbsUrl(url))
      }
    } else {
      ElMessage.error('上传失败：未返回 URL')
    }
  } catch (_e) {
    ElMessage.error('上传失败')
  }
}

function applyPreviewTheme() {
  const mode = form.site_theme_mode
  if (mode === 'default') {
    applyDefaultTheme()
    return
  }
  if (mode === 'custom') {
    applyCustomTheme(form.site_theme_color || '#409eff')
    return
  }
  applyThemeFromLogoUrl(logoPreviewSrc.value).catch(() => applyDefaultTheme())
}

async function handleRestoreTheme() {
  try {
    const mode = (await getConfigByKey('site.theme_mode')) ?? 'auto'
    const color = (await getConfigByKey('site.theme_color')) ?? ''
    const logo = (await getConfigByKey('site.logo')) ?? ''
    const logoUrl = logo ? (logo.startsWith('http') ? logo : window.location.origin + logo) : ''
    await applyThemeFromConfig(mode, color, logoUrl)
    ElMessage.success('已恢复为已保存的主题')
  } catch (_e) {
    applyDefaultTheme()
    ElMessage.success('已恢复为默认主题')
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
          if (key === 'site.theme_mode') {
            const v = String(c.configValue ?? 'auto').toLowerCase()
            ;(form as Record<string, unknown>)[formKey] = (v === 'default' || v === 'custom' ? v : 'auto') as string
          } else if (key === 'site.theme_color') {
            ;(form as Record<string, unknown>)[formKey] = c.configValue ?? '#409eff'
          } else {
            ;(form as Record<string, unknown>)[formKey] = c.configValue ?? ''
          }
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
      'site.theme_mode': form.site_theme_mode,
      'site.theme_color': form.site_theme_mode === 'custom' ? (form.site_theme_color || '#409eff') : '',
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

watch(
  () => [form.site_theme_mode, form.site_theme_color, form.site_logo],
  () => {
    applyPreviewTheme()
  },
  { deep: true }
)

onMounted(async () => {
  await loadConfig()
  applyPreviewTheme()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .card-header-left {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .card-help-icon {
    font-size: 16px;
    cursor: pointer;
    color: #909399;

    &:hover {
      color: var(--el-color-primary);
    }
  }
}
.settings-container {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 10px;
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
.theme-color-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}
.theme-color-value {
  font-size: 13px;
  color: #606266;
}
.feishu-tip {
  max-width: 560px;
  font-size: 14px;
  line-height: 1.7;
  color: #606266;
}
.feishu-tip p { margin: 0 0 12px; }
.feishu-tip ul { margin: 8px 0 12px; padding-left: 1.4em; }
.feishu-tip code { background: #f5f7fa; padding: 2px 6px; border-radius: 4px; font-size: 13px; }
</style>
