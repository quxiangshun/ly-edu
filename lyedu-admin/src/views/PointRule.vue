<template>
  <div class="point-rule-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>积分规则</span>
          <span class="card-desc">完成课程/考试合格/完成任务时按规则发放积分，同一项只发一次</span>
        </div>
      </template>

      <el-table :data="ruleList" v-loading="loading" border>
        <el-table-column prop="ruleKey" label="规则键" width="140" />
        <el-table-column prop="ruleName" label="规则名称" min-width="120" />
        <el-table-column prop="points" label="奖励积分" width="100">
          <template #default="{ row }">
            <el-input-number
              v-model="row.points"
              :min="0"
              :max="9999"
              size="small"
              @change="() => handleRuleChange(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="启用" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" :active-value="1" :inactive-value="0" @change="() => handleRuleChange(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="180" show-overflow-tooltip />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getPointRuleList, updatePointRule, type PointRuleItem } from '@/api/pointRule'

const loading = ref(false)
const ruleList = ref<PointRuleItem[]>([])

async function loadList() {
  loading.value = true
  try {
    const res = await getPointRuleList()
    ruleList.value = (res as unknown as { data?: PointRuleItem[] })?.data ?? res ?? []
  } catch (_e) {
    ElMessage.error('加载积分规则失败')
  } finally {
    loading.value = false
  }
}

async function handleRuleChange(row: PointRuleItem) {
  try {
    await updatePointRule({
      ruleKey: row.ruleKey,
      ruleName: row.ruleName,
      points: row.points,
      enabled: row.enabled,
      remark: row.remark
    })
    ElMessage.success('已保存')
  } catch (_e) {
    ElMessage.error('保存失败')
  }
}

onMounted(loadList)
</script>

<style scoped lang="scss">
.point-rule-container {
  .card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    .card-desc {
      color: #909399;
      font-size: 13px;
    }
  }
}
</style>
