package com.lyedu.controller;

import com.lyedu.common.PageResult;
import com.lyedu.common.Result;
import com.lyedu.entity.Image;
import com.lyedu.service.ImageService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 图片库：上传、列表、删除，用于课程封面等
 *
 * @author LyEdu Team
 */
@RestController
@RequestMapping("/image")
@RequiredArgsConstructor
public class ImageController {

    private final ImageService imageService;

    @PostMapping("/upload")
    public Result<Map<String, Object>> upload(@RequestParam("file") MultipartFile file) {
        Image img = imageService.upload(file);
        Map<String, Object> vo = new HashMap<>();
        vo.put("id", img.getId());
        vo.put("name", img.getName());
        vo.put("path", img.getPath());
        vo.put("url", imageService.getUrl(img.getPath()));
        vo.put("fileSize", img.getFileSize());
        vo.put("createTime", img.getCreateTime());
        return Result.success(vo);
    }

    @GetMapping("/page")
    public Result<PageResult<Map<String, Object>>> page(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String keyword) {
        PageResult<Image> pr = imageService.page(page, size, keyword);
        List<Map<String, Object>> list = pr.getRecords().stream().map(img -> {
            Map<String, Object> m = new HashMap<>();
            m.put("id", img.getId());
            m.put("name", img.getName());
            m.put("path", img.getPath());
            m.put("url", imageService.getUrl(img.getPath()));
            m.put("fileSize", img.getFileSize());
            m.put("createTime", img.getCreateTime());
            return m;
        }).collect(Collectors.toList());
        PageResult<Map<String, Object>> result = new PageResult<>(list, pr.getTotal(), pr.getCurrent(), pr.getSize());
        result.setPages(pr.getPages());
        return Result.success(result);
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        imageService.deleteById(id);
        return Result.success();
    }
}
