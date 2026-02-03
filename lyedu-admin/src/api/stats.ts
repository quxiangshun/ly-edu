import axios from 'axios'
import request from '@/utils/request'

export interface Overview {
  userCount: number
  courseCount: number
  departmentCount: number
  videoCount: number
}

export interface ResourceStats {
  courseCount: number
  videoCount: number
  chapterCount: number
  attachmentCount: number
}

export const getOverview = () => {
  return request.get<Overview>('/stats/overview')
}

export const getLearningRank = (limit: number = 20) => {
  return request.get<Record<string, unknown>[]>('/stats/learning-rank', { params: { limit } })
}

export const getResourceStats = () => {
  return request.get<ResourceStats>('/stats/resource')
}

function getBaseUrl(): string {
  return (import.meta as any).env?.VITE_API_BASE ?? '/api'
}

/** 下载 CSV（带 token，blob 方式） */
function downloadCsv(path: string, filename: string): void {
  const token = localStorage.getItem('token')
  const base = getBaseUrl()
  const url = base.replace(/\/$/, '') + path
  axios.get(url, { responseType: 'blob', headers: token ? { Authorization: `Bearer ${token}` } : {} }).then((res) => {
    const blob = res.data
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = filename
    a.click()
    URL.revokeObjectURL(a.href)
  }).catch(() => {})
}

export const downloadLearnersCsv = () => downloadCsv('/stats/export/learners.csv', '学员信息.csv')
export const downloadLearningCsv = () => downloadCsv('/stats/export/learning.csv', '学习记录.csv')
export const downloadDepartmentLearningCsv = () => downloadCsv('/stats/export/department-learning.csv', '部门学习统计.csv')
