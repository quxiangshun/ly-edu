package com.lyedu.controller;

import com.lyedu.annotation.NoAuth;
import com.lyedu.common.Result;
import com.lyedu.entity.FileUpload;
import com.lyedu.service.FileUploadService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.util.List;
import java.util.UUID;

/**
 * 文件上传控制器（支持分片上传和断点续传）
 *
 * @author LyEdu Team
 */
@RestController
@RequestMapping("/upload")
@RequiredArgsConstructor
public class FileUploadController {

    private final FileUploadService fileUploadService;

    @Value("${lyedu.upload.chunk-size:5242880}")
    private Long defaultChunkSize; // 默认分片大小 5MB

    /**
     * 初始化文件上传
     */
    @PostMapping("/init")
    public Result<InitUploadResponse> initUpload(@RequestBody InitUploadRequest request) {
        String fileId = request.getFileId();
        if (fileId == null || fileId.isEmpty()) {
            // 如果没有提供 fileId，生成一个（基于文件名和大小）
            fileId = generateFileId(request.getFileName(), request.getFileSize());
        }
        
        Long chunkSize = request.getChunkSize() != null ? request.getChunkSize() : defaultChunkSize;
        FileUpload upload = fileUploadService.initUpload(
                fileId,
                request.getFileName(),
                request.getFileSize(),
                request.getFileType(),
                chunkSize
        );
        
        InitUploadResponse response = new InitUploadResponse();
        response.setFileId(upload.getFileId());
        response.setChunkSize(upload.getChunkSize());
        response.setTotalChunks(upload.getTotalChunks());
        response.setUploadedChunks(fileUploadService.getUploadedChunks(fileId));
        
        return Result.success(response);
    }

    /**
     * 获取上传进度
     */
    @GetMapping("/progress/{fileId}")
    public Result<UploadProgressResponse> getProgress(@PathVariable String fileId) {
        FileUpload upload = fileUploadService.getUploadProgress(fileId);
        if (upload == null) {
            return Result.error(404, "Upload record not found");
        }
        
        List<Integer> uploadedChunks = fileUploadService.getUploadedChunks(fileId);
        
        UploadProgressResponse response = new UploadProgressResponse();
        response.setFileId(upload.getFileId());
        response.setFileName(upload.getFileName());
        response.setFileSize(upload.getFileSize());
        response.setTotalChunks(upload.getTotalChunks());
        response.setUploadedChunks(uploadedChunks.size());
        response.setUploadedChunkIndexes(uploadedChunks);
        response.setStatus(upload.getStatus());
        response.setProgress((double) uploadedChunks.size() / upload.getTotalChunks() * 100);
        
        return Result.success(response);
    }

    /**
     * 上传分片
     */
    @PostMapping("/chunk")
    public Result<Void> uploadChunk(
            @RequestParam("fileId") String fileId,
            @RequestParam("chunkIndex") Integer chunkIndex,
            @RequestParam("chunkSize") Long chunkSize,
            @RequestParam("file") MultipartFile file) {
        
        try (InputStream inputStream = file.getInputStream()) {
            boolean success = fileUploadService.uploadChunk(fileId, chunkIndex, chunkSize, inputStream);
            if (success) {
                return Result.success();
            } else {
                return Result.error(500, "Failed to upload chunk");
            }
        } catch (IOException e) {
            return Result.error(500, "Failed to read chunk data: " + e.getMessage());
        }
    }

    /**
     * 合并分片
     */
    @PostMapping("/merge/{fileId}")
    public Result<MergeResponse> mergeChunks(@PathVariable String fileId) {
        try {
            String filePath = fileUploadService.mergeChunks(fileId);
            MergeResponse response = new MergeResponse();
            response.setFileId(fileId);
            response.setFilePath(filePath);
            response.setUrl("/uploads/" + filePath); // 相对URL
            return Result.success(response);
        } catch (Exception e) {
            return Result.error(500, "Failed to merge chunks: " + e.getMessage());
        }
    }

    /**
     * 取消上传（删除上传记录和临时文件）
     */
    @DeleteMapping("/{fileId}")
    public Result<Void> cancelUpload(@PathVariable String fileId) {
        fileUploadService.deleteUpload(fileId);
        return Result.success();
    }

    /**
     * 生成文件ID（基于文件名和大小）
     */
    private String generateFileId(String fileName, Long fileSize) {
        return UUID.randomUUID().toString().replace("-", "");
    }

    @Data
    public static class InitUploadRequest {
        private String fileId;
        private String fileName;
        private Long fileSize;
        private String fileType;
        private Long chunkSize;
    }

    @Data
    public static class InitUploadResponse {
        private String fileId;
        private Long chunkSize;
        private Integer totalChunks;
        private List<Integer> uploadedChunks;
    }

    @Data
    public static class UploadProgressResponse {
        private String fileId;
        private String fileName;
        private Long fileSize;
        private Integer totalChunks;
        private Integer uploadedChunks;
        private List<Integer> uploadedChunkIndexes;
        private Integer status;
        private Double progress;
    }

    @Data
    public static class MergeResponse {
        private String fileId;
        private String filePath;
        private String url;
    }
}
