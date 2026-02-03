<template>
  <div class="certificate-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>证书颁发规则</span>
          <el-button type="primary" @click="handleAdd">新增规则</el-button>
        </div>
      </template>

      <el-table :data="certList" v-loading="loading" border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="证书名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="templateId" label="模板ID" width="90" />
        <el-table-column prop="sourceType" label="来源类型" width="100">
          <template #default="{ row }">
            <el-tag>{{ row.sourceType === 'exam' ? '考试' : row.sourceType === 'task' ? '任务' : row.sourceType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sourceId" label="来源ID" width="90" />
        <el-table-column label="来源名称" width="160">
          <template #default="{ row }">
            {{ row.sourceType === 'exam' ? (examNameMap.get(row.sourceId) ?? row.sourceId) : row.sourceId }}
          </template>
        </el-table-column>
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column prop="status" label="状态" width="90">
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
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="560px">
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="证书名称" prop="name">
          <el-input v-model="form.name" placeholder="如：Java 考试合格证" />
        </el-form-item>
        <el-form-item label="证书模板" prop="templateId">
          <el-select v-model="form.templateId" placeholder="请选择模板" style="width: 100%" filterable>
            <el-option
              v-for="t in templateOptions"
              :key="t.id"
              :label="t.name"
              :value="t.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="来源类型" prop="sourceType">
          <el-select v-model="form.sourceType" placeholder="请选择" style="width: 100%" @change="onSourceTypeChange">
            <el-option label="考试" value="exam" />
            <el-option label="任务" value="task" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.sourceType === 'exam'" label="关联考试" prop="sourceId">
          <el-select v-model="form.sourceId" placeholder="请选择考试" style="width: 100%" filterable>
            <el-option
              v-for="e in examOptions"
              :key="e.id"
              :label="e.title"
              :value="e.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.sourceType === 'task'" label="来源ID(任务)" prop="sourceId">
          <el-input-number v-model="form.sourceId" :min="1" placeholder="任务ID（后续周期任务）" style="width: 100%" />
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
import {
  getCertificateList,
  getCertificateById,
  createCertificate,
  updateCertificate,
  deleteCertificate,
  type CertificateRule
} from '@/api/certificate'
import { getTemplateList, type CertificateTemplate } from '@/api/certificateTemplate'
import { getExamPage, type Exam } from '@/api/exam'

const loading = ref(false)
const certList = ref<CertificateRule[]>([])
const templateOptions = ref<CertificateTemplate[]>([])
const examOptions = ref<Exam[]>([])
const examNameMap = computed(() => {
  const m = new Map<number, string>()
  examOptions.value.forEach((e) => m.set(e.id, e.title))
  return m
})
const dialogVisible = ref(false)
const dialogTitle = ref('新增规则')
const formRef = ref<FormInstance>()
const form = reactive<Partial<CertificateRule> & { name: string; templateId?: number; sourceType: string; sourceId?: number }>({
  name: '',
  templateId: undefined,
  sourceType: 'exam',
  sourceId: undefined,
  sort: 0,
  status: 1
})
const formRules: FormRules = {
  name: [{ required: true, message: '请输入证书名称', trigger: 'blur' }],
  templateId: [{ required: true, message: '请选择证书模板', trigger: 'change' }],
  sourceType: [{ required: true, message: '请选择来源类型', trigger: 'change' }],
  sourceId: [{ required: true, message: '请选择/输入来源', trigger: 'change' }]
}

const loadList = async () => {
  loading.value = true
  try {
    const res = await getCertificateList()
    certList.value = (res as unknown as { data: CertificateRule[] }).data ?? res ?? []
  } finally {
    loading.value = false
  }
}

const loadTemplates = async () => {
  const res = await getTemplateList()
  templateOptions.value = (res as unknown as { data: CertificateTemplate[] }).data ?? res ?? []
}

const loadExams = async () => {
  const res = await getExamPage({ page: 1, size: 500 })
  const page = (res as unknown as { data: { records: Exam[] } }).data
  examOptions.value = page?.records ?? (res as unknown as { records: Exam[] })?.records ?? []
}

const onSourceTypeChange = () => {
  form.sourceId = undefined
}

const handleAdd = () => {
  dialogTitle.value = '新增规则'
  form.id = undefined
  form.name = ''
  form.templateId = undefined
  form.sourceType = 'exam'
  form.sourceId = undefined
  form.sort = 0
  form.status = 1
  dialogVisible.value = true
}

const handleEdit = async (row: CertificateRule) => {
  dialogTitle.value = '编辑规则'
  try {
    const res = await getCertificateById(row.id)
    const c = (res as unknown as { data: CertificateRule }).data ?? res
    form.id = c.id
    form.name = c.name
    form.templateId = c.templateId
    form.sourceType = c.sourceType
    form.sourceId = c.sourceId
    form.sort = c.sort ?? 0
    form.status = c.status ?? 1
    dialogVisible.value = true
  } catch (e) {
    ElMessage.error('获取规则失败')
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      if (form.id) {
        await updateCertificate(form.id, form)
        ElMessage.success('更新成功')
      } else {
        await createCertificate({
          name: form.name!,
          templateId: form.templateId!,
          sourceType: form.sourceType,
          sourceId: form.sourceId!,
          sort: form.sort,
          status: form.status
        })
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      loadList()
    } catch (e: unknown) {
      ElMessage.error((e as { message?: string })?.message ?? '操作失败')
    }
  })
}

const handleDelete = async (row: CertificateRule) => {
  await ElMessageBox.confirm('确定删除该规则吗？', '提示', { type: 'warning' })
  try {
    await deleteCertificate(row.id)
    ElMessage.success('删除成功')
    loadList()
  } catch (e: unknown) {
    ElMessage.error((e as { message?: string })?.message ?? '删除失败')
  }
}

onMounted(async () => {
  await Promise.all([loadList(), loadTemplates(), loadExams()])
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
