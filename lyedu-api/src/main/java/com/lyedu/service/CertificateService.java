package com.lyedu.service;

import com.lyedu.entity.Certificate;

import java.util.List;

/**
 * 证书颁发规则服务（关联考试/任务，合格后颁发）
 *
 * @author LyEdu Team
 */
public interface CertificateService {

    List<Certificate> listAll();

    Certificate getById(Long id);

    /** 按来源查找启用规则 */
    Certificate getBySource(String sourceType, Long sourceId);

    long save(Certificate entity);

    void update(Certificate entity);

    void delete(Long id);
}
