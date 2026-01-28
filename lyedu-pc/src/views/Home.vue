<template>
  <div class="home-container">
    <el-header class="header">
      <div class="header-content">
        <div class="logo">
          <h1>LyEdu</h1>
        </div>
        <el-menu
          mode="horizontal"
          :default-active="activeMenu"
          class="header-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="home">首页</el-menu-item>
          <el-menu-item index="courses">课程中心</el-menu-item>
          <el-menu-item index="my">我的学习</el-menu-item>
        </el-menu>
        <div class="header-right">
          <el-button type="primary" @click="$router.push('/login')">登录</el-button>
        </div>
      </div>
    </el-header>
    <el-main class="main-content">
      <div class="banner">
        <h2>欢迎来到 LyEdu 企业培训平台</h2>
        <p>专业的在线学习解决方案，助力企业人才培养</p>
        <el-button type="primary" size="large" @click="$router.push('/courses')">
          开始学习
        </el-button>
      </div>
      <div class="features">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="feature-card">
              <template #header>
                <div class="card-header">
                  <el-icon :size="40"><VideoCamera /></el-icon>
                  <span>在线视频学习</span>
                </div>
              </template>
              <p>支持高清视频播放，随时随地学习</p>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="feature-card">
              <template #header>
                <div class="card-header">
                  <el-icon :size="40"><Document /></el-icon>
                  <span>学习进度追踪</span>
                </div>
              </template>
              <p>实时记录学习进度，掌握学习情况</p>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="feature-card">
              <template #header>
                <div class="card-header">
                  <el-icon :size="40"><DataAnalysis /></el-icon>
                  <span>数据统计分析</span>
                </div>
              </template>
              <p>多维度数据分析，科学评估学习效果</p>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-main>
    <el-footer class="footer">
      <p>© 2026 LyEdu. All rights reserved.</p>
    </el-footer>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { VideoCamera, Document, DataAnalysis } from '@element-plus/icons-vue'

const activeMenu = ref('home')

const handleMenuSelect = (index: string) => {
  if (index === 'courses') {
    window.location.href = '/courses'
  }
}
</script>

<style scoped lang="scss">
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;

  .header-content {
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;

    .logo {
      h1 {
        color: #667eea;
        font-size: 24px;
        margin: 0;
      }
    }

    .header-menu {
      flex: 1;
      justify-content: center;
      border: none;
    }

    .header-right {
      margin-left: 20px;
    }
  }
}

.main-content {
  flex: 1;
  padding: 0;

  .banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-align: center;
    padding: 80px 20px;

    h2 {
      font-size: 42px;
      margin-bottom: 20px;
    }

    p {
      font-size: 18px;
      margin-bottom: 30px;
      opacity: 0.9;
    }
  }

  .features {
    max-width: 1200px;
    margin: 60px auto;
    padding: 0 20px;

    .feature-card {
      text-align: center;
      height: 100%;

      .card-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        color: #667eea;
        font-size: 18px;
        font-weight: bold;
      }

      p {
        color: #606266;
        margin-top: 10px;
      }
    }
  }
}

.footer {
  background: #303133;
  color: #fff;
  text-align: center;
  line-height: 60px;
}
</style>
