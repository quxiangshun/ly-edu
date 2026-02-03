package com.lyedu.service;

import com.lyedu.config.FeishuProperties;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Map;

/**
 * 飞书开放平台 API 调用（app_access_token、OIDC 换 token、用户信息）
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class FeishuApiService {

    private static final String FEISHU_BASE = "https://open.feishu.cn/open-apis";
    private static final String SCOPE = "contact:user.base:readonly";

    private final FeishuProperties feishuProperties;
    private final RestTemplate restTemplate = new RestTemplate();

    /**
     * 生成飞书授权页 URL（用户扫码或点击后跳转飞书，授权后回调到 redirectUri?code=xxx）
     *
     * @param redirectUri 前端回调地址（需与飞书开放平台配置一致）
     * @param state       可选，防 CSRF
     */
    public String buildAuthorizeUrl(String redirectUri, String state) {
        String appId = feishuProperties.getAppId();
        if (appId == null || appId.isEmpty()) {
            throw new IllegalStateException("飞书 App ID 未配置");
        }
        String encoded = URLEncoder.encode(redirectUri, StandardCharsets.UTF_8);
        String url = FEISHU_BASE + "/authen/v1/authorize"
                + "?app_id=" + appId
                + "&redirect_uri=" + encoded
                + "&response_type=code"
                + "&scope=" + SCOPE;
        if (state != null && !state.isEmpty()) {
            url += "&state=" + URLEncoder.encode(state, StandardCharsets.UTF_8);
        }
        return url;
    }

    /**
     * 用授权码换取 user_access_token，再拉取用户信息
     *
     * @param code        飞书回调带来的 code
     * @param redirectUri 与授权时一致的 redirect_uri
     * @return 用户信息 map，含 open_id、name、avatar_url 等；失败返回 null
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getUserInfoByCode(String code, String redirectUri) {
        String appId = feishuProperties.getAppId();
        String appSecret = feishuProperties.getAppSecret();
        if (appId == null || appId.isEmpty() || appSecret == null || appSecret.isEmpty()) {
            log.warn("飞书 App ID/Secret 未配置");
            return null;
        }

        String appAccessToken = getAppAccessToken(appId, appSecret);
        if (appAccessToken == null) return null;

        String userAccessToken = getOidcAccessToken(appAccessToken, code, redirectUri);
        if (userAccessToken == null) return null;

        return getUserInfo(userAccessToken);
    }

    private String getAppAccessToken(String appId, String appSecret) {
        String url = FEISHU_BASE + "/auth/v3/app_access_token/internal";
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        Map<String, String> body = Map.of("app_id", appId, "app_secret", appSecret);
        ResponseEntity<Map> resp = restTemplate.exchange(url, HttpMethod.POST, new HttpEntity<>(body, headers), Map.class);
        if (resp.getBody() == null) return null;
        Object token = resp.getBody().get("app_access_token");
        return token != null ? token.toString() : null;
    }

    @SuppressWarnings("unchecked")
    private String getOidcAccessToken(String appAccessToken, String code, String redirectUri) {
        String url = FEISHU_BASE + "/authen/v1/oidc/access_token";
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBearerAuth(appAccessToken);
        Map<String, String> body = Map.of(
                "grant_type", "authorization_code",
                "code", code,
                "redirect_uri", redirectUri != null ? redirectUri : feishuProperties.getRedirectUri()
        );
        ResponseEntity<Map> resp = restTemplate.exchange(url, HttpMethod.POST, new HttpEntity<>(body, headers), Map.class);
        if (resp.getBody() == null) return null;
        Object data = resp.getBody().get("data");
        if (data instanceof Map) {
            Object at = ((Map<?, ?>) data).get("access_token");
            return at != null ? at.toString() : null;
        }
        return null;
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> getUserInfo(String userAccessToken) {
        String url = FEISHU_BASE + "/authen/v1/user_info";
        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(userAccessToken);
        ResponseEntity<Map> resp = restTemplate.exchange(url, HttpMethod.GET, new HttpEntity<>(headers), Map.class);
        if (resp.getBody() == null) return null;
        Object data = resp.getBody().get("data");
        return data instanceof Map ? (Map<String, Object>) data : null;
    }
}
