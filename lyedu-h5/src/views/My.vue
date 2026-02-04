<template>
  <div class="my-container">
    <van-nav-bar title="我的" fixed placeholder />

    <div class="user-info">
      <van-cell-group inset>
        <van-cell is-link @click="handleUserCellClick">
          <template #title>
            <div class="user-avatar">
              <van-image
                round
                width="60"
                height="60"
                :src="userInfo.avatar || 'https://via.placeholder.com/60'"
              />
              <div class="user-detail">
                <div class="username">{{ userInfo.displayName }}</div>
                <div class="user-desc">{{ userInfo.desc }}</div>
              </div>
            </div>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- 个人统计（与管理后台统计口径一致，仅展示当前用户） -->
    <div v-if="isLoggedIn" class="stats-section">
      <van-grid :column-num="5" :border="false">
        <van-grid-item>
          <div class="stat-value">{{ personalStats.courseCount }}</div>
          <div class="stat-label">学习课程</div>
        </van-grid-item>
        <van-grid-item>
          <div class="stat-value">{{ personalStats.avgProgress }}%</div>
          <div class="stat-label">平均进度</div>
        </van-grid-item>
        <van-grid-item @click="$router.push('/my-points')">
          <div class="stat-value">{{ personalStats.totalPoints }}</div>
          <div class="stat-label">积分</div>
        </van-grid-item>
        <van-grid-item @click="$router.push('/my-certificates')">
          <div class="stat-value">{{ personalStats.certificateCount }}</div>
          <div class="stat-label">证书</div>
        </van-grid-item>
        <van-grid-item @click="$router.push('/my-tasks')">
          <div class="stat-value">{{ personalStats.taskCompletedCount }}</div>
          <div class="stat-label">已完成</div>
        </van-grid-item>
      </van-grid>
    </div>

    <div class="menu-section">
      <van-cell-group inset>
        <van-cell title="我的学习" is-link icon="video-o" to="/my-learning" />
        <van-cell title="课程中心" is-link icon="orders-o" to="/courses" />
        <van-cell title="考试中心" is-link icon="notes-o" to="/exam" />
        <van-cell title="我的积分" is-link icon="gold-coin-o" to="/my-points" />
        <van-cell title="我的证书" is-link icon="medal-o" to="/my-certificates" />
        <van-cell title="我的任务" is-link icon="todo-list-o" to="/my-tasks" />
      </van-cell-group>
    </div>

    <div class="menu-section">
      <van-cell-group inset>
        <van-cell title="设置" is-link icon="setting-o" to="/settings" />
        <van-cell title="关于" is-link icon="info-o" to="/about" />
      </van-cell-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onActivated, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getWatchedCourses } from '@/api/learning'
import { getMyTotal } from '@/api/point'
import { getMyCertificates } from '@/api/userCertificate'
import { getMyTasks } from '@/api/userTask'

const router = useRouter()
const token = ref<string | null>(null)
const user = ref<Record<string, unknown>>({})

const personalStats = ref({
  courseCount: 0,
  avgProgress: 0,
  totalPoints: 0,
  certificateCount: 0,
  taskCompletedCount: 0
})

const isLoggedIn = computed(() => !!token.value)

const userInfo = computed(() => {
  if (!token.value) {
    return { displayName: '学员', desc: '点击登录', avatar: '' }
  }
  const u = user.value
  const name = (u.nickname as string) || (u.realName as string) || (u.username as string) || '学员'
  const role = (u.role as string) === 'admin' ? '管理员' : '学员'
  return {
    displayName: name,
    desc: role,
    avatar: (u.avatar as string) || ''
  }
})

function goLogin() {
  router.push({ path: '/login', query: { redirect: '/my' } })
}

function handleUserCellClick() {
  if (!token.value) {
    goLogin()
    return
  }
  router.push('/profile')
}

function loadUser() {
  token.value = localStorage.getItem('token')
  try {
    const raw = localStorage.getItem('user')
    user.value = raw ? JSON.parse(raw) : {}
  } catch {
    user.value = {}
  }
}

async function loadPersonalStats() {
  if (!token.value) return
  try {
    const [watched, points, certs, tasks] = await Promise.all([
      getWatchedCourses().catch(() => []),
      getMyTotal().catch(() => 0),
      getMyCertificates().catch(() => []),
      getMyTasks().catch(() => [])
    ])
    const list = Array.isArray(watched) ? watched : []
    const courseCount = list.length
    const avgProgress = courseCount > 0
      ? Math.round(list.reduce((s: number, i: { progress?: number }) => s + (i.progress ?? 0), 0) / courseCount)
      : 0
    const certList = Array.isArray(certs) ? certs : []
    const taskList = Array.isArray(tasks) ? tasks : []
    const taskCompletedCount = taskList.filter(
      (t: { userTask?: { status?: number } }) => t.userTask?.status === 1
    ).length
    personalStats.value = {
      courseCount,
      avgProgress,
      totalPoints: typeof points === 'number' ? points : 0,
      certificateCount: certList.length,
      taskCompletedCount
    }
  } catch {
    // 保持默认 0
  }
}

onMounted(() => {
  loadUser()
  loadPersonalStats()
  document.body.style.overflow = 'hidden'
})
onActivated(() => {
  loadUser()
  loadPersonalStats()
})
onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

<style scoped lang="scss">
.my-container {
  height: 100%;
  min-height: 0;
  overflow: hidden;
  background: #f7f8fa;
  padding-bottom: 20px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.stats-section {
  background: #fff;
  margin: 0 16px 16px;
  border-radius: 8px;
  padding: 16px 0;

  .stat-value {
    font-size: 18px;
    font-weight: bold;
    color: #323233;
    margin-bottom: 4px;
  }
  .stat-label {
    font-size: 12px;
    color: #969799;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1.2;
  }
}

.user-info {
  margin: 20px 0;

  .user-avatar {
    display: flex;
    align-items: center;
    gap: 15px;

    .user-detail {
      .username {
        font-size: 18px;
        font-weight: bold;
        color: #323233;
        margin-bottom: 5px;
      }

      .user-desc {
        font-size: 14px;
        color: #969799;
      }
    }
  }
}

.menu-section {
  margin-bottom: 20px;
}
</style>
