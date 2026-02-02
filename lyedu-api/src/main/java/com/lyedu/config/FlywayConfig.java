package com.lyedu.config;

import org.flywaydb.core.Flyway;
import org.flywaydb.core.api.MigrationVersion;
import org.springframework.boot.ApplicationRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.sql.DataSource;

/**
 * Flyway 配置（显式触发 migrate，避免自动配置未生效导致迁移未执行）
 *
 * @author LyEdu Team
 */
@Configuration
public class FlywayConfig {

    @Bean
    public Flyway flyway(DataSource dataSource) {
        return Flyway.configure()
                .dataSource(dataSource)
                // 优先 classpath，备用仓库根 db/flyway（防止仅部署 Java 时缺迁移）
                .locations("classpath:db/migration", "filesystem:../db/flyway")
                .baselineOnMigrate(true)
                .baselineVersion(MigrationVersion.fromVersion("1"))
                .load();
    }

    @Bean
    public ApplicationRunner flywayRunner(Flyway flyway) {
        return args -> flyway.migrate();
    }
}

