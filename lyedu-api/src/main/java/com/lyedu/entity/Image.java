package com.lyedu.entity;

import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 图片库实体
 *
 * @author LyEdu Team
 */
@Data
public class Image implements Serializable {

    private static final long serialVersionUID = 1L;

    private Long id;
    private String name;
    private String path;
    private Long fileSize;
    private LocalDateTime createTime;
}
