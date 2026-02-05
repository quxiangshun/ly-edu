<template>
  <div class="dashboard-container">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="banner-content">
        <h1 class="banner-title">
          <el-icon class="title-icon"><DataBoard /></el-icon>
          欢迎使用 LyEdu 企业培训系统
        </h1>
        <p class="banner-subtitle">这是一个完全开源的企业培训解决方案，助力企业构建高效的学习体系</p>
      </div>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-section" v-loading="loadingOverview">
      <div class="stats-grid">
        <el-card class="stat-card stat-card-user" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon-wrapper user-icon">
              <el-icon class="stat-icon"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ formatNumber(overview.userCount) }}</div>
              <div class="stat-label">学员总数</div>
            </div>
          </div>
          <div class="stat-footer">
            <span class="stat-trend">活跃学员</span>
          </div>
        </el-card>

        <el-card class="stat-card stat-card-course" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon-wrapper course-icon">
              <el-icon class="stat-icon"><Notebook /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ formatNumber(overview.courseCount) }}</div>
              <div class="stat-label">课程总数</div>
            </div>
          </div>
          <div class="stat-footer">
            <span class="stat-trend">优质课程</span>
          </div>
        </el-card>

        <el-card class="stat-card stat-card-department" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon-wrapper department-icon">
              <el-icon class="stat-icon"><OfficeBuilding /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ formatNumber(overview.departmentCount) }}</div>
              <div class="stat-label">部门总数</div>
            </div>
          </div>
          <div class="stat-footer">
            <span class="stat-trend">组织架构</span>
          </div>
        </el-card>

        <el-card class="stat-card stat-card-video" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon-wrapper video-icon">
              <el-icon class="stat-icon"><VideoPlay /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ formatNumber(overview.videoCount) }}</div>
              <div class="stat-label">视频总数</div>
            </div>
          </div>
          <div class="stat-footer">
            <span class="stat-trend">学习资源</span>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content-section">
      <!-- 学习排行榜 -->
      <el-card class="rank-card" shadow="hover" v-loading="loadingRank">
        <template #header>
          <div class="card-header-custom">
            <el-icon class="header-icon"><Trophy /></el-icon>
            <span>学习排行榜</span>
          </div>
        </template>
        <div class="rank-table-wrapper">
          <el-table :data="learningRank" stripe style="width: 100%" :max-height="550">
            <el-table-column type="index" label="排名" width="80" align="center">
              <template #default="{ $index }">
                <div class="rank-badge" :class="getRankClass($index)">
                  {{ $index + 1 }}
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="realName" label="姓名" min-width="100">
              <template #default="{ row }">
                <div class="user-info">
                  <el-icon class="user-avatar-icon"><User /></el-icon>
                  <span>{{ row.realName || row.username || '未知' }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="username" label="用户名" min-width="120" />
            <el-table-column prop="departmentName" label="部门" min-width="120">
              <template #default="{ row }">
                <el-tag size="small" type="info">{{ row.departmentName || '-' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="courseCount" label="学习课程数" width="120" align="center">
              <template #default="{ row }">
                <el-tag type="success" size="small">{{ row.courseCount || 0 }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="avgProgress" label="平均进度" width="140" align="center">
              <template #default="{ row }">
                <div class="progress-cell">
                  <el-progress
                    :percentage="row.avgProgress != null ? Math.round(Number(row.avgProgress)) : 0"
                    :color="getProgressColor(row.avgProgress)"
                    :stroke-width="8"
                    :show-text="true"
                  />
                </div>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="learningRank.length === 0" class="empty-rank">
            <el-empty description="暂无学习数据" :image-size="100" />
          </div>
        </div>
      </el-card>

      <!-- 数据导出 -->
      <el-card class="export-card" shadow="hover">
        <template #header>
          <div class="card-header-custom">
            <el-icon class="header-icon"><Download /></el-icon>
            <span>数据导出</span>
          </div>
        </template>
        <div class="export-buttons">
          <el-button type="primary" size="large" @click="downloadLearnersCsv" class="export-btn">
            <el-icon><User /></el-icon>
            <span>学员信息导出</span>
          </el-button>
          <el-button type="success" size="large" @click="downloadLearningCsv" class="export-btn">
            <el-icon><Document /></el-icon>
            <span>学习记录导出</span>
          </el-button>
          <el-button type="warning" size="large" @click="downloadDepartmentLearningCsv" class="export-btn">
            <el-icon><OfficeBuilding /></el-icon>
            <span>部门学习统计导出</span>
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import {
  DataBoard,
  User,
  Notebook,
  OfficeBuilding,
  VideoPlay,
  Trophy,
  Download,
  Document
} from '@element-plus/icons-vue'
import {
  getOverview,
  getLearningRank,
  downloadLearnersCsv as doDownloadLearners,
  downloadLearningCsv as doDownloadLearning,
  downloadDepartmentLearningCsv as doDownloadDept
} from '@/api/stats'

const loadingOverview = ref(false)
const loadingRank = ref(false)
const overview = reactive({ userCount: 0, courseCount: 0, departmentCount: 0, videoCount: 0 })
const learningRank = ref<Record<string, unknown>[]>([])

const formatNumber = (num: number): string => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toString()
}

const getRankClass = (index: number): string => {
  if (index === 0) return 'rank-gold'
  if (index === 1) return 'rank-silver'
  if (index === 2) return 'rank-bronze'
  return ''
}

const getProgressColor = (progress: unknown): string => {
  const p = progress != null ? Number(progress) : 0
  if (p >= 80) return '#67c23a'
  if (p >= 60) return '#e6a23c'
  if (p >= 40) return '#f56c6c'
  return '#909399'
}

const loadOverview = async () => {
  loadingOverview.value = true
  try {
    const res = await getOverview()
    if (res) {
      overview.userCount = res.userCount ?? 0
      overview.courseCount = res.courseCount ?? 0
      overview.departmentCount = res.departmentCount ?? 0
      overview.videoCount = res.videoCount ?? 0
    }
  } finally {
    loadingOverview.value = false
  }
}

const loadRank = async () => {
  loadingRank.value = true
  try {
    const res = await getLearningRank(20)
    learningRank.value = Array.isArray(res) ? res : []
  } finally {
    loadingRank.value = false
  }
}

function downloadLearnersCsv() {
  doDownloadLearners()
}
function downloadLearningCsv() {
  doDownloadLearning()
}
function downloadDepartmentLearningCsv() {
  doDownloadDept()
}

onMounted(() => {
  loadOverview()
  loadRank()
})
</script>

<style scoped lang="scss">
.dashboard-container {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 0;
  // 移除固定高度，让内容自适应
}

// 欢迎横幅
.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 0;
  padding: 32px 40px;
  margin-bottom: 0;
  box-shadow: none;
  color: white;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
    animation: rotate 20s linear infinite;
  }

  .banner-content {
    position: relative;
    z-index: 1;
  }

  .banner-title {
    font-size: 32px;
    font-weight: 700;
    margin: 0 0 12px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;

    .title-icon {
      font-size: 36px;
    }
  }

  .banner-subtitle {
    font-size: 16px;
    margin: 0;
    opacity: 0.95;
    line-height: 1.6;
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// 统计卡片区域
.stats-section {
  margin-bottom: 0;
  padding: 24px 24px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.stat-card {
  border-radius: 16px;
  border: none;
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  }

  .stat-content {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
  }

  .stat-icon-wrapper {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    .stat-icon {
      font-size: 28px;
      color: white;
    }

    &.user-icon {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    &.course-icon {
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }

    &.department-icon {
      background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }

    &.video-icon {
      background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
  }

  .stat-info {
    flex: 1;
    min-width: 0;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 700;
    color: #303133;
    margin-bottom: 6px;
    line-height: 1;
  }

  .stat-label {
    font-size: 13px;
    color: #909399;
    font-weight: 500;
  }

  .stat-footer {
    padding: 10px 20px;
    background: #f8f9fa;
    border-top: 1px solid #ebeef5;
    font-size: 12px;
    color: #909399;
  }
}

// 内容区域
.content-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  padding: 0 24px 24px;

  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
  }
}

.rank-card,
.export-card {
  border-radius: 16px;
  border: none;

  :deep(.el-card__header) {
    padding: 20px 24px;
    border-bottom: 1px solid #ebeef5;
  }

  :deep(.el-card__body) {
    padding: 24px;
  }
}

.card-header-custom {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;

  .header-icon {
    font-size: 20px;
    color: var(--el-color-primary);
  }
}

.rank-table-wrapper {
  max-height: 550px;
  overflow-y: auto;

  // 自定义滚动条样式
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;

    &:hover {
      background: #a8a8a8;
    }
  }

  .rank-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    font-weight: 600;
    font-size: 14px;
    background: #f0f2f5;
    color: #606266;

    &.rank-gold {
      background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
      color: #fff;
      box-shadow: 0 2px 8px rgba(255, 215, 0, 0.4);
    }

    &.rank-silver {
      background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
      color: #fff;
      box-shadow: 0 2px 8px rgba(192, 192, 192, 0.4);
    }

    &.rank-bronze {
      background: linear-gradient(135deg, #cd7f32 0%, #e6a857 100%);
      color: #fff;
      box-shadow: 0 2px 8px rgba(205, 127, 50, 0.4);
    }
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;

    .user-avatar-icon {
      color: #909399;
      font-size: 16px;
    }
  }

  .progress-cell {
    padding: 4px 0;
  }

  .empty-rank {
    padding: 40px 0;
  }
}

.export-card {
  .export-buttons {
    display: grid;
    grid-template-columns: 1fr;
    gap: 12px;

    .export-btn {
      width: 100%;
      justify-content: center;
      padding: 14px 20px;
      font-size: 14px;
      border-radius: 8px;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      gap: 8px;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }

      .el-icon {
        font-size: 16px;
      }

      span {
        flex: 1;
        text-align: center;
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .dashboard-container {
    padding: 16px;
  }

  .welcome-banner {
    padding: 24px;

    .banner-title {
      font-size: 24px;
      flex-direction: column;
      gap: 8px;
    }

    .banner-subtitle {
      font-size: 14px;
    }
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .content-section {
    gap: 16px;
  }
}
</style>
