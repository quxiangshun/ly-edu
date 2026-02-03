<template>
  <div class="exam-take-container">
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <img src="/icon-192.png" alt="" class="header-logo-icon" />
          <h1>LyEdu</h1>
        </div>
        <span class="exam-title">{{ exam?.title || '考试' }}</span>
        <el-button type="primary" link @click="$router.push('/exam')">返回考试列表</el-button>
      </div>
    </el-header>
    <el-main class="main-content">
      <template v-if="submitted">
        <el-result
          :icon="record?.passed === 1 ? 'success' : 'warning'"
          :title="record?.passed === 1 ? '考试通过' : '未通过'"
        >
          <template #sub-title>
            <p>得分：{{ record?.score ?? 0 }} 分</p>
          </template>
          <template #extra>
            <el-button type="primary" @click="$router.push('/exam')">返回考试列表</el-button>
          </template>
        </el-result>
      </template>
      <template v-else>
        <div v-loading="loading" class="questions-area">
          <template v-if="questions.length > 0">
            <div v-for="(item, index) in questions" :key="item.questionId" class="question-block">
              <div class="question-title">
                {{ index + 1 }}. {{ item.question?.title }}（{{ item.score }} 分）
              </div>
              <div class="question-answer">
                <template v-if="item.question?.type === 'single'">
                  <el-radio-group v-model="answers[String(item.questionId)]">
                    <el-radio
                      v-for="(opt, i) in parseOptions(item.question?.options)"
                      :key="i"
                      :label="optLabel(i)"
                    >
                      {{ opt }}
                    </el-radio>
                  </el-radio-group>
                </template>
                <template v-else-if="item.question?.type === 'multi'">
                  <el-checkbox-group v-model="multiAnswers[String(item.questionId)]">
                    <el-checkbox
                      v-for="(opt, i) in parseOptions(item.question?.options)"
                      :key="i"
                      :label="optLabel(i)"
                    >
                      {{ opt }}
                    </el-checkbox-group>
                  </el-checkbox-group>
                </template>
                <template v-else-if="item.question?.type === 'judge'">
                  <el-radio-group v-model="answers[String(item.questionId)]">
                    <el-radio label="T">正确</el-radio>
                    <el-radio label="F">错误</el-radio>
                  </el-radio-group>
                </template>
                <template v-else>
                  <el-input
                    v-model="answers[String(item.questionId)]"
                    type="textarea"
                    :rows="item.question?.type === 'short' ? 4 : 1"
                    placeholder="请输入答案"
                  />
                </template>
              </div>
            </div>
            <div class="submit-row">
              <el-button type="primary" size="large" :loading="submitting" @click="handleSubmit">
                交卷
              </el-button>
            </div>
          </template>
          <el-empty v-else-if="!loading" description="暂无题目" />
        </div>
      </template>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  getExamById,
  getPaperQuestions,
  submitExam,
  type Exam,
  type PaperQuestionDto,
  type ExamRecord
} from '@/api/exam'

const route = useRoute()
const router = useRouter()
const examId = ref(Number(route.params.id))
const loading = ref(true)
const submitting = ref(false)
const submitted = ref(false)
const exam = ref<Exam | null>(null)
const questions = ref<PaperQuestionDto[]>([])
const answers = reactive<Record<string, string>>({})
const multiAnswers = reactive<Record<string, string[]>>({})
const record = ref<ExamRecord | null>(null)

function parseOptions(options?: string): string[] {
  if (!options) return []
  try {
    const arr = JSON.parse(options)
    return Array.isArray(arr) ? arr : []
  } catch {
    return []
  }
}

function optLabel(i: number): string {
  return String.fromCharCode(65 + i)
}

function buildAnswersJson(): string {
  const out: Record<string, string> = { ...answers }
  Object.keys(multiAnswers).forEach((qid) => {
    const arr = multiAnswers[qid]
    out[qid] = Array.isArray(arr) ? arr.sort().join('') : ''
  })
  return JSON.stringify(out)
}

async function loadExam() {
  if (!examId.value) {
    router.push('/exam')
    return
  }
  loading.value = true
  try {
    exam.value = await getExamById(examId.value)
    if (!exam.value) {
      ElMessage.error('考试不存在')
      router.push('/exam')
      return
    }
    const list = await getPaperQuestions(exam.value.paperId)
    questions.value = list ?? []
    questions.value.forEach((item) => {
      if (item.question?.type === 'multi') {
        multiAnswers[String(item.questionId)] = []
      }
    })
  } catch (_e) {
    ElMessage.error('加载失败')
    router.push('/exam')
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  submitting.value = true
  try {
    const json = buildAnswersJson()
    const res = await submitExam(examId.value, json)
    record.value = res
    submitted.value = true
    ElMessage.success('交卷成功')
  } catch (_e) {
    ElMessage.error('交卷失败')
  } finally {
    submitting.value = false
  }
}

watch(
  () => route.params.id,
  (id) => {
    examId.value = Number(id)
    if (examId.value) loadExam()
  },
  { immediate: false }
)

onMounted(() => loadExam())
</script>

<style scoped lang="scss">
.exam-take-container {
  min-height: 100vh;
  .header {
    background: #fff;
    border-bottom: 1px solid #e4e7ed;
    padding: 0 24px;
  }
  .header-content {
    max-width: 900px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .logo {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    .header-logo-icon {
      width: 32px;
      height: 32px;
    }
    h1 {
      margin: 0;
      font-size: 20px;
      color: #409eff;
    }
  }
  .exam-title {
    flex: 1;
    font-size: 16px;
    color: #303133;
  }
  .main-content {
    max-width: 900px;
    margin: 0 auto;
    padding: 24px 16px;
  }
  .questions-area {
    min-height: 400px;
  }
  .question-block {
    margin-bottom: 24px;
    padding: 16px;
    border: 1px solid #ebeef5;
    border-radius: 8px;
  }
  .question-title {
    font-weight: 500;
    margin-bottom: 12px;
    color: #303133;
  }
  .question-answer {
    padding-left: 8px;
  }
  .submit-row {
    margin-top: 32px;
    text-align: center;
  }
}
</style>
