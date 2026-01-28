<template>
  <div class="courses-container">
    <van-nav-bar title="课程中心" left-arrow @click-left="$router.back()" fixed placeholder />
    
    <van-tabs v-model:active="activeTab" sticky>
      <van-tab title="全部" name="all">
        <div class="courses-list">
          <van-card
            v-for="i in 10"
            :key="i"
            :title="`示例课程 ${i}`"
            :desc="'这是课程描述信息，包含课程的主要内容介绍'"
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
      </van-tab>
      <van-tab title="进行中" name="ongoing">
        <van-empty description="暂无进行中的课程" />
      </van-tab>
      <van-tab title="已完成" name="completed">
        <van-empty description="暂无已完成的课程" />
      </van-tab>
    </van-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeTab = ref('all')

const handleCourseClick = (id: number) => {
  // TODO: 跳转到课程详情页
  console.log('点击课程:', id)
}
</script>

<style scoped lang="scss">
.courses-container {
  min-height: 100vh;
  background: #f7f8fa;
}

.courses-list {
  padding: 10px;
}
</style>
