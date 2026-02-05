<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '200px'" class="aside">
      <div class="logo">
        <img v-if="!isCollapse" :src="logoSrc" alt="LyEdu" class="logo-icon" />
        <img v-else :src="logoSrc" alt="LyEdu" class="logo-icon collapse" />
        <h2 v-if="!isCollapse">{{ siteTitle }}</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="false"
        router
        class="menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        <el-sub-menu index="org">
          <template #title>
            <el-icon><OfficeBuilding /></el-icon>
            <span>组织与人员</span>
          </template>
          <el-menu-item index="/department">公司架构</el-menu-item>
          <el-menu-item index="/user">员工管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="course-resource">
          <template #title>
            <el-icon><Notebook /></el-icon>
            <span>课程与资源</span>
          </template>
          <el-menu-item index="/course">课程管理</el-menu-item>
          <el-menu-item index="/course-comment">评论管理</el-menu-item>
          <el-menu-item index="/video">视频管理</el-menu-item>
          <el-menu-item index="/image">图片库</el-menu-item>
          <el-menu-item index="/knowledge">知识库</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="exam-center">
          <template #title>
            <el-icon><EditPen /></el-icon>
            <span>考试中心</span>
          </template>
          <el-menu-item index="/question">试题管理</el-menu-item>
          <el-menu-item index="/paper">试卷管理</el-menu-item>
          <el-menu-item index="/exam">考试管理</el-menu-item>
          <el-menu-item index="/exam-record">考试记录</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="training">
          <template #title>
            <el-icon><Aim /></el-icon>
            <span>培训任务</span>
          </template>
          <el-menu-item index="/task">周期任务</el-menu-item>
          <el-menu-item index="/user-task">用户任务</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="user-data">
          <template #title>
            <el-icon><User /></el-icon>
            <span>用户数据</span>
          </template>
          <el-menu-item index="/user-learning">学习记录</el-menu-item>
          <el-menu-item index="/user-point">积分记录</el-menu-item>
          <el-menu-item index="/user-certificate">用户证书</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="reward">
          <template #title>
            <el-icon><Medal /></el-icon>
            <span>证书与激励</span>
          </template>
          <el-menu-item index="/certificate-template">证书模板</el-menu-item>
          <el-menu-item index="/certificate">证书规则</el-menu-item>
          <el-menu-item index="/point-rule">积分规则</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-icon" @click="toggleCollapse">
            <Expand v-if="isCollapse" />
            <Fold v-else />
          </el-icon>
        </div>
        <div class="header-right">
          <el-tooltip content="查看系统使用说明" placement="bottom">
            <el-icon class="help-icon" @click="openSystemHelp">
              <QuestionFilled />
            </el-icon>
          </el-tooltip>
          <el-dropdown>
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ userInfo?.realName || userInfo?.username || '管理员' }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人设置</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getConfigByKey } from '@/api/config'
import { applyCustomTheme, applyDefaultTheme, applyThemeFromLogoUrl } from '@/utils/theme'
import { useHelp } from '@/hooks/useHelp'
import {
  DataBoard,
  OfficeBuilding,
  User,
  Notebook,
  VideoPlay,
  Picture,
  Collection,
  EditPen,
  Medal,
  Aim,
  Setting,
  Expand,
  Fold,
  ArrowDown,
  QuestionFilled
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const isCollapse = ref(false)
const siteTitle = ref('LyEdu')
const siteLogo = ref('')

const activeMenu = computed(() => route.path)

const logoSrc = computed(() => {
  const raw = siteLogo.value || '/icon-192.png'
  if (raw.startsWith('http://') || raw.startsWith('https://')) return raw
  if (raw.startsWith('/')) return window.location.origin + raw
  return raw
})

const userInfo = computed(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      return JSON.parse(userStr)
    } catch {
      return null
    }
  }
  return null
})

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const { openSystemHelp } = useHelp()

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  ElMessage.success('已退出登录')
  router.push('/login')
}

async function loadBranding() {
  try {
    const title = await getConfigByKey('site.title')
    if (title) siteTitle.value = title
  } catch (_e) {}
  try {
    const logo = await getConfigByKey('site.logo')
    if (logo) siteLogo.value = logo
  } catch (_e) {}

  try {
    const mode = (await getConfigByKey('site.theme_mode')) ?? 'auto'
    const modeStr = String(mode).toLowerCase()
    if (modeStr === 'custom') {
      const color = (await getConfigByKey('site.theme_color')) ?? '#409eff'
      applyCustomTheme(color)
    } else if (modeStr === 'default') {
      applyDefaultTheme()
    } else {
      await applyThemeFromLogoUrl(logoSrc.value)
    }
  } catch (_e) {}
}

onMounted(() => {
  loadBranding()
})
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
}

.aside {
  background-color: var(--sidebar-bg-color, #304156);
  transition: width 0.3s;
  overflow: hidden;

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    color: #fff;
    font-size: 20px;
    font-weight: bold;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);

    .logo-icon {
      width: 32px;
      height: 32px;
      flex-shrink: 0;
      display: block;
      object-fit: contain;

      &.collapse {
        width: 28px;
        height: 28px;
      }
    }

    h2 {
      margin: 0;
      max-width: 120px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-size: 16px;
      line-height: 32px;
      color: var(--el-color-primary);
    }
  }

  .menu {
    height: calc(100vh - 60px);
    overflow-y: auto;
    scrollbar-width: none; /* Firefox */
    -ms-overflow-style: none; /* IE 10+ */

    &::-webkit-scrollbar {
      width: 0;
      height: 0;
    }

    border-right: none;
    background-color: var(--sidebar-bg-color, #304156);

    :deep(.el-menu-item),
    :deep(.el-sub-menu__title) {
      color: rgba(255, 255, 255, 0.7);

      &:hover {
        background-color: rgba(255, 255, 255, 0.1);
        color: #fff;
      }
    }

    :deep(.el-menu-item) {
      &.is-active {
        background-color: var(--el-color-primary);
        color: var(--brand-on-primary, #fff);
      }
    }

    :deep(.el-sub-menu.is-opened > .el-sub-menu__title) {
      color: #fff;
    }

    /* 考试中心/证书中心 子菜单：背景与文字与侧栏一致 */
    :deep(.el-sub-menu .el-menu) {
      background-color: rgba(0, 0, 0, 0.15);
    }
    :deep(.el-sub-menu .el-menu .el-menu-item) {
      color: rgba(255, 255, 255, 0.7);
      background-color: transparent;
      &:hover {
        background-color: rgba(255, 255, 255, 0.1);
        color: #fff;
      }
      &.is-active {
        background-color: var(--el-color-primary);
        color: var(--brand-on-primary, #fff);
      }
    }

    :deep(.el-icon) {
      color: inherit;
    }
  }
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;

  .header-left {
    .collapse-icon {
      font-size: 20px;
      cursor: pointer;
      color: #606266;

      &:hover {
        color: var(--el-color-primary);
      }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;

    .help-icon {
      font-size: 20px;
      cursor: pointer;
      color: #909399;

      &:hover {
        color: var(--el-color-primary);
      }
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      color: #606266;

      &:hover {
        color: var(--el-color-primary);
      }
    }
  }
}

.main {
  background-color: #f0f2f5;
  padding: 0;
  overflow: hidden;
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;

  // 仪表盘页面允许全局滚动
  :deep(.dashboard-container) {
    overflow-y: auto;
    height: 100%;
  }

  // 非仪表盘页面：限制高度，只允许内容滚动
  :deep(.user-container),
  :deep(.course-container),
  :deep(.video-container),
  :deep(.comment-container),
  :deep(.user-learning-container),
  :deep(.exam-record-container),
  :deep(.user-point-container),
  :deep(.user-certificate-container),
  :deep(.user-task-container),
  :deep(.department-container),
  :deep(.knowledge-container),
  :deep(.exam-container),
  :deep(.paper-container),
  :deep(.question-container),
  :deep(.point-rule-container),
  :deep(.certificate-container),
  :deep(.certificate-template-container),
  :deep(.task-container),
  :deep(.image-library-container),
  :deep(.settings-container) {
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    > .el-card {
      height: 100%;
      display: flex;
      flex-direction: column;
      margin: 0;
      border-radius: 0;
      border-left: none;
      border-right: none;
      border-top: none;

      .el-card__header {
        padding: 16px 20px;
        flex-shrink: 0;
      }

      .el-card__body {
        padding: 20px;
        flex: 1;
        overflow: hidden;
        min-height: 0;
        display: flex;
        flex-direction: column;

        // 搜索表单不滚动，固定在顶部
        .search-form {
          flex-shrink: 0;
          margin-bottom: 20px;
        }

        // 表格区域：自动填充剩余空间
        .el-table {
          flex: 1;
          min-height: 0;
          display: flex;
          flex-direction: column;
          
          // Element Plus 表格内部结构：让 body-wrapper 滚动
          :deep(.el-table__inner) {
            flex: 1;
            min-height: 0;
            display: flex;
            flex-direction: column;
          }
          
          :deep(.el-table__header-wrapper) {
            flex-shrink: 0;
          }
          
          :deep(.el-table__body-wrapper) {
            flex: 1;
            min-height: 0;
            overflow-y: auto !important;
          }
        }

        // 分页器固定在底部
        .el-pagination {
          flex-shrink: 0;
          margin-top: 20px;
        }
      }
    }
  }

  // 移除所有页面容器的顶部间距
  :deep(.el-card) {
    margin: 0;
    border-radius: 0;
    border-left: none;
    border-right: none;
    border-top: none;

    .el-card__header {
      padding: 16px 20px;
    }

    .el-card__body {
      padding: 20px;
    }
  }
}
</style>
