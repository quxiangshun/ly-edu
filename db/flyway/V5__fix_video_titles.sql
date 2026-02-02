-- Flyway V5: 修复视频标题乱码

UPDATE ly_video SET title = 'Java基础入门视频1：环境搭建与第一个程序' WHERE id = 1;
UPDATE ly_video SET title = 'Java基础入门视频2：变量与数据类型' WHERE id = 2;
UPDATE ly_video SET title = 'Java基础入门视频3：控制流程与循环' WHERE id = 3;
UPDATE ly_video SET title = 'Vue3入门视频1：项目创建与组件' WHERE id = 4;
UPDATE ly_video SET title = 'Vue3入门视频2：响应式数据' WHERE id = 5;
