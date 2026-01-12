# Interaction Flows (交互逻辑流)

本文件描述核心业务流程的用户交互逻辑。
后端 API 设计与前端状态管理必须实现此处的逻辑。

## Flow 1: 用户报名 (User Booking Flow)

### 场景
用户在“场次详情页”点击“立即报名” (Join Now) 按钮。

### 交互步骤

1.  **前端校验 (Frontend Validation)**
    *   检查用户是否登录。未登录 -> 跳转登录页。
    *   检查 `SessionStatus` 是否为 `PUBLISHED`。

2.  **发起请求 (API Request)**
    *   `POST /api/v1/bookings`
    *   Body: `{ sessionId: "...", notes: "..." }`
    *   UI 状态：按钮变为 `Loading` 状态，显示全屏遮罩（防止重复点击）。

3.  **后端处理 (Backend Processing)**
    *   **Check 1**: 用户是否已经预约过该场次？(幂等性/业务约束) -> 若是，返回 `400 B_001_ALREADY_BOOKED`。
    *   **Check 2**: 场次是否已结束？ -> 若是，返回 `400 B_002_SESSION_ENDED`。
    *   **Check 3**: 库存检查 (Concurrency Safe)。
        *   尝试扣减库存：`UPDATE t_session SET booked_count = booked_count + 1 WHERE id = ? AND booked_count < max_capacity`
        *   若 Update 失败 (返回 0 行)：
            *   进入 **Waitlist Logic**。
            *   创建状态为 `WAITING` 的 Booking 记录。
            *   返回 `200 OK`，但 Response Body 中 `status: "WAITING"`。
        *   若 Update 成功：
            *   创建状态为 `CONFIRMED` 的 Booking 记录。
            *   返回 `200 OK`，Response Body 中 `status: "CONFIRMED"`。

4.  **前端响应 (Frontend Response)**
    *   UI 关闭 Loading。
    *   **Case A (Confirmed)**:
        *   弹出 Toast: "报名成功！"
        *   刷新页面数据 (Re-fetch Session Detail)。
        *   按钮变为 "Cancel Booking" (Danger Style)。
    *   **Case B (Waitlisted)**:
        *   弹出 Modal: "名额已满，您已加入候补队列 (第 N 位)。"
        *   刷新页面数据。
        *   按钮变为 "Cancel Waitlist"。
    *   **Case C (Error)**:
        *   弹出 Toast (Error): 显示后端返回的 `message`。

## Flow 2: 取消报名 (Cancellation Flow)

### 场景
用户点击 "Cancel Booking" 或 "Cancel Waitlist"。

### 交互步骤
1.  **二次确认 (Confirmation)**
    *   弹出 Dialog: "确定要取消报名吗？如果当前已满员，重新报名可能需要排队。"
    *   用户点击 "Yes"。

2.  **发起请求**
    *   `POST /api/v1/bookings/{bookingId}/cancel`

3.  **后端处理**
    *   将 Booking 状态置为 `CANCELLED`。
    *   **如果是 `CONFIRMED` 的订单**：
        *   释放库存：`booked_count - 1`。
        *   **触发候补晋升 (Promotion Trigger)**: 检查 Waitlist 中最早的一条记录，将其自动转为 `CONFIRMED`，并发送通知。

4.  **前端响应**
    *   Toast: "已取消"。
    *   刷新页面，按钮变回 "Join Now" 或 "Join Waitlist"。
