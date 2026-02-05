<template>
  <div class="help-page">
    <el-page-header content="系统使用说明" @back="$router.back()" class="help-header" />

    <el-card class="help-card">
      <template #header>
        <div class="help-card-header">
          <span>如何使用本系统？</span>
        </div>
      </template>
      <p>
        本页用于集中展示各个功能模块（菜单）的使用说明和主要业务逻辑。你可以通过右上角的帮助图标或各页面的 Tip
        图标快速跳转到对应模块的说明位置。
      </p>
      <p>
        如需详细的企业内部规范或流程图，可以在后续按需补充到此页面，或链接到公司内部文档。
      </p>
    </el-card>

    <el-card id="dashboard" class="help-card">
      <template #header>
        <div class="help-card-header">
          <span>仪表盘（Dashboard）</span>
        </div>
      </template>
      <p>概览学习情况、考试情况等关键指标，为管理员提供快速总览入口。</p>
    </el-card>

    <el-card id="department" class="help-card">
      <template #header>
        <div class="help-card-header">
          <span>公司架构（组织与人员 - 部门）</span>
        </div>
      </template>
      <p>用于维护公司的组织架构，支持多级部门，其他模块（课程、考试等）的可见性会依赖部门信息。</p>
    </el-card>

    <el-card id="user" class="help-card">
      <template #header>
        <div class="help-card-header">
          <span>员工管理</span>
        </div>
      </template>
      <p>用于维护员工账号、所属部门等信息，是学习记录、考试记录等的基础。</p>
    </el-card>

    <el-card id="course" class="help-card">
      <template #header>
        <div class="help-card-header">
          <span>课程管理</span>
        </div>
      </template>
      <p>
        创建和维护培训课程，可配置章节与视频、课程可见性、是否必修等。课程可以不关联考试，也可以关联一场考试用于考核（同一场考试可被多门课共用）。
      </p>
      <ul>
        <li>课程下可维护章节与视频：章节用于组织课程结构，视频管理中上传的视频可挂载到课程章节或“未分类”。</li>
        <li>可见性支持公开/私有：私有课程需要关联部门后才对对应员工可见。</li>
        <li>在课程编辑弹窗中可选择“关联考试”，保存后学员在学员端课程详情页可直接从课程进入考试。</li>
      </ul>
    </el-card>

    <el-card id="course-comment" class="help-card">
      <template #header>
        <div class="help-card-header">
          <span>评论管理</span>
        </div>
      </template>
      <p>
        统一管理课程评论，支持查看、删除、隐藏/显示等操作，维护良好的学习交流环境。
      </p>
      <ul>
        <li>
          <strong>评论查看</strong>：管理员可以查看所有评论，包括已删除和隐藏的评论。列表显示评论内容、所属课程、评论用户、创建时间、状态等信息。
        </li>
        <li>
          <strong>搜索筛选</strong>：支持按关键词（评论内容/用户名）、课程ID、状态（显示/隐藏）进行筛选，快速定位目标评论。
        </li>
        <li>
          <strong>删除评论</strong>：管理员可以删除任意评论。删除为"假删除"（软删除），数据不会从数据库中物理删除，只是标记为已删除状态，用户端将不再显示。
        </li>
        <li>
          <strong>隐藏/显示评论</strong>：管理员可以将评论设置为"隐藏"状态，隐藏的评论在H5端（学员端）不会显示，但管理员仍可在后台查看。可以随时将隐藏的评论重新设置为"显示"状态。
        </li>
        <li>
          <strong>用户端删除</strong>：在H5端（学员端），用户可以删除自己发表的评论。用户只能删除自己的评论，删除后评论在用户端不再显示，但管理员仍可在后台查看和管理。
        </li>
        <li>
          <strong>默认状态</strong>：新发表的评论默认状态为"显示"（status=1），用户端正常展示。管理员可以根据内容质量、合规性等因素调整评论的显示状态。
        </li>
      </ul>
    </el-card>

    <el-card id="video" class="help-card">
      <template #header>
        <div class="help-card-header">
          <span>视频管理</span>
        </div>
      </template>
      <p>统一管理上传的视频资源，并绑定到课程中供学员学习。</p>
      <ul>
        <li>基础信息：视频标题、所属课程与章节、排序等。</li>
        <li>上传视频：通过“视频上传”组件上传本地视频文件，上传成功后自动填充视频地址。</li>
        <li>
          上传封面：可为视频上传单独的封面图片；有封面时优先展示封面，无封面时在学员端播放页会使用视频第一帧作为封面显示。
        </li>
        <li>自动获取时长：上传完成后系统会自动读取视频时长并回填到“时长（秒）”字段，便于统计学习进度。</li>
        <li>播放/点赞统计：后台可看到每个视频的播放次数与点赞次数，用于评估内容受欢迎程度（数据来自学员端实际观看与点赞行为）。</li>
      </ul>
    </el-card>

    <el-card id="image" class="help-card">
      <template #header>
        <div class="help-card-header">
          <span>图片库</span>
        </div>
      </template>
      <p>统一管理图片素材，可用于课程封面、证书模板等场景。</p>
    </el-card>

    <el-card id="knowledge" class="help-card">
      <template #header>
        <div class="help-card-header">
          <span>知识库</span>
        </div>
      </template>
      <p>用于维护文档类知识内容，可与课程一起为员工提供系统化学习资料。</p>
    </el-card>

    <el-card id="question" class="help-card">
      <template #header>
        <div class="help-card-header">
          <span>试题管理</span>
        </div>
      </template>
      <p>维护题库（单选、多选、判断等），供试卷和考试引用。</p>
    </el-card>

    <el-card id="paper" class="help-card">
      <template #header>
        <div class="help-card-header">
          <span>试卷管理</span>
        </div>
      </template>
      <p>基于题库组卷，配置分值、及格分等信息，为考试提供试卷模板。</p>
    </el-card>

    <el-card id="exam" class="help-card">
      <template #header>
        <div class="help-card-header">
          <span>考试管理</span>
        </div>
      </template>
      <p>
        创建考试任务，可配置时间范围（固定时间或不限时）、关联试卷、可见性和状态。课程可以关联到某场考试，实现“学完后参加考试”的流程。
      </p>
      <ul>
        <li>一门课程最多关联一场考试，但一场考试可以被多门课程复用。</li>
        <li>
          考试时间模式（在考试管理里通过「开始时间」「结束时间」控制）：
          <ul>
            <li><strong>不限时间</strong>：开始时间和结束时间<strong>都不设置</strong>（留空）。表示该考试没有开放时间段限制，学员随时可以点击“开始考试”开始作答，系统只统计作答时长，不限制何时可考、何时必须结束。</li>
            <li><strong>固定时间</strong>：配置了开始时间和/或结束时间。学员只有在开始时间之后、结束时间之前才能开始考试；到达结束时间后不能继续作答，只能交卷。若只设结束时间不设开始时间，表示“随时可开始，但有截止时间”。</li>
          </ul>
          <strong>简要总结</strong>：“不设置开始时间”要结合结束时间理解——开始、结束都不设 = 不限时间、随时可考；只不设开始但设了结束 = 截止前随时可开始，到点结束。
        </li>
        <li>作答时长统计：无论是否固定时间，学员点击开始答题时开始计时，交卷时记录本次作答耗时，便于后续统计分析。</li>
        <li>可见性与部门：与课程类似，考试支持公开/私有，私有考试仅对关联部门员工可见。</li>
      </ul>
    </el-card>

    <el-card id="task" class="help-card">
      <template #header>
        <div class="help-card-header">
          <span>培训任务</span>
        </div>
      </template>
      <p>配置周期性任务，将课程、考试等组合到一起，作为员工的培训计划。</p>
    </el-card>

    <el-card id="certificate-template" class="help-card">
      <template #header>
        <div class="help-card-header">
          <span>证书模板</span>
        </div>
      </template>
      <p>设计和管理证书的样式（背景、文案、签名等），供证书规则在发放证书时引用。</p>
    </el-card>

    <el-card id="certificate" class="help-card">
      <template #header>
        <div class="help-card-header">
          <span>证书规则</span>
        </div>
      </template>
      <p>配置在什么条件下为学员颁发哪一种证书，例如考试通过、任务完成等。</p>
    </el-card>

    <el-card id="point-rule" class="help-card">
      <template #header>
        <div class="help-card-header">
          <span>积分规则</span>
        </div>
      </template>
      <p>配置完成课程、通过考试、完成任务等行为获得多少积分，用于激励员工学习。</p>
    </el-card>

    <el-card id="settings" class="help-card">
      <template #header>
        <div class="help-card-header">
          <span>系统设置</span>
        </div>
      </template>
      <p>配置站点标题、Logo、主题色等基础信息，以及其他全局参数。</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

onMounted(async () => {
  await nextTick()
  const section = (route.query.section as string) || ''
  if (section) {
    const el = document.getElementById(section)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }
})
</script>

<style scoped lang="scss">
.help-page {
  padding: 0 0 12px;
}

.help-header {
  margin-bottom: 16px;
}

.help-card {
  margin-bottom: 16px;

  .help-card-header {
    font-weight: 600;
  }
}
</style>

