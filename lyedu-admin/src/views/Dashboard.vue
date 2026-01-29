<template>
  <div class="dashboard-container">
    <div class="welcome">
      <h1>欢迎使用 LyEdu 企业培训系统</h1>
      <p>这是一个完全开源的企业培训解决方案</p>
      <div class="stats">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">0</div>
            <div class="stat-label">学员总数</div>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">0</div>
            <div class="stat-label">课程总数</div>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">0</div>
            <div class="stat-label">部门总数</div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Dashboard 页面 - 已使用 Layout 组件，无需重复的 header 和菜单
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

    .stat-card {
      width: 200px;

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
}
</style>
