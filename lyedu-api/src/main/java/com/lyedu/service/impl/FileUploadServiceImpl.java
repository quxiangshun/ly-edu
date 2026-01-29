package com.lyedu.service.impl;

import com.lyedu.entity.FileUpload;
import com.lyedu.service.FileUploadService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 文件上传服务实现
 *
 * @author LyEdu Team
 */
@Service
@RequiredArgsConstructor
public class FileUploadServiceImpl implements FileUploadService {

    private final JdbcTemplate jdbcTemplate;

    @Value("${lyedu.upload.path:./uploads}")
    private String uploadPath;

    private static final String SELECT_BY_FILE_ID_SQL =
            "SELECT id, file_id, file_name, file_size, file_type, chunk_size, total_chunks, uploaded_chunks, upload_path, status, create_time, update_time " +
            "FROM ly_file_upload WHERE file_id = ?";

    private static final String INSERT_UPLOAD_SQL =
            "INSERT INTO ly_file_upload (file_id, file_name, file_size, file_type, chunk_size, total_chunks, uploaded_chunks, upload_path, status) " +
            "VALUES (?, ?, ?, ?, ?, ?, 0, ?, 0)";

    private static final String UPDATE_UPLOAD_PROGRESS_SQL =
            "UPDATE ly_file_upload SET uploaded_chunks = uploaded_chunks + 1, status = CASE WHEN uploaded_chunks + 1 >= total_chunks THEN 1 ELSE 0 END WHERE file_id = ?";

    private static final String UPDATE_UPLOAD_PATH_SQL =
            "UPDATE ly_file_upload SET upload_path = ?, status = 1 WHERE file_id = ?";

    private static final String SELECT_UPLOADED_CHUNKS_SQL =
            "SELECT chunk_index FROM ly_file_chunk WHERE file_id = ? ORDER BY chunk_index";

    private static final String INSERT_CHUNK_SQL =
            "INSERT INTO ly_file_chunk (file_id, chunk_index, chunk_size, chunk_path) VALUES (?, ?, ?, ?)";

    private static final String DELETE_UPLOAD_SQL =
            "DELETE FROM ly_file_upload WHERE file_id = ?";

    private static final String DELETE_CHUNKS_SQL =
            "DELETE FROM ly_file_chunk WHERE file_id = ?";

    @Override
    @Transactional
    public FileUpload initUpload(String fileId, String fileName, Long fileSize, String fileType, Long chunkSize) {
        // 计算总分片数
        int totalChunks = (int) Math.ceil((double) fileSize / chunkSize);
        
        // 生成上传路径
        String relativePath = "videos/" + fileId + "/" + fileName;
        String fullPath = uploadPath + "/" + relativePath;
        
        // 创建目录
        try {
            Path dir = Paths.get(uploadPath, "videos", fileId, "chunks");
            Files.createDirectories(dir);
        } catch (IOException e) {
            throw new RuntimeException("Failed to create upload directory", e);
        }
        
        // 插入上传记录
        jdbcTemplate.update(INSERT_UPLOAD_SQL,
                fileId, fileName, fileSize, fileType, chunkSize, totalChunks, relativePath);
        
        return getUploadProgress(fileId);
    }

    @Override
    public FileUpload getUploadProgress(String fileId) {
        List<FileUpload> list = jdbcTemplate.query(SELECT_BY_FILE_ID_SQL, new Object[]{fileId}, new FileUploadRowMapper());
        return list.isEmpty() ? null : list.get(0);
    }

    @Override
    @Transactional
    public boolean uploadChunk(String fileId, Integer chunkIndex, Long chunkSize, InputStream inputStream) {
        try {
            // 检查是否已上传
            List<Integer> uploaded = getUploadedChunks(fileId);
            if (uploaded.contains(chunkIndex)) {
                return true; // 已上传，跳过
            }
            
            // 保存分片文件
            Path chunkDir = Paths.get(uploadPath, "videos", fileId, "chunks");
            Files.createDirectories(chunkDir);
            Path chunkFile = chunkDir.resolve(chunkIndex + ".chunk");
            
            // 写入分片数据
            try (FileOutputStream fos = new FileOutputStream(chunkFile.toFile());
                 BufferedOutputStream bos = new BufferedOutputStream(fos)) {
                byte[] buffer = new byte[8192];
                int bytesRead;
                while ((bytesRead = inputStream.read(buffer)) != -1) {
                    bos.write(buffer, 0, bytesRead);
                }
                bos.flush();
            }
            
            // 记录分片信息
            jdbcTemplate.update(INSERT_CHUNK_SQL,
                    fileId, chunkIndex, chunkSize, chunkFile.toString());
            
            // 更新上传进度
            jdbcTemplate.update(UPDATE_UPLOAD_PROGRESS_SQL, fileId);
            
            return true;
        } catch (IOException e) {
            throw new RuntimeException("Failed to upload chunk", e);
        }
    }

    @Override
    public List<Integer> getUploadedChunks(String fileId) {
        return jdbcTemplate.query(SELECT_UPLOADED_CHUNKS_SQL, new Object[]{fileId},
                (rs, rowNum) -> rs.getInt("chunk_index"));
    }

    @Override
    @Transactional
    public String mergeChunks(String fileId) {
        FileUpload upload = getUploadProgress(fileId);
        if (upload == null) {
            throw new RuntimeException("Upload record not found: " + fileId);
        }
        
        // 检查所有分片是否已上传
        List<Integer> uploaded = getUploadedChunks(fileId);
        if (uploaded.size() != upload.getTotalChunks()) {
            throw new RuntimeException("Not all chunks uploaded. Expected: " + upload.getTotalChunks() + ", Uploaded: " + uploaded.size());
        }
        
        try {
            // 合并文件路径
            Path mergedFile = Paths.get(uploadPath, upload.getUploadPath());
            Files.createDirectories(mergedFile.getParent());
            
            // 合并分片
            try (FileOutputStream fos = new FileOutputStream(mergedFile.toFile());
                 BufferedOutputStream bos = new BufferedOutputStream(fos)) {
                
                for (int i = 0; i < upload.getTotalChunks(); i++) {
                    Path chunkFile = Paths.get(uploadPath, "videos", fileId, "chunks", i + ".chunk");
                    if (!Files.exists(chunkFile)) {
                        throw new RuntimeException("Chunk file not found: " + chunkFile);
                    }
                    
                    try (FileInputStream fis = new FileInputStream(chunkFile.toFile());
                         BufferedInputStream bis = new BufferedInputStream(fis)) {
                        byte[] buffer = new byte[8192];
                        int bytesRead;
                        while ((bytesRead = bis.read(buffer)) != -1) {
                            bos.write(buffer, 0, bytesRead);
                        }
                    }
                }
                bos.flush();
            }
            
            // 删除分片文件
            Path chunkDir = Paths.get(uploadPath, "videos", fileId, "chunks");
            if (Files.exists(chunkDir)) {
                Files.walk(chunkDir)
                        .sorted((a, b) -> -a.compareTo(b))
                        .forEach(path -> {
                            try {
                                Files.delete(path);
                            } catch (IOException e) {
                                // Ignore
                            }
                        });
            }
            
            // 更新上传记录
            jdbcTemplate.update(UPDATE_UPLOAD_PATH_SQL, upload.getUploadPath(), fileId);
            
            return upload.getUploadPath();
        } catch (IOException e) {
            throw new RuntimeException("Failed to merge chunks", e);
        }
    }

    @Override
    @Transactional
    public void deleteUpload(String fileId) {
        FileUpload upload = getUploadProgress(fileId);
        if (upload != null) {
            // 删除文件
            try {
                if (upload.getUploadPath() != null) {
                    Path file = Paths.get(uploadPath, upload.getUploadPath());
                    if (Files.exists(file)) {
                        Files.delete(file);
                    }
                }
                // 删除分片目录
                Path chunkDir = Paths.get(uploadPath, "videos", fileId);
                if (Files.exists(chunkDir)) {
                    Files.walk(chunkDir)
                            .sorted((a, b) -> -a.compareTo(b))
                            .forEach(path -> {
                                try {
                                    Files.delete(path);
                                } catch (IOException e) {
                                    // Ignore
                                }
                            });
                }
            } catch (IOException e) {
                // Ignore
            }
        }
        
        // 删除数据库记录
        jdbcTemplate.update(DELETE_CHUNKS_SQL, fileId);
        jdbcTemplate.update(DELETE_UPLOAD_SQL, fileId);
    }

    private static class FileUploadRowMapper implements RowMapper<FileUpload> {
        @Override
        public FileUpload mapRow(ResultSet rs, int rowNum) throws SQLException {
            FileUpload upload = new FileUpload();
            upload.setId(rs.getLong("id"));
            upload.setFileId(rs.getString("file_id"));
            upload.setFileName(rs.getString("file_name"));
            upload.setFileSize(rs.getLong("file_size"));
            upload.setFileType(rs.getString("file_type"));
            upload.setChunkSize(rs.getLong("chunk_size"));
            upload.setTotalChunks(rs.getInt("total_chunks"));
            upload.setUploadedChunks(rs.getInt("uploaded_chunks"));
            upload.setUploadPath(rs.getString("upload_path"));
            upload.setStatus(rs.getInt("status"));
            return upload;
        }
    }
}
