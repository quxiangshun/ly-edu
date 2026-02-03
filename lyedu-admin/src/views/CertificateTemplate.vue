<template>
  <div class="certificate-template-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>证书模板管理</span>
          <el-button type="primary" @click="handleAdd">新增模板</el-button>
        </div>
      </template>

      <el-table :data="templateList" v-loading="loading" border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="模板名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="description" label="说明" min-width="200" show-overflow-tooltip />
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px">
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="form.name" placeholder="如：考试合格证模板" />
        </el-form-item>
        <el-form-item label="说明" prop="description">
          <el-input v-model="form.description" type="textarea" rows="2" placeholder="可选" />
        </el-form-item>
        <el-form-item label="配置(JSON)" prop="config">
          <el-input v-model="form.config" type="textarea" rows="4" placeholder='占位符、样式等 JSON，如 {"title":"证书标题"}' />
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  getTemplateList,
  getTemplateById,
  createTemplate,
  updateTemplate,
  deleteTemplate,
  type CertificateTemplate
} from '@/api/certificateTemplate'

const loading = ref(false)
const templateList = ref<CertificateTemplate[]>([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增模板')
const formRef = ref<FormInstance>()
const form = reactive<Partial<CertificateTemplate> & { name: string }>({
  name: '',
  description: '',
  config: '',
  sort: 0,
  status: 1
})
const formRules: FormRules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }]
}

const loadList = async () => {
  loading.value = true
  try {
    const res = await getTemplateList()
    templateList.value = (res as unknown as { data: CertificateTemplate[] }).data ?? res ?? []
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增模板'
  form.id = undefined
  form.name = ''
  form.description = ''
  form.config = ''
  form.sort = 0
  form.status = 1
  dialogVisible.value = true
}

const handleEdit = async (row: CertificateTemplate) => {
  dialogTitle.value = '编辑模板'
  try {
    const res = await getTemplateById(row.id)
    const t = (res as unknown as { data: CertificateTemplate }).data ?? res
    form.id = t.id
    form.name = t.name
    form.description = t.description ?? ''
    form.config = t.config ?? ''
    form.sort = t.sort ?? 0
    form.status = t.status ?? 1
    dialogVisible.value = true
  } catch (e) {
    ElMessage.error('获取模板失败')
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      if (form.id) {
        await updateTemplate(form.id, form)
        ElMessage.success('更新成功')
      } else {
        await createTemplate(form)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      loadList()
    } catch (e: unknown) {
      ElMessage.error((e as { message?: string })?.message ?? '操作失败')
    }
  })
}

const handleDelete = async (row: CertificateTemplate) => {
  await ElMessageBox.confirm('确定删除该模板吗？', '提示', {
    type: 'warning'
  })
  try {
    await deleteTemplate(row.id)
    ElMessage.success('删除成功')
    loadList()
  } catch (e: unknown) {
    ElMessage.error((e as { message?: string })?.message ?? '删除失败')
  }
}

onMounted(() => loadList())
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
