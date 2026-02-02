# 项目结构说明

## 目录结构

```
lyedu/
├── lyedu-api/              # 后端 API 服务
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/lyedu/
│   │   │   │   ├── annotation/      # 自定义注解
│   │   │   │   ├── common/          # 通用类（Result, ResultCode等）
│   │   │   │   ├── config/          # 配置类
│   │   │   │   ├── controller/      # 控制器
│   │   │   │   ├── entity/          # 实体类
│   │   │   │   ├── exception/       # 异常处理
│   │   │   │   ├── mapper/          # MyBatis Mapper
│   │   │   │   ├── service/         # 业务服务层
│   │   │   │   └── util/            # 工具类
│   │   │   └── resources/
│   │   │       ├── application.yml  # 应用配置
│   │   │       └── mapper/          # MyBatis XML
│   │   └── test/                    # 测试代码
│   ├── pom.xml                      # Maven 配置
│   └── Dockerfile                   # Docker 构建文件
│
├── lyedu-admin/            # 管理后台前端
│   ├── src/
│   │   ├── api/            # API 接口
│   │   ├── assets/         # 静态资源
│   │   ├── components/     # 组件
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── utils/          # 工具函数
│   │   ├── views/          # 页面组件
│   │   ├── App.vue         # 根组件
│   │   └── main.ts         # 入口文件
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── Dockerfile
│
├── lyedu-pc/               # PC 端前端
│   ├── src/
│   │   ├── api/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── router/
│   │   ├── stores/
│   │   ├── utils/
│   │   ├── views/
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
│
├── lyedu-h5/               # H5 端前端
│   ├── src/
│   │   ├── api/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── router/
│   │   ├── stores/
│   │   ├── utils/
│   │   ├── views/
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
│
├── docker/                  # Docker 相关文件
│   └── mysql/
│       └── init.sql        # 数据库初始化脚本
│
├── compose.yml              # Docker Compose 配置
├── .env.example             # 环境变量示例
├── .gitignore              # Git 忽略文件
├── .dockerignore           # Docker 忽略文件
├── README.md               # 项目说明
├── LICENSE                 # 许可证
└── CHANGELOG.md            # 更新日志
```

## 技术选型说明

### 后端技术栈
- **SpringBoot 4**: 最新版本的 Spring Boot 框架
- **JDK 25**: 最新版本的 Java 开发工具包
- **MyBatis Plus**: 增强的 MyBatis 框架，简化数据库操作
- **MySQL**: 关系型数据库
- **Redis**: 缓存数据库
- **JWT**: 无状态身份认证

### 前端技术栈
- **Vue 3**: 渐进式 JavaScript 框架
- **TypeScript**: 类型安全的 JavaScript 超集
- **Vite**: 下一代前端构建工具
- **Element Plus**: PC 端 UI 组件库（管理后台、PC 端）
- **Vant**: 移动端 UI 组件库（H5 端）
- **Pinia**: Vue 3 状态管理库
- **Vue Router**: Vue 官方路由管理器
- **Axios**: HTTP 客户端

## 开发规范

### 命名规范
- 类名：大驼峰命名（PascalCase），如 `UserController`
- 方法名：小驼峰命名（camelCase），如 `getUserInfo`
- 常量：全大写下划线分隔，如 `MAX_SIZE`
- 包名：全小写，如 `com.lyedu.controller`

### 代码规范
- 使用 4 个空格缩进
- 每行代码不超过 120 个字符
- 类和方法必须添加注释
- 使用 Lombok 简化实体类代码

### Git 提交规范
- feat: 新功能
- fix: 修复 bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建/工具相关

## 部署说明

### Docker 部署
使用 Docker Compose 一键部署所有服务：
```bash
docker-compose up -d
```

### 本地开发
1. 启动 MySQL 和 Redis
2. 运行后端服务（SpringBoot）
3. 运行前端服务（Vite dev server）

## 注意事项

1. **完全原创**：本项目所有代码均为原创，不包含任何第三方项目的代码
2. **图标使用**：前端图标使用 Iconify 开源图标库
3. **数据库初始化**：首次运行会自动执行初始化脚本
4. **环境变量**：生产环境请修改 `.env` 文件中的敏感信息
