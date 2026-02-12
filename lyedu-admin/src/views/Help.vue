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
          <p><strong>项目整体逻辑</strong></p>
          <ul>
            <li><strong>管理后台</strong>（本系统）：负责组织架构、用户、标签、课程、视频、考试、任务、证书、积分等配置与数据管理；课程/考试可见性依赖部门与标签（见「标签管理」）。</li>
            <li><strong>学员端</strong>（uni-app x / H5）：学员登录后使用首页、课程中心、我的学习、考试、任务、证书等；可见内容由用户有效标签、部门、课程可见性等规则决定。</li>
            <li><strong>后端接口</strong>（lyedu-api-python）：提供 REST API，对接管理后台与学员端；课程与视频的可见性、分页、排序、筛选逻辑在接口层统一实现。</li>
            <li><strong>学员端首页逻辑</strong>：
              <ul>
                <li><strong>标签</strong>：调用 <code>/tag/effective</code> 获取用户有效标签，展示「全部」+ 各标签 Tab；选「全部」不传 tagId，选某标签则传 <code>tagId</code>。</li>
                <li><strong>排序</strong>：综合排序、最新发布、最多播放、最多点赞、最多评论 对应参数 <code>sort=default|latest|play|like|comment</code>，请求 <code>/video/page</code> 时一并传入。</li>
                <li><strong>模糊查询</strong>：搜索框关键词请求时传 <code>keyword</code>，接口按视频标题 LIKE 匹配。</li>
                <li><strong>视频列表</strong>：调用 <code>GET /video/page</code>（参数 <code>page</code>、<code>size</code>、<code>tagId</code>、<code>keyword</code>、<code>sort</code>），两列展示，滚动触底分页加载。</li>
                <li><strong>相关课程</strong>：同屏调用 <code>GET /course/page</code>（相同 <code>tagId</code>、<code>keyword</code>），在视频列表上方展示「相关课程」区块，点击进入课程详情。</li>
              </ul>
            </li>
          </ul>
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
      <p>后台可以为<strong>用户</strong>、<strong>部门</strong>、<strong>课程</strong>打标签；同一标签可同时关联多类对象，用于统一分类与权限控制。</p>
      <p><strong>课程可见性（与标签的关系）</strong>：学员端「课程中心」中，某用户能看到的课程由以下规则共同决定：</p>
      <ul>
        <li><strong>公开课程</strong>：可见性为「公开」的课程，所有用户均可看到。</li>
        <li><strong>私有课程 + 部门关联</strong>：可见性为「私有」且关联了用户所属部门或其子部门的课程，该用户可见。</li>
        <li><strong>标签匹配</strong>：将「用户有效标签」与课程的标签做匹配——若课程带有用户有效标签中的<strong>任意一个</strong>，该用户即可看到该课程（与公开/私有、部门关联并列生效，满足其一即可）。</li>
      </ul>
      <p><strong>用户有效标签</strong> = 以下三类标签的<strong>合并去重</strong>：</p>
      <ol>
        <li>该<strong>用户自身</strong>关联的标签；</li>
        <li>该用户<strong>所属部门</strong>关联的标签；</li>
        <li>该用户所属部门及其<strong>所有子部门</strong>关联的标签。</li>
      </ol>
      <p><strong>通俗举例</strong>：</p>
      <ul>
        <li>公司有部门「研发部」，其下子部门有「研发部-前端组」「研发部-后端组」。</li>
        <li>学员<strong>张三</strong>属于「研发部-前端组」。给张三本人打了标签「新员工」；给部门「研发部」打了标签「技术岗」；给部门「研发部-前端组」打了标签「前端」。</li>
        <li>则张三的<strong>用户有效标签</strong> = 新员工 + 技术岗 + 前端（三类合并去重）。</li>
        <li>若课程《前端入门》打了标签「前端」，因「前端」在张三的有效标签里，<strong>张三在学员端能看到这门课</strong>（即使课程设为私有且未关联部门）。</li>
        <li>若课程《安全培训》只打了标签「安全」，而张三、其部门及子部门都没有「安全」标签，则张三的有效标签里没有「安全」，<strong>张三看不到《安全培训》</strong>——除非该课程设为公开，或私有但关联了张三所在部门/子部门。</li>
      </ul>
      <p><strong>用户有效标签 = 本人标签 + 本部门标签 + 本部门及子部门标签；课程只要带其中任一标签，该用户就能看到。</strong></p>
      <p>因此：给用户、部门、课程打标签后，只要课程的标签与「用户有效标签」有交集，该用户就能在学员端看到该课程；无需再把课程设为公开或单独关联部门。</p>
      <ul>
        <li><strong>标签维护</strong>：新增、编辑、删除标签，可设置标签名称与排序。</li>
        <li><strong>关联人员/机构/课程</strong>：在标签列表中点击某标签的「关联人员/机构/课程」，弹窗分「人员」「部门」「课程」三个 Tab，每个 Tab 均为：多选下拉选择要关联的项 → 点击「添加」加入已关联列表并即时保存；下方表格展示已关联项，每行可「移除」。</li>
        <li><strong>在业务中使用</strong>：在员工管理、公司架构（部门）、课程管理中，新增/编辑时可多选标签；列表中会展示对应标签名称，便于查看与区分。</li>
      </ul>
      </el-card>

      <el-card id="user-learning" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">📈</span>
            <span>学习记录</span>
          </div>
        </template>
        <p>查看所有学员的课程学习进度和记录。</p>
        <ul>
          <li><strong>搜索筛选</strong>：支持按关键词（用户名/姓名/课程名称）、用户ID、课程ID筛选。</li>
          <li><strong>进度展示</strong>：展示每名学员对每门课程的学习进度（百分比），便于追踪完成情况。</li>
          <li><strong>关联关系</strong>：记录由学员在学员端观看视频、完成学习时自动生成，管理员仅作查看与统计。</li>
        </ul>
      </el-card>

      <el-card id="user-point" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">💎</span>
            <span>积分记录</span>
          </div>
        </template>
        <p>查看所有学员的积分变动明细。</p>
        <ul>
          <li><strong>搜索筛选</strong>：支持按关键词（用户名/姓名/备注）、用户ID筛选。</li>
          <li><strong>积分明细</strong>：每条记录包含积分增减、规则Key、关联类型、关联ID、备注、获得时间等。</li>
          <li><strong>数据来源</strong>：积分由系统根据「积分规则」在学员完成课程、通过考试、完成任务等行为时自动发放。</li>
        </ul>
      </el-card>

      <el-card id="user-certificate" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">🎖️</span>
            <span>用户证书</span>
          </div>
        </template>
        <p>查看所有学员已获得的证书列表。</p>
        <ul>
          <li><strong>搜索筛选</strong>：支持按关键词（用户名/姓名/证书名称/证书编号）、用户ID、证书ID筛选。</li>
          <li><strong>证书信息</strong>：展示证书编号、颁发时间等，便于核实与归档。</li>
          <li><strong>发放逻辑</strong>：证书由系统根据「证书规则」在满足条件（如考试通过、任务完成）时自动颁发。</li>
        </ul>
      </el-card>

      <el-card id="user-task" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">✅</span>
            <span>用户任务</span>
          </div>
        </template>
        <p>查看所有学员的培训任务完成情况。</p>
        <ul>
          <li><strong>搜索筛选</strong>：支持按关键词（用户名/姓名/任务名称）、用户ID、任务ID筛选。</li>
          <li><strong>完成状态</strong>：展示每名学员对每个任务的完成状态（进行中/已完成）。</li>
          <li><strong>任务来源</strong>：任务由「培训任务」模块配置，系统按规则将任务分配给学员，完成情况由学员端操作自动更新。</li>
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
      <p>支持为课程打标签：在新增/编辑课程时可多选标签，列表中会展示该课程的标签名称。<strong>学员端可见性</strong>：用户能看到某课程的条件为（满足其一即可）——该课程为公开；或该课程为私有且关联了用户所属部门/子部门；或该课程带有「用户有效标签」中的任意一个（用户有效标签 = 用户自身标签 ∪ 用户所属部门标签 ∪ 用户所属部门及其子部门标签）。详见上方「标签管理」。</p>
      <ul>
        <li>课程下可维护章节与视频：章节用于组织课程结构，视频管理中上传的视频可挂载到课程章节或“未分类”。</li>
        <li>可见性支持公开/私有：私有课程可关联部门，也可通过标签控制可见范围（见标签管理）。</li>
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
      <p><strong>学员端首页与接口逻辑</strong></p>
      <ul>
        <li><strong>视频分页接口</strong> <code>GET /video/page</code>：支持 <code>page</code>、<code>size</code>、<code>courseId</code>、<code>keyword</code>（视频标题模糊查询）、<code>tagId</code>（标签筛选，不传为「全部」）、<code>sort</code>（排序方式）。</li>
        <li><strong>排序方式</strong> <code>sort</code>：<code>default</code> 综合排序，<code>latest</code> 最新发布，<code>play</code> 最多播放，<code>like</code> 最多点赞，<code>comment</code> 最多评论；服务端按对应字段排序后返回。</li>
        <li>学员端首页：顶部为搜索栏、标签横向滚动、排序方式横向滚动（均不随页面滚动）；下方为「相关课程」区块（调用 <code>/course/page</code>，与当前标签/关键词一致）和视频两列列表；视频列表滚动触底分页加载，每次请求携带当前标签、关键词、排序参数。</li>
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

      <el-card id="exam-record" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">📑</span>
            <span>考试记录</span>
          </div>
        </template>
        <p>查看所有学员的考试作答记录和成绩。</p>
        <ul>
          <li><strong>搜索筛选</strong>：支持按关键词（用户名/姓名/考试名称）、考试ID、用户ID筛选。</li>
          <li><strong>成绩信息</strong>：展示得分、是否通过、提交时间、作答时长等，便于统计与导出。</li>
          <li><strong>记录生成</strong>：学员在学员端提交考试后自动生成记录，管理员可据此评估学习效果和培训成效。</li>
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
        <p><strong>功能说明</strong>：将飞书企业通讯录中的<strong>部门</strong>和<strong>用户</strong>同步至本系统。支持仅同步部门、仅同步用户或同时同步；支持「覆盖已存在」选项。</p>
        <p><strong>同步方式（业务逻辑）</strong>：</p>
        <ol>
          <li><strong>先同步所有部门</strong>：从飞书根部门递归拉取全部部门，再同步到本系统。</li>
          <li><strong>再按部门拉取用户</strong>：遍历每个部门，调用飞书「部门下用户」接口拉取该部门及子部门下的用户，按 open_id 去重后逐条处理。</li>
          <li><strong>部门 ID 与缓存</strong>：本系统部门以 <code>feishu_department_id</code> 与飞书对应。同步用户前会构建「飞书部门 ID → 本地部门 id」缓存，写用户时直接用缓存得到所属部门，避免多次查库，保证效率。</li>
        </ol>
        <p><strong>只同步部门时</strong>：根据 <code>feishu_department_id</code> 匹配。勾选「覆盖」则已存在则更新，不勾选则已存在跳过、不存在则插入。</p>
        <p><strong>只同步用户时</strong>：仍按部门维度拉取用户（不处理部门数据）。用户以<strong>手机号</strong>做唯一性校验：已存在则按「覆盖」决定更新或跳过；不存在则插入。用户所属部门从上述缓存解析。</p>
        <p><strong>第三方配置</strong>：飞书 App ID、App Secret 在<strong>系统设置</strong>→「飞书应用」中配置（与飞书登录共用）。</p>
        <p><strong>使用前准备</strong>：</p>
        <ul>
          <li>飞书开放平台：自建应用<strong>权限管理</strong>中申请「通讯录 - 部门信息（只读）」「通讯录 - 用户信息（只读）」。</li>
          <li>系统设置：配置飞书 App ID、App Secret。</li>
          <li>数据库：部门表需有 <code>feishu_department_id</code> 字段（迁移已包含）。</li>
        </ul>
        <p><strong>触发同步</strong>：<strong>员工管理</strong> → 「从第三方同步」→ 选择「飞书」→ 勾选「同步部门」「同步用户」及「覆盖已存在」→ 确认。同步采用后台任务，完成后提示部门/用户新增与更新数量。接口：<code>POST /api/feishu/sync?background=1</code>，轮询 <code>GET /api/feishu/sync/task/{task_id}</code> 获取结果。</p>
        <p><strong>定时更新</strong>：可由后端配置定时任务定期调用 <code>POST /api/feishu/sync</code>（可传 <code>sync_departments</code>、<code>sync_users</code>、<code>overwrite_existing</code>），建议按企业人员变动频率设置（如每日或每周）。</p>
      </el-card>

      <el-card id="settings" class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header">
            <span class="help-card-icon">⚙️</span>
            <span>系统设置</span>
          </div>
        </template>
        <p>配置站点标题、Logo、主题色等基础信息，以及其他全局参数。</p>
        <p><strong>第三方配置</strong>：飞书等第三方应用的 App ID、App Secret 等在「飞书应用」Tab 中配置，供飞书登录和飞书通讯录同步使用。数据同步的触发入口在<strong>员工管理</strong>页面的「从第三方同步」按钮。</p>
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

