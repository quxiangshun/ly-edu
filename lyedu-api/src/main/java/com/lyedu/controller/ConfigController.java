package com.lyedu.controller;

import com.lyedu.annotation.NoAuth;
import com.lyedu.common.Result;
import com.lyedu.entity.Config;
import com.lyedu.service.ConfigService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/config")
@RequiredArgsConstructor
public class ConfigController {

    private final ConfigService configService;

    @NoAuth
    @GetMapping("/key/{key}")
    public Result<String> getByKey(@PathVariable String key) {
        String value = configService.getByKey(key);
        return Result.success(value);
    }

    @NoAuth
    @GetMapping("/category/{category}")
    public Result<List<Config>> listByCategory(@PathVariable String category) {
        return Result.success(configService.listByCategory(category));
    }

    @GetMapping("/all")
    public Result<List<Config>> listAll() {
        return Result.success(configService.listAll());
    }

    @PostMapping("/set")
    public Result<Void> set(@RequestBody ConfigSetRequest body) {
        configService.set(body.getConfigKey(), body.getConfigValue(), body.getCategory(), body.getRemark());
        return Result.success();
    }

    @PostMapping("/batch")
    public Result<Void> batchSet(@RequestBody Map<String, String> map) {
        if (map != null) {
            for (Map.Entry<String, String> e : map.entrySet()) {
                if (e.getKey() != null && !e.getKey().isBlank()) {
                    configService.set(e.getKey(), e.getValue(), null, null);
                }
            }
        }
        return Result.success();
    }

    @Data
    public static class ConfigSetRequest {
        private String configKey;
        private String configValue;
        private String category;
        private String remark;
    }
}
