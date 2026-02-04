<template>
  <div class="exam-take-page">
    <van-nav-bar
      :title="exam?.title || '考试'"
      left-arrow
      fixed
      placeholder
      @click-left="handleBack"
    />

    <div class="content">
      <template v-if="submitted">
        <van-result
          :icon="record?.passed === 1 ? 'success' : 'fail'"
          :title="record?.passed === 1 ? '考试通过' : '未通过'"
        >
          <template #default>
            <p class="result-score">得分：{{ record?.score ?? 0 }} 分</p>
          </template>
          <template #button>
            <van-button type="primary" block round @click="$router.push('/exam')">返回考试列表</van-button>
          </template>
        </van-result>
      </template>

      <template v-else>
        <van-loading v-if="loading" class="loading-wrap" vertical>加载题目...</van-loading>

        <template v-else-if="questions.length > 0">
          <div v-for="(item, index) in questions" :key="item.questionId" class="question-block">
            <div class="question-title">
              {{ index + 1 }}. {{ item.question?.title }}（{{ item.score }} 分）
            </div>
            <div class="question-answer">
              <template v-if="item.question?.type === 'single'">
                <van-radio-group v-model="answers[String(item.questionId)]">
                  <van-radio
                    v-for="(opt, i) in parseOptions(item.question?.options)"
                    :key="i"
                    :name="optLabel(i)"
                  >
                    {{ opt }}
                  </van-radio>
                </van-radio-group>
              </template>
              <template v-else-if="item.question?.type === 'multi'">
                <van-checkbox-group v-model="multiAnswers[String(item.questionId)]">
                  <van-checkbox
                    v-for="(opt, i) in parseOptions(item.question?.options)"
                    :key="i"
                    :name="optLabel(i)"
                    shape="square"
                  >
                    {{ opt }}
                  </van-checkbox>
                </van-checkbox-group>
              </template>
              <template v-else-if="item.question?.type === 'judge'">
                <van-radio-group v-model="answers[String(item.questionId)]">
                  <van-cell-group inset>
                    <van-cell clickable @click="answers[String(item.questionId)] = 'T'">
                      <template #title>
                        <van-radio name="T" shape="dot">正确</van-radio>
                      </template>
                    </van-cell>
                    <van-cell clickable @click="answers[String(item.questionId)] = 'F'">
                      <template #title>
                        <van-radio name="F" shape="dot">错误</van-radio>
                      </template>
                    </van-cell>
                  </van-cell-group>
                </van-radio-group>
              </template>
              <template v-else>
                <van-field
                  v-model="answers[String(item.questionId)]"
                  type="textarea"
                  :rows="item.question?.type === 'short' ? 4 : 1"
                  placeholder="请输入答案"
                  autosize
                />
              </template>
            </div>
          </div>

          <div class="submit-row">
            <van-button
              type="primary"
              block
              round
              size="large"
              :loading="submitting"
              @click="handleSubmit"
            >
              交卷
            </van-button>
          </div>
        </template>

        <van-empty v-else description="暂无题目" />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showConfirmDialog } from 'vant'
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

function handleBack() {
  if (submitted.value) {
    router.push('/exam')
    return
  }
  showConfirmDialog({
    title: '提示',
    message: '确定离开？未交卷将不保存答题。'
  })
    .then(() => router.push('/exam'))
    .catch(() => {})
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
      showToast('考试不存在')
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
    showToast('加载失败')
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
    showToast('交卷成功')
  } catch (_e) {
    // 具体错误信息由全局请求拦截器弹出，这里避免覆盖
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
.exam-take-page {
  min-height: 100vh;
  background: #f7f8fa;
}
.content {
  padding: 16px;
  padding-bottom: 32px;
}
.loading-wrap {
  padding: 40px 0;
}
.question-block {
  background: #fff;
  border-radius: 8px;
  padding: 14px 16px;
  margin-bottom: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.question-title {
  font-weight: 500;
  font-size: 15px;
  color: #323233;
  margin-bottom: 12px;
  line-height: 1.5;
}
.question-answer {
  padding-left: 0;
}
.question-answer :deep(.van-cell-group--inset) {
  margin: 0;
}
.question-answer :deep(.van-field) {
  padding: 0;
}
.result-score {
  font-size: 18px;
  color: #323233;
  margin: 12px 0;
}
.submit-row {
  margin-top: 24px;
  padding: 0 8px;
}
</style>
