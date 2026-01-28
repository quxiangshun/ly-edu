ARG NPM_REGISTRY=https://registry.npmmirror.com

# 使用 mcr.microsoft.com + 腾讯云 Node.js 镜像，完全绕过 docker.io

FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04 AS builder

WORKDIR /app

# 安装 Node.js（从腾讯云镜像下载二进制包）
RUN apt-get update && \
    apt-get install -y curl xz-utils ca-certificates && \
    curl -fsSL https://mirrors.cloud.tencent.com/nodejs-release/v18.12.0/node-v18.12.0-linux-x64.tar.xz -o node.tar.xz && \
    mkdir -p /usr/local/lib/nodejs && \
    tar -xJf node.tar.xz -C /usr/local/lib/nodejs && \
    rm node.tar.xz && \
    ln -s /usr/local/lib/nodejs/node-v18.12.0-linux-x64/bin/node /usr/local/bin/node && \
    ln -s /usr/local/lib/nodejs/node-v18.12.0-linux-x64/bin/npm /usr/local/bin/npm && \
    npm config set registry ${NPM_REGISTRY}

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build:docker

FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

RUN apt-get update && \
    apt-get install -y nginx && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
