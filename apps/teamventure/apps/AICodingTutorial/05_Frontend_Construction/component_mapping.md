# Frontend Component Mapping

此文件指导 AI 如何将设计图 (`page_layouts_ascii.md`) 拆解为具体的代码文件。

## 1. Page Mapping (WeChat Miniprogram)

| ASCII Page Name | File Path | Responsibilities |
| :--- | :--- | :--- |
| **Home Page** | `pages/home/index` | List sessions, handle pull-to-refresh, filter tabs. |
| **Detail Page** | `pages/session/detail` | Show session info, handle booking action, share logic. |
| **My Bookings** | `pages/mine/bookings` | List user's history. |

## 2. Component Mapping (Atomic Design)

| Component Name | Path | Props (Inputs) | Events (Outputs) |
| :--- | :--- | :--- | :--- |
| `SessionCard` | `components/session-card/index` | `session: Object` | `bind:tap` |
| `StatusBadge` | `components/status-badge/index` | `status: String` | - |
| `AvatarList` | `components/avatar-list/index` | `list: Array`, `limit: Number` | - |

## 3. Data Binding Spec (DTO -> ViewModel)

**Backend DTO** (`SessionDTO`):
```json
{
  "id": 1001,
  "startTime": "2026-01-12T18:00:00",
  "status": "PUBLISHED"
}
```

**Frontend ViewModel** (Used in WXML):
```js
{
  id: 1001,
  timeDisplay: "Tonight 18:00", // Computed
  isBookable: true,             // Computed based on status
  statusColor: "green"          // Mapped from design tokens
}
```
