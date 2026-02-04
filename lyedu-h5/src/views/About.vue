<template>
  <div class="page">
    <van-nav-bar title="关于" left-arrow @click-left="$router.back()" fixed placeholder />
    <div class="content">
      <div class="logo-block">
        <van-image round width="80" height="80" src="/icon-192.png" class="logo" />
        <h1 class="app-name">LyEdu</h1>
        <p class="tagline">企业培训系统</p>
      </div>
      <van-cell-group inset class="info-group">
        <van-cell title="版本" value="1.0.0" />
        <van-cell title="开源协议" value="Apache 2.0" />
      </van-cell-group>
      <p class="desc">
        LyEdu 是 100% 开源的企业培训系统，支持部门/学员管理、在线视频学习、进度追踪、知识中心、考试、证书、积分与任务等，管理后台、PC 端、H5 多端一致体验。
      </p>
      <div class="footer">
        <p>以爱之名，为教育赋能</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 关于页面
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #f7f8fa;
}
.content {
  padding: 24px 16px;
}
.logo-block {
  text-align: center;
  padding: 32px 0 24px;
  .logo {
    display: block;
    margin: 0 auto 16px;
  }
  .app-name {
    font-size: 24px;
    font-weight: bold;
    color: #323233;
    margin: 0 0 8px;
  }
  .tagline {
    font-size: 14px;
    color: #969799;
    margin: 0;
  }
}
.info-group {
  margin-bottom: 20px;
}
.desc {
  font-size: 14px;
  color: #646566;
  line-height: 1.6;
  margin: 0 0 24px;
}
.footer {
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid #ebedf0;
  p {
    font-size: 13px;
    color: #969799;
    margin: 0;
  }
}
</style>
