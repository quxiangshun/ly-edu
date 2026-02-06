import { useRouter, useRoute } from 'vue-router'

const routeToSectionMap: Record<string, string> = {
  '/dashboard': 'dashboard',
  '/department': 'department',
  '/user': 'user',
  '/tag': 'tag',
  '/course': 'course',
  '/course-comment': 'course-comment',
  '/video': 'video',
  '/image': 'image',
  '/knowledge': 'knowledge',
  '/question': 'question',
  '/paper': 'paper',
  '/exam': 'exam',
  '/task': 'task',
  '/certificate-template': 'certificate-template',
  '/certificate': 'certificate',
  '/point-rule': 'point-rule',
  '/settings': 'settings'
}

export function useHelp() {
  const router = useRouter()
  const route = useRoute()

  /** 打开系统使用说明首页 */
  const openSystemHelp = () => {
    router.push({ path: '/help' })
  }

  /**
   * 打开当前页面对应的帮助说明
   * @param sectionKey 可指定模块 key，不传则根据当前路由自动匹配
   */
  const openPageHelp = (sectionKey?: string) => {
    const section =
      sectionKey ||
      routeToSectionMap[route.path] ||
      (route.meta && typeof route.meta.title === 'string' ? '' : '')

    if (section) {
      router.push({ path: '/help', query: { section } })
    } else {
      router.push({ path: '/help' })
    }
  }

  return {
    openSystemHelp,
    openPageHelp
  }
}

