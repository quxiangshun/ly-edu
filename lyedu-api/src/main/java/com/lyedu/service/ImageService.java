package com.lyedu.service;

import com.lyedu.common.PageResult;
import com.lyedu.entity.Image;
import org.springframework.web.multipart.MultipartFile;

/**
 * 图片库服务
 *
 * @author LyEdu Team
 */
public interface ImageService {

    /**
     * 上传图片，保存到 images/yyyy/MM/ 下，写入 ly_image
     *
     * @param file 图片文件
     * @return 图片记录，含 url（/uploads/images/ + path）
     */
    Image upload(MultipartFile file);

    /**
     * 分页列表
     */
    PageResult<Image> page(int page, int size, String keyword);

    /**
     * 按 ID 删除（同时删除文件）
     */
    void deleteById(Long id);

    /**
     * 获取访问 URL（相对路径）
     */
    String getUrl(String path);
}
