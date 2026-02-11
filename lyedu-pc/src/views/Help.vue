<template>
  <div class="help-container">
    <AppHeader />
    <el-main class="main-content">
      <div class="help-content">
        <h2>使用说明</h2>
        <p class="help-intro">本页为学员端使用说明，帮助您快速上手企业培训平台。您可通过顶栏菜单进入各功能模块。</p>

        <el-card id="login" class="help-card" shadow="hover">
          <template #header>
            <span class="help-card-title">登录与退出</span>
          </template>
          <ul class="help-list">
            <li><strong>账号密码登录</strong>：在登录页输入用户名、密码后点击「登录」。</li>
            <li><strong>飞书扫码登录</strong>：若管理员已开启飞书登录，可点击「飞书扫码登录」使用飞书 App 扫码完成登录。</li>
            <li><strong>退出</strong>：点击顶栏右侧用户名，在下拉菜单中选择「退出登录」。</li>
          </ul>
        </el-card>

        <el-card id="nav" class="help-card" shadow="hover">
          <template #header>
            <span class="help-card-title">顶栏与导航</span>
          </template>
          <p>顶栏左侧为平台 Logo，点击可返回首页。中间为功能菜单：首页、课程中心、知识中心、考试中心、我的证书、我的任务、积分、我的学习、使用说明。右侧为登录入口或当前用户信息（头像/昵称），点击用户名可进入个人中心或退出登录。</p>
        </el-card>

        <el-card id="home" class="help-card" shadow="hover">
          <template #header>
            <span class="help-card-title">首页</span>
          </template>
          <p>首页展示平台欢迎语、快捷入口与功能简介。登录后还会显示：</p>
          <ul class="help-list">
            <li><strong>最近学习</strong>：您最近在学的课程，点击「继续学习」可进入课程详情或播放页。</li>
            <li><strong>推荐课程</strong>：系统推荐的课程，点击「开始学习」可加入课程并进入详情页。</li>
          </ul>
          <p>点击「开始学习」按钮或顶栏「课程中心」可进入课程列表。</p>
        </el-card>

        <el-card id="courses" class="help-card" shadow="hover">
          <template #header>
            <span class="help-card-title">课程中心</span>
          </template>
          <p>课程中心展示所有您可见的课程，支持分页浏览。</p>
          <ul class="help-list">
            <li><strong>搜索</strong>：在关键词框中输入课程名称等，按回车或点击「搜索」进行筛选。</li>
            <li><strong>分类筛选</strong>：在分类下拉框中选择某一分类，可只显示该分类下的课程。</li>
            <li><strong>重置</strong>：点击「重置」可清空搜索与分类条件，恢复全部列表。</li>
            <li><strong>加入课程</strong>：点击课程卡片上的「开始学习」或进入课程详情页后加入课程，即可观看视频、参与评论等。</li>
          </ul>
          <p>点击课程卡片可进入<strong>课程详情</strong>页，查看章节与视频列表、评论、附件等，并可从详情页进入视频播放。</p>
        </el-card>

        <el-card id="video" class="help-card" shadow="hover">
          <template #header>
            <span class="help-card-title">视频学习与进度</span>
          </template>
          <p>在课程详情页点击某一视频即可进入<strong>视频播放</strong>页。右侧为同课程下的视频列表，可点击切换播放。</p>
          <ul class="help-list">
            <li><strong>进度记录</strong>：播放过程中系统会自动保存学习进度，下次进入可从上次位置继续。</li>
            <li><strong>禁止拖拽/倍速</strong>：部分课程由管理员设置了「禁止拖拽进度条」或「禁止倍速」，此时进度条拖拽或倍速选择可能不可用或无效，请按页面实际显示为准。</li>
            <li><strong>连续播放</strong>：当前视频播放结束后，若该课程还有下一集，系统会提示并自动跳转到下一集。</li>
          </ul>
          <p>您可在顶栏<strong>我的学习</strong>中查看已加入课程及每个视频的学习进度。</p>
        </el-card>

        <el-card id="knowledge" class="help-card" shadow="hover">
          <template #header>
            <span class="help-card-title">知识中心与文档</span>
          </template>
          <p>顶栏点击<strong>知识中心</strong>可浏览文档、资料等学习资源。列表会展示文档标题、分类等信息，点击某条记录即可<strong>在线预览</strong>，支持常见文档格式（如 PDF、Office 等，以系统支持为准）。</p>
        </el-card>

        <el-card id="exam" class="help-card" shadow="hover">
          <template #header>
            <span class="help-card-title">考试与证书</span>
          </template>
          <p><strong>考试中心</strong>：在考试中心可看到可参加的考试列表，点击进入答题。作答完成后提交试卷，系统会给出成绩与结果；部分考试可能允许查看答题详情，请以页面显示为准。</p>
          <p><strong>我的证书</strong>：完成相应学习或考试要求后，管理员会发放证书。在「我的证书」中可查看已获得的证书，并支持<strong>打印</strong>（进入证书详情后使用打印功能）。</p>
        </el-card>

        <el-card id="task" class="help-card" shadow="hover">
          <template #header>
            <span class="help-card-title">任务与积分</span>
          </template>
          <p><strong>我的任务</strong>：展示您需要完成的任务列表（如学习某课程、参加某考试等）。点击任务可查看详情与完成要求，按要求完成后任务状态会更新。</p>
          <p><strong>积分</strong>：积分页可查看您当前积分及<strong>排行榜</strong>。积分规则由管理员在后台配置，完成学习、考试等行为可能会获得积分。</p>
        </el-card>

        <el-card id="profile" class="help-card" shadow="hover">
          <template #header>
            <span class="help-card-title">个人中心</span>
          </template>
          <p>点击顶栏右侧<strong>用户名</strong>，在下拉菜单中选择「个人信息」即可进入个人中心。</p>
          <ul class="help-list">
            <li><strong>查看资料</strong>：个人中心展示您的用户名、真实姓名、昵称、邮箱、手机号等（以管理员开放字段为准）。</li>
            <li><strong>编辑资料</strong>：点击「编辑资料」后可修改真实姓名、昵称、邮箱、手机号。修改完成后点击「保存」生效。</li>
            <li><strong>头像</strong>：编辑时可上传头像——点击上传区域选择本地图片（支持 JPG、PNG、GIF、WebP），上传成功后头像地址会自动填入；您也可以手动输入头像链接。保存后，顶栏会显示新头像。</li>
          </ul>
        </el-card>

        <el-card id="other" class="help-card" shadow="hover">
          <template #header>
            <span class="help-card-title">其他说明</span>
          </template>
          <ul class="help-list">
            <li>页面标题（浏览器标签文字）会随当前页面自动更新，便于区分不同功能。</li>
            <li>若您使用飞书等第三方登录，首次登录后系统会创建或绑定账号，后续可直接使用该方式登录。</li>
            <li>遇到无法访问的课程、考试或功能，可能是权限或可见范围限制，请联系管理员。</li>
          </ul>
        </el-card>

        <p class="help-footer">如有疑问或需要更详细的企业内部规范说明，请联系管理员或查看管理员提供的补充文档。</p>
      </div>
    </el-main>
  </div>
</template>

<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
</script>

<style scoped lang="scss">
.help-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  background: #f5f7fa;
  padding: 40px 20px;
  margin-top: 60px;
}

.help-content {
  max-width: 720px;
  margin: 0 auto;

  h2 {
    margin-bottom: 12px;
    color: #303133;
  }

  .help-intro {
    margin-bottom: 24px;
    color: #606266;
    font-size: 14px;
  }

  .help-card {
    margin-bottom: 16px;

    .help-card-title {
      font-weight: 600;
      color: #303133;
    }

    p {
      margin: 0 0 10px 0;
      color: #606266;
      line-height: 1.6;
      font-size: 14px;

      &:last-child {
        margin-bottom: 0;
      }
    }

    .help-list {
      margin: 0 0 10px 0;
      padding-left: 20px;
      color: #606266;
      font-size: 14px;
      line-height: 1.7;

      li {
        margin-bottom: 6px;

        &:last-child {
          margin-bottom: 0;
        }
      }
    }
  }

  .help-footer {
    margin-top: 24px;
    padding-top: 16px;
    border-top: 1px solid #ebeef5;
    color: #909399;
    font-size: 13px;
  }
}
</style>
