<template>
  <div class="profile-container">
    <AppHeader />
    <el-main class="main-content">
      <div class="profile-content">
        <h2>个人中心</h2>
        <el-card v-loading="loading" class="profile-card">
          <template v-if="detail">
            <div class="profile-header">
              <el-avatar :size="80" :src="avatarUrl" class="profile-avatar">
                {{ (detail.nickname || detail.realName || detail.username || '用').charAt(0) }}
              </el-avatar>
              <div class="profile-basic">
                <div class="username">{{ detail.username }}</div>
                <div class="role-tag">{{ roleText }}</div>
              </div>
            </div>
            <el-form
              v-if="editing"
              ref="formRef"
              :model="form"
              :rules="rules"
              label-width="100px"
              class="profile-form"
            >
              <el-form-item label="真实姓名" prop="realName">
                <el-input v-model="form.realName" placeholder="真实姓名" clearable />
              </el-form-item>
              <el-form-item label="昵称" prop="nickname">
                <el-input v-model="form.nickname" placeholder="昵称" clearable />
              </el-form-item>
              <el-form-item label="邮箱" prop="email">
                <el-input v-model="form.email" placeholder="邮箱" clearable />
              </el-form-item>
              <el-form-item label="手机号" prop="mobile">
                <el-input v-model="form.mobile" placeholder="手机号" clearable />
              </el-form-item>
              <el-form-item label="头像地址" prop="avatar">
                <el-input v-model="form.avatar" placeholder="头像 URL（可选）" clearable />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
                <el-button @click="editing = false">取消</el-button>
              </el-form-item>
            </el-form>
            <div v-else class="profile-view">
              <div class="profile-row">
                <span class="label">真实姓名</span>
                <span class="value">{{ detail.realName || detail.real_name || '-' }}</span>
              </div>
              <div class="profile-row">
                <span class="label">昵称</span>
                <span class="value">{{ detail.nickname || '-' }}</span>
              </div>
              <div class="profile-row">
                <span class="label">邮箱</span>
                <span class="value">{{ detail.email || '-' }}</span>
              </div>
              <div class="profile-row">
                <span class="label">手机号</span>
                <span class="value">{{ detail.mobile || '-' }}</span>
              </div>
              <el-button type="primary" class="edit-btn" @click="startEdit">编辑资料</el-button>
            </div>
          </template>
          <el-empty v-else description="请先登录" />
        </el-card>
      </div>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import AppHeader from '@/components/AppHeader.vue'
import { getCurrentUser, getUserById, updateUser, type UserDetail } from '@/api/user'

const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const editing = ref(false)
const detail = ref<UserDetail | null>(null)
const formRef = ref<FormInstance>()
const form = ref({
  realName: '',
  nickname: '',
  email: '',
  mobile: '',
  avatar: ''
})

const rules: FormRules = {
  realName: [],
  nickname: [],
  email: [{ type: 'email', message: '请输入正确的邮箱', trigger: 'blur' }],
  mobile: []
}

const avatarUrl = computed(() => {
  const d = detail.value
  if (!d?.avatar) return ''
  const url = d.avatar
  if (url.startsWith('http')) return url
  if (url.startsWith('/')) return window.location.origin + url
  return url
})

const roleText = computed(() => {
  const r = detail.value?.role
  if (r === 'admin') return '管理员'
  if (r === 'teacher') return '教师'
  return '学员'
})

const loadDetail = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    router.push({ path: '/login', query: { redirect: '/profile' } })
    return
  }
  loading.value = true
  try {
    const current = await getCurrentUser()
    if (!current?.id) {
      router.push({ path: '/login', query: { redirect: '/profile' } })
      return
    }
    const res = await getUserById(current.id)
    detail.value = res
    form.value = {
      realName: res.realName ?? res.real_name ?? '',
      nickname: res.nickname ?? '',
      email: res.email ?? '',
      mobile: res.mobile ?? '',
      avatar: res.avatar ?? ''
    }
  } catch (_e) {
    ElMessage.error('获取用户信息失败')
    router.push('/')
  } finally {
    loading.value = false
  }
}

const startEdit = () => {
  if (detail.value) {
    form.value = {
      realName: detail.value.realName ?? (detail.value as { real_name?: string }).real_name ?? '',
      nickname: detail.value.nickname ?? '',
      email: detail.value.email ?? '',
      mobile: detail.value.mobile ?? '',
      avatar: detail.value.avatar ?? ''
    }
    editing.value = true
  }
}

const handleSave = async () => {
  if (!formRef.value || !detail.value) return
  try {
    await formRef.value.validate()
    saving.value = true
    await updateUser(detail.value.id, {
      realName: form.value.realName || undefined,
      nickname: form.value.nickname || undefined,
      email: form.value.email || undefined,
      mobile: form.value.mobile || undefined,
      avatar: form.value.avatar || undefined
    })
    ElMessage.success('保存成功')
    editing.value = false
    await loadDetail()
    // 更新本地缓存，便于 Header 展示
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        const u = JSON.parse(userStr) as Record<string, unknown>
        u.realName = form.value.realName || u.realName
        u.nickname = form.value.nickname || u.nickname
        localStorage.setItem('user', JSON.stringify(u))
      } catch (_e) {
        // ignore
      }
    }
  } catch (_e) {
    // 校验或请求失败
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped lang="scss">
.profile-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  background: #f5f7fa;
  padding: 40px 20px;
  margin-top: 60px;
}

.profile-content {
  max-width: 600px;
  margin: 0 auto;

  h2 {
    margin-bottom: 24px;
    color: #303133;
  }

  .profile-card {
    .profile-header {
      display: flex;
      align-items: center;
      gap: 24px;
      margin-bottom: 24px;
      padding-bottom: 24px;
      border-bottom: 1px solid #ebeef5;

      .profile-avatar {
        flex-shrink: 0;
      }

      .profile-basic {
        .username {
          font-size: 18px;
          font-weight: 600;
          color: #303133;
          margin-bottom: 8px;
        }

        .role-tag {
          font-size: 14px;
          color: #909399;
        }
      }
    }

    .profile-form {
      max-width: 400px;
    }

    .profile-view {
      .profile-row {
        display: flex;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #f0f0f0;

        .label {
          width: 100px;
          color: #909399;
          font-size: 14px;
        }

        .value {
          flex: 1;
          color: #303133;
        }
      }

      .edit-btn {
        margin-top: 24px;
      }
    }
  }
}
</style>
