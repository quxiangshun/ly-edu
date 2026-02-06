# LyEdu 目录与文件说明

本文档说明仓库中主要目录和文件的作用，便于新人快速了解项目结构。

---

## 仓库根目录

| 文件/目录 | 作用 |
|-----------|------|
| **README.md** | 项目介绍、快速开始、技术栈、功能列表、许可证与支持说明 |
| **LICENSE** | Apache 2.0 开源协议全文 |
| **.gitignore** | Git 忽略规则（如 node_modules、target、.env 等） |
| **.dockerignore** | Docker 构建时忽略的文件 |
| **.env.example** | 根目录环境变量示例（Docker 镜像源、端口等） |
| **compose.yml** | 完整 Docker Compose：MySQL + Redis + Java API + admin/pc/h5 前端 |
| **compose-mysql-redis.yml** | 仅启动 MySQL + Redis，供本地开发直连 |
| **build-api.ps1** / **build-api.sh** | 构建 Java 后端 jar 并复制到 pkg/ |
| **init-gradle.ps1** | Windows 下初始化 Gradle 包装器（可选） |
| **pkg/** | 构建产物目录，存放 lyedu-api.jar 等 |

---

## db/ — 数据库迁移（与 Flyway/Alembic 同源）

| 文件/目录 | 作用 |
|-----------|------|
| **db/README.md** | 数据库迁移说明（Flyway 与 Alembic 版本对应） |
| **db/flyway/** | Java 端使用的 Flyway SQL 脚本 |
| **db/flyway/V1__init_schema.sql** | 完整初始化（整合原 V1～V18：用户/部门/课程/视频/考试/证书/任务/知识库/积分/配置等） |
| **db/alembic/** | Python 端使用的 Alembic 迁移（与 Flyway 版本对应） |
| **db/alembic/env.py** | Alembic 环境：从 lyedu-api-python/config 读库连接，执行迁移 |
| **db/alembic/script.py.mako** | 生成新迁移脚本的模板 |
| **db/alembic/versions/** | Alembic 迁移版本脚本（v1～v11 与 Flyway V1～V11 对应） |

---

## docker/ — Docker 相关

| 文件/目录 | 作用 |
|-----------|------|
| **docker/mysql/init.sql** | MySQL 容器首次启动时执行的初始化 SQL（如建库、用户等） |

---

## docs/ — 项目文档

| 文件 | 作用 |
|------|------|
| **PROJECT_STRUCTURE.md** | 项目结构、技术选型、开发规范、部署说明 |
| **FILE_STRUCTURE.md** | 本文件：目录与每个文件的作用说明 |
| **DOCKER_SETUP.md** | Docker 部署步骤、常见问题、仅 MySQL+Redis 与完整启动方式 |
| **FEATURES_DESIGN.md** | 功能设计说明 |
| **FEISHU_APP.md** | 飞书应用配置与登录对接说明 |
| **CHANGELOG.md** | 版本更新记录 |
| **COMMIT_UTF8.md** | Git 提交中文乱码的解决与 UTF-8 配置 |
| **GRADLE_SETUP.md** | Gradle 环境与构建说明 |
| **JDK25_DOCKER_FIX.md** / **QUICK_FIX_JDK25.md** | JDK 25 在 Docker 下的问题与修复 |
| **SUPPORT.md** | 用户支持与打赏说明 |
| **支付宝收款码.jpg** / **微信收款码.jpg** | 打赏用图片 |

---

## lyedu-api/ — 后端 API（Java，SpringBoot 4）

| 文件/目录 | 作用 |
|-----------|------|
| **pom.xml** | Maven 依赖与构建配置 |
| **build.gradle** / **settings.gradle** / **gradle.properties** | Gradle 构建配置（与 Maven 二选一或并行） |
| **gradlew** / **gradlew.bat** | Gradle 包装器脚本 |
| **gradle/wrapper/** | Gradle 包装器 jar 与配置 |
| **Dockerfile** | 构建 Java API 镜像（依赖 pkg/lyedu-api.jar） |
| **src/main/java/com/lyedu/** | Java 源码包 |
| **annotation/** | 自定义注解 |
| **common/** | 通用类（如 Result、ResultCode） |
| **config/** | 配置类（安全、CORS、飞书等） |
| **controller/** | REST 控制器（与前端 API 对应） |
| **entity/** | 实体类（与表对应） |
| **exception/** | 全局异常处理 |
| **mapper/** | MyBatis Mapper 接口 |
| **service/** | 业务服务层 |
| **util/** | 工具类（JWT、飞书等） |
| **src/main/resources/application*.yml** | 应用配置（含 MySQL、Redis、飞书等） |
| **src/main/resources/db/migration/** | Flyway 迁移脚本（可指向 db/flyway 或本地副本） |
| **src/main/resources/mapper/** | MyBatis XML 映射文件 |

---

## lyedu-api-python/ — 后端 API（Python，FastAPI）

| 文件/目录 | 作用 |
|-----------|------|
| **main.py** | FastAPI 应用入口；启动时子进程执行 Alembic 迁移，再挂载路由 |
| **config.py** | 配置（MySQL、JWT、飞书、上传路径等，与 Java 配置对齐） |
| **db.py** | MySQL 连接（pymysql） |
| **requirements.txt** | Python 依赖（FastAPI、uvicorn、pymysql、alembic 等） |
| **alembic.ini** | Alembic 配置（script_location 指向仓库根 db/alembic） |
| **.env.example** | 环境变量示例（MYSQL_* 等，供复制为 .env） |
| **Dockerfile** | 构建 Python API 镜像（需在仓库根构建，含 db/alembic） |
| **docker-entrypoint.sh** | 容器入口：等 MySQL 就绪 → alembic upgrade head → uvicorn |
| **install.ps1** / **install.bat** | Windows 下安装依赖与虚拟环境 |
| **start.ps1** / **start.sh** | 先执行 Alembic 迁移再启动 uvicorn |
| **routers/** | 路由模块（与 Java Controller 对应） |
| **auth.py** | 登录、飞书回调、JWT |
| **course.py** / **chapter.py** / **video.py** | 课程、章节、视频接口 |
| **user.py** / **department.py** | 用户、部门接口 |
| **learning.py** | 学习进度、视频进度 |
| **knowledge.py** / **question.py** / **paper.py** / **exam.py** / **exam_record.py** | 知识库、试题、试卷、考试、考试记录 |
| **certificate.py** / **certificate_template.py** / **user_certificate.py** | 证书、模板、用户证书 |
| **task.py** / **user_task.py** | 培训任务、用户任务 |
| **config.py** | 系统配置接口 |
| **point.py** / **point_rule.py** | 积分、积分规则 |
| **image.py** | 图片库上传/列表/删除 |
| **stats.py** | 统计与导出 |
| **services/** | 业务逻辑层（每个 router 对应若干 service） |
| **models/schemas.py** | Pydantic 请求/响应模型 |
| **common/result.py** | 统一响应结构 |
| **util/jwt_util.py** | JWT 生成与校验 |
| **util/feishu_api.py** | 飞书 API 调用 |
| **alembic/** | 本地 Alembic 占位（实际迁移在 db/alembic） |

---

## lyedu-admin/ — 管理后台前端（Vue3 + Element Plus）

| 文件/目录 | 作用 |
|-----------|------|
| **package.json** / **package-lock.json** | 依赖与脚本 |
| **vite.config.ts** | Vite 配置（代理、构建） |
| **tsconfig.json** / **tsconfig.node.json** | TypeScript 配置 |
| **index.html** | 入口 HTML |
| **Dockerfile** / **nginx.conf** | 构建与生产 nginx 配置 |
| **public/** | 静态资源（favicon、图片等） |
| **src/main.ts** | 应用入口 |
| **src/App.vue** | 根组件 |
| **src/router/index.ts** | 路由与菜单对应 |
| **src/utils/request.ts** | Axios 封装、baseURL、鉴权 |
| **src/components/Layout.vue** | 后台布局（侧栏菜单、顶栏、内容区） |
| **src/components/ChunkUpload.vue** | 分片上传组件 |
| **src/api/*.ts** | 各模块 API 封装（user、course、exam、config 等） |
| **src/views/Login.vue** | 登录页 |
| **src/views/Dashboard.vue** | 仪表盘 |
| **src/views/User.vue** / **Department.vue** | 用户、部门管理 |
| **src/views/Course.vue** / **Chapter.vue** / **Video.vue** | 课程、章节、视频管理 |
| **src/views/Question.vue** / **Paper.vue** / **Exam.vue** | 试题、试卷、考试管理 |
| **src/views/Knowledge.vue** | 知识库管理 |
| **src/views/Task.vue** | 培训任务管理 |
| **src/views/Certificate.vue** / **CertificateTemplate.vue** | 证书与模板 |
| **src/views/PointRule.vue** | 积分规则 |
| **src/views/ImageLibrary.vue** | 图片库 |
| **src/views/Settings.vue** | 系统设置 |
| **src/style.css** | 全局样式 |

---

## lyedu-pc/ — PC 端学员前端（Vue3 + Element Plus）

| 文件/目录 | 作用 |
|-----------|------|
| **package.json** / **vite.config.ts** / **tsconfig.json** 等 | 同管理后台，为 PC 端独立工程 |
| **.env.example** | 环境变量示例（API 地址等） |
| **src/router/index.ts** | PC 端路由（登录、首页、课程、学习、考试、任务、证书等） |
| **src/utils/auth.ts** | 登录态、token 存储与校验 |
| **src/utils/request.ts** | 请求封装与鉴权 |
| **src/api/*.ts** | 学员端 API（auth、course、learning、exam、task、point 等） |
| **src/views/Login.vue** | 登录页 |
| **src/views/Home.vue** | 首页 |
| **src/views/Courses.vue** / **CourseDetail.vue** | 课程列表与详情 |
| **src/views/VideoPlayer.vue** | 视频播放（含防拖拽/禁倍速） |
| **src/views/MyLearning.vue** | 我的学习 |
| **src/views/ExamList.vue** / **ExamTake.vue** / **ExamResult.vue** | 考试列表、答题、结果 |
| **src/views/TaskList.vue** / **TaskDetail.vue** | 任务列表与详情 |
| **src/views/MyCertificates.vue** / **CertificatePrint.vue** | 我的证书、证书打印 |
| **src/views/MyPoints.vue** | 我的积分 |
| **src/views/KnowledgeCenter.vue** / **DocumentPreview.vue** | 知识中心、文档预览 |

---

## lyedu-h5/ — H5 移动端学员前端（Vue3 + Vant）

| 文件/目录 | 作用 |
|-----------|------|
| **package.json** / **vite.config.ts** 等 | H5 独立工程 |
| **src/router/index.ts** | H5 路由（含底部 Tab：首页、课程、我的） |
| **src/views/MainLayout.vue** | 主布局（底部 Tab 栏常驻） |
| **src/views/Home.vue** / **Courses.vue** / **My.vue** | Tab 对应页面 |
| **src/views/Login.vue** | 登录 |
| **src/views/CourseDetail.vue** / **VideoPlayer.vue** | 课程详情、视频播放 |
| **src/views/MyLearning.vue** | 我的学习 |
| **src/views/KnowledgeCenter.vue** | 知识中心 |
| **src/api/** | H5 端 API 封装 |
| **src/utils/auth.ts** / **request.ts** | 鉴权与请求 |

---

## lyedu-entry/ — 统一入口（可选）

| 文件/目录 | 作用 |
|-----------|------|
| **ENTRY_CONFIG.md** | 统一入口配置说明 |
| **.env.example** | 环境变量示例 |
| **index.html** / **src/App.vue** 等 | 简单入口页，可跳转到 admin/pc/h5 或登录选择端 |

---

## 小结

- **根目录**：Compose、构建脚本、README、许可证。  
- **db/**：与 Flyway/Alembic 同源的迁移脚本，Java 用 Flyway，Python 用 Alembic。  
- **docker/**：MySQL 容器初始化 SQL。  
- **docs/**：结构、部署、功能、飞书、JDK/Gradle、支持等文档。  
- **lyedu-api/**：Java 后端（SpringBoot、MyBatis、Flyway）。  
- **lyedu-api-python/**：Python 后端（FastAPI、Alembic 自动迁移）。  
- **lyedu-admin/**：管理后台（课程、考试、用户、配置等）。  
- **lyedu-pc/**：PC 学员端（学习、考试、任务、证书、积分）。  
- **lyedu-h5/**：H5 学员端（精简功能、底部 Tab）。  
- **lyedu-entry/**：可选统一入口。

更多细节可参考 **README.md** 与 **docs/PROJECT_STRUCTURE.md**。
