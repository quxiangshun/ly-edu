package com.lyedu.controller;

import com.lyedu.common.PageResult;
import com.lyedu.common.PaperQuestionDto;
import com.lyedu.entity.Paper;
import com.lyedu.service.PaperService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 试卷管理（管理端）；试卷题目列表（用于组卷与考试作答）
 *
 * @author LyEdu Team
 */
@RestController
@RequestMapping("/paper")
@RequiredArgsConstructor
public class PaperController {

    private final PaperService paperService;

    @GetMapping("/page")
    public Result<PageResult<Paper>> page(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "20") Integer size,
            @RequestParam(required = false) String keyword) {
        return Result.success(paperService.page(page, size, keyword));
    }

    @GetMapping("/{id}")
    public Result<Paper> getById(@PathVariable Long id) {
        Paper p = paperService.getById(id);
        if (p == null) return Result.error(ResultCode.NOT_FOUND);
        return Result.success(p);
    }

    /** 获取试卷题目列表（含题目详情、分值、顺序；用于考试作答时不含 answer/analysis，由前端调用时需鉴权） */
    @GetMapping("/{id}/questions")
    public Result<List<PaperQuestionDto>> getQuestions(@PathVariable Long id) {
        List<PaperQuestionDto> list = paperService.listQuestionsByPaperId(id);
        for (PaperQuestionDto dto : list) {
            if (dto.getQuestion() != null) {
                dto.getQuestion().setAnswer(null);
                dto.getQuestion().setAnalysis(null);
            }
        }
        return Result.success(list);
    }

    @PostMapping
    public Result<Long> create(@RequestBody PaperRequest request) {
        Paper p = new Paper();
        p.setTitle(request.getTitle());
        p.setTotalScore(request.getTotalScore() != null ? request.getTotalScore() : 100);
        p.setPassScore(request.getPassScore() != null ? request.getPassScore() : 60);
        p.setDurationMinutes(request.getDurationMinutes() != null ? request.getDurationMinutes() : 60);
        p.setStatus(request.getStatus() != null ? request.getStatus() : 1);
        p.setQuestions(request.getQuestions());
        long id = paperService.save(p);
        return Result.success(id);
    }

    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody PaperRequest request) {
        Paper p = paperService.getById(id);
        if (p == null) return Result.error(ResultCode.NOT_FOUND);
        p.setTitle(request.getTitle());
        p.setTotalScore(request.getTotalScore() != null ? request.getTotalScore() : 100);
        p.setPassScore(request.getPassScore() != null ? request.getPassScore() : 60);
        p.setDurationMinutes(request.getDurationMinutes() != null ? request.getDurationMinutes() : 60);
        p.setStatus(request.getStatus() != null ? request.getStatus() : 1);
        p.setQuestions(request.getQuestions());
        paperService.update(p);
        return Result.success();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        Paper paper = paperService.getById(id);
        if (paper == null) return Result.error(ResultCode.NOT_FOUND);
        paperService.delete(id);
        return Result.success();
    }

    @Data
    public static class PaperRequest {
        private String title;
        private Integer totalScore;
        private Integer passScore;
        private Integer durationMinutes;
        private Integer status;
        private List<com.lyedu.entity.PaperQuestionItem> questions;
    }
}
