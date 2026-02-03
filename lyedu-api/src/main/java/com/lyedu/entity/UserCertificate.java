package com.lyedu.entity;

import lombok.Data;

import java.time.LocalDateTime;

/**
 * 用户已获证书记录
 *
 * @author LyEdu Team
 */
@Data
public class UserCertificate {

    private Long id;
    private Long userId;
    private Long certificateId;
    private Long templateId;
    private String certificateNo;
    private String title;
    private LocalDateTime issuedAt;
    private LocalDateTime createTime;
}
