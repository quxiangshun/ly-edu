package com.lyedu.service.impl;

import com.lyedu.entity.UserVideoProgress;
import com.lyedu.service.UserVideoProgressService;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Service;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

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
        String checkSql = "SELECT COUNT(*) FROM ly_user_video_progress WHERE user_id = ? AND video_id = ?";
        Integer count = jdbcTemplate.queryForObject(checkSql, new Object[]{userId, videoId}, Integer.class);
        
        Integer isFinished = (progress != null && duration != null && progress >= duration * 0.9) ? 1 : 0;
        
        if (count == 0) {
            String insertSql = "INSERT INTO ly_user_video_progress (user_id, video_id, progress, duration, is_finished) VALUES (?, ?, ?, ?, ?)";
            jdbcTemplate.update(insertSql, userId, videoId, progress, duration, isFinished);
        } else {
            String updateSql = "UPDATE ly_user_video_progress SET progress = ?, duration = ?, is_finished = ? WHERE user_id = ? AND video_id = ?";
            jdbcTemplate.update(updateSql, progress, duration, isFinished, userId, videoId);
        }
    }

    @Override
    public UserVideoProgress getByUserAndVideo(Long userId, Long videoId) {
        String sql = "SELECT id, user_id, video_id, progress, duration, is_finished, create_time, update_time " +
                "FROM ly_user_video_progress WHERE user_id = ? AND video_id = ?";
        List<UserVideoProgress> list = jdbcTemplate.query(sql, new Object[]{userId, videoId}, new UserVideoProgressRowMapper());
        return list.isEmpty() ? null : list.get(0);
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
