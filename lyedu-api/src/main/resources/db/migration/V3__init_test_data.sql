-- Flyway V3: 初始化测试数据

-- 插入测试部门
INSERT INTO `ly_department` (`name`, `parent_id`, `sort`, `status`) VALUES
('技术部', 0, 1, 1),
('产品部', 0, 2, 1),
('运营部', 0, 3, 1)
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- 插入测试课程
INSERT INTO `ly_course` (`title`, `cover`, `description`, `status`, `sort`) VALUES
('Java 基础教程', 'https://via.placeholder.com/300x200?text=Java', 'Java 编程语言基础入门课程，适合零基础学员', 1, 1),
('Vue3 前端开发', 'https://via.placeholder.com/300x200?text=Vue3', 'Vue3 框架学习，包含组合式 API 和 TypeScript', 1, 2),
('SpringBoot 实战', 'https://via.placeholder.com/300x200?text=SpringBoot', 'SpringBoot 企业级应用开发实战', 1, 3),
('MySQL 数据库', 'https://via.placeholder.com/300x200?text=MySQL', 'MySQL 数据库设计与优化', 1, 4),
('Docker 容器化', 'https://via.placeholder.com/300x200?text=Docker', 'Docker 容器化部署实践', 1, 5),
('Linux 系统管理', 'https://via.placeholder.com/300x200?text=Linux', 'Linux 系统管理与运维', 1, 6)
ON DUPLICATE KEY UPDATE title = VALUES(title);
