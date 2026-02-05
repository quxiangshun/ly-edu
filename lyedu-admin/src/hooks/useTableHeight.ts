import { computed, onMounted, onUnmounted, ref } from 'vue'

/** 主内容区表格最大高度，仅表格内容滚动、不触发整页滚动 */
export function useTableMaxHeight(offset = 280) {
  const viewportHeight = ref(typeof window !== 'undefined' ? window.innerHeight : 600)

  const update = () => {
    viewportHeight.value = window.innerHeight
  }

  onMounted(() => {
    update()
    window.addEventListener('resize', update)
  })
  onUnmounted(() => {
    window.removeEventListener('resize', update)
  })

  return computed(() => Math.max(400, viewportHeight.value - offset))
}
