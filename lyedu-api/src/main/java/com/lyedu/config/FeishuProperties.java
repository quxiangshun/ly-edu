package com.lyedu.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * 飞书开放平台配置（扫码登录）
 */
@Data
@Component
@ConfigurationProperties(prefix = "lyedu.feishu")
public class FeishuProperties {

    private String appId = "";
    private String appSecret = "";
    /**
     * 飞书授权后回调到前端的完整地址，需在飞书开放平台配置一致，如 https://your-domain.com/login/feishu-callback
     */
    private String redirectUri = "";
}
