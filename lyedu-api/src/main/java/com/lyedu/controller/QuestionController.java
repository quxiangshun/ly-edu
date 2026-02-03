package com.lyedu.controller;

import com.lyedu.common.PageResult;
import com.lyedu.common.Result;
import com.lyedu.common.ResultCode;
import com.lyedu.entity.Question;
import com.lyedu.service.QuestionService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/question")
@RequiredArgsConstructor
public class QuestionController {

    private final QuestionService questionService;

    @GetMapping("/page")
    public Result<PageResult<Question>> page(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "20") Integer size,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String type) {
        return Result.success(questionService.page(page, size, keyword, type));
    }

    @GetMapping("/{id}")
    public Result<Question> getById(@PathVariable Long id) {
        Question q = questionService.getById(id);
        if (q == null) return Result.error(ResultCode.NOT_FOUND);
        return Result.success(q);
    }

    @PostMapping
    public Result<Long> create(@RequestBody QuestionRequest request) {
        Question q = new Question();
        q.setType(request.getType());
        q.setTitle(request.getTitle());
        q.setOptions(request.getOptions());
        q.setAnswer(request.getAnswer());
        q.setScore(request.getScore() != null ? request.getScore() : 10);
        q.setAnalysis(request.getAnalysis());
        q.setSort(request.getSort() != null ? request.getSort() : 0);
        long id = questionService.save(q);
        return Result.success(id);
    }

    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody QuestionRequest request) {
        Question q = questionService.getById(id);
        if (q == null) return Result.error(ResultCode.NOT_FOUND);
        q.setType(request.getType());
        q.setTitle(request.getTitle());
        q.setOptions(request.getOptions());
        q.setAnswer(request.getAnswer());
        q.setScore(request.getScore() != null ? request.getScore() : 10);
        q.setAnalysis(request.getAnalysis());
        q.setSort(request.getSort() != null ? request.getSort() : 0);
        questionService.update(q);
        return Result.success();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        Question q = questionService.getById(id);
        if (q == null) return Result.error(ResultCode.NOT_FOUND);
        questionService.delete(id);
        return Result.success();
    }

    @Data
    public static class QuestionRequest {
        private String type;
        private String title;
        private String options;
        private String answer;
        private Integer score;
        private String analysis;
        private Integer sort;
    }
}
