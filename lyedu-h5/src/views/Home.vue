<template>
  <div class="home-container">
    <van-nav-bar title="LyEdu" fixed placeholder />
    
    <div class="banner">
      <h2>欢迎来到 LyEdu</h2>
      <p>随时随地，轻松学习</p>
    </div>

    <div class="features">
      <van-grid :column-num="3" :border="false">
        <van-grid-item icon="video-o" text="视频学习" />
        <van-grid-item icon="orders-o" text="我的课程" />
        <van-grid-item icon="chart-trending-o" text="学习统计" />
      </van-grid>
    </div>

    <div class="courses-section">
      <div class="section-header">
        <h3>推荐课程</h3>
        <span @click="$router.push('/courses')">更多 ></span>
      </div>
      <van-card
        v-for="i in 3"
        :key="i"
        :title="`示例课程 ${i}`"
        :desc="'这是课程描述信息'"
        thumb="https://via.placeholder.com/200x120"
        @click="handleCourseClick(i)"
      >
        <template #tags>
          <van-tag type="primary">热门</van-tag>
        </template>
        <template #footer>
          <van-button size="mini" type="primary">开始学习</van-button>
        </template>
      </van-card>
    </div>

    <van-tabbar v-model="active" fixed placeholder>
      <van-tabbar-item icon="home-o" to="/">首页</van-tabbar-item>
      <van-tabbar-item icon="apps-o" to="/courses">课程</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/my">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const active = ref(0)

const handleCourseClick = (id: number) => {
  // TODO: 跳转到课程详情页
  console.log('点击课程:', id)
}
</script>

<style scoped lang="scss">
.home-container {
  padding-bottom: 50px;
}

.banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  padding: 40px 20px;
  margin-bottom: 20px;

  h2 {
    font-size: 28px;
    margin-bottom: 10px;
  }

  p {
    font-size: 14px;
    opacity: 0.9;
  }
}

.features {
  background: white;
  margin-bottom: 20px;
  padding: 20px 0;
}

.courses-section {
  background: white;
  padding: 20px;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;

    h3 {
      font-size: 18px;
      color: #323233;
    }

    span {
      font-size: 14px;
      color: #969799;
    }
  }
}
</style>
