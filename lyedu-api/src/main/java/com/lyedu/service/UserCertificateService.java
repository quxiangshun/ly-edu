package com.lyedu.service;

import com.lyedu.entity.UserCertificate;

import java.util.List;

/**
 * 用户证书记录服务
 *
 * @author LyEdu Team
 */
public interface UserCertificateService {

    List<UserCertificate> listByUserId(Long userId);

    UserCertificate getById(Long id);

    /** 用户是否已有该证书规则颁发的证书 */
    boolean hasCertificate(Long certificateId, Long userId);

    /**
     * 考试/任务合格后尝试颁发证书：若存在对应启用规则且用户尚未获得，则颁发
     * @return 新颁发的证书记录，若未颁发则 null
     */
    UserCertificate issueIfEligible(String sourceType, Long sourceId, Long userId);
}
