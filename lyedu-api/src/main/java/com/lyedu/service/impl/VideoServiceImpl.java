package com.lyedu.service.impl;

import com.lyedu.entity.Video;
import com.lyedu.service.VideoService;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Service;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

/**
 * 视频服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class VideoServiceImpl implements VideoService {

    private final JdbcTemplate jdbcTemplate;

    @Override
    public List<Video> listByCourseId(Long courseId) {
        String sql = "SELECT id, course_id, chapter_id, title, url, duration, sort, create_time, update_time, deleted " +
                "FROM ly_video WHERE course_id = ? AND deleted = 0 ORDER BY sort ASC, id ASC";
        return jdbcTemplate.query(sql, new Object[]{courseId}, new VideoRowMapper());
    }

    @Override
    public List<Video> listByChapterId(Long chapterId) {
        String sql = "SELECT id, course_id, chapter_id, title, url, duration, sort, create_time, update_time, deleted " +
                "FROM ly_video WHERE chapter_id = ? AND deleted = 0 ORDER BY sort ASC, id ASC";
        return jdbcTemplate.query(sql, new Object[]{chapterId}, new VideoRowMapper());
    }

    @Override
    public Video getById(Long id) {
        String sql = "SELECT id, course_id, chapter_id, title, url, duration, sort, create_time, update_time, deleted " +
                "FROM ly_video WHERE id = ? AND deleted = 0";
        List<Video> list = jdbcTemplate.query(sql, new Object[]{id}, new VideoRowMapper());
        return list.isEmpty() ? null : list.get(0);
    }

    @Override
    public void save(Video video) {
        String sql = "INSERT INTO ly_video (course_id, chapter_id, title, url, duration, sort) VALUES (?, ?, ?, ?, ?, ?)";
        jdbcTemplate.update(sql,
                video.getCourseId(),
                video.getChapterId(),
                video.getTitle(),
                video.getUrl(),
                video.getDuration() != null ? video.getDuration() : 0,
                video.getSort() != null ? video.getSort() : 0);
    }

    @Override
    public void update(Video video) {
        String sql = "UPDATE ly_video SET course_id = ?, chapter_id = ?, title = ?, url = ?, duration = ?, sort = ? WHERE id = ? AND deleted = 0";
        jdbcTemplate.update(sql,
                video.getCourseId(),
                video.getChapterId(),
                video.getTitle(),
                video.getUrl(),
                video.getDuration(),
                video.getSort(),
                video.getId());
    }

    @Override
    public void delete(Long id) {
        String sql = "UPDATE ly_video SET deleted = 1 WHERE id = ?";
        jdbcTemplate.update(sql, id);
    }

    private static class VideoRowMapper implements RowMapper<Video> {
        @Override
        public Video mapRow(ResultSet rs, int rowNum) throws SQLException {
            Video video = new Video();
            video.setId(rs.getLong("id"));
            video.setCourseId(rs.getLong("course_id"));
            Long chapterId = rs.getLong("chapter_id");
            if (!rs.wasNull()) {
                video.setChapterId(chapterId);
            }
            video.setTitle(rs.getString("title"));
            video.setUrl(rs.getString("url"));
            video.setDuration(rs.getInt("duration"));
            video.setSort(rs.getInt("sort"));
            return video;
        }
    }
}
