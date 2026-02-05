<template>
  <div class="task-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="card-header-left">
            <span>周期任务</span>
            <el-tooltip content="查看本模块使用说明" placement="right">
              <el-icon class="card-help-icon" @click="openPageHelp('task')">
                <QuestionFilled />
              </el-icon>
            </el-tooltip>
          </div>
          <el-button type="primary" @click="handleAdd">新增任务</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="任务名称" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadList">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="taskList" v-loading="loading" border :max-height="tableMaxHeight">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="任务名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="cycleType" label="周期" width="90">
          <template #default="{ row }">
            {{ row.cycleType === 'once' ? '一次性' : row.cycleType === 'daily' ? '每日' : row.cycleType === 'weekly' ? '每周' : row.cycleType === 'monthly' ? '每月' : row.cycleType === 'newcomer' ? '新员工' : row.cycleType }}
          </template>
        </el-table-column>
        <el-table-column label="闯关项" width="100">
          <template #default="{ row }">
            {{ itemsCount(row.items) }} 项
          </template>
        </el-table-column>
        <el-table-column prop="certificateId" label="证书" width="90">
          <template #default="{ row }">{{ row.certificateId ? certificateNameMap.get(row.certificateId) ?? row.certificateId : '-' }}</template>
        </el-table-column>
        <el-table-column prop="departmentIds" label="指派部门" width="160">
          <template #default="{ row }">
            {{ row.departmentIds?.length ? (row.departmentIds as number[]).map(d => departmentNameMap.get(d) ?? d).join('、') : '全员' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
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
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadList"
        @current-change="loadList"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="640px">
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="任务名称" prop="title">
          <el-input v-model="form.title" placeholder="任务名称" />
        </el-form-item>
        <el-form-item label="说明" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="可选" />
        </el-form-item>
        <el-form-item label="周期" prop="cycleType">
          <el-select v-model="form.cycleType" placeholder="请选择" style="width: 100%">
            <el-option label="一次性" value="once" />
            <el-option label="每日" value="daily" />
            <el-option label="每周" value="weekly" />
            <el-option label="每月" value="monthly" />
            <el-option label="新员工（按入职时间）" value="newcomer" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.cycleType === 'newcomer'" label="入职多少天内可见" prop="withinDays">
          <el-input-number v-model="form.withinDays" :min="1" :max="365" placeholder="如 30 表示入职30天内可见" style="width: 100%" />
          <div class="form-tip">仅入职日期（或创建时间）在此天数内的用户可见此任务</div>
        </el-form-item>
        <el-form-item label="闯关项(JSON)" prop="items">
          <el-input v-model="form.items" type="textarea" :rows="4" placeholder='[{"type":"course","id":1},{"type":"exam","id":2}] 按顺序完成' />
          <div class="form-tip">type: course|exam，id: 课程ID或考试ID，按顺序闯关</div>
        </el-form-item>
        <el-form-item label="完成证书" prop="certificateId">
          <el-select v-model="form.certificateId" placeholder="可选，完成后颁发" clearable style="width: 100%" filterable>
            <el-option
              v-for="c in certificateOptions"
              :key="c.id"
              :label="c.name"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="指派部门" prop="departmentIds">
          <el-tree-select
            v-model="form.departmentIds"
            :data="departmentTreeOptions"
            :props="{ label: 'name', value: 'id' }"
            placeholder="不选则全员可见"
            clearable
            check-strictly
            default-expand-all
            multiple
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="form.sort" :min="0" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="开始时间" prop="startTime">
          <el-date-picker v-model="form.startTime" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="可选" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束时间" prop="endTime">
          <el-date-picker v-model="form.endTime" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="可选" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import { getTaskPage, getTaskByIdAdmin, createTask, updateTask, deleteTask, type Task } from '@/api/task'
import { getDepartmentTree, type Department } from '@/api/department'
import { getCertificateList, type CertificateRule } from '@/api/certificate'
import { useHelp } from '@/hooks/useHelp'
import { useTableMaxHeight } from '@/hooks/useTableHeight'

function flattenDepartments(list: Department[]): Department[] {
  const out: Department[] = []
  function walk(items: Department[]) {
    for (const d of items) {
      out.push(d)
      if (d.children?.length) walk(d.children)
    }
  }
  walk(list)
  return out
}

function itemsCount(itemsStr: string): number {
  if (!itemsStr || !itemsStr.trim()) return 0
  try {
    const arr = JSON.parse(itemsStr)
    return Array.isArray(arr) ? arr.length : 0
  } catch {
    return 0
  }
}

const loading = ref(false)
const departmentTree = ref<Department[]>([])
const departmentTreeOptions = computed(() => departmentTree.value || [])
const departmentNameMap = computed(() => {
  const flat = flattenDepartments(departmentTree.value || [])
  const map = new Map<number, string>()
  flat.forEach((d) => map.set(d.id, d.name))
  return map
})
const certificateOptions = ref<CertificateRule[]>([])
const certificateNameMap = computed(() => {
  const map = new Map<number, string>()
  certificateOptions.value.forEach((c) => map.set(c.id, c.name))
  return map
})

const taskList = ref<Task[]>([])
const formRef = ref<FormInstance>()
const dialogVisible = ref(false)
const dialogTitle = ref('新增任务')
const editId = ref<number | null>(null)

const searchForm = reactive({ keyword: '' })
const pagination = reactive({ page: 1, size: 10, total: 0 })

const tableMaxHeight = useTableMaxHeight()
const { openPageHelp } = useHelp()

const form = reactive({
  title: '',
  description: '',
  cycleType: 'once',
  withinDays: 30,
  items: '[]',
  certificateId: undefined as number | undefined,
  sort: 0,
  status: 1,
  departmentIds: [] as number[],
  startTime: '',
  endTime: ''
})

const formRules: FormRules = {
  title: [{ required: true, message: '请输入任务名称', trigger: 'blur' }]
}

async function loadList() {
  loading.value = true
  try {
    const res = await getTaskPage({
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword || undefined
    })
    taskList.value = res?.records ?? []
    pagination.total = res?.total ?? 0
  } catch (_e) {
    taskList.value = []
  } finally {
    loading.value = false
  }
}

function handleReset() {
  searchForm.keyword = ''
  pagination.page = 1
  loadList()
}

async function handleAdd() {
  editId.value = null
  dialogTitle.value = '新增任务'
  form.title = ''
  form.description = ''
  form.cycleType = 'once'
  form.items = '[]'
  form.certificateId = undefined
  form.sort = 0
  form.status = 1
  form.departmentIds = []
  form.startTime = ''
  form.endTime = ''
  dialogVisible.value = true
}

async function handleEdit(row: Task) {
  editId.value = row.id
  dialogTitle.value = '编辑任务'
  try {
    const t = await getTaskByIdAdmin(row.id)
    form.title = t.title ?? ''
    form.description = t.description ?? ''
    form.cycleType = t.cycleType ?? 'once'
    try {
      const cc = t.cycleConfig ? JSON.parse(t.cycleConfig) : {}
      form.withinDays = cc.within_days ?? 30
    } catch {
      form.withinDays = 30
    }
    form.items = t.items ?? '[]'
    form.certificateId = t.certificateId
    form.sort = t.sort ?? 0
    form.status = t.status ?? 1
    form.departmentIds = t.departmentIds ?? []
    form.startTime = t.startTime ?? ''
    form.endTime = t.endTime ?? ''
    dialogVisible.value = true
  } catch (_e) {
    ElMessage.error('加载失败')
  }
}

async function handleSubmit() {
  await formRef.value?.validate().catch(() => {})
  try {
    if (editId.value != null) {
      await updateTask(editId.value, {
        title: form.title,
        description: form.description || undefined,
        cycleType: form.cycleType,
        items: form.items,
        certificateId: form.certificateId,
        sort: form.sort,
        status: form.status,
        departmentIds: form.departmentIds,
        startTime: form.startTime || undefined,
        endTime: form.endTime || undefined
      })
      ElMessage.success('更新成功')
    } else {
      await createTask({
        title: form.title,
        description: form.description || undefined,
        cycleType: form.cycleType,
        cycleConfig: cycleConfig,
        items: form.items,
        certificateId: form.certificateId,
        sort: form.sort,
        status: form.status,
        departmentIds: form.departmentIds,
        startTime: form.startTime || undefined,
        endTime: form.endTime || undefined
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadList()
  } catch (_e) {
    ElMessage.error('操作失败')
  }
}

async function handleDelete(row: Task) {
  await ElMessageBox.confirm(`确定删除任务「${row.title}」？`, '提示', {
    type: 'warning'
  }).catch(() => {})
  try {
    await deleteTask(row.id)
    ElMessage.success('删除成功')
    loadList()
  } catch (_e) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadList()
  getDepartmentTree().then((res) => (departmentTree.value = res ?? []))
  getCertificateList().then((res) => (certificateOptions.value = res ?? []))
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

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
.task-container {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.search-form {
  margin-bottom: 16px;
}
.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
</style>
