package com.lyedu.service.impl;

import com.lyedu.entity.UserVideoProgress;
import com.lyedu.service.UserVideoProgressService;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Service;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDateTime;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 用户视频学习进度服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class UserVideoProgressServiceImpl implements UserVideoProgressService {

    private final JdbcTemplate jdbcTemplate;

    @Override
    public void updateProgress(Long userId, Long videoId, Integer progress, Integer duration) {
        String checkSql = "SELECT COUNT(*) FROM `ly_user_video_progress` WHERE `user_id` = ? AND `video_id` = ?";
        Integer count = jdbcTemplate.queryForObject(checkSql, new Object[]{userId, videoId}, Integer.class);
        
        Integer isFinished = (progress != null && duration != null && progress >= duration * 0.9) ? 1 : 0;
        
        if (count == 0) {
            String insertSql = "INSERT INTO `ly_user_video_progress` (`user_id`, `video_id`, `progress`, `duration`, `is_finished`) VALUES (?, ?, ?, ?, ?)";
            jdbcTemplate.update(insertSql, userId, videoId, progress, duration, isFinished);
        } else {
            String updateSql = "UPDATE `ly_user_video_progress` SET `progress` = ?, `duration` = ?, `is_finished` = ? WHERE `user_id` = ? AND `video_id` = ?";
            jdbcTemplate.update(updateSql, progress, duration, isFinished, userId, videoId);
        }
    }

    @Override
    public UserVideoProgress getByUserAndVideo(Long userId, Long videoId) {
        String sql = "SELECT `id`, `user_id`, `video_id`, `progress`, `duration`, `is_finished`, `create_time`, `update_time` " +
                "FROM `ly_user_video_progress` WHERE `user_id` = ? AND `video_id` = ?";
        List<UserVideoProgress> list = jdbcTemplate.query(sql, new Object[]{userId, videoId}, new UserVideoProgressRowMapper());
        return list.isEmpty() ? null : list.get(0);
    }

    @Override
    public Map<Long, UserVideoProgress> getProgressMap(Long userId, List<Long> videoIds) {
        if (videoIds == null || videoIds.isEmpty()) {
            return Collections.emptyMap();
        }
        StringBuilder in = new StringBuilder();
        for (int i = 0; i < videoIds.size(); i++) {
            if (i > 0) in.append(",");
            in.append("?");
        }
        String sql = "SELECT id, user_id, video_id, progress, duration, is_finished, create_time, update_time " +
                "FROM `ly_user_video_progress` WHERE `user_id` = ? AND `video_id` IN (" + in + ")";
        Object[] params = new Object[videoIds.size() + 1];
        params[0] = userId;
        for (int i = 0; i < videoIds.size(); i++) {
            params[i + 1] = videoIds.get(i);
        }
        List<UserVideoProgress> list = jdbcTemplate.query(sql, params, new UserVideoProgressRowMapper());
        Map<Long, UserVideoProgress> map = new HashMap<>();
        for (UserVideoProgress p : list) {
            map.put(p.getVideoId(), p);
        }
        return map;
    }

    @Override
    public void updateLastPlayPing(Long userId, Long videoId) {
        String sql = "UPDATE `ly_user_video_progress` SET `last_play_ping_at` = ? WHERE `user_id` = ? AND `video_id` = ?";
        jdbcTemplate.update(sql, LocalDateTime.now(), userId, videoId);
    }

    @Override
    public List<Long> listWatchedCourseIds(Long userId) {
        // 仅统计「真正看过」的课程：至少有一条视频进度 > 0 秒（排除仅点开未播放）
        // 使用子查询 + GROUP BY 避免 MySQL DISTINCT 与 ORDER BY 非 SELECT 列不兼容
        String sql = "SELECT t.`course_id` FROM (" +
                "SELECT v.`course_id`, MAX(uvp.`update_time`) AS last_time FROM `ly_user_video_progress` uvp " +
                "JOIN `ly_video` v ON uvp.`video_id` = v.`id` WHERE uvp.`user_id` = ? AND uvp.`progress` > 0 " +
                "GROUP BY v.`course_id`" +
                ") t ORDER BY t.`last_time` DESC";
        return jdbcTemplate.query(sql, (rs, rowNum) -> rs.getLong("course_id"), userId);
    }

    private static class UserVideoProgressRowMapper implements RowMapper<UserVideoProgress> {
        @Override
        public UserVideoProgress mapRow(ResultSet rs, int rowNum) throws SQLException {
            UserVideoProgress progress = new UserVideoProgress();
            progress.setId(rs.getLong("id"));
            progress.setUserId(rs.getLong("user_id"));
            progress.setVideoId(rs.getLong("video_id"));
            progress.setProgress(rs.getInt("progress"));
            progress.setDuration(rs.getInt("duration"));
            progress.setIsFinished(rs.getInt("is_finished"));
            progress.setCreateTime(rs.getTimestamp("create_time").toLocalDateTime());
            progress.setUpdateTime(rs.getTimestamp("update_time").toLocalDateTime());
            return progress;
        }
    }
}
