# TeamVenture Phase 1 - Java业务服务详细设计

**版本**: v1.0
**创建日期**: 2026-01-04
**作者**: TeamVenture开发团队
**用途**: Java Spring Boot业务服务完整架构设计文档

---

## 目录

1. [概述](#1-概述)
2. [COLA四层架构](#2-cola四层架构)
3. [核心业务流程](#3-核心业务流程)
4. [数据持久化设计](#4-数据持久化设计)
5. [领域事件机制](#5-领域事件机制)
6. [中间件集成](#6-中间件集成)
7. [异常处理与安全](#7-异常处理与安全)
8. [配置管理](#8-配置管理)
9. [监控与运维](#9-监控与运维)

---

## 1. 概述

### 1.1 服务定位

TeamVenture Java业务服务是整个系统的**核心协调层**，负责：

- **业务逻辑处理**: 用户认证、方案生成请求、方案查询、方案确认
- **数据持久化**: 用户、方案、供应商、领域事件的CRUD操作
- **消息队列集成**: 发布方案生成请求到RabbitMQ，接收AI服务回调
- **会话管理**: JWT Token生成与验证，Redis会话存储
- **API网关**: 为微信小程序提供RESTful API

### 1.2 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Spring Boot** | 3.x | 应用框架 |
| **MyBatis Plus** | 3.5.x | ORM框架 |
| **Druid** | 1.2.x | 数据库连接池 + 监控 |
| **Redis** | 7.x (Lettuce客户端) | 会话缓存 |
| **RabbitMQ** | 3.12 | 异步消息队列 |
| **MySQL** | 8.0 | 主从分离数据库 |
| **Jackson** | 2.x | JSON序列化 |
| **ULID** | 5.x | 分布式ID生成 |

### 1.3 架构原则

- **COLA架构**: Adapter → App → Domain → Infrastructure四层分离
- **DDD设计**: 聚合根、值对象、领域事件
- **Event Sourcing**: 所有关键业务动作记录到domain_events表
- **幂等性**: 方案确认等操作支持重复调用
- **权限隔离**: 每个API都验证userId，禁止跨用户访问

---

## 2. COLA四层架构

### 2.1 架构全景

```
┌─────────────────────────────────────────────────────────┐
│                    Adapter 层 (Web适配器)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ AuthController│  │PlanController│  │SupplierCtrl  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│           ↓                ↓                  ↓           │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                      App 层 (应用服务)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  AuthService │  │ PlanService  │  │SupplierSvc   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │       InternalPlanCallbackService (AI回调)       │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Domain 层 (领域模型)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │     User     │  │PlanRequest   │  │     Plan     │   │
│  │  (聚合根)     │  │  (聚合根)     │  │  (聚合根)     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                           │
│  领域事件：PlanRequestCreated, PlanGenerated, ...         │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Infrastructure 层 (基础设施)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │UserMapper    │  │PlanMapper    │  │SupplierMapper│   │
│  │(MyBatis Plus)│  │(MyBatis Plus)│  │(MyBatis Plus)│   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  UserPO      │  │  PlanPO      │  │ DomainEventPO│   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                           │
│  中间件：Redis, RabbitMQ, Druid连接池                      │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Adapter层 (适配器层)

**职责**: 接收HTTP请求，参数验证，调用App层服务，返回统一响应格式

#### 2.2.1 PlanController (方案控制器)

**文件**: `adapter/web/plans/PlanController.java`

**关键代码**:
```java
@RestController
@RequestMapping("/api/v1/plans")
public class PlanController {
    private final AuthService authService;
    private final PlanService planService;

    // 生成方案
    @PostMapping("/generate")
    public ApiResponse<GenerateResponse> generate(
        @RequestHeader(value = "Authorization", required = false) String authorization,
        @Valid @RequestBody GenerateRequest req
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(planService.createPlanRequestAndPublish(userId, req));
    }

    // 查询方案列表
    @GetMapping
    public ApiResponse<?> list(
        @RequestHeader("Authorization") String authorization,
        @RequestParam(defaultValue = "1") int page,
        @RequestParam(defaultValue = "10") int pageSize
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(planService.listPlans(userId, page, pageSize));
    }

    // 查询方案详情
    @GetMapping("/{planId}")
    public ApiResponse<?> detail(
        @RequestHeader("Authorization") String authorization,
        @PathVariable String planId
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(planService.getPlanDetail(userId, planId));
    }

    // 确认方案（幂等）
    @PostMapping("/{planId}/confirm")
    public ApiResponse<Void> confirm(
        @RequestHeader("Authorization") String authorization,
        @PathVariable String planId
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        planService.confirmPlan(userId, planId);
        return ApiResponse.success();
    }

    // 记录供应商联系
    @PostMapping("/{planId}/supplier-contacts")
    public ApiResponse<Void> contact(
        @RequestHeader("Authorization") String authorization,
        @PathVariable String planId,
        @Valid @RequestBody SupplierContactRequest req
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        planService.logSupplierContact(userId, planId, req);
        return ApiResponse.success();
    }
}
```

**DTO定义**:
```java
public static class GenerateRequest {
    @NotNull public Integer people_count;          // 必需
    @NotNull public BigDecimal budget_min;          // 必需
    @NotNull public BigDecimal budget_max;          // 必需
    @NotBlank public String start_date;             // YYYY-MM-DD
    @NotBlank public String end_date;               // YYYY-MM-DD
    @NotBlank public String departure_city;         // 出发城市
    public Map<String, Object> preferences;         // 可选偏好
}

public static class GenerateResponse {
    public String plan_request_id;
    public String status;  // "generating"
}

public static class SupplierContactRequest {
    @NotBlank public String supplier_id;
    @NotBlank public String channel;  // PHONE/WECHAT/EMAIL
    public String notes;
}
```

**设计要点**:
- **Authorization header**: 所有接口都需要JWT Token
- **参数验证**: 使用`@Valid`注解触发JSR-303校验
- **统一响应**: 所有接口返回`ApiResponse<T>`包装器
- **权限检查**: 通过`authService.getUserIdFromAuthorization()`获取当前用户ID

#### 2.2.2 AuthController (认证控制器)

**文件**: `adapter/web/auth/AuthController.java`

**关键代码**:
```java
@RestController
@RequestMapping("/api/v1/auth")
public class AuthController {
    private final AuthService authService;

    @PostMapping("/wechat/login")
    public ApiResponse<LoginResponse> login(@Valid @RequestBody LoginRequest req) {
        return ApiResponse.success(
            authService.loginWithWeChat(req.code, req.nickname, req.avatarUrl)
        );
    }
}

public static class LoginRequest {
    @NotBlank public String code;       // 微信登录code（必需）
    public String nickname;              // 用户昵称（可选）
    public String avatarUrl;             // 头像URL（可选）
}

public static class LoginResponse {
    public String sessionToken;          // JWT Token
    public UserInfo userInfo;            // 用户信息
}
```

#### 2.2.3 InternalPlanController (内部回调控制器)

**文件**: `adapter/web/internal/InternalPlanController.java`

**用途**: 接收Python AI服务的方案生成回调

**关键代码**:
```java
@RestController
@RequestMapping("/internal")
public class InternalPlanController {
    private final InternalPlanCallbackService callbackService;
    private final String internalSecret;

    @PostMapping("/plans/batch")
    public ApiResponse<Void> createPlans(
        @RequestHeader("X-Internal-Secret") String secret,
        @Valid @RequestBody BatchPlanRequest req
    ) {
        // 校验内部Secret
        if (!internalSecret.equals(secret)) {
            return ApiResponse.failure("UNAUTHORIZED", "invalid internal secret");
        }
        callbackService.handleGeneratedPlans(req);
        return ApiResponse.success();
    }

    public static class BatchPlanRequest {
        @NotBlank public String plan_request_id;
        @NotBlank public String user_id;
        public List<Map<String, Object>> plans;  // 3套方案
        public String trace_id;
    }
}
```

**安全机制**:
- **X-Internal-Secret header**: 仅内部服务可调用
- **配置项**: `teamventure.ai-service.callback-secret`

#### 2.2.4 SupplierController (供应商控制器)

**文件**: `adapter/web/suppliers/SupplierController.java`

**关键代码**:
```java
@RestController
@RequestMapping("/api/v1/suppliers")
public class SupplierController {
    private final SupplierService supplierService;

    @GetMapping("/search")
    public ApiResponse<List<SupplierPO>> search(
        @RequestParam(required = false) String city,
        @RequestParam(required = false) String category
    ) {
        return ApiResponse.success(supplierService.search(city, category));
    }

    @GetMapping("/{supplierId}")
    public ApiResponse<SupplierPO> detail(@PathVariable String supplierId) {
        return ApiResponse.success(supplierService.getById(supplierId));
    }
}
```

### 2.3 App层 (应用服务层)

**职责**: 编排业务逻辑，调用Domain层聚合，操作Infrastructure层Mapper

#### 2.3.1 PlanService (方案服务)

**文件**: `app/service/PlanService.java` (154行)

**核心方法**:

##### 1) createPlanRequestAndPublish (生成方案请求)

**流程**:
1. 生成`plan_request_id` (ULID)
2. 创建`PlanRequestPO`并插入数据库 (状态: GENERATING)
3. 记录领域事件`PlanRequestCreated`
4. 构建MQ消息并发送到RabbitMQ
5. 返回`plan_request_id`给前端

**代码**:
```java
public GenerateResponse createPlanRequestAndPublish(String userId, GenerateRequest req) {
    // 1. 生成ID
    String planRequestId = IdGenerator.newId("plan_req");

    // 2. 创建PlanRequest记录
    PlanRequestPO po = new PlanRequestPO();
    po.setPlanRequestId(planRequestId);
    po.setUserId(userId);
    po.setPeopleCount(req.people_count);
    po.setBudgetMin(req.budget_min);
    po.setBudgetMax(req.budget_max);
    po.setStartDate(req.start_date);
    po.setEndDate(req.end_date);
    po.setDepartureCity(req.departure_city);
    po.setPreferencesJson(req.preferences == null ? "{}" : Jsons.toJson(req.preferences));
    po.setStatus("GENERATING");
    po.setGenerationStartedAt(Instant.now());
    planRequestMapper.insert(po);

    // 3. 记录领域事件
    recordEvent("PlanRequestCreated", "PlanRequest", planRequestId, userId,
                Map.of("plan_request_id", planRequestId));

    // 4. 发送MQ消息
    Map<String, Object> mq = new HashMap<>();
    mq.put("plan_request_id", planRequestId);
    mq.put("user_id", userId);
    mq.put("people_count", req.people_count);
    mq.put("budget_min", req.budget_min);
    mq.put("budget_max", req.budget_max);
    mq.put("start_date", req.start_date);
    mq.put("end_date", req.end_date);
    mq.put("departure_city", req.departure_city);
    mq.put("preferences", req.preferences == null ? Map.of() : req.preferences);
    mq.put("trace_id", IdGenerator.newId("trace"));

    rabbitTemplate.convertAndSend(exchange, routingKey, Jsons.toJson(mq));

    // 5. 返回响应
    return new GenerateResponse(planRequestId, "generating");
}
```

**关键点**:
- **异步处理**: MQ消息发送后立即返回，不等待AI生成完成
- **JSON序列化**: `preferences`对象序列化为JSON字符串存储
- **领域事件**: 记录事件用于后续分析和审计
- **Trace ID**: 用于全链路追踪

##### 2) listPlans (查询方案列表)

**流程**:
1. 使用MyBatis Plus分页查询
2. 按创建时间倒序排列
3. 仅返回当前用户的方案

**代码**:
```java
public Object listPlans(String userId, int page, int pageSize) {
    Page<PlanPO> p = new Page<>(page, pageSize);
    Page<PlanPO> res = planMapper.selectPage(
        p,
        new QueryWrapper<PlanPO>()
            .eq("user_id", userId)
            .orderByDesc("create_time")
    );
    return res;  // 直接返回MyBatis Plus的Page对象
}
```

**返回格式**:
```json
{
  "success": true,
  "data": {
    "records": [
      { "plan_id": "plan_01ke3d123", "plan_name": "北京3日游", ... }
    ],
    "total": 15,
    "size": 10,
    "current": 1,
    "pages": 2
  }
}
```

##### 3) getPlanDetail (查询方案详情)

**流程**:
1. 根据`plan_id`查询方案
2. 验证方案是否存在
3. 验证用户权限（只能查询自己的方案）
4. 返回完整方案信息

**代码**:
```java
public Object getPlanDetail(String userId, String planId) {
    PlanPO plan = planMapper.selectById(planId);
    if (plan == null) {
        throw new BizException("NOT_FOUND", "plan not found");
    }
    if (!userId.equals(plan.getUserId())) {
        throw new BizException("UNAUTHORIZED", "not owner");
    }
    return plan;
}
```

**安全设计**:
- **NOT_FOUND**: 方案不存在
- **UNAUTHORIZED**: 跨用户访问被拒绝

##### 4) confirmPlan (确认方案 - 幂等)

**流程**:
1. 查询方案并验证权限
2. 检查是否已确认（幂等处理）
3. 更新状态为`CONFIRMED`
4. 记录领域事件`PlanConfirmed`

**代码**:
```java
public void confirmPlan(String userId, String planId) {
    PlanPO plan = planMapper.selectById(planId);
    if (plan == null) {
        throw new BizException("NOT_FOUND", "plan not found");
    }
    if (!userId.equals(plan.getUserId())) {
        throw new BizException("UNAUTHORIZED", "not owner");
    }

    // 幂等处理：如果已确认，直接返回
    if ("CONFIRMED".equalsIgnoreCase(plan.getStatus())) {
        return;
    }

    // 更新状态
    plan.setStatus("CONFIRMED");
    plan.setConfirmedTime(Instant.now());
    planMapper.updateById(plan);

    // 记录领域事件
    recordEvent("PlanConfirmed", "Plan", planId, userId, Map.of("plan_id", planId));
}
```

**幂等性保证**:
- 重复调用不会报错
- 北极星指标（确认数）正确计算

##### 5) logSupplierContact (记录供应商联系)

**流程**:
1. 生成`contact_id`
2. 插入`supplier_contact_logs`表
3. 记录领域事件`SupplierContacted`

**代码**:
```java
public void logSupplierContact(String userId, String planId, SupplierContactRequest req) {
    SupplierContactLogPO po = new SupplierContactLogPO();
    po.setContactId(IdGenerator.newId("contact"));
    po.setPlanId(planId);
    po.setSupplierId(req.supplier_id);
    po.setUserId(userId);
    po.setChannel(req.channel);  // PHONE/WECHAT/EMAIL
    po.setNotes(req.notes);
    contactLogMapper.insert(po);

    recordEvent(
        "SupplierContacted",
        "SupplierContactLog",
        po.getContactId(),
        userId,
        Map.of("plan_id", planId, "supplier_id", req.supplier_id, "channel", req.channel)
    );
}
```

**用途**:
- 转化漏斗分析（方案确认 → 联系供应商 → 成单）
- 供应商热度统计

#### 2.3.2 AuthService (认证服务)

**文件**: `app/service/AuthService.java`

**核心方法**:

##### 1) loginWithWeChat (微信登录)

**流程**:
1. 使用`code`换取`openid`（伪实现，生产需调用微信API）
2. 查询用户是否存在
3. 如果是新用户，创建用户记录
4. 如果是老用户，更新昵称和头像（如果提供且有变化）
5. 生成JWT Token
6. 存储Session到Redis
7. 返回`sessionToken`和`userInfo`

**代码** (简化版):
```java
public LoginResponse loginWithWeChat(String code, String nickname, String avatarUrl) {
    // 1. 获取openid（生产环境需调用微信API）
    String openid = pseudoOpenId(code);

    // 2. 查询用户
    UserPO user = userMapper.selectOne(
        new QueryWrapper<UserPO>().eq("wechat_openid", openid)
    );

    // 3. 新用户创建
    if (user == null) {
        user = new UserPO();
        user.setUserId(IdGenerator.newId("user"));
        user.setWechatOpenid(openid);
        user.setNickname(hasText(nickname) ? nickname.trim() : "微信用户");
        user.setAvatarUrl(hasText(avatarUrl) ? avatarUrl : "");
        user.setRole("user");
        user.setStatus("active");
        userMapper.insert(user);
    } else {
        // 4. 老用户更新信息
        boolean needUpdate = false;
        if (hasText(nickname) && !nickname.trim().equals(user.getNickname())) {
            user.setNickname(nickname.trim());
            needUpdate = true;
        }
        if (hasText(avatarUrl) && !avatarUrl.equals(user.getAvatarUrl())) {
            user.setAvatarUrl(avatarUrl);
            needUpdate = true;
        }
        if (needUpdate) {
            userMapper.updateById(user);
        }
    }

    // 5. 生成JWT Token
    String sessionToken = jwtSupport.generateToken(user.getUserId());

    // 6. 存储Session到Redis
    String sessionId = IdGenerator.newId("session");
    SessionPO session = new SessionPO();
    session.setSessionId(sessionId);
    session.setUserId(user.getUserId());
    session.setToken(sessionToken);
    session.setExpiresAt(Instant.now().plusSeconds(86400)); // 24小时
    sessionMapper.insert(session);

    // 存储到Redis
    redisTemplate.opsForValue().set(
        "session:" + user.getUserId(),
        sessionToken,
        24,
        TimeUnit.HOURS
    );

    // 7. 返回响应
    LoginResponse resp = new LoginResponse();
    resp.sessionToken = sessionToken;
    resp.userInfo = UserInfo.fromPO(user);
    return resp;
}
```

**关键点**:
- **幂等性**: 重复登录更新昵称/头像
- **双重验证**: JWT Token + Redis Session
- **过期时间**: 24小时（可配置）

##### 2) getUserIdFromAuthorization (从Token获取用户ID)

**流程**:
1. 解析Authorization header (`Bearer <token>`)
2. 验证JWT Token签名
3. 检查Redis Session是否存在
4. 返回`userId`

**代码**:
```java
public String getUserIdFromAuthorization(String authorization) {
    if (authorization == null || !authorization.startsWith("Bearer ")) {
        throw new BizException("UNAUTHENTICATED", "missing or invalid token");
    }

    String token = authorization.substring(7);

    // 验证JWT签名
    String userId = jwtSupport.extractUserId(token);
    if (userId == null) {
        throw new BizException("UNAUTHENTICATED", "invalid token");
    }

    // 检查Redis Session
    String redisToken = redisTemplate.opsForValue().get("session:" + userId);
    if (!token.equals(redisToken)) {
        throw new BizException("UNAUTHENTICATED", "session expired or invalid");
    }

    return userId;
}
```

#### 2.3.3 InternalPlanCallbackService (AI回调服务)

**文件**: `app/service/InternalPlanCallbackService.java`

**核心方法**:

##### handleGeneratedPlans (处理生成的方案)

**流程**:
1. 校验`plan_request_id`是否存在
2. 遍历3套方案，逐个插入`plans`表
3. 为每套方案记录`PlanGenerated`事件
4. 更新`plan_requests`状态为`COMPLETED`

**代码**:
```java
@Transactional
public void handleGeneratedPlans(BatchPlanRequest req) {
    // 1. 校验plan_request是否存在
    PlanRequestPO planRequest = planRequestMapper.selectById(req.plan_request_id);
    if (planRequest == null) {
        throw new BizException("NOT_FOUND", "plan request not found");
    }

    // 2. 插入3套方案
    List<Map<String, Object>> plans = req.plans == null ? List.of() : req.plans;
    for (Map<String, Object> planMap : plans) {
        PlanPO plan = PlanPO.fromMap(planMap);  // 从Map构建PO
        plan.setPlanRequestId(req.plan_request_id);
        plan.setUserId(req.user_id);
        planMapper.insert(plan);

        // 记录领域事件
        recordEvent("PlanGenerated", "Plan", plan.getPlanId(), req.user_id,
                    Map.of("plan_id", plan.getPlanId()));
    }

    // 3. 更新plan_request状态
    planRequest.setStatus("COMPLETED");
    planRequest.setGenerationCompletedAt(Instant.now());
    planRequestMapper.updateById(planRequest);
}
```

**事务保证**:
- `@Transactional`: 方案插入和状态更新必须原子执行
- 失败时全部回滚

#### 2.3.4 SupplierService (供应商服务)

**文件**: `app/service/SupplierService.java`

**核心方法**:

##### 1) search (搜索供应商)

**代码**:
```java
public List<SupplierPO> search(String city, String category) {
    QueryWrapper<SupplierPO> q = new QueryWrapper<>();
    if (city != null && !city.isBlank()) {
        q.eq("city", city);
    }
    if (category != null && !category.isBlank()) {
        q.eq("category", category);
    }
    q.eq("status", "active").orderByDesc("rating");
    return supplierMapper.selectList(q);
}
```

**查询逻辑**:
- 城市过滤（可选）
- 类别过滤（可选）
- 只返回`active`状态
- 按评分倒序

##### 2) getById (获取供应商详情)

**代码**:
```java
public SupplierPO getById(String supplierId) {
    SupplierPO po = supplierMapper.selectById(supplierId);
    if (po == null) {
        throw new BizException("NOT_FOUND", "supplier not found");
    }
    return po;
}
```

### 2.4 Domain层 (领域模型层)

**设计原则**: DDD战术设计，聚合根定义边界

#### 2.4.1 聚合根

| 聚合根 | 实体 | 值对象 | 生命周期 |
|-------|------|--------|---------|
| **User** | UserPO | SessionToken, OpenID | 注册→活跃→失活 |
| **PlanRequest** | PlanRequestPO | Preferences (JSON) | 创建→生成中→完成 |
| **Plan** | PlanPO | Itinerary, BudgetBreakdown, SupplierSnapshots | 草稿→已生成→已确认 |
| **Supplier** | SupplierPO | PriceRange, GeoLocation | 活跃→下架 |

#### 2.4.2 聚合边界设计

**PlanRequest聚合**:
```
PlanRequest (聚合根)
├── plan_request_id (标识)
├── user_id (关联User)
├── people_count, budget_min, budget_max, start_date, end_date
├── preferences (值对象 - JSON)
└── status (GENERATING → COMPLETED)
```

**Plan聚合**:
```
Plan (聚合根)
├── plan_id (标识)
├── plan_request_id (关联PlanRequest)
├── user_id (关联User)
├── plan_type (budget/standard/premium)
├── itinerary (值对象 - JSON)
├── budget_breakdown (值对象 - JSON)
├── supplier_snapshots (值对象 - JSON)
└── status (draft → CONFIRMED)
```

**值对象示例**:
```json
// Itinerary (行程安排)
{
  "day1": {
    "date": "2026-02-01",
    "morning": "上午抵达酒店，团队破冰活动",
    "afternoon": "下午团建拓展训练",
    "evening": "晚上烧烤晚会"
  },
  "day2": {...},
  "day3": {...}
}

// BudgetBreakdown (预算明细)
{
  "accommodation": 15000,
  "dining": 8000,
  "activities": 5000,
  "transportation": 2000,
  "total": 30000
}

// SupplierSnapshots (供应商快照)
[
  {
    "supplier_id": "sup_hotel_001",
    "name": "北京怀柔会议酒店",
    "category": "accommodation",
    "price": 300,
    "contact": "010-12345678"
  }
]
```

#### 2.4.3 领域不变量 (Invariants)

**PlanRequest**:
- `budget_min <= budget_max`
- `start_date < end_date`
- `people_count > 0`

**Plan**:
- `budget_total` ≈ `budget_min` ~ `budget_max` (由AI决定)
- `budget_per_person = budget_total / people_count`
- `duration_days = end_date - start_date + 1`

### 2.5 Infrastructure层 (基础设施层)

**职责**: 数据持久化、中间件访问、第三方API集成

#### 2.5.1 Mapper接口 (MyBatis Plus)

**文件结构**:
```
infrastructure/persistence/mapper/
├── UserMapper.java
├── SessionMapper.java
├── PlanRequestMapper.java
├── PlanMapper.java
├── SupplierMapper.java
├── SupplierContactLogMapper.java
└── DomainEventMapper.java
```

**示例 - PlanMapper**:
```java
@Mapper
public interface PlanMapper extends BaseMapper<PlanPO> {
    // 继承BaseMapper，自动获得CRUD方法
    // - insert(PlanPO)
    // - selectById(String)
    // - selectPage(Page, QueryWrapper)
    // - updateById(PlanPO)
    // - deleteById(String)
}
```

#### 2.5.2 PO对象 (Persistence Object)

##### PlanPO

**文件**: `infrastructure/persistence/po/PlanPO.java`

**设计**:
```java
@TableName("plans")
public class PlanPO {
    @TableId
    private String plan_id;              // 主键
    private String plan_request_id;      // 关联PlanRequest
    private String user_id;              // 关联User
    private String plan_type;            // budget/standard/premium
    private String plan_name;            // 方案名称
    private String summary;              // 摘要
    private String highlights;           // 亮点 (JSON数组)
    private String itinerary;            // 行程 (JSON)
    private String budget_breakdown;     // 预算明细 (JSON)
    private String supplier_snapshots;   // 供应商快照 (JSON数组)
    private BigDecimal budget_total;     // 总预算
    private BigDecimal budget_per_person;// 人均预算
    private Integer duration_days;       // 天数
    private String departure_city;       // 出发城市
    private String status;               // draft/CONFIRMED
    private Instant confirmed_time;      // 确认时间

    // Getter/Setter...

    // 从Map构建PO（用于AI回调）
    public static PlanPO fromMap(Map<String, Object> m) {
        PlanPO po = new PlanPO();
        po.plan_id = (String) m.getOrDefault("plan_id", IdGenerator.newId("plan"));
        po.plan_type = (String) m.getOrDefault("plan_type", "standard");
        po.plan_name = (String) m.getOrDefault("plan_name", "");
        po.summary = (String) m.getOrDefault("summary", "");
        po.highlights = JsonHelper.safeJson(m.get("highlights"));
        po.itinerary = JsonHelper.safeJson(m.get("itinerary"));
        po.budget_breakdown = JsonHelper.safeJson(m.get("budget_breakdown"));
        po.supplier_snapshots = JsonHelper.safeJson(m.get("supplier_snapshots"));
        po.budget_total = JsonHelper.safeDecimal(m.get("budget_total"));
        po.budget_per_person = JsonHelper.safeDecimal(m.get("budget_per_person"));
        po.duration_days = JsonHelper.safeInt(m.get("duration_days"));
        po.departure_city = (String) m.getOrDefault("departure_city", "");
        po.status = (String) m.getOrDefault("status", "draft");
        return po;
    }
}
```

**设计要点**:
- **JSON字段**: `highlights`, `itinerary`, `budget_breakdown`, `supplier_snapshots`存储为TEXT
- **fromMap方法**: 便于从AI服务回调的Map构建PO
- **snake_case命名**: 字段名与数据库列名一致

##### PlanRequestPO

**文件**: `infrastructure/persistence/po/PlanRequestPO.java`

**设计**:
```java
@TableName("plan_requests")
public class PlanRequestPO {
    @TableId
    private String plan_request_id;
    private String user_id;
    private Integer people_count;
    private BigDecimal budget_min;
    private BigDecimal budget_max;
    private String start_date;           // YYYY-MM-DD
    private String end_date;             // YYYY-MM-DD
    private String departure_city;
    private String preferences;          // JSON字符串
    private String status;               // GENERATING/COMPLETED/FAILED
    private Instant generation_started_at;
    private Instant generation_completed_at;

    // Getter/Setter...
}
```

##### DomainEventPO

**文件**: `infrastructure/persistence/po/DomainEventPO.java`

**设计**:
```java
@TableName("domain_events")
public class DomainEventPO {
    @TableId
    private String event_id;
    private String event_type;           // PlanRequestCreated, PlanGenerated, ...
    private String aggregate_type;       // PlanRequest, Plan, User, ...
    private String aggregate_id;         // 聚合根ID
    private String user_id;              // 操作用户
    private String payload;              // JSON payload
    private Instant occurred_at;         // 事件发生时间
    private Boolean processed;           // 是否已处理

    // Getter/Setter...
}
```

**用途**:
- Event Sourcing
- 数据分析（用户行为追踪）
- 异步事件处理（未来可集成）

---

## 3. 核心业务流程

### 3.1 微信登录流程

**时序图**:
```
小程序              AuthController        AuthService       UserMapper       Redis
  │                      │                    │                 │              │
  │──wx.login()──────────┤                    │                 │              │
  │                      │                    │                 │              │
  │──POST /api/v1/auth/──┤                    │                 │              │
  │   wechat/login       │                    │                 │              │
  │   {code, nickname,   │                    │                 │              │
  │    avatarUrl}        │                    │                 │              │
  │                      │                    │                 │              │
  │                      │──loginWithWeChat()─┤                 │              │
  │                      │                    │                 │              │
  │                      │                    │──调用微信API─────┤              │
  │                      │                    │  (code→openid)  │              │
  │                      │                    │                 │              │
  │                      │                    │──查询用户────────┤              │
  │                      │                    │  (wechat_openid)│              │
  │                      │                    │                 │              │
  │                      │                    │◄─UserPO or null─┤              │
  │                      │                    │                 │              │
  │                      │                    │──insert/update──┤              │
  │                      │                    │  UserPO         │              │
  │                      │                    │                 │              │
  │                      │                    │──生成JWT Token───┤              │
  │                      │                    │                 │              │
  │                      │                    │──存储Session─────┼──SET────────┤
  │                      │                    │                 │  session:uid │
  │                      │                    │                 │              │
  │                      │◄─LoginResponse─────┤                 │              │
  │◄─────────────────────┤  {sessionToken,    │                 │              │
  │  200 OK              │   userInfo}        │                 │              │
  │                      │                    │                 │              │
  │──存储sessionToken─────┤                    │                 │              │
  │  到LocalStorage      │                    │                 │              │
```

**关键步骤**:
1. 小程序调用`wx.login()`获取`code`
2. 小程序调用后端`POST /api/v1/auth/wechat/login`
3. 后端调用微信API将`code`换成`openid`（当前是伪实现）
4. 根据`openid`查询用户：
   - **新用户**: 创建用户记录
   - **老用户**: 更新昵称/头像（如果提供且有变化）
5. 生成JWT Token
6. 存储Session到Redis（key: `session:<user_id>`, value: token, TTL: 24h）
7. 返回`sessionToken`和`userInfo`
8. 小程序存储`sessionToken`到LocalStorage

**生产环境改进点**:
- 集成真实微信OAuth API (`https://api.weixin.qq.com/sns/jscode2session`)
- 增加安全校验（签名验证、频率限制）

### 3.2 方案生成请求流程

**时序图**:
```
小程序         PlanController    PlanService    PlanRequestMapper  RabbitMQ  Python AI服务
  │                 │                │                 │             │            │
  │──POST /api/v1/──┤                │                 │             │            │
  │   plans/generate│                │                 │             │            │
  │   + Auth header │                │                 │             │            │
  │                 │                │                 │             │            │
  │                 │──校验Token──────┤                 │             │            │
  │                 │  getUserId()   │                 │             │            │
  │                 │                │                 │             │            │
  │                 │──createPlanReq─┤                 │             │            │
  │                 │   AndPublish() │                 │             │            │
  │                 │                │                 │             │            │
  │                 │                │──生成plan_req_id─┤             │            │
  │                 │                │  (ULID)         │             │            │
  │                 │                │                 │             │            │
  │                 │                │──insert─────────┤             │            │
  │                 │                │  PlanRequestPO  │             │            │
  │                 │                │  (status:       │             │            │
  │                 │                │   GENERATING)   │             │            │
  │                 │                │                 │             │            │
  │                 │                │──recordEvent────┤             │            │
  │                 │                │  (PlanRequest   │             │            │
  │                 │                │   Created)      │             │            │
  │                 │                │                 │             │            │
  │                 │                │──convertAndSend─┼─publish─────┤            │
  │                 │                │  (exchange,     │  JSON msg   │            │
  │                 │                │   routingKey,   │             │            │
  │                 │                │   message)      │             │            │
  │                 │                │                 │             │            │
  │                 │◄─GenerateResp──┤                 │             │            │
  │◄────────────────┤  {plan_req_id, │                 │             │            │
  │  200 OK         │   status:      │                 │             │            │
  │                 │   generating}  │                 │             │            │
  │                 │                │                 │             │            │
  │                 │                │                 │             │──consume────┤
  │                 │                │                 │             │  MQ msg     │
  │                 │                │                 │             │             │
  │                 │                │                 │             │◄─LangGraph──┤
  │                 │                │                 │             │  workflow   │
  │                 │                │                 │             │  (3 plans)  │
  │                 │                │                 │             │             │
  │                 │                │                 │             │◄─POST /int──┤
  │                 │                │                 │             │  ernal/plans│
  │                 │                │                 │             │  /batch     │
  │                 │                │◄────────────────┼─────────────┤             │
  │                 │  InternalPlanCallbackService     │             │             │
  │                 │  .handleGeneratedPlans()         │             │             │
  │                 │  (插入3套方案到plans表)             │             │             │
```

**关键步骤**:
1. 小程序提交生成请求（人数、预算、日期、出发地、偏好）
2. `PlanController`校验Token获取`userId`
3. `PlanService.createPlanRequestAndPublish()`：
   - 生成`plan_request_id` (ULID)
   - 插入`plan_requests`表（状态: GENERATING）
   - 记录领域事件`PlanRequestCreated`
   - 发送MQ消息到RabbitMQ
4. 立即返回`plan_request_id`给前端（不等待AI生成）
5. Python AI服务消费MQ消息
6. 执行LangGraph工作流生成3套方案
7. 回调Java服务`POST /internal/plans/batch`
8. `InternalPlanCallbackService.handleGeneratedPlans()`：
   - 插入3套方案到`plans`表
   - 记录3个`PlanGenerated`事件
   - 更新`plan_requests.status`为`COMPLETED`

**异步处理优势**:
- 前端无需等待AI生成（可能需要10-60秒）
- 解耦Java和Python服务
- 支持重试和错误恢复

### 3.3 方案查询流程

**时序图**:
```
小程序         PlanController    PlanService    PlanMapper
  │                 │                │              │
  │──GET /api/v1/───┤                │              │
  │   plans?page=1  │                │              │
  │   pageSize=10   │                │              │
  │   + Auth header │                │              │
  │                 │                │              │
  │                 │──校验Token──────┤              │
  │                 │  getUserId()   │              │
  │                 │                │              │
  │                 │──listPlans()───┤              │
  │                 │  (userId, page)│              │
  │                 │                │              │
  │                 │                │──selectPage──┤
  │                 │                │  (Page,      │
  │                 │                │   QueryWrap  │
  │                 │                │   .eq(user_  │
  │                 │                │    id)       │
  │                 │                │   .orderBy   │
  │                 │                │    Desc(...))│
  │                 │                │              │
  │                 │                │◄─Page<PlanPO>│
  │                 │◄─Page对象───────┤              │
  │◄────────────────┤  {records: [], │              │
  │  200 OK         │   total: 15,   │              │
  │                 │   current: 1,  │              │
  │                 │   pages: 2}    │              │
```

**关键点**:
- **权限隔离**: 仅返回当前用户的方案
- **分页查询**: MyBatis Plus自动处理LIMIT/OFFSET
- **排序**: 按创建时间倒序

### 3.4 方案确认流程 (幂等)

**时序图**:
```
小程序         PlanController    PlanService    PlanMapper    DomainEventMapper
  │                 │                │              │                 │
  │──POST /api/v1/──┤                │              │                 │
  │   plans/{planId}│                │              │                 │
  │   /confirm      │                │              │                 │
  │   + Auth header │                │              │                 │
  │                 │                │              │                 │
  │                 │──校验Token──────┤              │                 │
  │                 │  getUserId()   │              │                 │
  │                 │                │              │                 │
  │                 │──confirmPlan() │              │                 │
  │                 │  (userId, id)  │              │                 │
  │                 │                │              │                 │
  │                 │                │──selectById──┤                 │
  │                 │                │  (planId)    │                 │
  │                 │                │              │                 │
  │                 │                │◄─PlanPO──────┤                 │
  │                 │                │              │                 │
  │                 │                │──校验owner────┤                 │
  │                 │                │              │                 │
  │                 │                │──检查status───┤                 │
  │                 │                │  (幂等处理)   │                 │
  │                 │                │              │                 │
  │                 │                │──updateById──┤                 │
  │                 │                │  (status:    │                 │
  │                 │                │   CONFIRMED) │                 │
  │                 │                │              │                 │
  │                 │                │──recordEvent─┼─insert──────────┤
  │                 │                │  (PlanConf   │  DomainEventPO  │
  │                 │                │   irmed)     │                 │
  │                 │                │              │                 │
  │                 │◄─void───────────┤              │                 │
  │◄────────────────┤                │              │                 │
  │  200 OK         │                │              │                 │
```

**幂等性保证**:
```java
if ("CONFIRMED".equalsIgnoreCase(plan.getStatus())) {
    return;  // 已确认，直接返回成功
}
```

**北极星指标**:
- 每次确认记录`PlanConfirmed`事件
- 通过`SELECT COUNT(*) FROM domain_events WHERE event_type='PlanConfirmed'`统计确认数

### 3.5 供应商联系记录流程

**时序图**:
```
小程序         PlanController    PlanService    SupplierContactLogMapper  DomainEventMapper
  │                 │                │                     │                      │
  │──POST /api/v1/──┤                │                     │                      │
  │   plans/{planId}│                │                     │                      │
  │   /supplier-    │                │                     │                      │
  │   contacts      │                │                     │                      │
  │   {supplier_id, │                │                     │                      │
  │    channel,     │                │                     │                      │
  │    notes}       │                │                     │                      │
  │                 │                │                     │                      │
  │                 │──logSupplier───┤                     │                      │
  │                 │   Contact()    │                     │                      │
  │                 │                │                     │                      │
  │                 │                │──生成contact_id──────┤                      │
  │                 │                │  (ULID)             │                      │
  │                 │                │                     │                      │
  │                 │                │──insert─────────────┤                      │
  │                 │                │  SupplierContactPO  │                      │
  │                 │                │                     │                      │
  │                 │                │──recordEvent────────┼──insert──────────────┤
  │                 │                │  (SupplierContacted)│  DomainEventPO       │
  │                 │                │                     │                      │
  │                 │◄─void───────────┤                     │                      │
  │◄────────────────┤                │                     │                      │
  │  200 OK         │                │                     │                      │
```

**用途**:
- 转化漏斗分析（方案确认 → 联系供应商 → 成单）
- 供应商热度统计
- CRM数据源

---

## 4. 数据持久化设计

### 4.1 MyBatis Plus配置

**文件**: `infrastructure/config/MybatisPlusConfig.java`

**配置**:
```java
@Configuration
public class MybatisPlusConfig {
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        // 添加分页插件
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor());
        return interceptor;
    }
}
```

**application.yml配置**:
```yaml
mybatis-plus:
  mapper-locations: classpath*:/mapper/**/*.xml
  type-aliases-package: com.teamventure.domain.model
  configuration:
    map-underscore-to-camel-case: true  # 下划线转驼峰
    log-impl: org.apache.ibatis.logging.slf4j.Slf4jImpl
    cache-enabled: false  # 禁用二级缓存
  global-config:
    db-config:
      id-type: INPUT  # 手动输入ID（使用ULID）
      logic-delete-field: deleted  # 逻辑删除字段
      logic-delete-value: 1
      logic-not-delete-value: 0
```

### 4.2 数据库表设计

#### 4.2.1 核心表

**users (用户表)**:
```sql
CREATE TABLE users (
  user_id VARCHAR(64) PRIMARY KEY,
  wechat_openid VARCHAR(128) UNIQUE,
  nickname VARCHAR(100),
  avatar_url VARCHAR(500),
  phone VARCHAR(20),
  company VARCHAR(200),
  role VARCHAR(20) DEFAULT 'user',
  status VARCHAR(20) DEFAULT 'active',
  create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_openid (wechat_openid),
  INDEX idx_status (status)
);
```

**plan_requests (方案请求表)**:
```sql
CREATE TABLE plan_requests (
  plan_request_id VARCHAR(64) PRIMARY KEY,
  user_id VARCHAR(64) NOT NULL,
  people_count INT NOT NULL,
  budget_min DECIMAL(10,2) NOT NULL,
  budget_max DECIMAL(10,2) NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  departure_city VARCHAR(100),
  preferences JSON,
  status VARCHAR(20) DEFAULT 'GENERATING',
  generation_started_at TIMESTAMP,
  generation_completed_at TIMESTAMP,
  create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_id (user_id),
  INDEX idx_status (status),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

**plans (方案表)**:
```sql
CREATE TABLE plans (
  plan_id VARCHAR(64) PRIMARY KEY,
  plan_request_id VARCHAR(64) NOT NULL,
  user_id VARCHAR(64) NOT NULL,
  plan_type VARCHAR(20),  -- budget/standard/premium
  plan_name VARCHAR(200),
  summary TEXT,
  highlights JSON,
  itinerary JSON,
  budget_breakdown JSON,
  supplier_snapshots JSON,
  budget_total DECIMAL(10,2),
  budget_per_person DECIMAL(10,2),
  duration_days INT,
  departure_city VARCHAR(100),
  status VARCHAR(20) DEFAULT 'draft',
  confirmed_time TIMESTAMP,
  create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_id (user_id),
  INDEX idx_plan_request_id (plan_request_id),
  INDEX idx_status (status),
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (plan_request_id) REFERENCES plan_requests(plan_request_id)
);
```

**domain_events (领域事件表)**:
```sql
CREATE TABLE domain_events (
  event_id VARCHAR(64) PRIMARY KEY,
  event_type VARCHAR(50) NOT NULL,
  aggregate_type VARCHAR(50) NOT NULL,
  aggregate_id VARCHAR(64) NOT NULL,
  user_id VARCHAR(64),
  payload JSON,
  occurred_at TIMESTAMP NOT NULL,
  processed BOOLEAN DEFAULT FALSE,
  create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_event_type (event_type),
  INDEX idx_aggregate (aggregate_type, aggregate_id),
  INDEX idx_user_id (user_id),
  INDEX idx_processed (processed)
);
```

#### 4.2.2 索引策略

**已创建索引**:
```sql
-- users表
CREATE INDEX idx_openid ON users(wechat_openid);
CREATE INDEX idx_status ON users(status);

-- plan_requests表
CREATE INDEX idx_user_id ON plan_requests(user_id);
CREATE INDEX idx_status ON plan_requests(status);

-- plans表
CREATE INDEX idx_user_id ON plans(user_id);
CREATE INDEX idx_plan_request_id ON plans(plan_request_id);
CREATE INDEX idx_status ON plans(status);

-- domain_events表
CREATE INDEX idx_event_type ON domain_events(event_type);
CREATE INDEX idx_aggregate ON domain_events(aggregate_type, aggregate_id);
CREATE INDEX idx_user_id ON domain_events(user_id);
CREATE INDEX idx_processed ON domain_events(processed);
```

**性能优化索引** (V1.0.2迁移脚本):
```sql
-- 优化方案列表查询（按创建时间倒序）
CREATE INDEX idx_user_create_time ON plans(user_id, create_time DESC);

-- 优化请求历史查询
CREATE INDEX idx_user_request_time ON plan_requests(user_id, create_time DESC);
```

### 4.3 JSON字段处理

**Jsons工具类**:
```java
public class Jsons {
    private static final ObjectMapper MAPPER = new ObjectMapper();

    public static String toJson(Object obj) {
        try {
            return MAPPER.writeValueAsString(obj);
        } catch (JsonProcessingException e) {
            throw new BizException("INTERNAL_ERROR", "json serialization failed");
        }
    }
}
```

**使用示例**:
```java
// 存储
po.setPreferencesJson(Jsons.toJson(req.preferences));

// 读取
String preferencesJson = planRequest.getPreferencesJson();
Map<String, Object> preferences = Jsons.fromJson(preferencesJson, Map.class);
```

### 4.4 分页查询策略

**MyBatis Plus自动分页**:
```java
Page<PlanPO> page = new Page<>(pageNum, pageSize);
Page<PlanPO> result = planMapper.selectPage(
    page,
    new QueryWrapper<PlanPO>()
        .eq("user_id", userId)
        .orderByDesc("create_time")
);

// 返回结果包含：
// - records: List<PlanPO>
// - total: 总记录数
// - size: 每页大小
// - current: 当前页
// - pages: 总页数
```

**SQL示例**:
```sql
SELECT * FROM plans
WHERE user_id = 'user_01ke3abc123'
ORDER BY create_time DESC
LIMIT 10 OFFSET 0;
```

---

## 5. 领域事件机制

### 5.1 事件类型定义

| 事件类型 | 聚合根 | 触发时机 | Payload | 后续动作 |
|---------|--------|---------|---------|---------|
| **WeChatLoginSucceeded** | User | 微信登录成功 | `{user_id, openid}` | 创建Session |
| **PlanRequestCreated** | PlanRequest | 用户提交方案请求 | `{plan_request_id}` | 发送MQ消息 |
| **PlanGenerated** | Plan | AI生成单套方案 | `{plan_id, plan_type}` | 写入plans表 |
| **PlanConfirmed** | Plan | 用户确认方案 | `{plan_id, user_id}` | 北极星指标+1 |
| **SupplierContacted** | SupplierContactLog | 用户联系供应商 | `{plan_id, supplier_id, channel}` | 转化漏斗分析 |

### 5.2 事件记录实现

**recordEvent方法** (在PlanService中):
```java
private void recordEvent(String eventType, String aggregateType, String aggregateId,
                         String userId, Map<String, Object> payload) {
    DomainEventPO evt = new DomainEventPO();
    evt.setEventId(IdGenerator.newId("evt"));
    evt.setEventType(eventType);
    evt.setAggregateType(aggregateType);
    evt.setAggregateId(aggregateId);
    evt.setUserId(userId);
    evt.setPayloadJson(Jsons.toJson(payload));
    evt.setOccurredAt(Instant.now());
    evt.setProcessed(false);
    eventMapper.insert(evt);
}
```

**调用示例**:
```java
// 方案确认事件
recordEvent(
    "PlanConfirmed",
    "Plan",
    planId,
    userId,
    Map.of("plan_id", planId, "confirmed_at", Instant.now())
);
```

### 5.3 Event Sourcing应用

**事件溯源查询示例**:
```sql
-- 查看用户的所有操作历史
SELECT event_type, aggregate_type, aggregate_id, occurred_at, payload
FROM domain_events
WHERE user_id = 'user_01ke3abc123'
ORDER BY occurred_at DESC;

-- 统计北极星指标（方案确认数）
SELECT COUNT(*) AS total_confirmed
FROM domain_events
WHERE event_type = 'PlanConfirmed';

-- 转化漏斗分析
SELECT
  SUM(CASE WHEN event_type = 'PlanConfirmed' THEN 1 ELSE 0 END) AS confirmed_count,
  SUM(CASE WHEN event_type = 'SupplierContacted' THEN 1 ELSE 0 END) AS contacted_count
FROM domain_events;
```

### 5.4 异步事件处理 (未来扩展)

**设计方案**:
1. 定时任务扫描`processed = false`的事件
2. 根据`event_type`分发到不同的Handler
3. 处理成功后标记`processed = true`

**示例Handler**:
```java
@Component
public class PlanConfirmedEventHandler {
    public void handle(DomainEventPO event) {
        // 发送确认通知给用户
        // 更新数据分析报表
        // 触发CRM系统创建跟进任务
    }
}
```

---

## 6. 中间件集成

### 6.1 Redis Session管理

**配置** (application.yml):
```yaml
spring:
  data:
    redis:
      host: localhost
      port: 6379
      password: redis123456
      database: 0
      timeout: 3000ms
      lettuce:
        pool:
          max-active: 20
          max-idle: 10
          min-idle: 5
          max-wait: 3000ms
```

**Session存储策略**:
```java
// 存储Session
redisTemplate.opsForValue().set(
    "session:" + userId,
    sessionToken,
    24,
    TimeUnit.HOURS
);

// 验证Session
String redisToken = redisTemplate.opsForValue().get("session:" + userId);
if (!token.equals(redisToken)) {
    throw new BizException("UNAUTHENTICATED", "session expired");
}

// 删除Session（登出）
redisTemplate.delete("session:" + userId);
```

**Key设计**:
- **格式**: `session:<user_id>`
- **TTL**: 24小时（可配置）
- **数据结构**: String

### 6.2 RabbitMQ消息队列

**配置** (application.yml):
```yaml
spring:
  rabbitmq:
    host: localhost
    port: 5672
    username: admin
    password: admin123456
    virtual-host: /
    listener:
      simple:
        acknowledge-mode: manual  # 手动确认
        prefetch: 5
        retry:
          enabled: true
          max-attempts: 3
          initial-interval: 1000ms

teamventure:
  mq:
    exchange:
      plan-generation: plan.generation.topic
    queue:
      ai-gen-request: ai.gen.req.queue
    routing-key:
      plan-request: plan.request.#
```

**Exchange/Queue设计**:
```
Exchange: plan.generation.topic (Topic类型)
  ├── Queue: ai.gen.req.queue
  │   └── Binding: plan.request.#
  │
  └── Consumer: Python AI服务
```

**发送消息** (在PlanService中):
```java
rabbitTemplate.convertAndSend(exchange, routingKey, Jsons.toJson(message));
```

**消息格式**:
```json
{
  "plan_request_id": "plan_req_01ke3cnw4t5dvp8jhjvfdafq1v",
  "user_id": "user_01ke3abc123",
  "people_count": 50,
  "budget_min": 10000,
  "budget_max": 15000,
  "start_date": "2026-02-01",
  "end_date": "2026-02-03",
  "departure_city": "Beijing",
  "preferences": {
    "activity_types": ["team_building", "leisure"],
    "accommodation_level": "standard",
    "dining_style": ["bbq", "hotpot"]
  },
  "trace_id": "trace_01ke3d456"
}
```

### 6.3 MySQL主从分离

**配置** (application.yml):
```yaml
spring:
  datasource:
    type: com.alibaba.druid.pool.DruidDataSource
    druid:
      # 主库（写操作）
      master:
        url: jdbc:mysql://localhost:3306/teamventure_main?useSSL=false&serverTimezone=Asia/Shanghai
        username: root
        password: root123456
        driver-class-name: com.mysql.cj.jdbc.Driver

      # 从库（读操作）
      slave:
        url: jdbc:mysql://localhost:3307/teamventure_main?useSSL=false&serverTimezone=Asia/Shanghai
        username: root
        password: root123456
        driver-class-name: com.mysql.cj.jdbc.Driver

      # 连接池配置
      initial-size: 5
      min-idle: 5
      max-active: 20
      max-wait: 60000
```

**读写分离策略**:
- **写操作**: INSERT, UPDATE, DELETE → 主库
- **读操作**: SELECT → 从库（负载均衡）
- **事务内**: 全部路由到主库

**Druid监控**:
```yaml
druid:
  stat-view-servlet:
    enabled: true
    url-pattern: /druid/*
    login-username: admin
    login-password: admin123456

  filter:
    stat:
      enabled: true
      log-slow-sql: true
      slow-sql-millis: 2000  # 慢SQL阈值
```

访问监控面板: `http://localhost:8080/druid/`

---

## 7. 异常处理与安全

### 7.1 BizException设计

**文件**: `app/support/BizException.java`

**实现**:
```java
public class BizException extends RuntimeException {
    private final String code;

    public BizException(String code, String message) {
        super(message);
        this.code = code;
    }

    public BizException(String code) {
        this(code, code);
    }

    public String getCode() {
        return code;
    }
}
```

**使用示例**:
```java
// 资源不存在
throw new BizException("NOT_FOUND", "plan not found");

// 权限不足
throw new BizException("UNAUTHORIZED", "not owner");

// 参数错误
throw new BizException("INVALID_ARGUMENT", "budget_min must <= budget_max");
```

### 7.2 GlobalExceptionHandler

**文件**: `adapter/web/common/GlobalExceptionHandler.java`

**实现**:
```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BizException.class)
    public ResponseEntity<ApiResponse<Void>> handleBiz(BizException e) {
        HttpStatus status = HttpStatus.BAD_REQUEST;
        if ("UNAUTHENTICATED".equals(e.getCode())) {
            status = HttpStatus.UNAUTHORIZED;  // 401
        }
        if ("UNAUTHORIZED".equals(e.getCode())) {
            status = HttpStatus.FORBIDDEN;  // 403
        }
        return ResponseEntity.status(status)
                .body(ApiResponse.failure(e.getCode(), e.getMessage()));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleGeneric(Exception e) {
        // 记录日志
        logger.error("Unhandled exception", e);

        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.failure("INTERNAL_ERROR", "Internal server error"));
    }
}
```

**错误码映射**:
| 错误码 | HTTP状态 | 说明 |
|-------|---------|------|
| UNAUTHENTICATED | 401 | 未登录或Token过期 |
| UNAUTHORIZED | 403 | 无权访问 |
| NOT_FOUND | 404 | 资源不存在 |
| INVALID_ARGUMENT | 400 | 参数验证失败 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

### 7.3 ApiResponse统一响应

**文件**: `adapter/web/common/ApiResponse.java`

**实现**:
```java
public class ApiResponse<T> {
    private boolean success;
    private T data;
    private ApiError error;

    public static <T> ApiResponse<T> success(T data) {
        ApiResponse<T> resp = new ApiResponse<>();
        resp.success = true;
        resp.data = data;
        return resp;
    }

    public static ApiResponse<Void> success() {
        return success(null);
    }

    public static ApiResponse<Void> failure(String code, String message) {
        ApiResponse<Void> resp = new ApiResponse<>();
        resp.success = false;
        resp.error = new ApiError(code, message);
        return resp;
    }

    // Getter/Setter...
}

public class ApiError {
    private String code;
    private String message;

    public ApiError(String code, String message) {
        this.code = code;
        this.message = message;
    }

    // Getter/Setter...
}
```

**响应格式**:
```json
// 成功
{
  "success": true,
  "data": { "plan_id": "plan_01ke3d123", ... },
  "error": null
}

// 失败
{
  "success": false,
  "data": null,
  "error": {
    "code": "NOT_FOUND",
    "message": "plan not found"
  }
}
```

### 7.4 权限验证设计

**用户权限校验**:
```java
// 在PlanService.getPlanDetail()中
if (!userId.equals(plan.getUserId())) {
    throw new BizException("UNAUTHORIZED", "not owner");
}
```

**内部接口Secret校验**:
```java
// 在InternalPlanController中
if (!internalSecret.equals(secret)) {
    return ApiResponse.failure("UNAUTHORIZED", "invalid internal secret");
}
```

**JWT Token验证**:
```java
// 在AuthService.getUserIdFromAuthorization()中
String userId = jwtSupport.extractUserId(token);
if (userId == null) {
    throw new BizException("UNAUTHENTICATED", "invalid token");
}

String redisToken = redisTemplate.opsForValue().get("session:" + userId);
if (!token.equals(redisToken)) {
    throw new BizException("UNAUTHENTICATED", "session expired");
}
```

---

## 8. 配置管理

### 8.1 配置文件结构

**application.yml** (多环境配置):
```yaml
spring:
  profiles:
    active: dev  # 默认开发环境

---
# 开发环境
spring:
  config:
    activate:
      on-profile: dev

teamventure:
  wechat:
    appid: your_wechat_appid
    secret: your_wechat_secret

  ai-service:
    url: http://localhost:8000
    timeout: 300000
    callback-secret: change-this-in-production

---
# 生产环境
spring:
  config:
    activate:
      on-profile: prod

  datasource:
    druid:
      master:
        url: jdbc:mysql://prod-master-host:3306/teamventure_main?useSSL=true
      slave:
        url: jdbc:mysql://prod-slave-host:3307/teamventure_main?useSSL=true

  data:
    redis:
      host: prod-redis-host
      password: ${REDIS_PASSWORD}  # 环境变量

  rabbitmq:
    host: prod-rabbitmq-host
    password: ${RABBITMQ_PASSWORD}

teamventure:
  ai-service:
    callback-secret: ${AI_SERVICE_CALLBACK_SECRET}

logging:
  level:
    root: WARN
    com.teamventure: INFO
```

### 8.2 敏感配置管理

**生产环境最佳实践**:
1. **环境变量**: 数据库密码、Redis密码、RabbitMQ密码
2. **配置中心**: 使用Spring Cloud Config或Nacos
3. **加密存储**: 敏感配置使用Jasypt加密

**示例 - 环境变量注入**:
```yaml
spring:
  datasource:
    druid:
      master:
        password: ${MYSQL_MASTER_PASSWORD}
```

**Docker Compose环境变量**:
```yaml
services:
  java-business-service:
    environment:
      MYSQL_MASTER_PASSWORD: ${MYSQL_MASTER_PASSWORD}
      REDIS_PASSWORD: ${REDIS_PASSWORD}
```

---

## 9. 监控与运维

### 9.1 Spring Boot Actuator

**配置** (application.yml):
```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: always
```

**健康检查**:
```bash
curl http://localhost:8080/actuator/health

# 响应
{
  "status": "UP",
  "components": {
    "db": {
      "status": "UP",
      "details": {
        "database": "MySQL",
        "validationQuery": "isValid()"
      }
    },
    "redis": {
      "status": "UP",
      "details": {
        "version": "7.0.0"
      }
    },
    "rabbit": {
      "status": "UP",
      "details": {
        "version": "3.12.0"
      }
    }
  }
}
```

**指标监控**:
```bash
curl http://localhost:8080/actuator/metrics/jvm.memory.used
curl http://localhost:8080/actuator/metrics/http.server.requests
```

### 9.2 Druid监控

访问监控面板:
```
http://localhost:8080/druid/
用户名: admin
密码: admin123456
```

**监控指标**:
- SQL执行统计
- 慢SQL记录
- 连接池状态
- URI请求统计

### 9.3 日志配置

**日志格式** (application.yml):
```yaml
logging:
  level:
    root: INFO
    com.teamventure: DEBUG
    com.alibaba.cola: DEBUG
  pattern:
    console: '%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n'
```

**日志示例**:
```
2026-01-04 15:30:00.123 [http-nio-8080-exec-1] INFO  c.t.a.w.p.PlanController -
  Received plan generation request: userId=user_01ke3abc123, people_count=50

2026-01-04 15:30:00.456 [http-nio-8080-exec-1] DEBUG c.t.a.s.PlanService -
  Created plan_request_id: plan_req_01ke3cnw4t5dvp8jhjvfdafq1v

2026-01-04 15:30:00.789 [http-nio-8080-exec-1] INFO  c.t.a.s.PlanService -
  Published MQ message to exchange: plan.generation.topic, routingKey: plan.request.#
```

### 9.4 Prometheus集成

**Prometheus端点**:
```
http://localhost:8080/actuator/prometheus
```

**关键指标**:
- `http_server_requests_seconds`: HTTP请求耗时
- `jvm_memory_used_bytes`: JVM内存使用
- `jdbc_connections_active`: 数据库连接数
- `rabbitmq_published_total`: MQ消息发送数

**Grafana Dashboard配置**:
```yaml
# 导入Spring Boot 2.x dashboard
# Dashboard ID: 4701
# Data Source: Prometheus
```

---

## 附录

### A. 关键代码文件清单

**Adapter层**:
- `adapter/web/plans/PlanController.java` (87行)
- `adapter/web/auth/AuthController.java`
- `adapter/web/internal/InternalPlanController.java` (44行)
- `adapter/web/suppliers/SupplierController.java`
- `adapter/web/common/GlobalExceptionHandler.java` (26行)
- `adapter/web/common/ApiResponse.java` (38行)

**App层**:
- `app/service/PlanService.java` (154行)
- `app/service/AuthService.java`
- `app/service/InternalPlanCallbackService.java` (64行)
- `app/service/SupplierService.java` (38行)
- `app/service/Jsons.java` (17行)

**App Support**:
- `app/support/BizException.java` (19行)
- `app/support/IdGenerator.java` (10行)
- `app/support/JwtSupport.java`

**Infrastructure**:
- `infrastructure/config/MybatisPlusConfig.java` (18行)
- `infrastructure/config/DataSourceConfig.java`
- `infrastructure/persistence/mapper/*.java` (7个Mapper接口)
- `infrastructure/persistence/po/*.java` (6个PO对象)

**配置文件**:
- `resources/application.yml` (189行)

### B. API端点清单

**认证接口**:
- `POST /api/v1/auth/wechat/login`

**方案接口**:
- `POST /api/v1/plans/generate`
- `GET /api/v1/plans?page=1&pageSize=10`
- `GET /api/v1/plans/{planId}`
- `POST /api/v1/plans/{planId}/confirm`
- `POST /api/v1/plans/{planId}/supplier-contacts`

**供应商接口**:
- `GET /api/v1/suppliers/search?city=Beijing&category=accommodation`
- `GET /api/v1/suppliers/{supplierId}`

**内部接口**:
- `POST /internal/plans/batch` (仅AI服务可调用)

**监控接口**:
- `GET /actuator/health`
- `GET /actuator/metrics`
- `GET /actuator/prometheus`
- `GET /druid/`

### C. 数据库迁移脚本

**V1.0.0__init.sql**: 初始化schema
**V1.0.1__extend_id_fields.sql**: 扩展ID字段长度（VARCHAR(32) → VARCHAR(64)）
**V1.0.2__add_performance_indexes.sql**: 添加性能优化索引

---

**文档版本**: v1.0
**最后更新**: 2026-01-04
**维护者**: TeamVenture开发团队
