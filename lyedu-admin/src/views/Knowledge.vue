<template>
  <div class="knowledge-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="card-header-left">
            <span>知识库管理</span>
            <el-tooltip content="查看本模块使用说明" placement="right">
              <el-icon class="card-help-icon" @click="openPageHelp('knowledge')">
                <QuestionFilled />
              </el-icon>
            </el-tooltip>
          </div>
          <el-button type="primary" @click="handleAdd">新增知识</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="标题/分类" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="searchForm.category" placeholder="分类筛选" clearable style="width: 140px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="knowledgeList" v-loading="loading" border :max-height="tableMaxHeight">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="160" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">{{ row.category || '-' }}</template>
        </el-table-column>
        <el-table-column prop="fileUrl" label="文件地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="visibility" label="可见性" width="90">
          <template #default="{ row }">
            <el-tag :type="row.visibility === 1 ? 'success' : 'warning'">
              {{ row.visibility === 1 ? '公开' : '私有' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sort" label="排序" width="80" />
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
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="560px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="知识标题/名称" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-input v-model="form.category" placeholder="如：制度文档、技术文档（可选）" />
        </el-form-item>
        <el-form-item label="文件地址" prop="fileUrl">
          <el-input v-model="form.fileUrl" placeholder="文件 URL 或上传后地址" />
        </el-form-item>
        <el-form-item label="文件名" prop="fileName">
          <el-input v-model="form.fileName" placeholder="下载时显示名称（可选）" />
        </el-form-item>
        <el-form-item label="文件大小" prop="fileSize">
          <el-input-number v-model="form.fileSize" :min="0" placeholder="字节（可选）" style="width: 100%" />
        </el-form-item>
        <el-form-item label="文件类型" prop="fileType">
          <el-input v-model="form.fileType" placeholder="如 pdf、doc（可选）" />
        </el-form-item>
        <el-form-item label="可见性" prop="visibility">
          <el-radio-group v-model="form.visibility">
            <el-radio :label="1">公开</el-radio>
            <el-radio :label="0">私有</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="form.visibility === 0" label="关联部门" prop="departmentIds">
          <el-tree-select
            v-model="form.departmentIds"
            :data="departmentTreeOptions"
            :props="{ label: 'name', value: 'id' }"
            placeholder="可多选关联部门"
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
import {
  getKnowledgePage,
  getKnowledgeByIdAdmin,
  createKnowledge,
  updateKnowledge,
  deleteKnowledge,
  type Knowledge
} from '@/api/knowledge'
import { getDepartmentTree, type Department } from '@/api/department'
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

const tableMaxHeight = useTableMaxHeight()
const loading = ref(false)
const departmentTree = ref<Department[]>([])
const departmentTreeOptions = computed(() => departmentTree.value || [])
const departmentNameMap = computed(() => {
  const flat = flattenDepartments(departmentTree.value || [])
  const map = new Map<number, string>()
  flat.forEach((d) => map.set(d.id, d.name))
  return map
})

const knowledgeList = ref<Knowledge[]>([])
const formRef = ref<FormInstance>()
const dialogVisible = ref(false)
const dialogTitle = ref('新增知识')
const isEdit = ref(false)
const editId = ref<number | null>(null)

const searchForm = reactive({
  keyword: '',
  category: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const { openPageHelp } = useHelp()

const form = reactive({
  title: '',
  category: '',
  fileUrl: '',
  fileName: '',
  fileSize: undefined as number | undefined,
  fileType: '',
  sort: 0,
  visibility: 1,
  departmentIds: [] as number[]
})

const rules: FormRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  fileUrl: [{ required: true, message: '请输入文件地址', trigger: 'blur' }]
}

async function loadList() {
  loading.value = true
  try {
    const res = await getKnowledgePage({
      page: pagination.page,
      size: pagination.size,
      keyword: searchForm.keyword || undefined,
      category: searchForm.category || undefined
    })
    knowledgeList.value = res?.records ?? []
    pagination.total = res?.total ?? 0
  } catch (_e) {
    knowledgeList.value = []
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  loadList()
}

function handleReset() {
  searchForm.keyword = ''
  searchForm.category = ''
  pagination.page = 1
  loadList()
}

function handleSizeChange() {
  loadList()
}

function handlePageChange() {
  loadList()
}

function handleAdd() {
  isEdit.value = false
  editId.value = null
  dialogTitle.value = '新增知识'
  form.title = ''
  form.category = ''
  form.fileUrl = ''
  form.fileName = ''
  form.fileSize = undefined
  form.fileType = ''
  form.sort = 0
  form.visibility = 1
  form.departmentIds = []
  dialogVisible.value = true
}

async function handleEdit(row: Knowledge) {
  isEdit.value = true
  editId.value = row.id
  dialogTitle.value = '编辑知识'
  try {
    const k = await getKnowledgeByIdAdmin(row.id)
    form.title = k.title ?? ''
    form.category = k.category ?? ''
    form.fileUrl = k.fileUrl ?? ''
    form.fileName = k.fileName ?? ''
    form.fileSize = k.fileSize
    form.fileType = k.fileType ?? ''
    form.sort = k.sort ?? 0
    form.visibility = k.visibility ?? 1
    form.departmentIds = Array.isArray(k.departmentIds) ? [...k.departmentIds] : []
  } catch (_e) {
    ElMessage.error('获取详情失败')
    return
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      const payload = {
        title: form.title.trim(),
        category: form.category.trim() || undefined,
        fileName: form.fileName.trim() || undefined,
        fileUrl: form.fileUrl.trim(),
        fileSize: form.fileSize,
        fileType: form.fileType.trim() || undefined,
        sort: form.sort,
        visibility: form.visibility,
        departmentIds: form.visibility === 0 ? form.departmentIds : undefined
      }
      if (isEdit.value && editId.value != null) {
        await updateKnowledge(editId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createKnowledge(payload)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      loadList()
    } catch (_e) {
      // 错误由 request 拦截器提示
    }
  })
}

function handleDelete(row: Knowledge) {
  ElMessageBox.confirm(`确定删除「${row.title}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteKnowledge(row.id)
      ElMessage.success('删除成功')
      loadList()
    } catch (_e) {
      // 错误由 request 拦截器提示
    }
  }).catch(() => {})
}

onMounted(() => {
  loadList()
  getDepartmentTree().then((data) => {
    departmentTree.value = data ?? []
  }).catch(() => {
    departmentTree.value = []
  })
})
</script>

<style scoped lang="scss">
.knowledge-container {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;

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
  .search-form {
    margin-bottom: 16px;
  }
}
</style>
