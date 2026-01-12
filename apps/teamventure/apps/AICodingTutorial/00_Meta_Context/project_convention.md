# Project Technical Conventions

定义本项目的技术栈选择、命名规范和工程结构标准。

## 1. 技术栈 (Tech Stack)

### Backend (Admin & API)
*   **Language**: Java 17
*   **Framework**: Spring Boot 3.x
*   **Architecture**: COLA (Clean Object-Oriented and Layered Architecture) 4.0 simplified
*   **ORM**: MyBatis-Plus
*   **Database**: MySQL 8.0
*   **Build Tool**: Maven

### Frontend (User Side)
*   **Platform**: WeChat Miniprogram (原生小程序)
*   **Language**: JavaScript (ES6+) / WXML / WXSS
*   **UI Library**: Vant Weapp (Optional, prefer custom components based on Design Tokens)

### Frontend (Admin Side)
*   **Framework**: React 18+
*   **UI Library**: Ant Design 5.x
*   **State Management**: Zustand or React Context

### Infrastructure
*   **Reverse Proxy**: Nginx
*   **Container**: Docker & Docker Compose

## 2. 命名规范 (Naming Conventions)

| 对象类型 | 规范 | 示例 | 备注 |
| :--- | :--- | :--- | :--- |
| **Java Class** | PascalCase | `BookingService`, `UserDTO` | |
| **Java Method** | camelCase | `createBooking`, `getUserById` | |
| **Database Table** | snake_case | `t_booking_order`, `t_user` | 必须以 `t_` 开头 |
| **DB Column** | snake_case | `user_id`, `created_at` | |
| **API Path** | kebab-case | `/api/v1/booking-orders` | 复数名词 |
| **JSON Field** | camelCase | `bookingId`, `userName` | 前后端交互统一 |
| **CSS Class** | kebab-case | `.btn-primary`, `.card-container` | BEM 风格推荐 |

## 3. 标准目录结构 (Backend - COLA)

```text
com.company.project/
├── api/             # DTOs, Dubbo Interfaces (对外暴露)
├── app/             # Application Services, Command Handlers (编排业务)
├── domain/          # Entities, Aggregates, Domain Services (核心业务逻辑)
│   ├── model/
│   └── gateway/     # Interface definition for infra
├── infrastructure/  # DB Implementation, External API Client (技术实现)
│   ├── mapper/
│   └── repository/
└── start/           # Application Main, Configuration (启动入口)
```

## 4. 错误码规范
*   **200**: Success
*   **400**: Bad Request (Param error)
*   **401**: Unauthorized (Login required)
*   **403**: Forbidden (No permission)
*   **500**: Internal Server Error
*   **Biz Error**: 
    *   `B_001_xxx`: Business Logic Error (e.g., Inventory shortage)
    *   `S_001_xxx`: System Error
