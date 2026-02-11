<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted, watch, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getConfigByKey } from '@/api/config'
import { applyThemeFromConfig, applyDefaultTheme } from '@/utils/theme'

const router = useRouter()
const globalBrandingLoaded = ref(false)

async function loadGlobalBranding() {
  if (globalBrandingLoaded.value) return
  try {
    const title = await getConfigByKey('site.title')
    if (title) {
      document.title = title
    }
  } catch (_e) {}

  try {
    const mode = (await getConfigByKey('site.theme_mode')) ?? 'auto'
    const color = (await getConfigByKey('site.theme_color')) ?? ''
    const logo = await getConfigByKey('site.logo')
    let logoUrl = ''
    if (logo) {
      logoUrl = logo.startsWith('http') ? logo : (logo.startsWith('/') ? window.location.origin + logo : logo)
    }
    await applyThemeFromConfig(String(mode), String(color), logoUrl)
    globalBrandingLoaded.value = true
  } catch (_e) {
    applyDefaultTheme()
  }
}

onMounted(() => {
  if (router.currentRoute.value.path !== '/login') {
    loadGlobalBranding()
  }
})

watch(
  () => router.currentRoute.value.path,
  (path) => {
    if (path && path !== '/login') {
      loadGlobalBranding()
    }
  }
)
</script>

<style scoped>
</style>
