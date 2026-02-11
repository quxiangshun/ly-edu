<template>
  <div class="pptist-container">
    <AppHeader />
    <div class="pptist-frame-wrap">
      <iframe
        :src="iframeSrc"
        class="pptist-iframe"
        title="PPT 制作"
        frameborder="0"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import AppHeader from '@/components/AppHeader.vue'

// 优先使用环境变量，否则用相对路径（需将 PPTist 构建产物放到 public/pptist/）
const iframeSrc = computed(() => {
  const env = import.meta.env.VITE_PPTIST_URL
  if (env && typeof env === 'string' && env.trim()) return env.trim()
  return '/pptist/'
})
</script>

<style scoped lang="scss">
.pptist-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.pptist-frame-wrap {
  flex: 1;
  min-height: 0;
  position: relative;
}

.pptist-iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: block;
}
</style>
