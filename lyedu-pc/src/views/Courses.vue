<template>
  <div class="courses-container">
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <h1>LyEdu</h1>
        </div>
        <el-menu
          mode="horizontal"
          default-active="courses"
          class="header-menu"
        >
          <el-menu-item index="home" @click="$router.push('/')">首页</el-menu-item>
          <el-menu-item index="courses">课程中心</el-menu-item>
          <el-menu-item index="my">我的学习</el-menu-item>
        </el-menu>
      </div>
    </el-header>
    <el-main class="main-content">
      <div class="courses-content">
        <h2>课程中心</h2>
        <el-row :gutter="20">
          <el-col :span="6" v-for="i in 8" :key="i">
            <el-card class="course-card" shadow="hover">
              <img
                src="https://via.placeholder.com/300x200"
                class="course-image"
                alt="课程封面"
              />
              <div class="course-info">
                <h3>示例课程 {{ i }}</h3>
                <p>这是课程描述信息</p>
                <el-button type="primary" size="small">开始学习</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-main>
  </div>
</template>

<script setup lang="ts">
// 课程列表页面
</script>

<style scoped lang="scss">
.courses-container {
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
    padding: 0 20px;

    .logo {
      cursor: pointer;
      h1 {
        color: #667eea;
        font-size: 24px;
        margin: 0;
      }
    }

    .header-menu {
      flex: 1;
      margin-left: 40px;
      border: none;
    }
  }
}

.main-content {
  flex: 1;
  background: #f5f7fa;
  padding: 40px 20px;

  .courses-content {
    max-width: 1200px;
    margin: 0 auto;

    h2 {
      margin-bottom: 30px;
      color: #303133;
    }

    .course-card {
      margin-bottom: 20px;
      cursor: pointer;
      transition: transform 0.3s;

      &:hover {
        transform: translateY(-5px);
      }

      .course-image {
        width: 100%;
        height: 150px;
        object-fit: cover;
        margin-bottom: 15px;
      }

      .course-info {
        h3 {
          font-size: 16px;
          margin-bottom: 10px;
          color: #303133;
        }

        p {
          font-size: 14px;
          color: #909399;
          margin-bottom: 15px;
        }
      }
    }
  }
}
</style>
