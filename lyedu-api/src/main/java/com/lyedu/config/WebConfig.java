package com.lyedu.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import tools.jackson.databind.json.JsonMapper;

/**
 * Web 配置（Jackson 3 + Spring Framework 7）
 *
 * @author LyEdu Team
 */
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Value("${lyedu.upload.path:./uploads}")
    private String uploadPath;

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOriginPatterns("*")
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .allowCredentials(true)
                .maxAge(3600);
    }

    @Bean
    @Primary
    public JsonMapper jsonMapper() {
        return JsonMapper.builderWithJackson2Defaults().build();
    }

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // 配置上传文件的静态资源访问（图片等）
        // 视频文件由VideoFileController专门处理，支持Range请求
        registry.addResourceHandler("/uploads/images/**")
                .addResourceLocations("file:" + uploadPath + "/images/")
                .setCachePeriod(3600); // 缓存1小时
    }
}
