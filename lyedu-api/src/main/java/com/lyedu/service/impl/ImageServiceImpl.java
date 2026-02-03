package com.lyedu.service.impl;

import com.lyedu.common.PageResult;
import com.lyedu.entity.Image;
import com.lyedu.service.ImageService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.jdbc.support.KeyHolder;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.UUID;

/**
 * 图片库服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class ImageServiceImpl implements ImageService {

    private static final DateTimeFormatter DIR_FORMAT = DateTimeFormatter.ofPattern("yyyy/MM");
    private static final List<String> ALLOWED_EXT = List.of("jpg", "jpeg", "png", "gif", "webp");

    private final JdbcTemplate jdbcTemplate;

    @Value("${lyedu.upload.path:./uploads}")
    private String uploadPath;

    @Override
    public Image upload(MultipartFile file) {
        if (file == null || file.isEmpty()) throw new IllegalArgumentException("File is empty");
        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null || originalFilename.isBlank()) throw new IllegalArgumentException("File name is empty");
        String ext = getExtension(originalFilename);
        if (!ALLOWED_EXT.contains(ext.toLowerCase())) throw new IllegalArgumentException("Only image types allowed: jpg, png, gif, webp");

        String subDir = LocalDateTime.now().format(DIR_FORMAT);
        String fileName = UUID.randomUUID().toString().replace("-", "") + "." + ext;
        String relativePath = subDir + "/" + fileName;
        Path fullPath = Paths.get(uploadPath, "images", subDir);

        try {
            Files.createDirectories(fullPath);
            Path targetFile = fullPath.resolve(fileName);
            try (InputStream in = file.getInputStream()) {
                Files.copy(in, targetFile);
            }
        } catch (Exception e) {
            throw new RuntimeException("Failed to save image", e);
        }

        String sql = "INSERT INTO ly_image (name, path, file_size) VALUES (?, ?, ?)";
        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(con -> {
            PreparedStatement ps = con.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
            ps.setString(1, originalFilename);
            ps.setString(2, relativePath);
            ps.setLong(3, file.getSize());
            return ps;
        }, keyHolder);
        Number key = keyHolder.getKey();
        if (key == null) throw new RuntimeException("Failed to insert image record");

        Image img = new Image();
        img.setId(key.longValue());
        img.setName(originalFilename);
        img.setPath(relativePath);
        img.setFileSize(file.getSize());
        img.setCreateTime(LocalDateTime.now());
        return img;
    }

    @Override
    public PageResult<Image> page(int page, int size, String keyword) {
        StringBuilder where = new StringBuilder(" WHERE 1=1 ");
        List<Object> params = new java.util.ArrayList<>();
        if (keyword != null && !keyword.trim().isEmpty()) {
            where.append(" AND name LIKE ? ");
            params.add("%" + keyword.trim() + "%");
        }
        String countSql = "SELECT COUNT(*) FROM ly_image " + where;
        Long total = jdbcTemplate.queryForObject(countSql, Long.class, params.toArray());

        int offset = (page - 1) * size;
        String listSql = "SELECT id, name, path, file_size, create_time FROM ly_image " + where + " ORDER BY id DESC LIMIT ? OFFSET ?";
        params.add(size);
        params.add(offset);
        List<Image> records = jdbcTemplate.query(listSql, new ImageRowMapper(), params.toArray());

        return new PageResult<>(records, total != null ? total : 0L, (long) page, (long) size);
    }

    @Override
    public void deleteById(Long id) {
        if (id == null) return;
        Image img = jdbcTemplate.query("SELECT id, name, path, file_size, create_time FROM ly_image WHERE id = ?",
                new ImageRowMapper(), id).stream().findFirst().orElse(null);
        if (img != null && img.getPath() != null) {
            Path file = Paths.get(uploadPath, "images", img.getPath());
            try {
                Files.deleteIfExists(file);
            } catch (Exception ignored) { }
        }
        jdbcTemplate.update("DELETE FROM ly_image WHERE id = ?", id);
    }

    @Override
    public String getUrl(String path) {
        if (path == null || path.isBlank()) return "";
        return "/uploads/images/" + path;
    }

    private static String getExtension(String filename) {
        int i = filename.lastIndexOf('.');
        return i > 0 ? filename.substring(i + 1) : "jpg";
    }

    private static class ImageRowMapper implements RowMapper<Image> {
        @Override
        public Image mapRow(ResultSet rs, int rowNum) throws SQLException {
            Image img = new Image();
            img.setId(rs.getLong("id"));
            img.setName(rs.getString("name"));
            img.setPath(rs.getString("path"));
            img.setFileSize(rs.getObject("file_size", Long.class));
            img.setCreateTime(rs.getObject("create_time", LocalDateTime.class));
            return img;
        }
    }
}
