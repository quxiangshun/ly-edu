<template>
  <div class="page">
    <van-nav-bar title="个人资料" left-arrow @click-left="$router.back()" fixed placeholder />

    <div class="content">
      <div class="avatar-block">
        <van-uploader
          :max-count="1"
          accept="image/*"
          :after-read="onAfterRead"
          :preview-image="false"
        >
          <div class="avatar-wrap">
            <van-image
              round
              width="76"
              height="76"
              :src="form.avatar || 'https://via.placeholder.com/76'"
            />
            <div class="avatar-tip">点击更换头像</div>
          </div>
        </van-uploader>
      </div>

      <van-cell-group inset>
        <van-field v-model="form.nickname" label="昵称" placeholder="请输入昵称" maxlength="20" />
      </van-cell-group>

      <div class="actions">
        <van-button type="primary" block round @click="handleSave">保存</van-button>
        <van-button type="default" block round @click="handleReset" class="btn-secondary">恢复为登录信息</van-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from 'vue'
import { showSuccessToast, showFailToast } from 'vant'

type UserLike = Record<string, any>

const form = reactive({
  avatar: '',
  nickname: ''
})

function readUser(): UserLike {
  try {
    const raw = localStorage.getItem('user')
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

function writeUser(patch: Partial<UserLike>) {
  const u = readUser()
  const next = { ...u, ...patch }
  localStorage.setItem('user', JSON.stringify(next))
  return next
}

function loadFromStorage() {
  const u = readUser()
  form.avatar = (u.avatar as string) || ''
  form.nickname = (u.nickname as string) || (u.realName as string) || (u.username as string) || ''
}

function onAfterRead(file: any) {
  // van-uploader after-read: file.content 可能是 base64，也可能只有 file.file（取决于版本）
  const content = file?.content
  if (typeof content === 'string' && content.startsWith('data:')) {
    form.avatar = content
    return
  }
  const f: File | undefined = file?.file
  if (!f) {
    showFailToast('读取图片失败')
    return
  }
  const reader = new FileReader()
  reader.onload = () => {
    const result = reader.result
    if (typeof result === 'string') form.avatar = result
  }
  reader.onerror = () => showFailToast('读取图片失败')
  reader.readAsDataURL(f)
}

function handleSave() {
  const nickname = form.nickname.trim()
  if (!nickname) {
    showFailToast('请输入昵称')
    return
  }
  writeUser({ avatar: form.avatar, nickname })
  showSuccessToast('保存成功')
}

function handleReset() {
  // 清掉本地覆盖字段，回退到登录返回的 userInfo
  const u = readUser()
  delete u.nickname
  delete u.avatar
  localStorage.setItem('user', JSON.stringify(u))
  loadFromStorage()
  showSuccessToast('已恢复')
}

onMounted(() => {
  loadFromStorage()
})
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #f7f8fa;
}
.content {
  padding: 16px;
}
.avatar-block {
  display: flex;
  justify-content: center;
  padding: 8px 0 14px;
}
.avatar-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.avatar-tip {
  font-size: 12px;
  color: #969799;
}
.actions {
  margin-top: 16px;
  padding: 0 8px;
}
.btn-secondary {
  margin-top: 10px;
}
</style>

