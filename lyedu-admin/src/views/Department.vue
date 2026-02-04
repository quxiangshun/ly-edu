<template>
  <div class="department-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>公司架构</span>
          <el-button type="primary" @click="handleAdd">新增部门</el-button>
        </div>
      </template>

      <el-table
        :data="departmentList"
        v-loading="loading"
        border
        row-key="id"
        default-expand-all
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
      >
        <el-table-column prop="name" label="部门名称" min-width="200" />
        <el-table-column prop="sort" label="排序" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link @click="handleCourses(row)">关联课程</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 关联课程对话框 -->
    <el-dialog v-model="courseDialogVisible" :title="`关联课程 - ${currentDept?.name || ''}`" width="640px">
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
            v-for="c in allCourseOptions"
            :key="c.id"
            :label="c.title"
            :value="c.id"
            :disabled="linkedCourseIds.has(c.id)"
          />
        </el-select>
        <el-button type="primary" size="small" style="margin-left: 8px; margin-top: 8px" @click="addSelectedCourses">添加</el-button>
      </div>
      <el-table :data="linkedCourses" border size="small">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="课程名称" />
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button type="danger" link size="small" @click="removeCourse(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="courseDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="上级部门" prop="parentId">
          <el-tree-select
            v-model="form.parentId"
            :data="departmentTreeOptions"
            :props="{ label: 'name', value: 'id' }"
            placeholder="不选则为根级部门"
            clearable
            check-strictly
            default-expand-all
            style="width: 100%"
            :render-after-expand="false"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
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
import { getDepartmentTree, createDepartment, updateDepartment, deleteDepartment, getDepartmentCourses, addCoursesToDepartment, removeCourseFromDepartment, type Department } from '@/api/department'
import { getCoursePage, type Course } from '@/api/course'

const loading = ref(false)
const courseDialogVisible = ref(false)
const currentDept = ref<Department | null>(null)
const linkedCourses = ref<Course[]>([])
const allCourseOptions = ref<Course[]>([])
const courseSelectIds = ref<number[]>([])
const departmentList = ref<Department[]>([])
const formRef = ref<FormInstance>()
const dialogVisible = ref(false)
const dialogTitle = ref('新增部门')
const isEdit = ref(false)

const form = reactive<Partial<Department>>({
  name: '',
  parentId: 0,
  status: 1,
  sort: 0
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }]
}

/** 从树中排除某节点及其所有子孙（避免选自己或下级为上级） */
function filterTreeExcludeId(tree: Department[], excludeId: number | undefined): Department[] {
  if (!excludeId) return tree
  return tree
    .filter((node) => node.id !== excludeId)
    .map((node) => ({
      ...node,
      children: node.children ? filterTreeExcludeId(node.children, excludeId) : undefined
    }))
    .filter((node) => node.id !== undefined)
}

/** 上级部门下拉用：根级 + 树（编辑时排除当前及其子级） */
const departmentTreeOptions = computed(() => {
  const list = departmentList.value || []
  const filtered = isEdit.value && form.id ? filterTreeExcludeId(list, form.id) : list
  return [{ id: 0, name: '根级（顶级）', children: filtered }]
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getDepartmentTree()
    departmentList.value = res
  } catch (e) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增部门'
  Object.assign(form, {
    name: '',
    parentId: 0,
    status: 1,
    sort: 0
  })
  dialogVisible.value = true
}

const handleEdit = (row: Department) => {
  isEdit.value = true
  dialogTitle.value = '编辑部门'
  Object.assign(form, { ...row, parentId: row.parentId ?? 0 })
  dialogVisible.value = true
}

const handleDelete = async (row: Department) => {
  try {
    await ElMessageBox.confirm('确定要删除该部门吗？', '提示', {
      type: 'warning'
    })
    await deleteDepartment(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    // 用户取消或删除失败
  }
}

const linkedCourseIds = computed(() => new Set(linkedCourses.value.map((c) => c.id)))

const handleCourses = async (row: Department) => {
  currentDept.value = row
  courseDialogVisible.value = true
  courseSelectIds.value = []
  try {
    const list = await getDepartmentCourses(row.id)
    linkedCourses.value = Array.isArray(list) ? list : []
    const page = await getCoursePage({ page: 1, size: 500 })
    allCourseOptions.value = page?.records ?? []
  } catch (e) {
    ElMessage.error('加载失败')
    linkedCourses.value = []
    allCourseOptions.value = []
  }
}

const addSelectedCourses = async () => {
  if (!currentDept.value || courseSelectIds.value.length === 0) return
  try {
    await addCoursesToDepartment(currentDept.value.id, courseSelectIds.value)
    ElMessage.success('添加成功')
    const list = await getDepartmentCourses(currentDept.value.id)
    linkedCourses.value = Array.isArray(list) ? list : []
    courseSelectIds.value = []
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

const removeCourse = async (course: Course) => {
  if (!currentDept.value) return
  try {
    await removeCourseFromDepartment(currentDept.value.id, course.id)
    ElMessage.success('已移除')
    linkedCourses.value = linkedCourses.value.filter((c) => c.id !== course.id)
  } catch (e) {
    ElMessage.error('移除失败')
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  try {
    if (isEdit.value) {
      await updateDepartment(form.id!, form)
      ElMessage.success('更新成功')
    } else {
      await createDepartment(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.department-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
