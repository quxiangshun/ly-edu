package com.lyedu.service;

import com.lyedu.entity.CertificateTemplate;

import java.util.List;

/**
 * 证书模板服务
 *
 * @author LyEdu Team
 */
public interface CertificateTemplateService {

    List<CertificateTemplate> listAll();

    CertificateTemplate getById(Long id);

    long save(CertificateTemplate entity);

    void update(CertificateTemplate entity);

    void delete(Long id);
}
