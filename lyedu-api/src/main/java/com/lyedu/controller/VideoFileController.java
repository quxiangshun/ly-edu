package com.lyedu.controller;

import com.lyedu.annotation.NoAuth;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.File;
import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * 视频文件服务控制器
 * 用于提供视频文件的流式传输，支持Range请求（断点续传）
 *
 * @author LyEdu Team
 */
@RestController
@RequestMapping("/uploads")
@RequiredArgsConstructor
public class VideoFileController {

    @Value("${lyedu.upload.path:./uploads}")
    private String uploadPath;

    /**
     * 获取视频文件
     * 支持Range请求，用于视频播放的断点续传
     */
    @NoAuth
    @GetMapping("/videos/**")
    public ResponseEntity<Resource> getVideoFile(jakarta.servlet.http.HttpServletRequest request) {
        try {
            // 获取请求路径（去掉 /api/uploads/videos/ 前缀）
            String requestURI = request.getRequestURI();
            String contextPath = request.getContextPath(); // /api
            String prefix = contextPath + "/uploads/videos/";
            
            if (!requestURI.startsWith(prefix)) {
                return ResponseEntity.notFound().build();
            }
            
            String relativePath = requestURI.substring(prefix.length());
            
            // 分割路径：fileId/filename
            String[] pathParts = relativePath.split("/", 2);
            if (pathParts.length < 2) {
                return ResponseEntity.notFound().build();
            }
            
            String fileId = pathParts[0];
            String encodedFileName = pathParts[1];
            
            // URL解码文件名
            String fileName = encodedFileName;
            try {
                // 尝试多次解码（处理多次编码的情况）
                String temp = URLDecoder.decode(encodedFileName, StandardCharsets.UTF_8.toString());
                // 如果解码后仍然包含编码字符，再次解码
                if (temp.contains("%")) {
                    fileName = URLDecoder.decode(temp, StandardCharsets.UTF_8.toString());
                } else {
                    fileName = temp;
                }
            } catch (Exception e) {
                // 如果解码失败，使用原始文件名
                fileName = encodedFileName;
            }
            
            // 构建完整文件路径
            Path filePath = Paths.get(uploadPath, "videos", fileId, fileName);
            File file = filePath.toFile();
            
            // 如果文件不存在，尝试在目录中查找任何mp4文件（处理文件名编码问题）
            if (!file.exists() || !file.isFile()) {
                File dir = Paths.get(uploadPath, "videos", fileId).toFile();
                if (dir.exists() && dir.isDirectory()) {
                    File[] files = dir.listFiles((d, name) -> name.toLowerCase().endsWith(".mp4"));
                    if (files != null && files.length > 0) {
                        file = files[0]; // 使用找到的第一个mp4文件
                    }
                }
            }
            
            if (!file.exists() || !file.isFile()) {
                return ResponseEntity.notFound().build();
            }
            
            // 确定Content-Type
            String contentType = determineContentType(file.getName());
            
            // 创建Resource
            Resource resource = new FileSystemResource(file);
            
            // 设置响应头
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.parseMediaType(contentType));
            headers.setContentLength(file.length());
            headers.set("Accept-Ranges", "bytes");
            headers.set("Cache-Control", "public, max-age=3600");
            
            // 处理Range请求（支持视频播放的断点续传）
            String rangeHeader = request.getHeader("Range");
            if (rangeHeader != null && rangeHeader.startsWith("bytes=")) {
                return handleRangeRequest(file, rangeHeader, contentType, headers);
            }
            
            return ResponseEntity.ok()
                    .headers(headers)
                    .body(resource);
                    
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.internalServerError().build();
        }
    }
    
    /**
     * 处理Range请求（支持视频播放的断点续传）
     */
    private ResponseEntity<Resource> handleRangeRequest(File file, String rangeHeader, String contentType, HttpHeaders headers) {
        try {
            long fileSize = file.length();
            String range = rangeHeader.substring(6); // 去掉 "bytes="
            String[] ranges = range.split("-");
            
            long start = 0;
            long end = fileSize - 1;
            
            if (ranges.length > 0 && !ranges[0].isEmpty()) {
                start = Long.parseLong(ranges[0]);
            }
            if (ranges.length > 1 && !ranges[1].isEmpty()) {
                end = Long.parseLong(ranges[1]);
            }
            
            if (start > end || start < 0 || end >= fileSize) {
                return ResponseEntity.status(416).build(); // Range Not Satisfiable
            }
            
            long contentLength = end - start + 1;
            headers.setContentLength(contentLength);
            headers.set("Content-Range", String.format("bytes %d-%d/%d", start, end, fileSize));
            
            Resource resource = new FileSystemResource(file);
            
            return ResponseEntity.status(206) // Partial Content
                    .headers(headers)
                    .body(resource);
                    
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
    
    /**
     * 根据文件名确定Content-Type
     */
    private String determineContentType(String fileName) {
        String lowerName = fileName.toLowerCase();
        if (lowerName.endsWith(".mp4")) {
            return "video/mp4";
        } else if (lowerName.endsWith(".webm")) {
            return "video/webm";
        } else if (lowerName.endsWith(".ogg")) {
            return "video/ogg";
        } else if (lowerName.endsWith(".jpg") || lowerName.endsWith(".jpeg")) {
            return "image/jpeg";
        } else if (lowerName.endsWith(".png")) {
            return "image/png";
        } else if (lowerName.endsWith(".gif")) {
            return "image/gif";
        }
        return "application/octet-stream";
    }
}
