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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getConfigAll, batchSetConfig, type ConfigItem } from '@/api/config'

const activeTab = ref('site')
const saving = ref(false)
const form = reactive({
  site_title: '',
  site_keywords: '',
  site_description: '',
  player_allow_download: '0',
  player_disable_seek: '0',
  player_disable_speed: '0',
  student_default_page_size: 20
})

const keyToForm: Record<string, string> = {
  'site.title': 'site_title',
  'site.keywords': 'site_keywords',
  'site.description': 'site_description',
  'player.allow_download': 'player_allow_download',
  'student.default_page_size': 'student_default_page_size'
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
</style>
