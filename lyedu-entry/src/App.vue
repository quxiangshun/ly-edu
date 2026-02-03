<template>
  <div class="entry-page">
    <img src="/icon-192.png" alt="LyEdu" class="logo" />
    <h1>LyEdu</h1>
    <p class="subtitle">企业培训平台 · 请选择访问端</p>
    <div class="entry-links">
      <a :href="pcUrl" class="entry-link">
        PC 端
        <span class="desc">电脑浏览器学习</span>
      </a>
      <a :href="h5Url" class="entry-link secondary">
        H5 端
        <span class="desc">手机浏览器 / 飞书内打开</span>
      </a>
      <a :href="adminUrl" class="entry-link danger">
        管理后台
        <span class="desc">课程、用户、部门管理</span>
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'

// 从环境变量读取各端地址（构建时注入），便于同域/跨域部署
const pcUrl = computed(() => (import.meta.env.VITE_PC_URL as string) || '/pc/')
const h5Url = computed(() => (import.meta.env.VITE_H5_URL as string) || '/h5/')
const adminUrl = computed(() => (import.meta.env.VITE_ADMIN_URL as string) || '/admin/')
const autoRedirect = (import.meta.env.VITE_AUTO_REDIRECT as string) === 'true'

function isMobile(): boolean {
  const ua = navigator.userAgent.toLowerCase()
  return /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(ua)
}

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  const t = params.get('t')
  if (t === 'pc') {
    window.location.href = pcUrl.value
    return
  }
  if (t === 'h5') {
    window.location.href = h5Url.value
    return
  }
  if (t === 'admin') {
    window.location.href = adminUrl.value
    return
  }
  if (autoRedirect) {
    window.location.href = isMobile() ? h5Url.value : pcUrl.value
  }
})
</script>
