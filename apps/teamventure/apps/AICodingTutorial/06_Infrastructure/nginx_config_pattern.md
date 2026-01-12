# Nginx Configuration Pattern

此配置展示了标准的 Nginx 设置，用于同时托管静态资源（Admin Web）和反向代理 API（Backend）。

```nginx
# /etc/nginx/conf.d/teamventure.conf

upstream backend_api {
    server app-service:8080; # Docker internal DNS
    keepalive 32;
}

server {
    listen 80;
    server_name admin.teamventure.com;

    # 1. Security Headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";

    # 2. Serve Admin Frontend (React/Vue Static Files)
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html; # History Mode Support
    }

    # 3. Reverse Proxy to Backend API
    location /api/ {
        proxy_pass http://backend_api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Timeouts for slow operations (e.g. Export Excel)
        proxy_read_timeout 60s;
    }

    # 4. Gzip Compression (Performance)
    gzip on;
    gzip_types text/plain application/json application/javascript text/css;
}
```

## AI Instructions
当要求 AI 生成 Nginx 配置时，请提供以下信息：
1.  **Backend Port**: (e.g., 8080)
2.  **Frontend Path**: (e.g., /dist)
3.  **Domain Name**: (e.g., example.com)
