package com.lyedu.controller;

import com.lyedu.common.Result;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

/**
 * 测试控制器
 *
 * @author LyEdu Team
 */
@RestController
@RequestMapping("/hello")
public class HelloController {

    @GetMapping
    public Result<Map<String, Object>> hello() {
        Map<String, Object> data = new HashMap<>();
        data.put("message", "欢迎使用 LyEdu 企业培训系统！");
        data.put("version", "1.0.0");
        data.put("author", "LyEdu Team");
        return Result.success(data);
    }
}
