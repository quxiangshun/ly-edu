package com.lyedu.service;

import com.lyedu.entity.FileUpload;

import java.io.InputStream;
import java.util.List;

/**
 * 文件上传服务接口
 *
 * @author LyEdu Team
 */
public interface FileUploadService {

    /**
     * 初始化文件上传（创建上传记录）
     *
     * @param fileId 文件唯一标识
     * @param fileName 文件名
     * @param fileSize 文件大小
     * @param fileType 文件类型
     * @param chunkSize 分片大小
     * @return 文件上传记录
     */
    FileUpload initUpload(String fileId, String fileName, Long fileSize, String fileType, Long chunkSize);

    /**
     * 获取文件上传进度
     *
     * @param fileId 文件唯一标识
     * @return 文件上传记录，未找到返回 null
     */
    FileUpload getUploadProgress(String fileId);

    /**
     * 上传分片
     *
     * @param fileId 文件唯一标识
     * @param chunkIndex 分片索引（从0开始）
     * @param chunkSize 分片大小
     * @param inputStream 分片数据流
     * @return 是否成功
     */
    boolean uploadChunk(String fileId, Integer chunkIndex, Long chunkSize, InputStream inputStream);

    /**
     * 获取已上传的分片索引列表（用于断点续传）
     *
     * @param fileId 文件唯一标识
     * @return 已上传的分片索引列表
     */
    List<Integer> getUploadedChunks(String fileId);

    /**
     * 合并分片
     *
     * @param fileId 文件唯一标识
     * @return 合并后的文件路径
     */
    String mergeChunks(String fileId);

    /**
     * 删除文件上传记录和临时文件
     *
     * @param fileId 文件唯一标识
     */
    void deleteUpload(String fileId);
}
