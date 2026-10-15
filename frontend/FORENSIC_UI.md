# Forensic UI Components Implementation

## Overview

The forensic UI layer provides intelligent anomaly detection, audit trail analysis, and real-time alert management. These components make the risk management system feel genuinely intelligent by surfacing suspicious patterns and changes.

## 1. Toast Notification System

**File:** `src/context/ToastContext.tsx`

### Features
- Global notification management (no external library)
- Auto-dismiss after 4 seconds
- Manual dismiss X button
- Stack up to 3 toasts (overflow queues silently)
- 4 types: success (green), error (red), warning (amber), info (blue)

### Usage
```typescript
const { addToast } = useToast()

// Add notification
addToast('Risk created successfully', 'success')
addToast('Failed to save', 'error', 5000) // Custom duration
addToast('Forensic scan running...', 'info')
```

### Setup
Wrap app with `ToastProvider` in `App.tsx`:
```typescript
<ToastProvider>
  <Router />
</ToastProvider>
```

## 2. Alerts Bell (Navbar)

**File:** `src/components/navbar/AlertsBell.tsx`

### Features
- Bell icon with red badge (unread count)
- Fetches unread count every 30s
- Click → dropdown with last 5 alerts
- Unread alerts: light blue background
- Mark as read: auto-trigger after 2s hover
- "View All Alerts" link at bottom

### Data Flow
```
useUnreadAlertCount()  (refetches every 30s)
      ↓
useAlerts()            (last 5 alerts)
      ↓
AlertsBell component   (displays + marks as read)
```

### Styling
- Unread: `bg-blue-50`
- Severity icons: 🔴 (critical), 🟠 (high), 🟡 (medium), 🔵 (info)
- Click-outside closes dropdown

## 3. Alerts Page

**Route:** `/alerts`

### Features

#### Filter Tabs
- **All** — All alerts
- **Forensic** — Critical/High severity only
- **High Risk** — High + Critical
- **Overdue** — Title contains "Overdue"
- **Emerging Chain** — Title contains "Chain"

#### Alert Cards
```
┌─────────────────────────────────┐
│ 🔴 ForensicFlag | Suppression    │
│ Score dropped 65pts before audit │
│ Severity: CRITICAL | Forensic    │
│ [View Risk] [Dismiss]            │
└─────────────────────────────────┘
```

Features:
- Severity icon + color badge
- Forensic alerts: red-outlined card (`border-2 border-risk-critical`)
- Linked risk (if any)
- Time ago (relative)
- View Risk & Dismiss buttons
- Grid layout (3 cols on desktop, 2 on tablet, 1 on mobile)

#### Run Forensic Scan Button
- Visible only to `risk_officer` and `admin`
- Calls `POST /api/alerts/forensic-scan`
- Shows progress indicator (spinner)
- Auto-refreshes alert list on completion
- Toast feedback: "Forensic scan completed"

## 4. Forensic Panel Page

**Route:** `/forensic` (risk_officer & admin only)

### Sections

#### 1. Forensic Scan Summary (KPI Cards)
Four cards with metrics:
- Score Suppressions Detected
- Sudden Closures
- Chronic Unresolved Risks
- Active Risk Chains

Color-coded by severity (Critical/High/Medium/Low)

#### 2. Risk Suppression Log Table
```
Risk Title | Before | After | %Drop | Changed By | Date | Days to Report
```

- Sorted by: largest drop % first, then closest deadline
- Color coding:
  - Before score: Critical badge
  - After score: Low badge
  - Drop %: Red (text-risk-critical)
  - Days < 21: Highlighted red
- "Investigate" button per row

#### 3. Chronic Unresolved Risks Table
```
Risk Title | Department | Score | Days Open | Last Action | Actions
```

- Days Open > 90 flagged
- Score colored by severity band
- Last Action: text description
- "Review" button

#### 4. Risk Chain Network
- Placeholder for `react-force-graph` integration
- Shows connected risks via dependency links
- Force-directed layout
- Node colors: severity bands
- Edge thickness: relationship weight

#### 5. Audit Anomaly Feed
- Scrollable list (max-height with overflow)
- Last 20 forensic-flagged events
- Card per event:
  - Type badge (Score Suppression, Sudden Closure, etc.)
  - Severity chip
  - Description
  - Risk title, user, timestamp
  - "Investigate" button

Colors:
- Critical: `bg-red-50 border-l-risk-critical`
- High: `bg-orange-50 border-l-risk-high`

## 5. Audit Trail Page

**Route:** `/audit-trail` (admin & risk_officer only)

### Features

#### Filters (Side-by-side inputs)
- **User** — Text search by email
- **Action** — Dropdown (All, Created, Updated, Deleted, etc.)
- **From Date** — Date picker
- **To Date** — Date picker

#### Main Table
```
Timestamp | User | Action | Risk Affected | Changed Fields | IP Address
```

Columns:
- Timestamp: formatted date/time
- User: email address
- Action: badge (blue bg) — "Created Risk", "Updated Risk", etc.
- Risk Title: linked to detail page (optional)
- Changed Fields: comma-separated list
- IP Address: monospace font

#### Expandable Rows
Click row to expand and show detailed change diff:

```
Previous:
  Likelihood: 2
  Impact: 3

New:
  Likelihood: 5
  Impact: 5
```

Layout:
- 2 columns side-by-side
- Left: `bg-red-50` (Previous)
- Right: `bg-green-50` (New)
- Font: monospace
- Fields highlighted if different

#### Export to Excel
- Button: `Download` icon + "Export to Excel"
- Calls: `GET /api/reports/forensic-audit?filters=...`
- Outputs: CSV with all visible columns
- Filename: `audit-trail-YYYY-MM-DD.csv`

#### Pagination
- 50 records per page
- Cursor-based navigation (Previous/Next)
- Current page indicator: "Showing 1-50 of N records"

## API Endpoints Required

### Alerts
```
GET /api/alerts/unread-count         → { count: number }
GET /api/alerts?unreadOnly=false     → Alert[]
POST /api/alerts/forensic-scan       → void (triggers scan)
PATCH /api/alerts/:id/read           → Alert
DELETE /api/alerts/:id               → void (dismiss)
```

### Forensic
```
GET /api/alerts/forensic-summary     → {
  suppressions: number,
  suddenClosures: number,
  chronicUnresolved: number,
  activeChains: number
}

GET /api/forensic/suppressions       → SuppressionLog[]
GET /api/forensic/chronic-risks      → ChronicRisk[]
GET /api/forensic/anomalies          → AnomalyEvent[]
```

### Audit Trail
```
GET /api/audit-logs?filters=...      → AuditLogEntry[]
GET /api/reports/forensic-audit?...  → CSV file
```

## Component Hierarchy

```
App
├── ToastProvider        ← Wraps all
├── Router
│   ├── Navbar
│   │   └── AlertsBell   ← Global notification bell
│   ├── Sidebar
│   ├── Pages
│   │   ├── AlertsPage   ← /alerts
│   │   ├── ForensicPanel ← /forensic
│   │   └── AuditTrail   ← /audit-trail
```

## Styling

### Colors
- Forensic alerts: `border-2 border-risk-critical` (red outline)
- Suppression log: Score Before = Critical badge, After = Low badge
- Changed fields: Previous = `bg-red-50`, New = `bg-green-50`
- Anomaly feed: Critical = `bg-red-50`, High = `bg-orange-50`

### Responsive
- Desktop: Full layout (tables visible)
- Tablet: Collapsed columns, horizontal scroll
- Mobile: Stack layout, single column

## Performance

- Alerts Bell: Refetch every 30s via React Query
- Toast: 4s auto-dismiss, stack limit 3
- Tables: Client-side filtering, 50-record pagination
- Heatmap: CSS grid (no canvas)

## Testing Mock Data

All pages use mock data—replace with real API calls when backend ready:

```typescript
// Alerts Bell
GET /api/alerts/unread-count → Mock: { count: 3 }

// Alerts Page
GET /api/alerts → Mock: Alert[] (sample 8-10 alerts)

// Forensic Panel
GET /api/forensic/suppressions → Mock: SuppressionLog[] (2-3 entries)
GET /api/forensic/chronic-risks → Mock: ChronicRisk[] (2-3 entries)
GET /api/forensic/anomalies → Mock: AnomalyEvent[] (10-20 entries)

// Audit Trail
GET /api/audit-logs → Mock: AuditLogEntry[] (50 entries for pagination)
```

## Next Steps

1. Wire up backend APIs
2. Implement `react-force-graph` for risk chain visualization
3. Add WebSocket for real-time alert updates
4. Implement CSV export with correct filtering
5. Add forensic recommendation engine
6. Test with production data volumes
