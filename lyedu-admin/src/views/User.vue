<template>
  <div class="user-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="card-header-left">
            <span>员工管理</span>
            <el-tooltip content="查看本模块使用说明" placement="right">
              <el-icon class="card-help-icon" @click="openPageHelp('user')">
                <QuestionFilled />
              </el-icon>
            </el-tooltip>
          </div>
          <div>
            <el-button @click="handleDownloadTemplate">下载员工导入模板</el-button>
            <el-button @click="importDialogVisible = true">导入员工</el-button>
            <el-button @click="syncDialogVisible = true">从第三方同步</el-button>
            <el-button type="primary" @click="handleAdd">新增员工</el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="用户名/姓名/邮箱/手机号" clearable />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="searchForm.role" placeholder="请选择" clearable>
            <el-option label="全部" value="" />
            <el-option label="管理员" value="admin" />
            <el-option label="教师" value="teacher" />
            <el-option label="学员" value="student" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="全部" value="" />
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="userList" v-loading="loading" border :max-height="tableMaxHeight">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="真实姓名" width="120">
          <template #default="{ row }">
            {{ row.real_name || row.username || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="mobile" label="手机号" width="120" />
        <el-table-column prop="departmentId" label="部门" width="160">
          <template #default="{ row }">
            {{ row.departmentId ? (departmentNameMap.get(row.departmentId) || row.departmentId) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : row.role === 'teacher' ? 'warning' : 'success'">
              {{ row.role === 'admin' ? '管理员' : row.role === 'teacher' ? '教师' : '学员' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="warning" link @click="handleResetPassword(row)">重置密码</el-button>
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

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" :disabled="isEdit" />
        </el-form-item>
        <el-form-item v-if="!isEdit" label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="留空则使用默认密码123456" show-password />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="mobile">
          <el-input v-model="form.mobile" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="头像URL" prop="avatar">
          <el-input v-model="form.avatar" placeholder="请输入头像URL" />
        </el-form-item>
        <el-form-item label="部门" prop="departmentId">
          <el-tree-select
            v-model="form.departmentId"
            :data="departmentTreeOptions"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="请选择所属部门"
            clearable
            default-expand-all
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="入职日期" prop="entryDate">
          <el-date-picker v-model="form.entryDate" type="date" value-format="YYYY-MM-DD" placeholder="新员工任务可见性" style="width: 100%" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色">
            <el-option label="管理员" value="admin" />
            <el-option label="教师" value="teacher" />
            <el-option label="学员" value="student" />
          </el-select>
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

    <!-- 导入员工对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入员工" width="520px" :close-on-click-modal="false">
      <p class="import-tip">请先<a href="javascript:;" @click="handleDownloadTemplate">下载员工导入模板</a>，按模板填写后上传 Excel 文件。</p>
      <el-upload
        ref="importUploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".xlsx"
        :on-change="onImportFileChange"
        :on-exceed="() => ElMessage.warning('仅支持单文件上传')"
      >
        <el-button type="primary">选择 Excel 文件</el-button>
      </el-upload>
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

    <!-- 从第三方同步对话框 -->
    <el-dialog v-model="syncDialogVisible" title="从第三方同步" width="480px">
      <p class="sync-tip">可将飞书、企业微信、钉钉等通讯录同步至本系统员工。请先在「系统设置」中配置对应平台的应用与权限。</p>
      <div class="sync-options">
        <el-card shadow="hover" class="sync-card" @click="handleSyncPlatform('feishu')">
          <div class="sync-card-body">
            <span class="sync-label">飞书</span>
            <el-tag size="small" type="info">即将支持</el-tag>
          </div>
        </el-card>
        <el-card shadow="hover" class="sync-card" @click="handleSyncPlatform('wecom')">
          <div class="sync-card-body">
            <span class="sync-label">企业微信</span>
            <el-tag size="small" type="info">即将支持</el-tag>
          </div>
        </el-card>
        <el-card shadow="hover" class="sync-card" @click="handleSyncPlatform('dingtalk')">
          <div class="sync-card-body">
            <span class="sync-label">钉钉</span>
            <el-tag size="small" type="info">即将支持</el-tag>
          </div>
        </el-card>
      </div>
      <template #footer>
        <el-button @click="syncDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="重置密码" width="400px">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
        <el-form-item label="新密码" prop="password">
          <el-input v-model="passwordForm.password" type="password" placeholder="请输入新密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePasswordSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import * as XLSX from 'xlsx'
import { QuestionFilled } from '@element-plus/icons-vue'
import {
  getUserPage,
  createUser,
  updateUser,
  deleteUser,
  resetUserPassword,
  importUsersByExcel,
  type User
} from '@/api/user'
import { getDepartmentTree, type Department } from '@/api/department'
import { useHelp } from '@/hooks/useHelp'
import { useTableMaxHeight } from '@/hooks/useTableHeight'

const tableMaxHeight = useTableMaxHeight()
const loading = ref(false)
const userList = ref<User[]>([])
const formRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()
const dialogVisible = ref(false)
const passwordDialogVisible = ref(false)
const importDialogVisible = ref(false)
const syncDialogVisible = ref(false)
const importUploadRef = ref()
const importResult = ref<{ successCount: number; failCount: number; messages?: string[] } | null>(null)
const dialogTitle = ref('新增员工')
const isEdit = ref(false)
const currentUserId = ref<number>()

const searchForm = reactive({
  keyword: '',
  role: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const { openPageHelp } = useHelp()

const departmentTree = ref<Department[]>([])
const departmentTreeOptions = computed(() => departmentTree.value || [])

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

const departmentNameMap = computed(() => {
  const flat = flattenDepartments(departmentTree.value || [])
  const map = new Map<number, string>()
  flat.forEach((d) => map.set(d.id, d.name))
  return map
})

const form = reactive<Partial<User>>({
  username: '',
  password: '',
  real_name: '',
  email: '',
  mobile: '',
  avatar: '',
  departmentId: undefined,
  role: 'student',
  status: 1
})

const passwordForm = reactive({
  password: ''
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const passwordRules: FormRules = {
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const loadData = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      size: pagination.size
    }
    if (searchForm.keyword) {
      params.keyword = searchForm.keyword
    }
    if (searchForm.role) {
      params.role = searchForm.role
    }
    if (searchForm.status !== '') {
      params.status = searchForm.status
    }
    const res = await getUserPage(params)
    userList.value = res.records
    pagination.total = res.total
  } catch (e) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const loadDepartments = async () => {
  try {
    const list = await getDepartmentTree()
    departmentTree.value = Array.isArray(list) ? list : []
  } catch (_e) {
    departmentTree.value = []
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.role = ''
  searchForm.status = ''
  pagination.page = 1
  loadData()
}

const handleSizeChange = () => {
  loadData()
}

const handlePageChange = () => {
  loadData()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增员工'
  Object.assign(form, {
    username: '',
    password: '',
    real_name: '',
    email: '',
    mobile: '',
    avatar: '',
    departmentId: undefined,
    role: 'student',
    status: 1
  })
  dialogVisible.value = true
}

const handleEdit = (row: User) => {
  isEdit.value = true
  dialogTitle.value = '编辑员工'
  Object.assign(form, {
    username: row.username,
    real_name: row.real_name,
    email: row.email,
    mobile: row.mobile,
    avatar: row.avatar,
    departmentId: row.departmentId,
    entryDate: row.entryDate ?? '',
    role: row.role,
    status: row.status
  })
  currentUserId.value = row.id
  dialogVisible.value = true
}

const handleDelete = async (row: User) => {
  try {
    await ElMessageBox.confirm('确定要删除该员工吗？', '提示', {
      type: 'warning'
    })
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    // 用户取消或删除失败
  }
}

const EMPLOYEE_IMPORT_HEADERS = ['用户名', '密码', '真实姓名', '邮箱', '手机号', '部门ID', '角色', '状态', '入职日期']
const EMPLOYEE_IMPORT_EXAMPLE = ['zhangsan', '123456', '张三', 'zhangsan@example.com', '13800138000', 1, 'student', 1, '2024-01-01']

const handleDownloadTemplate = () => {
  const ws = XLSX.utils.aoa_to_sheet([EMPLOYEE_IMPORT_HEADERS, EMPLOYEE_IMPORT_EXAMPLE])
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '员工导入')
  XLSX.writeFile(wb, '员工导入模板.xlsx')
}

const onImportFileChange = async (uploadFile: { raw?: File }) => {
  const file = uploadFile?.raw
  if (!file) return
  importResult.value = null
  try {
    const res = await importUsersByExcel(file)
    importResult.value = res
    if (res.successCount > 0) {
      ElMessage.success(`成功导入 ${res.successCount} 条员工`)
      loadData()
    }
    if (res.failCount > 0 && res.messages?.length) {
      ElMessage.warning(`部分失败：${res.messages.length} 条`)
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '导入失败')
  }
}

const closeImportDialog = () => {
  importDialogVisible.value = false
  importResult.value = null
  importUploadRef.value?.clearFiles?.()
  loadData()
}

const handleSyncPlatform = (platform: string) => {
  const names: Record<string, string> = { feishu: '飞书', wecom: '企业微信', dingtalk: '钉钉' }
  ElMessage.info(`${names[platform] || platform} 同步功能即将上线，请先在「系统设置」中配置应用`)
}

const handleResetPassword = (row: User) => {
  currentUserId.value = row.id
  passwordForm.password = ''
  passwordDialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  try {
    if (isEdit.value) {
      await updateUser(currentUserId.value!, form)
      ElMessage.success('更新成功')
    } else {
      await createUser(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || (isEdit.value ? '更新失败' : '创建失败'))
  }
}

const handlePasswordSubmit = async () => {
  if (!passwordFormRef.value) return
  await passwordFormRef.value.validate()
  try {
    await resetUserPassword(currentUserId.value!, passwordForm.password)
    ElMessage.success('密码重置成功')
    passwordDialogVisible.value = false
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '密码重置失败')
  }
}

onMounted(() => {
  loadData()
  loadDepartments()
})
</script>

<style scoped lang="scss">
.user-container {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

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
  margin-bottom: 20px;
}

.import-tip {
  margin-bottom: 16px;
  color: var(--el-text-color-regular);
  a { color: var(--el-color-primary); }
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
.sync-tip {
  margin-bottom: 16px;
  color: var(--el-text-color-regular);
  font-size: 13px;
}
.sync-options {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.sync-card {
  flex: 1;
  min-width: 120px;
  cursor: pointer;
  .sync-card-body {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .sync-label {
    font-weight: 500;
  }
}
</style>
