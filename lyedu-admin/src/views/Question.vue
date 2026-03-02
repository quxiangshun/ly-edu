<template>
  <div class="question-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="card-header-left">
            <span>试题管理</span>
            <el-tooltip content="查看本模块使用说明" placement="right">
              <el-icon class="card-help-icon" @click="openPageHelp('question')">
                <QuestionFilled />
              </el-icon>
            </el-tooltip>
          </div>
          <div class="card-header-actions">
            <el-dropdown trigger="click" @command="handleDownloadTemplateByType">
              <el-button>下载上传模板<el-icon class="el-icon--right"><arrow-down /></el-icon></el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="xlsx">Excel 模板 (.xlsx)</el-dropdown-item>
                  <el-dropdown-item command="csv">CSV 模板 (.csv)</el-dropdown-item>
                  <el-dropdown-item command="json">JSON 模板 (.json)</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button @click="openImportDialog">上传试题</el-button>
            <el-button type="primary" @click="handleAdd">新增试题</el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="题干" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="题型">
          <el-select v-model="searchForm.type" placeholder="全部" clearable style="width: 120px">
            <el-option label="单选" value="single" />
            <el-option label="多选" value="multi" />
            <el-option label="判断" value="judge" />
            <el-option label="填空" value="fill" />
            <el-option label="简答" value="short" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadList">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="questionList" v-loading="loading" border stripe :max-height="tableMaxHeight">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="type" label="题型" width="90">
          <template #default="{ row }">{{ typeLabel(row.type) }}</template>
        </el-table-column>
        <el-table-column prop="title" label="题干" min-width="280" show-overflow-tooltip />
        <el-table-column prop="score" label="分值" width="80" />
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadList"
        @current-change="loadList"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="640px" :close-on-click-modal="false">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="90px">
        <el-form-item label="题型" prop="type">
          <el-select v-model="form.type" placeholder="请选择题型" style="width: 100%">
            <el-option label="单选" value="single" />
            <el-option label="多选" value="multi" />
            <el-option label="判断" value="judge" />
            <el-option label="填空" value="fill" />
            <el-option label="简答" value="short" />
          </el-select>
        </el-form-item>
        <el-form-item label="题干" prop="title">
          <el-input v-model="form.title" type="textarea" :rows="3" placeholder="题目标题/题干" />
        </el-form-item>
        <el-form-item v-if="['single','multi','judge'].includes(form.type)" label="选项(JSON)" prop="options">
          <el-input v-model="form.options" type="textarea" :rows="2" placeholder='如 ["A选项","B选项","C选项","D选项"] 或 判断 ["正确","错误"]' @blur="runOptionsValidation" />
          <div v-if="optionsValidationErrors.length > 0" class="options-validation-errors">
            <div class="options-validation-title">选项格式问题：</div>
            <ul>
              <li v-for="(msg, idx) in optionsValidationErrors" :key="idx" class="options-validation-item">{{ msg }}</li>
            </ul>
            <el-button type="primary" size="small" @click="fixOptionsFormat">修复</el-button>
          </div>
          <div v-else-if="form.options.trim()" class="options-validation-actions">
            <el-button size="small" @click="runOptionsValidation">校验选项</el-button>
          </div>
        </el-form-item>
        <el-form-item label="参考答案" prop="answer">
          <el-input v-model="form.answer" placeholder="单选填A/B/C/D，多选填AB，判断填T/F，填空/简答填文本" />
        </el-form-item>
        <el-form-item label="分值" prop="score">
          <el-input-number v-model="form.score" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="解析" prop="analysis">
          <el-input v-model="form.analysis" type="textarea" :rows="2" placeholder="可选" />
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="form.sort" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 上传试题对话框 -->
    <el-dialog v-model="importDialogVisible" title="上传试题" width="1280px" :close-on-click-modal="false">
      <p class="import-tip">
        支持 Excel(.xlsx)、CSV、JSON 文件，或直接在下方粘贴 JSON 数组。请先
        <el-dropdown trigger="click" @command="handleDownloadTemplateByType">
          <a href="javascript:;">下载模板</a>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="xlsx">Excel 模板</el-dropdown-item>
              <el-dropdown-item command="csv">CSV 模板</el-dropdown-item>
              <el-dropdown-item command="json">JSON 模板</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        后按模板填写。
      </p>
      <el-tabs v-model="importTab" class="import-tabs">
        <el-tab-pane label="上传文件" name="file">
          <el-upload
            ref="importUploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".xlsx,.csv,.json"
            :on-change="onImportFileChange"
            :on-exceed="() => ElMessage.warning('仅支持单文件上传')"
          >
            <el-button type="primary">选择文件（.xlsx / .csv / .json）</el-button>
          </el-upload>
          <div v-if="importFileLoading" class="import-preview-loading">正在解析文件…</div>
          <div v-else-if="importPreviewError" class="import-preview-error">{{ importPreviewError }}</div>
          <template v-else-if="importPreviewRows.length > 0">
            <p class="import-preview-title">共解析到 {{ importPreviewRows.length }} 条，请确认后点击「提交」导入。</p>
            <div class="import-preview-table-wrap">
              <el-table :data="importPreviewRows" border stripe size="small" max-height="320">
                <el-table-column prop="0" label="题型" width="80" show-overflow-tooltip />
                <el-table-column prop="1" label="题干" min-width="180" show-overflow-tooltip />
                <el-table-column prop="2" label="选项(JSON)" min-width="220" show-overflow-tooltip />
                <el-table-column label="描述问题" min-width="280" class="option-issue-column">
                  <template #default="scope">
                    <div class="option-issue-cell">
                      <template v-if="importPreviewOptionFixedDetails[scope.$index]">
                        <div v-for="(line, k) in (importPreviewOptionFixedDetails[scope.$index] || '').split('；').filter(Boolean)" :key="'f-' + k" class="option-issue-line option-fixed-detail">· {{ line }}</div>
                      </template>
                      <template v-else-if="importPreviewOptionIssues[scope.$index]">
                        <div v-for="(line, k) in (importPreviewOptionIssues[scope.$index] || '').split('；').filter(Boolean)" :key="'e-' + k" class="option-issue-line option-issue-desc">· {{ line }}</div>
                      </template>
                      <span v-else class="option-issue-ok">—</span>
                      <el-button v-if="importPreviewOptionIssues[scope.$index]" type="primary" size="small" class="fix-btn" @click="fixPreviewRowOption(scope.$index)">修复</el-button>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="3" label="参考答案" width="90" show-overflow-tooltip />
                <el-table-column prop="4" label="分值" width="64" />
                <el-table-column prop="6" label="排序" width="64" />
              </el-table>
            </div>
            <div class="import-preview-actions">
              <el-button type="primary" :loading="importSubmitLoading" @click="handleSubmitImportFile">提交</el-button>
              <el-button :disabled="!hasAnyOptionIssue" @click="fixAllPreviewRowOptions">一键修复</el-button>
            </div>
          </template>
        </el-tab-pane>
        <el-tab-pane label="粘贴 JSON" name="json">
          <el-input
            v-model="importJsonText"
            type="textarea"
            :rows="18"
            placeholder="下方已预填五种题型模板，可直接编辑或追加后点击导入"
            class="import-json-textarea"
          />
          <div class="import-json-actions">
            <el-button type="primary" :loading="importJsonLoading" @click="handleImportJson">导入 JSON 数据</el-button>
            <el-button @click="importJsonText = getDefaultJsonTemplate()">恢复默认模板</el-button>
          </div>
          <div v-if="importJsonErrors.length" class="import-json-error-panel">
            <p class="import-json-error-title">
              检测到 <strong>{{ importJsonErrors.length }}</strong> 个 JSON 格式问题，请根据下表中的高亮位置修正括号或引号。
            </p>
            <el-table :data="importJsonErrors" border stripe size="small" max-height="220" class="import-json-error-table">
              <el-table-column prop="line" label="行号" width="80" />
              <el-table-column prop="column" label="列号" width="80" />
              <el-table-column prop="message" label="错误信息" min-width="220" show-overflow-tooltip />
              <el-table-column label="附近内容" min-width="260">
                <template #default="{ row }">
                  <span class="json-error-snippet" v-html="row.snippet"></span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
      <div v-if="importResult" class="import-result">
        <p>导入完成：成功 <strong>{{ importResult.successCount }}</strong> 条，失败 <strong>{{ importResult.failCount }}</strong> 条。</p>
        <ul v-if="importResult.messages?.length" class="import-errors">
          <li v-for="(msg, idx) in importResult.messages" :key="idx">{{ msg }}</li>
        </ul>
      </div>
      <template #footer>
        <el-button @click="closeImportDialog">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import * as XLSX from 'xlsx'
import { ArrowDown, QuestionFilled } from '@element-plus/icons-vue'
import {
  getQuestionPage,
  getQuestionById,
  createQuestion,
  updateQuestion,
  deleteQuestion,
  importQuestionsByFile,
  importQuestionsByJson,
  type Question
} from '@/api/question'
import { useHelp } from '@/hooks/useHelp'
import { useTableMaxHeight } from '@/hooks/useTableHeight'

const tableMaxHeight = useTableMaxHeight()
const typeLabels: Record<string, string> = {
  single: '单选',
  multi: '多选',
  judge: '判断',
  fill: '填空',
  short: '简答'
}
function typeLabel(type: string) {
  return typeLabels[type] || type
}

const loading = ref(false)
const questionList = ref<Question[]>([])
const formRef = ref<FormInstance>()
const dialogVisible = ref(false)
const dialogTitle = ref('新增试题')
const editId = ref<number | null>(null)
const importDialogVisible = ref(false)
const importTab = ref<'file' | 'json'>('file')
const importUploadRef = ref()
const importJsonText = ref('')
const importJsonLoading = ref(false)
const importResult = ref<{ successCount: number; failCount: number; messages?: string[] } | null>(null)
const importSelectedFile = ref<File | null>(null)
const importPreviewRows = ref<string[][]>([])
/** 导入预览表每行「选项(JSON)」的校验问题描述，与 importPreviewRows 逐行对应 */
const importPreviewOptionIssues = ref<string[]>([])
/** 导入预览表每行修复后的修改说明（第几字符被修改等），修复后写入此列 */
const importPreviewOptionFixedDetails = ref<string[]>([])
/** 是否存在任意一行的选项格式问题（用于一键修复按钮可用状态） */
const hasAnyOptionIssue = computed(() => importPreviewOptionIssues.value.some((s) => (s ?? '').length > 0))
const importPreviewError = ref('')
const importFileLoading = ref(false)
const importSubmitLoading = ref(false)
const importJsonErrors = ref<{ line: number; column: number; index: number; message: string; snippet: string }[]>([])

const searchForm = reactive({ keyword: '', type: '' })
const pagination = reactive({ page: 1, size: 10, total: 0 })

const { openPageHelp } = useHelp()

const form = reactive({
  type: 'single',
  title: '',
  options: '',
  answer: '',
  score: 10,
  analysis: '',
  sort: 0
})

/** 单选/多选/判断题的选项(JSON) 校验结果，用于在表单中标注非法数据 */
const optionsValidationErrors = ref<string[]>([])

const rules: FormRules = {
  type: [{ required: true, message: '请选择题型', trigger: 'change' }],
  title: [{ required: true, message: '请输入题干', trigger: 'blur' }]
}

/** 校验选项(JSON) 格式，返回错误描述列表。单选/多选/判断的选项应为 JSON 数组。 */
function validateOptionsFormat(optionsStr: string): string[] {
  const s = optionsStr.trim()
  const errors: string[] = []
  if (!s) return errors

  // 括号：全角【】应为半角 []
  if (s.includes('\u3010') || s.includes('\u3011')) {
    errors.push('括号格式错误：使用了【或】，应为半角 [ 或 ]')
  }
  // 逗号：全角 ，应为半角 ,
  if (s.includes('\uFF0C')) {
    errors.push('逗号格式错误：使用了全角逗号 ，，应为半角逗号 ,')
  }
  // 引号：中文双引号 "" 或 直角「」应为半角 "
  if (s.includes('\u201C') || s.includes('\u201D') || s.includes('\u300C') || s.includes('\u300D')) {
    errors.push('引号格式错误：使用了中文/全角引号，应为半角双引号 "')
  }
  // 缺少结尾 ]
  if (s.length > 0 && s[s.length - 1] !== ']') {
    errors.push('缺少结尾的 ]')
  }
  // 缺少开头 [
  if (s.length > 0 && s[0] !== '[') {
    errors.push('缺少开头的 [')
  }

  // 若上述都无，再尝试解析
  if (errors.length === 0) {
    try {
      const parsed = JSON.parse(s)
      if (!Array.isArray(parsed)) errors.push('选项应为 JSON 数组，例如 ["A","B","C"]')
    } catch (_e) {
      errors.push('JSON 解析失败，请检查括号、逗号、引号是否成对且为半角符号')
    }
  }
  return errors
}

/** 修复选项字符串中的常见格式问题（全角→半角、补全括号） */
function doFixOptionsFormat(optionsStr: string): string {
  return doFixOptionsFormatWithDetail(optionsStr).fixed
}

/** 修复并返回修改说明，用于导入预览表「描述问题」列 */
function doFixOptionsFormatWithDetail(optionsStr: string): { fixed: string; details: string[] } {
  const details: string[] = []
  let s = optionsStr.trim()
  if (!s) return { fixed: s, details: [] }
  let out = ''
  for (let i = 0; i < s.length; i++) {
    const c = s[i]
    const pos = i + 1
    if (c === '\u3010') { out += '['; details.push(`第${pos}个字符【被修改成了[`) }
    else if (c === '\u3011') { out += ']'; details.push(`第${pos}个字符】被修改成了]`) }
    else if (c === '\uFF0C') { out += ','; details.push(`第${pos}个字符，被修改成了,`) }
    else if (c === '\u201C' || c === '\u201D') { out += '"'; details.push(`第${pos}个字符引号被修改成了"`) }
    else if (c === '\u300C' || c === '\u300D') { out += '"'; details.push(`第${pos}个字符「或」被修改成了"`) }
    else out += c
  }
  if (out.length > 0 && out[0] !== '[') { out = '[' + out; details.push('缺少[，已在开头新增[') }
  if (out.length > 0 && out[out.length - 1] !== ']') { out = out + ']'; details.push('缺少]，已在末尾新增]') }
  return { fixed: out, details }
}

function runOptionsValidation() {
  if (!['single', 'multi', 'judge'].includes(form.type)) return
  optionsValidationErrors.value = validateOptionsFormat(form.options)
}

function fixOptionsFormat() {
  form.options = doFixOptionsFormat(form.options)
  optionsValidationErrors.value = validateOptionsFormat(form.options)
  if (optionsValidationErrors.value.length === 0) ElMessage.success('已按规范修复选项格式')
}

async function loadList() {
  loading.value = true
  try {
    const res = await getQuestionPage({
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword || undefined,
      type: searchForm.type || undefined
    })
    questionList.value = res?.records ?? []
    pagination.total = res?.total ?? 0
  } catch (_e) {
    questionList.value = []
  } finally {
    loading.value = false
  }
}

function handleReset() {
  searchForm.keyword = ''
  searchForm.type = ''
  pagination.page = 1
  loadList()
}

function handleAdd() {
  editId.value = null
  dialogTitle.value = '新增试题'
  form.type = 'single'
  form.title = ''
  form.options = ''
  form.answer = ''
  form.score = 10
  form.analysis = ''
  form.sort = 0
  optionsValidationErrors.value = []
  dialogVisible.value = true
}

async function handleEdit(row: Question) {
  editId.value = row.id
  dialogTitle.value = '编辑试题'
  try {
    const q = await getQuestionById(row.id)
    form.type = q.type ?? 'single'
    form.title = q.title ?? ''
    form.options = q.options ?? ''
    form.answer = q.answer ?? ''
    form.score = q.score ?? 10
    form.analysis = q.analysis ?? ''
    form.sort = q.sort ?? 0
  } catch (_e) {
    ElMessage.error('获取详情失败')
    return
  }
  optionsValidationErrors.value = []
  dialogVisible.value = true
  nextTick(() => runOptionsValidation())
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      const payload = {
        type: form.type,
        title: form.title.trim(),
        options: form.options.trim() || undefined,
        answer: form.answer.trim() || undefined,
        score: form.score,
        analysis: form.analysis.trim() || undefined,
        sort: form.sort
      }
      if (editId.value != null) {
        await updateQuestion(editId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createQuestion(payload)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      loadList()
    } catch (_e) {}
  })
}

function handleDelete(row: Question) {
  ElMessageBox.confirm(`确定删除该试题吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteQuestion(row.id)
      ElMessage.success('删除成功')
      loadList()
    } catch (_e) {}
  }).catch(() => {})
}

// 试题导入模板表头（与后端解析一致），以下为各题型示例（以历史/种子题为参考）
const QUESTION_IMPORT_HEADERS = ['题型', '题干', '选项(JSON)', '参考答案', '分值', '解析', '排序']
const QUESTION_IMPORT_EXAMPLES = [
  ['单选', '以下哪项是 LyEdu 平台的主要功能？', '["A. 仅视频播放","B. 在线学习与考试","C. 仅文档管理","D. 仅聊天"]', 'B', 5, 'LyEdu 为企业培训平台，支持课程学习、考试、证书等完整学习流程。', 10],
  ['多选', '以下哪些属于 LyEdu 的典型功能？（多选）', '["A. 课程与章节","B. 试卷与考试","C. 证书与积分","D. 社交论坛"]', 'ABC', 10, '平台包含课程、考试、证书、积分等，暂无内置社交论坛。', 20],
  ['判断', '学员完成培训任务后可以自动获得证书。', '["正确","错误"]', 'T', 5, '任务可配置完成后颁发证书，由管理员在任务中设置。', 30],
  ['填空', 'LyEdu 中试题表名为 ly_____。（填一个单词）', '', 'question', 5, '试题表名为 ly_question。', 40],
  ['简答', '请简述 LyEdu 平台中「周期任务」的典型应用场景。', '', '用于新员工入职培训、定期安全考试、年度考核等需要按周期或一次性完成的学习与考核任务。', 10, '周期任务可配置闯关内容（课程/考试）、完成证书、指派部门等。', 50]
]

/** 粘贴 JSON 输入框的默认模板（含五种题型示例） */
function getDefaultJsonTemplate(): string {
  const keys = QUESTION_IMPORT_HEADERS
  const items = QUESTION_IMPORT_EXAMPLES.map((row) => {
    const obj: Record<string, string | number> = {}
    keys.forEach((k, i) => { obj[k] = row[i] != null ? row[i] : '' })
    return obj
  })
  return JSON.stringify(items, null, 2)
}

/** 根据表数据计算每列宽度（字符数），中文等宽字符按 2 计 */
function fitColWidths(rows: (string | number)[][]): { wch: number }[] {
  if (!rows.length) return []
  const colCount = Math.max(...rows.map((r) => r.length))
  const widths: number[] = new Array(colCount).fill(0)
  for (const row of rows) {
    for (let c = 0; c < row.length; c++) {
      const s = row[c] != null ? String(row[c]) : ''
      // 中文字符等宽按 2 计，其余按 1，取整后与当前最大比较
      const len = [...s].reduce((acc, ch) => acc + (ch.charCodeAt(0) > 255 ? 2 : 1), 0)
      widths[c] = Math.max(widths[c], Math.min(len + 1, 80))
    }
  }
  return widths.map((w) => ({ wch: Math.max(w, 6) }))
}

/** 将文本中的 HTML 特殊字符转义为安全文本 */
function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

/** 从 JSON.parse 的错误中解析出大致出错位置（行/列/索引） */
function analyzeJsonSyntaxError(
  text: string,
  error: unknown
): { line: number; column: number; index: number } | null {
  const msg = (error as { message?: string })?.message ?? String(error)
  const m = msg.match(/position\s+(\d+)/i)
  if (!m) return null
  const index = Number(m[1])
  if (!Number.isFinite(index) || index < 0 || index > text.length) return null
  let line = 1
  let column = 1
  for (let i = 0; i < index && i < text.length; i++) {
    const ch = text[i]
    if (ch === '\n') {
      line++
      column = 1
    } else {
      column++
    }
  }
  return { line, column, index }
}

/** 构造一段带高亮错误字符的 HTML 片段，便于在表格中展示 */
function buildJsonErrorSnippet(text: string, index: number, radius = 30): string {
  if (text.length === 0) return ''
  if (index < 0) index = 0
  if (index >= text.length) index = text.length - 1
  const start = Math.max(0, index - radius)
  const end = Math.min(text.length, index + radius)
  const snippet = text.slice(start, end)
  const innerIndex = index - start
  const before = escapeHtml(snippet.slice(0, innerIndex))
  const errorChar = escapeHtml(snippet[innerIndex] || '')
  const after = escapeHtml(snippet.slice(innerIndex + 1))
  const prefix = start > 0 ? '... ' : ''
  const suffix = end < text.length ? ' ...' : ''
  return `${prefix}${before}<span class="json-error-char">${errorChar || ' '}</span>${after}${suffix}`
}

/** CSV 单元格转义（含逗号、换行、双引号时用双引号包裹） */
function csvEscape(cell: string | number): string {
  const s = String(cell)
  if (/[",\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`
  return s
}

function handleDownloadTemplateByType(format: 'xlsx' | 'csv' | 'json') {
  if (format === 'xlsx') {
    const rows = [QUESTION_IMPORT_HEADERS, ...QUESTION_IMPORT_EXAMPLES]
    const ws = XLSX.utils.aoa_to_sheet(rows)
    ws['!cols'] = fitColWidths(rows)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '试题导入')
    XLSX.writeFile(wb, '试题上传模板.xlsx')
    return
  }
  if (format === 'csv') {
    const rows = [QUESTION_IMPORT_HEADERS, ...QUESTION_IMPORT_EXAMPLES]
    const line = (row: (string | number)[]) => row.map(csvEscape).join(',')
    const csvContent = '\uFEFF' + rows.map(line).join('\r\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '试题上传模板.csv'
    a.click()
    URL.revokeObjectURL(url)
    return
  }
  if (format === 'json') {
    const keys = QUESTION_IMPORT_HEADERS
    const items = QUESTION_IMPORT_EXAMPLES.map((row) => {
      const obj: Record<string, string | number> = {}
      keys.forEach((k, i) => { obj[k] = row[i] != null ? row[i] : '' })
      return obj
    })
    const jsonContent = JSON.stringify(items, null, 2)
    const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '试题上传模板.json'
    a.click()
    URL.revokeObjectURL(url)
  }
}

function openImportDialog() {
  importResult.value = null
  importJsonErrors.value = []
  importJsonText.value = getDefaultJsonTemplate()
  importPreviewRows.value = []
  importPreviewError.value = ''
  importSelectedFile.value = null
  importTab.value = 'file'
  importDialogVisible.value = true
  nextTick(() => {
    importUploadRef.value?.clearFiles?.()
  })
}

/** 解析 CSV 一行（简单处理双引号包裹的字段） */
function parseCsvLine(line: string): string[] {
  const out: string[] = []
  let i = 0
  while (i < line.length) {
    if (line[i] === '"') {
      let cell = ''
      i++
      while (i < line.length) {
        if (line[i] === '"') {
          i++
          if (line[i] === '"') { cell += '"'; i++; } else break
        } else { cell += line[i]; i++; }
      }
      out.push(cell)
    } else {
      let cell = ''
      while (i < line.length && line[i] !== ',') { cell += line[i]; i++ }
      out.push(cell.trim())
      if (line[i] === ',') i++
    }
  }
  return out
}

/** 前端解析文件用于预览，返回每行 7 列（题型、题干、选项、参考答案、分值、解析、排序） */
async function parseFileForPreview(file: File): Promise<{ rows: string[][] } | { error: string }> {
  const fn = file.name.toLowerCase()
  try {
    if (fn.endsWith('.xlsx')) {
      const buf = await file.arrayBuffer()
      const wb = XLSX.read(buf, { type: 'array' })
      const sheet = wb.Sheets[wb.SheetNames[0]]
      if (!sheet) return { error: '文件为空' }
      const data = XLSX.utils.sheet_to_json<string[]>(sheet, { header: 1 }) as string[][]
      if (!data.length) return { error: '文件为空' }
      const rows = data.slice(1).filter((row) => row && row.some((c) => c != null && String(c).trim() !== ''))
      const normalized = rows.map((row) => {
        const r = [...(row || [])]
        while (r.length < 7) r.push('')
        return r.slice(0, 7).map((c) => (c != null ? String(c).trim() : ''))
      })
      return { rows: normalized }
    }
    if (fn.endsWith('.csv')) {
      const text = await file.text()
      const lines = text.split(/\r?\n/).filter((l) => l.trim())
      if (lines.length < 2) return { error: '文件为空或仅有表头' }
      const rows = lines.slice(1).map((line) => {
        const arr = parseCsvLine(line).map((s) => (s != null ? String(s).trim() : ''))
        if (arr.length > 7) {
          const merged = [
            arr[0],
            arr[1],
            arr.slice(2, -4).join(','),
            arr[arr.length - 4],
            arr[arr.length - 3],
            arr[arr.length - 2],
            arr[arr.length - 1]
          ]
          return merged
        }
        while (arr.length < 7) arr.push('')
        return arr.slice(0, 7)
      }).filter((row) => row.some((c) => c !== ''))
      return { rows }
    }
    if (fn.endsWith('.json')) {
      const text = await file.text()
      const data = JSON.parse(text)
      if (!Array.isArray(data)) return { error: 'JSON 根节点须为数组' }
      const keys = ['题型', '题干', '选项(JSON)', '参考答案', '分值', '解析', '排序']
      const enKeys = ['type', 'title', 'options', 'answer', 'score', 'analysis', 'sort']
      const rows = data.map((item: Record<string, unknown>) => {
        const row: string[] = []
        keys.forEach((k, i) => {
          const v = item[k] ?? item[enKeys[i]]
          if (v == null) row.push('')
          else if (typeof v === 'object') row.push(JSON.stringify(v))
          else row.push(String(v).trim())
        })
        while (row.length < 7) row.push('')
        return row.slice(0, 7)
      })
      return { rows }
    }
    return { error: '不支持的文件格式' }
  } catch (e: any) {
    return { error: e?.message || '解析失败' }
  }
}

/** 对导入预览的一行取题型与选项，返回选项格式问题描述（单选/多选/判断才校验） */
function getOptionIssueForPreviewRow(row: string[]): string {
  const typeStr = (row[0] ?? '').trim()
  if (typeStr !== '单选' && typeStr !== '多选' && typeStr !== '判断') return ''
  const opts = (row[2] ?? '').trim()
  if (!opts) return ''
  const errs = validateOptionsFormat(opts)
  return errs.join('；')
}

async function onImportFileChange(uploadFile: { raw?: File }) {
  const file = uploadFile?.raw
  if (!file) return
  importResult.value = null
  importPreviewError.value = ''
  importPreviewRows.value = []
  importPreviewOptionIssues.value = []
  importPreviewOptionFixedDetails.value = []
  importSelectedFile.value = file
  importFileLoading.value = true
  try {
    const result = await parseFileForPreview(file)
    if ('error' in result) {
      importPreviewError.value = result.error
    } else {
      importPreviewRows.value = result.rows
      importPreviewOptionIssues.value = result.rows.map((row) => getOptionIssueForPreviewRow(row))
      importPreviewOptionFixedDetails.value = result.rows.map(() => '')
    }
  } finally {
    importFileLoading.value = false
  }
}

/** 导入预览表：修复第 index 行的选项(JSON)，并把修改说明写入「描述问题」列 */
function fixPreviewRowOption(index: number) {
  const rows = importPreviewRows.value
  if (index < 0 || index >= rows.length) return
  const row = rows[index]
  const opts = (row[2] ?? '').trim()
  const { fixed, details } = doFixOptionsFormatWithDetail(opts)
  const newRows = rows.map((r, i) => (i === index ? [...r.slice(0, 2), fixed, ...r.slice(3)] : r))
  importPreviewRows.value = newRows
  const issues = [...importPreviewOptionIssues.value]
  const fixedDetails = [...importPreviewOptionFixedDetails.value]
  issues[index] = ''
  fixedDetails[index] = details.length > 0 ? details.join('；') : '已修复'
  importPreviewOptionIssues.value = issues
  importPreviewOptionFixedDetails.value = fixedDetails
  if (details.length > 0) ElMessage.success(`第 ${index + 1} 行选项已修复`)
}

/** 一键修复：对所有存在选项问题的行执行修复 */
function fixAllPreviewRowOptions() {
  const issues = importPreviewOptionIssues.value
  const indices = issues.map((s, i) => (s && s.length > 0 ? i : -1)).filter((i) => i >= 0)
  if (indices.length === 0) {
    ElMessage.info('当前没有需要修复的选项')
    return
  }
  indices.forEach((i) => fixPreviewRowOption(i))
  ElMessage.success(`已修复 ${indices.length} 行选项`)
}

async function handleSubmitImportFile() {
  const file = importSelectedFile.value
  if (!file || importPreviewRows.value.length === 0) return
  if (hasAnyOptionIssue.value) {
    ElMessage.warning('存在问题，无法提交，请先修复')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定导入共 ${importPreviewRows.value.length} 条试题吗？`,
      '确认导入',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }
  importSubmitLoading.value = true
  importResult.value = null
  try {
    const res = await importQuestionsByFile(file)
    importResult.value = res
    if (res.successCount > 0) {
      ElMessage.success(`成功导入 ${res.successCount} 条试题`)
      loadList()
    }
    if (res.failCount > 0 && res.messages?.length) {
      ElMessage.warning(`部分失败：${res.messages.length} 条`)
    }
    importPreviewRows.value = []
    importSelectedFile.value = null
    importUploadRef.value?.clearFiles?.()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '导入失败')
  } finally {
    importSubmitLoading.value = false
  }
}

async function handleImportJson() {
  const raw = importJsonText.value.trim()
  if (!raw) {
    ElMessage.warning('请先粘贴或输入 JSON 数组')
    return
  }
  importResult.value = null
  importJsonErrors.value = []
  importJsonLoading.value = true
  try {
    let parsed: unknown
    try {
      parsed = JSON.parse(raw)
    } catch (e: any) {
      const detail = analyzeJsonSyntaxError(raw, e)
      if (detail) {
        const snippet = buildJsonErrorSnippet(raw, detail.index)
        importJsonErrors.value = [
          {
            line: detail.line,
            column: detail.column,
            index: detail.index,
            message: e?.message || 'JSON 格式错误',
            snippet
          }
        ]
      }
      ElMessage.error('JSON 格式错误，请根据下方提示修正括号、逗号与引号')
      return
    }
    const data = parsed as object[]
    if (!Array.isArray(data)) {
      ElMessage.error('JSON 须为数组格式')
      return
    }
    const res = await importQuestionsByJson(data)
    importResult.value = res
    if (res.successCount > 0) {
      ElMessage.success(`成功导入 ${res.successCount} 条试题`)
      loadList()
    }
    if (res.failCount > 0 && res.messages?.length) {
      ElMessage.warning(`部分失败：${res.messages.length} 条`)
    }
  } catch (e: any) {
    if (e?.message?.includes('JSON')) {
      ElMessage.error('JSON 格式错误，请检查括号、逗号与引号')
    } else {
      ElMessage.error(e?.response?.data?.message || '导入失败')
    }
  } finally {
    importJsonLoading.value = false
  }
}

function closeImportDialog() {
  importDialogVisible.value = false
  importTab.value = 'file'
  importJsonText.value = ''
  importResult.value = null
  importPreviewRows.value = []
  importPreviewOptionIssues.value = []
  importPreviewOptionFixedDetails.value = []
  importPreviewError.value = ''
  importSelectedFile.value = null
  importUploadRef.value?.clearFiles?.()
  loadList()
}

onMounted(loadList)
</script>

<style scoped lang="scss">
.question-container {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.question-container .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .card-header-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .card-header-left {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .card-help-icon {
    font-size: 16px;
    cursor: pointer;
    color: #909399;

    &:hover {
      color: var(--el-color-primary);
    }
  }
}
.question-container .search-form {
  margin-bottom: 16px;
}

.options-validation-errors {
  margin-top: 8px;
  padding: 10px 12px;
  background: rgba(245, 108, 108, 0.06);
  border: 1px solid rgba(245, 108, 108, 0.3);
  border-radius: 4px;
  font-size: 13px;
  .options-validation-title {
    color: var(--el-color-danger);
    font-weight: 600;
    margin-bottom: 6px;
  }
  ul {
    margin: 0 0 8px;
    padding-left: 18px;
  }
  .options-validation-item {
    color: var(--el-text-color-regular);
    margin-bottom: 2px;
  }
}

.options-validation-actions {
  margin-top: 6px;
}

.import-tip {
  margin-bottom: 16px;
  color: var(--el-text-color-regular);
  a { color: var(--el-color-primary); }
}

.import-tabs {
  margin-bottom: 12px;
}

.import-preview-loading {
  margin-top: 12px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.import-preview-error {
  margin-top: 12px;
  color: var(--el-color-danger);
  font-size: 13px;
}

.import-preview-title {
  margin: 12px 0 8px;
  font-size: 13px;
  color: var(--el-text-color-regular);
}

.import-preview-actions {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.import-preview-table-wrap {
  max-height: 320px;
  overflow: auto;
}

.option-issue-cell {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 6px 10px;
  font-size: 12px;
  .option-issue-line {
    white-space: nowrap;
    flex: 0 1 auto;
    min-width: 0;
  }
  .option-issue-line.option-issue-desc {
    color: var(--el-color-danger);
  }
  .option-issue-line.option-fixed-detail {
    color: var(--el-color-success);
  }
  .option-issue-ok {
    color: var(--el-text-color-secondary);
  }
  .fix-btn {
    flex-shrink: 0;
  }
}

.import-json-textarea {
  font-family: ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, monospace;
  font-size: 13px;
}

.import-json-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}

.import-json-error-panel {
  margin-top: 12px;
  padding: 10px 12px;
  border-radius: 4px;
  border: 1px solid rgba(245, 108, 108, 0.35);
  background: rgba(245, 108, 108, 0.04);
}

.import-json-error-title {
  font-size: 13px;
  color: var(--el-color-danger);
  margin: 0 0 8px;
}

.import-json-error-table {
  font-size: 12px;
}

.json-error-snippet {
  font-family: ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, monospace;
  white-space: pre-wrap;
  word-break: break-all;
}

.json-error-char {
  font-weight: 700;
  color: var(--el-color-danger);
  background-color: rgba(245, 108, 108, 0.16);
  border-bottom: 1px dashed var(--el-color-danger);
}

.import-result {
  margin-top: 16px;
  padding: 12px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
  .import-errors {
    margin: 8px 0 0;
    padding-left: 20px;
    max-height: 160px;
    overflow-y: auto;
    font-size: 12px;
    color: var(--el-color-danger);
  }
}
</style>
