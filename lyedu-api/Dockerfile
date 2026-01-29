# 运行阶段：只复制已构建的 jar 并运行
# 构建步骤已移除，jar 需要预先构建并放在 pkg/ 目录
#
# 构建 jar（在项目根目录执行）：
#   cd lyedu-api
#   ./gradlew bootJar
#   或
#   gradle bootJar
#
# jar 会自动复制到根目录 pkg/lyedu-api.jar
#
# 然后启动：
#   docker-compose up -d

FROM mcr.microsoft.com/openjdk/jdk:25-ubuntu

WORKDIR /app

# 从 pkg 目录复制 jar（构建时由 docker-compose 处理）
COPY pkg/lyedu-api.jar app.jar

EXPOSE 9700

ENV JAVA_OPTS="-Xms512m -Xmx1024m -XX:+UseG1GC -Dfile.encoding=UTF-8 -Duser.language=zh -Duser.country=CN"

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
