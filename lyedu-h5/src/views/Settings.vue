<template>
  <div class="page">
    <van-nav-bar title="设置" left-arrow @click-left="$router.back()" fixed placeholder />
    <div class="content">
      <van-cell-group inset title="播放规则">
        <van-cell title="防拖拽进度条" :value="playerConfig.disableSeek ? '已开启' : '未开启'" />
        <van-cell title="禁止倍速播放" :value="playerConfig.disableSpeed ? '已开启' : '未开启'" />
      </van-cell-group>
      <p class="config-tip">以上规则由管理员在后台设置，学习时请按要求完成观看。</p>

      <van-cell-group inset title="其他">
        <van-cell title="清除缓存" value="清除本地缓存数据" is-link @click="handleClearCache" />
      </van-cell-group>

      <div v-if="isLoggedIn" class="logout-wrap">
        <van-button type="danger" block round @click="handleLogout">退出登录</van-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, showSuccessToast } from 'vant'
import { getConfigByKey } from '@/api/config'

const router = useRouter()
const isLoggedIn = ref(!!localStorage.getItem('token'))
const playerConfig = reactive({ disableSeek: false, disableSpeed: false })

async function loadPlayerConfig() {
  try {
    const [seek, speed] = await Promise.all([
      getConfigByKey('player.disable_seek').catch(() => '0'),
      getConfigByKey('player.disable_speed').catch(() => '0')
    ])
    playerConfig.disableSeek = seek === '1' || seek === true
    playerConfig.disableSpeed = speed === '1' || speed === true
  } catch {
    // 保持默认
  }
}

function handleClearCache() {
  showConfirmDialog({
    title: '清除缓存',
    message: '将清除本地缓存，是否继续？'
  })
    .then(() => {
      try {
        // 仅清除非登录态相关缓存，保留 token/user
        const token = localStorage.getItem('token')
        const user = localStorage.getItem('user')
        localStorage.clear()
        if (token) localStorage.setItem('token', token)
        if (user) localStorage.setItem('user', user)
        showSuccessToast('已清除缓存')
      } catch {
        showSuccessToast('操作完成')
      }
    })
    .catch(() => {})
}

function handleLogout() {
  showConfirmDialog({
    title: '退出登录',
    message: '确定要退出登录吗？'
  })
    .then(() => {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      isLoggedIn.value = false
      showSuccessToast('已退出登录')
      router.replace('/login')
    })
    .catch(() => {})
}

onMounted(() => {
  isLoggedIn.value = !!localStorage.getItem('token')
  loadPlayerConfig()
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
.config-tip {
  font-size: 12px;
  color: #969799;
  margin: 8px 16px 16px;
  line-height: 1.5;
}
.logout-wrap {
  margin-top: 32px;
  padding: 0 16px;
}
</style>
