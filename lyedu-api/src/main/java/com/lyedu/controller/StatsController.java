package com.lyedu.controller;

import com.lyedu.common.Result;
import com.lyedu.service.StatsService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 数据统计与导出
 */
@RestController
@RequestMapping("/stats")
@RequiredArgsConstructor
public class StatsController {

    private final StatsService statsService;

    @GetMapping("/overview")
    public Result<Map<String, Long>> overview() {
        return Result.success(statsService.overview());
    }

    @GetMapping("/learning-rank")
    public Result<List<Map<String, Object>>> learningRank(@RequestParam(defaultValue = "20") int limit) {
        return Result.success(statsService.learningRank(limit));
    }

    @GetMapping("/resource")
    public Result<Map<String, Long>> resource() {
        return Result.success(statsService.resourceStats());
    }

    @GetMapping("/export/learners")
    public Result<List<Map<String, Object>>> exportLearners() {
        return Result.success(statsService.exportLearners());
    }

    @GetMapping("/export/learning")
    public Result<List<Map<String, Object>>> exportLearning() {
        return Result.success(statsService.exportLearning());
    }

    @GetMapping("/export/department-learning")
    public Result<List<Map<String, Object>>> exportDepartmentLearning() {
        return Result.success(statsService.exportDepartmentLearning());
    }

    /**
     * 学员信息导出为 CSV 文件下载
     */
    @GetMapping(value = "/export/learners.csv", produces = "text/csv;charset=UTF-8")
    public ResponseEntity<byte[]> downloadLearnersCsv() {
        List<Map<String, Object>> rows = statsService.exportLearners();
        byte[] csv = buildCsv(
                new String[]{"id","username","realName","email","mobile","role","status","departmentName","createTime"},
                rows,
                "学员信息"
        );
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=learners.csv")
                .contentType(MediaType.parseMediaType("text/csv;charset=UTF-8"))
                .body(csv);
    }

    /**
     * 学习记录导出为 CSV
     */
    @GetMapping(value = "/export/learning.csv", produces = "text/csv;charset=UTF-8")
    public ResponseEntity<byte[]> downloadLearningCsv() {
        List<Map<String, Object>> rows = statsService.exportLearning();
        byte[] csv = buildCsv(
                new String[]{"userId","realName","username","courseId","courseTitle","progress","completeStatus","joinTime","updateTime"},
                rows,
                "学习记录"
        );
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=learning.csv")
                .contentType(MediaType.parseMediaType("text/csv;charset=UTF-8"))
                .body(csv);
    }

    /**
     * 部门学习统计导出为 CSV
     */
    @GetMapping(value = "/export/department-learning.csv", produces = "text/csv;charset=UTF-8")
    public ResponseEntity<byte[]> downloadDepartmentLearningCsv() {
        List<Map<String, Object>> rows = statsService.exportDepartmentLearning();
        byte[] csv = buildCsv(
                new String[]{"departmentId","departmentName","userCount","completedUserCount","learningRecordCount"},
                rows,
                "部门学习统计"
        );
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=department-learning.csv")
                .contentType(MediaType.parseMediaType("text/csv;charset=UTF-8"))
                .body(csv);
    }

    private static byte[] buildCsv(String[] headers, List<Map<String, Object>> rows, String title) {
        StringBuilder sb = new StringBuilder();
        sb.append("\uFEFF"); // BOM for Excel UTF-8
        sb.append(String.join(",", headers)).append("\n");
        for (Map<String, Object> row : rows) {
            String line = java.util.Arrays.stream(headers)
                    .map(h -> escapeCsvField(row.get(h)))
                    .collect(Collectors.joining(","));
            sb.append(line).append("\n");
        }
        return sb.toString().getBytes(StandardCharsets.UTF_8);
    }

    private static String escapeCsvField(Object v) {
        if (v == null) return "";
        String s = v.toString().trim();
        if (s.contains(",") || s.contains("\"") || s.contains("\n")) {
            return "\"" + s.replace("\"", "\"\"") + "\"";
        }
        return s;
    }
}
