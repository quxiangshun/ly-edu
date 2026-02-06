<template>
  <div class="tag-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="card-header-left">
            <span>标签管理</span>
            <el-tooltip content="查看本模块使用说明" placement="right">
              <el-icon class="card-help-icon" @click="openPageHelp('tag')">
                <QuestionFilled />
              </el-icon>
            </el-tooltip>
            <span class="card-desc">标签可关联人员、机构、课程，在员工/部门/课程中可选择标签并在列表中展示</span>
          </div>
          <el-button type="primary" @click="handleAdd">新增标签</el-button>
        </div>
      </template>

      <el-table :data="tagList" v-loading="loading" border :max-height="tableMaxHeight">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="标签名称" min-width="160" />
        <el-table-column prop="sort" label="排序" width="100" />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link @click="handleEntities(row)">关联人员/机构/课程</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="440px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入标签名称" maxlength="50" show-word-limit />
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

    <!-- 关联人员/机构/课程对话框（风格与公司架构一致：多选+添加+表格+移除） -->
    <el-dialog v-model="entitiesDialogVisible" :title="`关联人员/机构/课程 - ${currentTag?.name || ''}`" width="640px">
      <el-tabs v-model="entitiesTab">
        <el-tab-pane label="人员" name="user">
          <div style="margin-bottom: 12px">
            <el-select
              v-model="userSelectIds"
              multiple
              filterable
              placeholder="选择人员后点击添加"
              style="width: 100%"
              value-key="id"
            >
              <el-option
                v-for="u in allUsers"
                :key="u.id"
                :label="(u.real_name || u.username) + (u.username ? ` (${u.username})` : '')"
                :value="u.id"
                :disabled="linkedUserIdsSet.has(u.id)"
              />
            </el-select>
            <el-button type="primary" size="small" style="margin-left: 8px; margin-top: 8px" @click="addSelectedUsers">添加</el-button>
          </div>
          <el-table :data="linkedUsers" border size="small" max-height="280">
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="displayName" label="姓名" />
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button type="danger" link size="small" @click="removeUser(row)">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="部门" name="department">
          <div style="margin-bottom: 12px">
            <el-select
              v-model="departmentSelectIds"
              multiple
              filterable
              placeholder="选择部门后点击添加"
              style="width: 100%"
              value-key="id"
            >
              <el-option
                v-for="d in departmentFlatOptions"
                :key="d.id"
                :label="d.name"
                :value="d.id"
                :disabled="linkedDepartmentIdsSet.has(d.id)"
              />
            </el-select>
            <el-button type="primary" size="small" style="margin-left: 8px; margin-top: 8px" @click="addSelectedDepartments">添加</el-button>
          </div>
          <el-table :data="linkedDepartments" border size="small" max-height="280">
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="name" label="部门名称" />
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button type="danger" link size="small" @click="removeDepartment(row)">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="课程" name="course">
          <div style="margin-bottom: 12px">
            <el-select
              v-model="courseSelectIds"
              multiple
              filterable
              placeholder="选择课程后点击添加"
              style="width: 100%"
              value-key="id"
            >
              <el-option
                v-for="c in allCourses"
                :key="c.id"
                :label="c.title"
                :value="c.id"
                :disabled="linkedCourseIdsSet.has(c.id)"
              />
            </el-select>
            <el-button type="primary" size="small" style="margin-left: 8px; margin-top: 8px" @click="addSelectedCourses">添加</el-button>
          </div>
          <el-table :data="linkedCourses" border size="small" max-height="280">
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="title" label="课程名称" />
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button type="danger" link size="small" @click="removeCourse(row)">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="entitiesDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import {
  getTagList,
  getTagById,
  createTag,
  updateTag,
  deleteTag,
  getTagUsers,
  getTagDepartments,
  getTagCourses,
  setTagEntities,
  type Tag
} from '@/api/tag'
import { getUserPage } from '@/api/user'
import { getDepartmentTree } from '@/api/department'
import { getCoursePage } from '@/api/course'
import { useHelp } from '@/hooks/useHelp'
import { useTableMaxHeight } from '@/hooks/useTableHeight'

const loading = ref(false)
const tagList = ref<Tag[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const form = reactive({ name: '', sort: 0 })
const rules: FormRules = {
  name: [{ required: true, message: '请输入标签名称', trigger: 'blur' }]
}

const entitiesDialogVisible = ref(false)
const entitiesTab = ref('user')
const currentTag = ref<Tag | null>(null)
const userSelectIds = ref<number[]>([])
const departmentSelectIds = ref<number[]>([])
const courseSelectIds = ref<number[]>([])
const linkedUsers = ref<{ id: number; username: string; real_name?: string; displayName: string }[]>([])
const linkedDepartments = ref<{ id: number; name: string }[]>([])
const linkedCourses = ref<{ id: number; title: string }[]>([])
const linkedUserIdsSet = computed(() => new Set(linkedUsers.value.map((u) => u.id)))
const linkedDepartmentIdsSet = computed(() => new Set(linkedDepartments.value.map((d) => d.id)))
const linkedCourseIdsSet = computed(() => new Set(linkedCourses.value.map((c) => c.id)))
const allUsers = ref<{ id: number; username: string; real_name?: string }[]>([])
const departmentTreeOptions = ref<{ id: number; name: string; children?: { id: number; name: string; children?: unknown[] }[] }[]>([])
const departmentFlatOptions = computed(() => {
  const flat: { id: number; name: string }[] = []
  function walk(nodes: { id: number; name: string; children?: unknown[] }[]) {
    for (const n of nodes) {
      flat.push({ id: n.id, name: n.name })
      if (n.children?.length) walk(n.children as { id: number; name: string; children?: unknown[] }[])
    }
  }
  walk(departmentTreeOptions.value)
  return flat
})
const allCourses = ref<{ id: number; title: string }[]>([])

const tableMaxHeight = useTableMaxHeight()
const { openPageHelp } = useHelp()

const dialogTitle = computed(() => (isEdit.value ? '编辑标签' : '新增标签'))

async function loadList() {
  loading.value = true
  try {
    const res = await getTagList()
    tagList.value = (res as unknown as { data?: Tag[] })?.data ?? res ?? []
  } catch (_e) {
    ElMessage.error('加载标签列表失败')
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  isEdit.value = false
  form.name = ''
  form.sort = 0
  dialogVisible.value = true
}

function handleEdit(row: Tag) {
  isEdit.value = true
  form.name = row.name
  form.sort = row.sort ?? 0
  currentTag.value = row
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value?.validate().catch(() => {})
  try {
    if (isEdit.value && currentTag.value) {
      await updateTag(currentTag.value.id, { name: form.name.trim(), sort: form.sort })
      ElMessage.success('保存成功')
    } else {
      await createTag({ name: form.name.trim(), sort: form.sort })
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadList()
  } catch (_e) {
    ElMessage.error(isEdit.value ? '保存失败' : '新增失败')
  }
}

async function handleDelete(row: Tag) {
  await ElMessageBox.confirm(`确定删除标签「${row.name}」吗？`, '提示', {
    type: 'warning'
  }).catch(() => {})
  try {
    await deleteTag(row.id)
    ElMessage.success('已删除')
    loadList()
  } catch (_e) {
    ElMessage.error('删除失败')
  }
}

function toUserRow(u: { id: number; username?: string; real_name?: string }) {
  return {
    ...u,
    username: u.username ?? '',
    displayName: (u.real_name || u.username || String(u.id)) as string
  }
}

async function handleEntities(row: Tag) {
  currentTag.value = row
  userSelectIds.value = []
  departmentSelectIds.value = []
  courseSelectIds.value = []
  try {
    const [usersRes, deptsRes, coursesRes, ur, dr, cr] = await Promise.all([
      getTagUsers(row.id),
      getTagDepartments(row.id),
      getTagCourses(row.id),
      getUserPage({ page: 1, size: 5000 }),
      getDepartmentTree(),
      getCoursePage({ page: 1, size: 5000 })
    ])
    const usersRaw = (usersRes as unknown as { data?: unknown[] })?.data ?? (Array.isArray(usersRes) ? usersRes : [])
    const deptsRaw = (deptsRes as unknown as { data?: unknown[] })?.data ?? (Array.isArray(deptsRes) ? deptsRes : [])
    const coursesRaw = (coursesRes as unknown as { data?: unknown[] })?.data ?? (Array.isArray(coursesRes) ? coursesRes : [])
    linkedUsers.value = (usersRaw as { id: number; username?: string; real_name?: string }[]).map(toUserRow)
    linkedDepartments.value = (deptsRaw as { id: number; name: string }[]).map((d) => ({ id: d.id, name: d.name }))
    linkedCourses.value = (coursesRaw as { id: number; title: string }[]).map((c) => ({ id: c.id, title: c.title }))
    const ud = (ur as unknown as { data?: { records?: unknown[] } })?.data?.records ?? (ur as { records?: unknown[] })?.records ?? []
    allUsers.value = ud as { id: number; username: string; real_name?: string }[]
    departmentTreeOptions.value = ((dr as unknown as { data?: unknown[] })?.data ?? dr ?? []) as {
      id: number
      name: string
      children?: { id: number; name: string; children?: unknown[] }[]
    }[]
    const cd = (cr as unknown as { data?: { records?: unknown[] } })?.data?.records ?? (cr as { records?: unknown[] })?.records ?? []
    allCourses.value = cd as { id: number; title: string }[]
    entitiesDialogVisible.value = true
  } catch (_e) {
    ElMessage.error('加载关联数据失败')
  }
}

async function addSelectedUsers() {
  if (!currentTag.value || userSelectIds.value.length === 0) return
  const toAdd = allUsers.value.filter((u) => userSelectIds.value.includes(u.id))
  const next = [...linkedUsers.value, ...toAdd.map(toUserRow)]
  const nextIds = next.map((u) => u.id)
  try {
    await setTagEntities(currentTag.value.id, { userIds: nextIds })
    ElMessage.success('添加成功')
    linkedUsers.value = next
    userSelectIds.value = []
  } catch (_e) {
    ElMessage.error('添加失败')
  }
}

function removeUser(row: { id: number }) {
  if (!currentTag.value) return
  const next = linkedUsers.value.filter((u) => u.id !== row.id)
  setTagEntities(currentTag.value.id, { userIds: next.map((u) => u.id) })
    .then(() => {
      ElMessage.success('已移除')
      linkedUsers.value = next
    })
    .catch(() => ElMessage.error('移除失败'))
}

async function addSelectedDepartments() {
  if (!currentTag.value || departmentSelectIds.value.length === 0) return
  const toAdd = departmentFlatOptions.value.filter((d) => departmentSelectIds.value.includes(d.id))
  const next = [...linkedDepartments.value, ...toAdd]
  const nextIds = next.map((d) => d.id)
  try {
    await setTagEntities(currentTag.value.id, { departmentIds: nextIds })
    ElMessage.success('添加成功')
    linkedDepartments.value = next
    departmentSelectIds.value = []
  } catch (_e) {
    ElMessage.error('添加失败')
  }
}

function removeDepartment(row: { id: number }) {
  if (!currentTag.value) return
  const next = linkedDepartments.value.filter((d) => d.id !== row.id)
  setTagEntities(currentTag.value.id, { departmentIds: next.map((d) => d.id) })
    .then(() => {
      ElMessage.success('已移除')
      linkedDepartments.value = next
    })
    .catch(() => ElMessage.error('移除失败'))
}

async function addSelectedCourses() {
  if (!currentTag.value || courseSelectIds.value.length === 0) return
  const toAdd = allCourses.value.filter((c) => courseSelectIds.value.includes(c.id))
  const next = [...linkedCourses.value, ...toAdd]
  const nextIds = next.map((c) => c.id)
  try {
    await setTagEntities(currentTag.value.id, { courseIds: nextIds })
    ElMessage.success('添加成功')
    linkedCourses.value = next
    courseSelectIds.value = []
  } catch (_e) {
    ElMessage.error('添加失败')
  }
}

function removeCourse(row: { id: number }) {
  if (!currentTag.value) return
  const next = linkedCourses.value.filter((c) => c.id !== row.id)
  setTagEntities(currentTag.value.id, { courseIds: next.map((c) => c.id) })
    .then(() => {
      ElMessage.success('已移除')
      linkedCourses.value = next
    })
    .catch(() => ElMessage.error('移除失败'))
}

onMounted(loadList)
</script>

<style scoped lang="scss">
.tag-container {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .card-header {
    display: flex;
    align-items: center;
    gap: 12px;

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
    .card-desc {
      color: #909399;
      font-size: 13px;
    }
  }
}
</style>
