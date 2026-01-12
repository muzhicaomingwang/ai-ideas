# UI Layout Specifications (ASCII Wireframes)

本文件使用 ASCII 艺术图描述小程序的核心页面结构。
生成前端代码时，请严格对应以下组件层级。

## 1. 首页 (Home Page)
**Path**: `pages/home/index`

```text
+-------------------------------------------------------+
|  [NavBar: TeamVenture]                                |
+-------------------------------------------------------+
|  [Header Section]                                     |
|  +-------------------------------------------------+  |
|  |  Greeting: "Hi, {EmployeeName}"                 |  |
|  |  Stat: "Upcoming Events: {Count}"               |  |
|  +-------------------------------------------------+  |
+-------------------------------------------------------+
|  [FilterTabs]                                         |
|  |  [Active: All Events]  [Inactive: My Bookings]  |  |
+-------------------------------------------------------+
|  [SessionList] (Vertical Scroll)                      |
|                                                       |
|  +--[SessionCard Component]------------------------+  |
|  |  [Image: ActivityCover (AspectFill)]            |  |
|  |  [Tag: Status (e.g. "Open")]                    |  |
|  |  **Title**: {ActivityName}                      |  |
|  |  Icon Time: {SessionStartTime} - {EndTime}      |  |
|  |  Icon Location: {LocationName}                  |  |
|  |  [ProgressBar]: {BookedCount}/{MaxCapacity}     |  |
|  +-------------------------------------------------+  |
|                                                       |
|  +--[SessionCard Component]------------------------+  |
|  |  ... (Repeat)                                   |
|  +-------------------------------------------------+  |
+-------------------------------------------------------+
```

## 2. 场次详情页 (Session Detail Page)
**Path**: `pages/session/detail?id={sessionId}`

```text
+-------------------------------------------------------+
|  [NavBar: < Back | Detail]                            |
+-------------------------------------------------------+
|  [ScrollArea]                                         |
|  |                                                    |
|  |  [HeroImage: ActivityCover]                        |
|  |                                                    |
|  |  [InfoCard]                                        |
|  |  |  **Title**: {ActivityName}                      |
|  |  |  [Tag: Status]                                  |
|  |  |  ---------------------------------------------  |
|  |  |  Icon Time: {Date} {StartTime}-{EndTime}        |
|  |  |  Icon Location: {LocationAddress}               |
|  |  |  Icon Host: {OrganizerName}                     |
|  |                                                    |
|  |  [DescriptionSection]                              |
|  |  |  Title: "About Activity"                        |
|  |  |  Text: {ActivityDescription}                    |
|  |                                                    |
|  |  [ParticipantsSection]                             |
|  |  |  Title: "Joined ({Current}/{Max})"              |
|  |  |  [AvatarList: Limit 5 + "More"]                 |
|  |                                                    |
+-------------------------------------------------------+
|  [BottomActionBar] (Fixed Bottom)                     |
|  +-------------------------------------------------+  |
|  |  [Button: Share]   [Button: MainAction]         |  |
|  +-------------------------------------------------+  |
+-------------------------------------------------------+
```

### MainAction Button Logic
The button style and text change based on `UserBookingStatus` and `SessionStatus`:

| User Status | Session Status | Button Text | Button Style | Action |
| :--- | :--- | :--- | :--- | :--- |
| `NONE` | `PUBLISHED` (Not Full) | "Join Now" | Primary | Call `bookSession` |
| `NONE` | `FULL` | "Join Waitlist" | Warning | Call `bookSession` (Waitlist mode) |
| `CONFIRMED` | `PUBLISHED`/`FULL` | "Cancel Booking" | Danger (Outline) | Call `cancelBooking` |
| `WAITING` | `FULL` | "Cancel Waitlist" | Danger (Outline) | Call `cancelBooking` |
| `ANY` | `COMPLETED` | "Ended" | Disabled | None |
