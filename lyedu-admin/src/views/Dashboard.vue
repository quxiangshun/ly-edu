<template>
  <div class="dashboard-container">
    <div class="welcome">
      <h1>欢迎使用 LyEdu 企业培训系统</h1>
      <p>这是一个完全开源的企业培训解决方案</p>
      <div class="stats" v-loading="loadingOverview">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ overview.userCount }}</div>
            <div class="stat-label">学员总数</div>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ overview.courseCount }}</div>
            <div class="stat-label">课程总数</div>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ overview.departmentCount }}</div>
            <div class="stat-label">部门总数</div>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ overview.videoCount }}</div>
            <div class="stat-label">视频总数</div>
          </div>
        </el-card>
      </div>

      <el-card class="rank-card" v-loading="loadingRank">
        <template #header><span>学习排行</span></template>
        <el-table :data="learningRank" stripe size="small">
          <el-table-column type="index" label="排名" width="60" />
          <el-table-column prop="realName" label="姓名" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="departmentName" label="部门" />
          <el-table-column prop="courseCount" label="学习课程数" width="110" />
          <el-table-column prop="avgProgress" label="平均进度" width="100">
            <template #default="{ row }">{{ row.avgProgress != null ? Math.round(Number(row.avgProgress)) + '%' : '-' }}</template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card class="export-card">
        <template #header><span>数据导出</span></template>
        <div class="export-buttons">
          <el-button type="primary" @click="downloadLearnersCsv">学员信息导出</el-button>
          <el-button type="primary" @click="downloadLearningCsv">学习记录导出</el-button>
          <el-button type="primary" @click="downloadDepartmentLearningCsv">部门学习统计导出</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getOverview, getLearningRank, downloadLearnersCsv as doDownloadLearners, downloadLearningCsv as doDownloadLearning, downloadDepartmentLearningCsv as doDownloadDept } from '@/api/stats'

const loadingOverview = ref(false)
const loadingRank = ref(false)
const overview = reactive({ userCount: 0, courseCount: 0, departmentCount: 0, videoCount: 0 })
const learningRank = ref<Record<string, unknown>[]>([])

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
  width: 100%;
  height: 100%;
}

.welcome {
  padding: 40px;
  text-align: center;

  h1 {
    font-size: 32px;
    color: #303133;
    margin-bottom: 10px;
  }

  p {
    font-size: 16px;
    color: #909399;
    margin-bottom: 40px;
  }

  .stats {
    display: flex;
    gap: 20px;
    justify-content: center;
    margin-top: 40px;
    flex-wrap: wrap;

    .stat-card {
      width: 180px;

      .stat-content {
        text-align: center;

        .stat-value {
          font-size: 36px;
          font-weight: bold;
          color: #667eea;
          margin-bottom: 10px;
        }

        .stat-label {
          font-size: 14px;
          color: #909399;
        }
      }
    }
  }

  .rank-card {
    max-width: 800px;
    margin: 30px auto 0;
  }

  .export-card {
    max-width: 800px;
    margin: 20px auto 0;

    .export-buttons {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }
  }
}
</style>
