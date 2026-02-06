<template>
  <div class="help-page">
    <div class="help-hero">
      <el-page-header content="" @back="$router.back()" class="help-header">
        <template #content>
          <span class="help-title">系统使用说明</span>
          <span class="help-subtitle">各功能模块说明与操作指引</span>
        </template>
      </el-page-header>
    </div>

    <div class="help-content">
      <el-card class="help-card help-card-intro" shadow="never">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">📖</span>
            <span>如何使用本系统？</span>
          </div>
        </template>
        <div class="help-body">
          <p>
            本页集中展示各个功能模块（菜单）的使用说明和主要业务逻辑。你可以通过<strong>右上角帮助图标</strong>或各页面的<strong>问号图标</strong>快速跳转到对应模块的说明位置。
          </p>
          <p>
            如需详细的企业内部规范或流程图，可在后续补充到此页面，或链接到公司内部文档。
          </p>
        </div>
      </el-card>

      <el-card id="dashboard" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">📊</span>
            <span>仪表盘（Dashboard）</span>
          </div>
        </template>
        <p>概览学习情况、考试情况等关键指标，为管理员提供快速总览入口。</p>
      </el-card>

      <el-card id="department" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">🏢</span>
            <span>公司架构（组织与人员 - 部门）</span>
          </div>
        </template>
      <p>用于维护公司的组织架构，支持多级部门，其他模块（课程、考试等）的可见性会依赖部门信息。</p>
      <p>支持为部门打标签：在新增/编辑部门时可多选标签，列表中会展示该部门的标签名称。</p>
      <p><strong>关联标签/课程</strong>：操作列有「关联标签/课程」按钮。点击后弹窗内分「标签」「课程」两个 Tab，风格一致：</p>
      <ul>
        <li>多选下拉：选择要关联的标签或课程（已关联项在下拉中禁用）。</li>
        <li>点击「添加」：将本次选中的项加入已关联列表并即时保存。</li>
        <li>下方表格：展示当前已关联的标签或课程，每行有「移除」按钮，移除后即时保存。</li>
        <li>弹窗底部仅「关闭」，无需「保存」——增删均即时生效。</li>
      </ul>
      </el-card>

      <el-card id="user" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">👤</span>
            <span>员工管理</span>
          </div>
        </template>
      <p>用于维护员工账号、所属部门等信息，是学习记录、考试记录等的基础。</p>
      <p>支持为员工打标签：在新增/编辑员工时可多选标签，列表中会展示该员工的标签名称，便于分类与筛选。</p>
      </el-card>

      <el-card id="tag" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">🏷️</span>
            <span>标签管理（组织与人员）</span>
          </div>
        </template>
      <p><strong>标签的作用</strong>：登录用户可以看到（1）自己关联的标签，以及（2）其所属部门关联的标签；与此类标签相对应、被该标签标注的视频会对该用户可见。</p>
      <p>标签可用于对人员、机构（部门）、课程进行统一分类与标记，同一标签可同时关联多类对象。</p>
      <ul>
        <li><strong>标签维护</strong>：新增、编辑、删除标签，可设置标签名称与排序。</li>
        <li><strong>关联人员/机构/课程</strong>：在标签列表中点击某标签的「关联人员/机构/课程」，弹窗与公司架构中的「关联标签/课程」风格一致，分「人员」「部门」「课程」三个 Tab，每个 Tab 均为：
          <ul>
            <li>多选下拉：选择要关联的人员、部门或课程（已关联项在下拉中禁用）。</li>
            <li>点击「添加」：将本次选中的项加入已关联列表并即时保存。</li>
            <li>下方表格：展示当前已关联项，每行有「移除」按钮，移除后即时保存。</li>
            <li>弹窗底部仅「关闭」，无需「保存」——增删均即时生效。</li>
          </ul>
        </li>
        <li><strong>在业务中使用</strong>：在员工管理、公司架构（部门）、课程管理中，新增/编辑时可多选标签；列表中会展示对应标签名称，便于查看与区分。</li>
      </ul>
      </el-card>

      <el-card id="course" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">📚</span>
            <span>课程管理</span>
          </div>
        </template>
      <p>
        创建和维护培训课程，可配置章节与视频、课程可见性、是否必修等。课程可以不关联考试，也可以关联一场考试用于考核（同一场考试可被多门课共用）。
      </p>
      <p>支持为课程打标签：在新增/编辑课程时可多选标签，列表中会展示该课程的标签名称。</p>
      <ul>
        <li>课程下可维护章节与视频：章节用于组织课程结构，视频管理中上传的视频可挂载到课程章节或“未分类”。</li>
        <li>可见性支持公开/私有：私有课程需要关联部门后才对对应员工可见。</li>
        <li>在课程编辑弹窗中可选择“关联考试”，保存后学员在学员端课程详情页可直接从课程进入考试。</li>
      </ul>
      </el-card>

      <el-card id="course-comment" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">💬</span>
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

      <el-card id="video" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">🎬</span>
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

      <el-card id="image" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">🖼️</span>
            <span>图片库</span>
          </div>
        </template>
      <p>统一管理图片素材，可用于课程封面、证书模板等场景。</p>
      </el-card>

      <el-card id="knowledge" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">📁</span>
            <span>知识库</span>
          </div>
        </template>
      <p>用于维护文档类知识内容，可与课程一起为员工提供系统化学习资料。</p>
      </el-card>

      <el-card id="question" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">❓</span>
            <span>试题管理</span>
          </div>
        </template>
      <p>维护题库（单选、多选、判断等），供试卷和考试引用。</p>
      </el-card>

      <el-card id="paper" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">📄</span>
            <span>试卷管理</span>
          </div>
        </template>
      <p>基于题库组卷，配置分值、及格分等信息，为考试提供试卷模板。</p>
      </el-card>

      <el-card id="exam" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">📝</span>
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

      <el-card id="task" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">📋</span>
            <span>培训任务</span>
          </div>
        </template>
      <p>配置周期性任务，将课程、考试等组合到一起，作为员工的培训计划。</p>
      </el-card>

      <el-card id="certificate-template" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">📜</span>
            <span>证书模板</span>
          </div>
        </template>
      <p>设计和管理证书的样式（背景、文案、签名等），供证书规则在发放证书时引用。</p>
      </el-card>

      <el-card id="certificate" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">🎓</span>
            <span>证书规则</span>
          </div>
        </template>
      <p>配置在什么条件下为学员颁发哪一种证书，例如考试通过、任务完成等。</p>
      </el-card>

      <el-card id="point-rule" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">⭐</span>
            <span>积分规则</span>
          </div>
        </template>
      <p>配置完成课程、通过考试、完成任务等行为获得多少积分，用于激励员工学习。</p>
      </el-card>

      <el-card id="feishu-sync" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">🔄</span>
            <span>飞书通讯录同步</span>
          </div>
        </template>
        <p><strong>功能说明</strong>：飞书同步功能可将企业通讯录中的<strong>机构（部门）</strong>和<strong>用户</strong>同步至本系统。同步逻辑：不存在则创建，存在则更新。支持手动触发与定时更新。</p>
        <p><strong>使用前准备</strong>：</p>
        <ul>
          <li><strong>飞书开放平台配置</strong>：在自建应用中，<strong>权限管理</strong> → 申请并启用「通讯录 - 部门信息（只读）」「通讯录 - 用户信息（只读）」。</li>
          <li><strong>后端环境变量配置</strong>：
            <ul>
              <li><strong>文件路径</strong>：<code>lyedu-api-python/.env</code>（如果不存在，可复制 <code>lyedu-api-python/.env.example</code> 为 <code>.env</code>）</li>
              <li><strong>配置项</strong>：在 <code>.env</code> 文件中添加以下两行（去掉注释符号 <code>#</code> 并填入实际值）：
                <pre style="background: #f5f7fa; padding: 8px; border-radius: 4px; font-size: 13px; margin: 8px 0;">FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret</pre>
              </li>
              <li><strong>说明</strong>：配置后重启后端服务（Python API）即可生效。与飞书登录配置使用相同的 App ID 和 App Secret。</li>
            </ul>
          </li>
          <li><strong>数据库迁移</strong>：需执行数据库迁移（Alembic v3 / Flyway V3），为部门表增加 <code>feishu_department_id</code> 字段。</li>
        </ul>
        <p><strong>手动同步</strong>：</p>
        <ul>
          <li>管理后台 → <strong>员工管理</strong> → 点击「从第三方同步」→ 选择「飞书」→ 点击后触发同步。</li>
          <li>同步完成后会提示部门/用户的新增与更新数量。</li>
          <li>接口：<code>POST /api/feishu/sync</code>，返回同步结果（部门与用户的 created、updated、errors）。</li>
        </ul>
        <p><strong>定时更新</strong>：由后端自行配置定时任务（如 cron、APScheduler）定期调用 <code>POST /api/feishu/sync</code> 即可。建议根据企业人员变动频率设置（如每日一次或每周一次）。</p>
        <p><strong>同步范围</strong>：同步时会拉取飞书企业通讯录中的全部部门（递归）和全部用户（含子部门用户），并自动建立部门层级关系与用户-部门关联。</p>
      </el-card>

      <el-card id="settings" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">⚙️</span>
            <span>系统设置</span>
          </div>
        </template>
        <p>配置站点标题、Logo、主题色等基础信息，以及其他全局参数。</p>
        <p><strong>飞书应用</strong>：在「飞书应用」Tab 中可查看飞书同步配置说明与权限要求。</p>
      </el-card>
    </div>
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
  padding: 0;
  min-height: 100%;
  background: linear-gradient(180deg, #f8fafc 0%, #f0f2f5 100%);
}

.help-hero {
  background: #fff;
  border-bottom: 1px solid var(--el-border-color-lighter);
  padding: 16px 24px;
  margin: 0 -1px 0 0;
}

.help-header {
  margin-bottom: 0;

  :deep(.el-page-header__content) {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
}

.help-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.help-subtitle {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  font-weight: 400;
}

.help-content {
  max-width: 820px;
  margin: 0 auto;
  padding: 24px 20px 32px;
}

.help-card {
  margin-bottom: 20px;
  border-radius: 12px;
  border: 1px solid var(--el-border-color-lighter);
  overflow: hidden;

  :deep(.el-card__header) {
    padding: 16px 20px;
    font-size: 15px;
    border-bottom: 1px solid var(--el-border-color-lighter);
    background: #fafbfc;
  }

  :deep(.el-card__body) {
    padding: 20px 24px;
    line-height: 1.72;
    color: var(--el-text-color-regular);

    p {
      margin: 0 0 12px;
      font-size: 14px;

      &:last-child {
        margin-bottom: 0;
      }
    }

    ul {
      margin: 0 0 12px;
      padding-left: 1.4em;

      ul {
        margin: 8px 0 0;
        padding-left: 1.2em;
      }
    }

    li {
      margin-bottom: 6px;
      font-size: 14px;

      &:last-child {
        margin-bottom: 0;
      }
    }

    strong {
      color: var(--el-text-color-primary);
      font-weight: 600;
    }
  }
}

.help-card-intro {
  border-left: 4px solid var(--el-color-primary);
  :deep(.el-card__header) {
    background: linear-gradient(135deg, rgba(var(--el-color-primary-rgb), 0.06) 0%, #fafbfc 100%);
  }
}

.help-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.help-card-icon {
  font-size: 1.2em;
  line-height: 1;
}

.help-body {
  p:last-child {
    margin-bottom: 0;
  }
}
</style>

