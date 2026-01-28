<template>
  <div class="my-container">
    <van-nav-bar title="我的" fixed placeholder />
    
    <div class="user-info">
      <van-cell-group inset>
        <van-cell>
          <template #title>
            <div class="user-avatar">
              <van-image
                round
                width="60"
                height="60"
                src="https://via.placeholder.com/60"
              />
              <div class="user-detail">
                <div class="username">学员</div>
                <div class="user-desc">点击登录</div>
              </div>
            </div>
          </template>
          <template #right-icon>
            <van-icon name="arrow" />
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <div class="menu-section">
      <van-cell-group inset>
        <van-cell title="我的课程" is-link icon="orders-o" to="/courses" />
        <van-cell title="学习记录" is-link icon="clock-o" />
        <van-cell title="学习统计" is-link icon="chart-trending-o" />
      </van-cell-group>
    </div>

    <div class="menu-section">
      <van-cell-group inset>
        <van-cell title="设置" is-link icon="setting-o" />
        <van-cell title="关于" is-link icon="info-o" />
      </van-cell-group>
    </div>
  </div>
</template>

<script setup lang="ts">
// 我的页面
</script>

<style scoped lang="scss">
.my-container {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 20px;
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
