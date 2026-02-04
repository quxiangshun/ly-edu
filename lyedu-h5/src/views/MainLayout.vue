<template>
  <div class="main-layout">
    <main class="main-content">
      <router-view />
    </main>
    <van-tabbar v-model="active" fixed placeholder route>
      <van-tabbar-item icon="home-o" to="/">首页</van-tabbar-item>
      <van-tabbar-item icon="apps-o" to="/courses">课程</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/my">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const active = ref(0)

function updateActive() {
  const path = route.path
  if (path === '/') active.value = 0
  else if (path === '/courses') active.value = 1
  else if (path === '/my') active.value = 2
  else active.value = 0
}

watch(() => route.path, updateActive, { immediate: true })
</script>

<style scoped lang="scss">
.main-layout {
  min-height: 100vh;
}
.main-content {
  padding-bottom: 50px;
  min-height: 100vh;
}
</style>
