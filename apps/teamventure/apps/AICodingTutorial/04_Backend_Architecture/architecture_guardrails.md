# Backend Architecture Guardrails (COLA)

本项目采用 **COLA (Clean Object-Oriented and Layered Architecture)**。
AI 生成代码时必须严格遵守以下分层职责。

## 1. Layer Responsibilities

### Adapter Layer (Controller)
*   **Path**: `com.company.project.adapter.web`
*   **职责**:
    1.  接收 HTTP 请求 (DTO)。
    2.  解析 Token 获取当前用户 ID。
    3.  调用 Application Service。
    4.  将结果转换为 Response DTO。
*   **禁止**: 编写任何业务逻辑（如 `if (stock < 0)`）。

### Application Layer (Service)
*   **Path**: `com.company.project.app.service`
*   **职责**:
    1.  编排业务流程 (Transaction Script)。
    2.  调用 Domain Service 执行核心规则。
    3.  控制事务 (`@Transactional`)。
*   **示例**: `bookingService.createBooking()` 负责协调“检查用户”、“扣减库存”、“保存记录”。

### Domain Layer (The Core)
*   **Path**: `com.company.project.domain`
*   **职责**:
    1.  **Entity**: 充血模型，包含业务行为（如 `session.isFull()`）。
    2.  **Domain Service**: 跨实体的复杂逻辑（如 `InventoryDomainService`）。
*   **禁止**: 依赖任何框架（无 Spring，无 MyBatis）。

### Infrastructure Layer (Gateway Impl)
*   **Path**: `com.company.project.infrastructure`
*   **职责**:
    1.  实现 Domain 定义的 Gateway 接口。
    2.  数据库访问 (MyBatis Mapper)。
    3.  发送消息 (RocketMQ/Kafka)。

## 2. Code Example (The "Right" Way)

### Controller
```java
@PostMapping("/bookings")
public Response<BookingResultDTO> createBooking(@RequestBody CreateBookingCmd cmd) {
    // Delegate to Application Service
    return Response.of(bookingAppService.create(cmd));
}
```

### Application Service
```java
@Transactional
public BookingResultDTO create(CreateBookingCmd cmd) {
    // 1. Load Aggregate
    Session session = sessionGateway.getById(cmd.getSessionId());
    
    // 2. Execute Domain Logic
    Booking booking = session.book(cmd.getEmployeeId()); // Domain method
    
    // 3. Persist
    bookingGateway.save(booking);
    sessionGateway.update(session);
    
    return convertToDTO(booking);
}
```
