# Dashboard Implementation Guide

## Overview

Three fully-featured production dashboards have been implemented with Recharts, skeleton loaders, and 60-second auto-refresh using React Query's `refetchInterval`.

## Dashboard 1: Department Dashboard

**Route:** `/dashboard/department/:deptId`

**Access:** dept_user (own dept), risk_officer, admin

**Key Features:**
- 4 KPI cards with trend indicators (Critical, High, Overdue)
- Top 5 risks table with sorting & actions
- Risk distribution pie chart (donut style)
- Risk heatmap (5x5 grid: Likelihood × Impact)
- 30-day trend line chart (avg risk score)
- Mitigation tracker with overdue highlighting

**Data Updates:**
All queries refresh every 60 seconds via React Query `refetchInterval: 60000`

**Skeleton Loaders:**
- `SkeletonCard` for KPIs
- `SkeletonTable` for risk & mitigation tables
- `SkeletonChart` for charts

**Color Coding:**
- Risk severity badges use custom palette
- Trend arrows show ↗ (increasing) / ↘ (decreasing)
- Overdue mitigations highlighted with red left border

## Dashboard 2: Cross-Department Dashboard

**Route:** `/dashboard/cross-department`

**Access:** risk_officer, admin

**Key Features:**
- 4 KPI cards (Inst. IRI, Active Chains, Linked Pairs, Forensic Alerts)
- IRI horizontal bar chart (departments sortable/clickable)
- Risk chain graph visualization stub (ready for react-force-graph)
- Emerging risk chain alerts cards with escalation button

**Risk Chain Detection:**
Each chain card shows:
- Title & description
- Departments involved (badge list)
- Combined IRI score
- Age of detection
- Escalate/View actions

**Drill-Down:**
Click any IRI bar to drill down to department dashboard

## Dashboard 3: Executive Dashboard

**Route:** `/dashboard/executive`

**Access:** executive, admin, risk_officer

**Key Features:**
- Institutional Risk Scorecard (4 large color blocks, boardroom-ready)
  - Click to filter by severity
- IRI trend line (30 days, institution-wide)
- Top 10 board-attention risks table
  - Blinking red dot for IRI > 50
  - Longest open, highest IRI risks
- Active forensic alerts panel
  - Severity chips (critical/high/medium)
  - Department & risk context

**Presentation Mode:**
- Large, bold typography
- High contrast colors
- Auto-refresh every 60s
- Last-update timestamp at bottom

## API Endpoints Required

The dashboards expect these backend endpoints (all auto-authenticated via Bearer token):

### Department Analytics
```
GET /api/dashboard/department/:deptId/analytics
GET /api/dashboard/department/:deptId/top-risks?limit=5
GET /api/dashboard/department/:deptId/heatmap
GET /api/dashboard/department/:deptId/mitigations
```

### Cross-Department
```
GET /api/dashboard/cross-department/analytics
GET /api/dashboard/cross-department/risk-chains
```

### Executive
```
GET /api/dashboard/executive/metrics
GET /api/dashboard/executive/iri-trend?days=30
GET /api/dashboard/executive/forensic-alerts
```

See `src/api/dashboardApi.ts` for complete endpoint definitions.

## Hooks

All dashboard hooks in `src/hooks/useDashboard.ts`:

```typescript
// Department Dashboard
useDepartmentAnalytics(deptId)        // KPI stats
useDepartmentTopRisks(deptId, 5)      // Risk table
useDepartmentHeatmap(deptId)          // Heatmap data
useDepartmentMitigations(deptId)      // Mitigation tracker

// Cross-Department
useCrossDepartmentAnalytics()         // KPI stats
useRiskChains()                       // Risk chain data

// Executive
useExecutiveMetrics()                 // Top risks + KPIs
useInstitutionIRITrend(30)           // IRI trend line
useForensicAlerts()                   // Alert data
```

All hooks automatically:
- Refetch every 60 seconds
- Use React Query caching
- Show loading states via skeleton loaders

## Components

**KPICard** (`src/components/dashboard/KPICard.tsx`)
```typescript
<KPICard
  label="Critical Risks 🔴"
  value={45}
  change={+5}
  changeLabel="vs last week"
  variant="critical"
  isLoading={false}
/>
```

**Skeleton Loaders** (`src/components/ui/Skeleton.tsx`)
```typescript
<SkeletonCard />          // KPI placeholder
<SkeletonTable rows={5} /> // Table placeholder
<SkeletonChart />         // Chart placeholder
```

## Recharts Integration

All charts use Recharts:

- **Department Dashboard**
  - PieChart (Risk Distribution)
  - LineChart (30-Day Trend)
  - Custom grid (Heatmap)

- **Cross-Department Dashboard**
  - BarChart (IRI Scores, horizontal layout)

- **Executive Dashboard**
  - AreaChart (IRI Trend)
  - BarChart (Top 10 risks in table form)

## Colors & Styling

Risk severity palette (Tailwind + custom colors):
```
Critical: #D32F2F (bg-risk-critical)
High:     #F57C00 (bg-risk-high)
Medium:   #FBC02D (bg-risk-medium)
Low:      #388E3C (bg-risk-low)

Brand:
Dark:     #1F3A6E (sidebar)
Mid:      #2E75B6 (primary)
Light:    #EBF3FB (backgrounds)
```

## Responsive Design

All dashboards are responsive:
- Mobile: Single column
- Tablet (md): 2-3 columns
- Desktop (lg): Full layout (60/40 or 75/25 splits)

## Known Stubs

- **Risk Chain Graph**: Ready for `react-force-graph` integration
  - Currently shows placeholder with count
  - Nodes = risks (colored by severity)
  - Edges = relationships (thickness = weight)
  - Implement with force simulation or D3

## Next Steps

1. **Connect Backend:** Update API base URL in `.env.local`
2. **Test Data:** Populate with mock data from backend
3. **Fine-tune Charts:** Adjust Recharts formatting per brand
4. **Risk Chain Graph:** Implement with force-graph library
5. **Forensic Alerts:** Connect to actual forensic system
6. **Role-Based Access:** Verify access control in ProtectedRoute

## Performance Optimization

- React Query caches for 5 minutes
- 60-second refetch intervals (configurable)
- Skeleton loaders show while fetching
- Lazy-loaded components possible (future)
- All charts memoized by Recharts

## Testing

Mock data structure for each dashboard:

```typescript
// Department Analytics
{
  totalRisks: 24,
  criticalCount: 3,
  highCount: 8,
  criticalChange: +2,
  highChange: -1,
  overdueCount: 5,
  riskDistribution: [...]
}

// Cross-Dept Analytics
{
  institutionIRIScore: 68,
  activeRiskChains: 4,
  linkedRiskPairs: 12,
  departmentScores: [...]
}

// Executive Metrics
{
  criticalRisks: 12,
  highRisks: 35,
  topBoardRisks: [...]
}
```
