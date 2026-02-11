<template>
  <div class="help-container">
    <AppHeader />
    <el-main class="main-content">
      <div class="help-content">
        <h2>使用说明</h2>
        <p class="help-intro">本页为学员端简要使用说明，帮助您快速上手企业培训平台。</p>

        <el-card class="help-card" shadow="hover">
          <template #header>
            <span class="help-card-title">首页与课程</span>
          </template>
          <p>登录后可从<strong>首页</strong>进入<strong>课程中心</strong>，浏览并加入课程。在课程详情页可查看章节、视频列表，点击视频即可进入播放页学习。</p>
        </el-card>

        <el-card class="help-card" shadow="hover">
          <template #header>
            <span class="help-card-title">学习与进度</span>
          </template>
          <p>视频播放过程中会自动记录学习进度，您可在<strong>我的学习</strong>中查看已学课程与进度。部分课程可能限制拖拽或倍速，请以实际播放器为准。</p>
        </el-card>

        <el-card class="help-card" shadow="hover">
          <template #header>
            <span class="help-card-title">知识中心与文档</span>
          </template>
          <p><strong>知识中心</strong>提供文档、资料等学习资源，点击即可预览。支持常见文档格式在线查看。</p>
        </el-card>

        <el-card class="help-card" shadow="hover">
          <template #header>
            <span class="help-card-title">考试与证书</span>
          </template>
          <p>在<strong>考试中心</strong>可参加考试，提交后查看成绩。完成相应要求后，可在<strong>我的证书</strong>中查看或打印证书。</p>
        </el-card>

        <el-card class="help-card" shadow="hover">
          <template #header>
            <span class="help-card-title">任务与积分</span>
          </template>
          <p><strong>我的任务</strong>展示需完成的任务列表；<strong>积分</strong>页可查看当前积分与排行榜。</p>
        </el-card>

        <el-card class="help-card" shadow="hover">
          <template #header>
            <span class="help-card-title">个人中心</span>
          </template>
          <p>点击右上角用户名可进入<strong>个人中心</strong>，查看或修改昵称、头像、邮箱、手机等资料。</p>
        </el-card>

        <p class="help-footer">如有疑问，请联系管理员或查看管理员后台提供的更多说明。</p>
      </div>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
</script>

<style scoped lang="scss">
.help-container {
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

.help-content {
  max-width: 720px;
  margin: 0 auto;

  h2 {
    margin-bottom: 12px;
    color: #303133;
  }

  .help-intro {
    margin-bottom: 24px;
    color: #606266;
    font-size: 14px;
  }

  .help-card {
    margin-bottom: 16px;

    .help-card-title {
      font-weight: 600;
      color: #303133;
    }

    p {
      margin: 0;
      color: #606266;
      line-height: 1.6;
      font-size: 14px;
    }
  }

  .help-footer {
    margin-top: 24px;
    padding-top: 16px;
    border-top: 1px solid #ebeef5;
    color: #909399;
    font-size: 13px;
  }
}
</style>
