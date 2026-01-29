package com.lyedu;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * LyEdu 应用启动类
 *
 * @author LyEdu Team
 */
@SpringBootApplication
public class LyEduApplication {

    public static void main(String[] args) {
        SpringApplication.run(LyEduApplication.class, args);
        System.out.println("""
                
                ========================================
                LyEdu API 启动成功！
                访问地址: http://localhost:9700/api
                ========================================
                """);
    }
}
