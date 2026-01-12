# Docker Compose Template

用于本地开发或单机部署的标准容器编排配置。

```yaml
version: '3.8'

services:
  # 1. Database
  mysql:
    image: mysql:8.0
    container_name: tv-mysql
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: teamventure_tutorial
    volumes:
      - ./mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "3306:3306"
    networks:
      - tv-net

  # 2. Backend Service
  app:
    build: ../backend
    container_name: tv-app
    ports:
      - "8080:8080"
    environment:
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/teamventure_tutorial
      SPRING_DATASOURCE_PASSWORD: root
    depends_on:
      - mysql
    networks:
      - tv-net

  # 3. Nginx Gateway
  nginx:
    image: nginx:alpine
    container_name: tv-nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ../frontend/dist:/usr/share/nginx/html
    depends_on:
      - app
    networks:
      - tv-net

networks:
  tv-net:
    driver: bridge
```
