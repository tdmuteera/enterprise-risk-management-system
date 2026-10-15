# Reports Page Implementation Guide

## Overview

The Reports page provides authorized users with the ability to generate and download four distinct report types with role-based access control, customizable parameters, and download history tracking.

## Architecture

### File Structure
```
src/
├── api/reportApi.ts              # Blob download + helper functions
├── pages/ReportsPage.tsx         # Main reports page
└── hooks/
    └── (useReports hook - optional)
```

## Four Report Types

### 1. Department Risk Report

**Route:** `/reports`  
**Access:** dept_user (own dept only), risk_officer, admin

**Inputs:**
- Department (dropdown) — filtered to user's dept for dept_user
- Date Range (start/end date pickers) — default: last 30 days
- Format toggle (PDF | Excel)

**Button:** "Generate Report"

**Filename:** `dept_risk_report_YYYYMMDD.{pdf|xlsx}`

**Response:** Blob (PDF or Excel file)

**Features:**
- Department dropdown populated from `useDepartments()`
- Date pickers default to last 30 days
- Format toggle switches between PDF and Excel
- Disabled state for unauthorized users (opacity-60)
- Lock icon shown if access denied

---

### 2. Institutional Report

**Route:** `/reports`  
**Access:** risk_officer, admin

**Inputs:** None (format fixed to PDF)

**Button:** "Generate Institutional Report"

**Filename:** `institutional_report_YYYYMMDD.pdf`

**Response:** Blob (PDF file)

**Features:**
- No inputs required
- Always generates as PDF
- Institution-wide risk posture included
- Cross-department analysis

---

### 3. Executive Summary

**Route:** `/reports`  
**Access:** executive, risk_officer, admin

**Inputs:** None (always current data)

**Button:** "Download Executive Summary (PDF)"

**Filename:** `executive_summary_YYYYMMDD.pdf`

**Response:** Blob (PDF file)

**Features:**
- Real-time data (no date filtering)
- Boardroom-ready format
- Key metrics and critical risks
- Download icon in button

---

### 4. Forensic Audit Report

**Route:** `/reports`  
**Access:** admin, risk_officer only

**Inputs:**
- Date Range (start/end date pickers) — default: last 90 days

**Button:** "Download Forensic Audit (Excel)"

**Filename:** `forensic_audit_YYYYMMDD.xlsx`

**Response:** Blob (Excel file)

**Features:**
- Red badge: "Admin & Risk Officer Only"
- Lock icon for unauthorized access
- Detailed anomalies, suppressions, audit trail
- Excel format for detailed analysis

---

## API Implementation

### Endpoint Structure
```typescript
GET /api/reports/department?departmentId=X&startDate=Y&endDate=Z&format=pdf
GET /api/reports/institutional?format=pdf
GET /api/reports/executive-summary
GET /api/reports/forensic-audit?startDate=X&endDate=Y
```

### Response Type
All endpoints return **blob** (binary file data):
```typescript
responseType: 'blob'
```

### Error Handling
```typescript
try {
  const blob = await reportApi.generateDepartmentReport(...)
  downloadBlob(blob, filename)
  addToast('Report downloaded successfully', 'success')
} catch (error) {
  addToast('Report generation failed — please try again', 'error')
}
```

---

## Download Implementation

### Helper Functions (reportApi.ts)

#### `downloadBlob(blob, filename)`
```typescript
export const downloadBlob = (blob: Blob, filename: string) => {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
```

Creates object URL, triggers download, cleans up.

#### `getFilenameFromResponse(response, fallback)`
Extracts filename from `Content-Disposition` header if present, otherwise uses fallback pattern.

```
Content-Disposition: attachment; filename="dept_risk_report_20250421.pdf"
```

#### `formatDateForFilename()`
Formats current date as `YYYYMMDD` for filenames.

---

## UX States

### Loading State
```
Button: "Generating..." (with spinner)
Disabled: true
```

Button shows spinner while `loading: true` during API request.

### Success State
```
Toast: "Report downloaded successfully" (green)
Icon: ✓
Auto-dismiss: 4s
```

File downloads automatically via browser download manager.

### Error State
```
Toast: "Report generation failed — please try again" (red)
Icon: ✗
Auto-dismiss: 4s
```

Error caught from API, user can retry.

### Access Denied State
```
Card: opacity-60
Lock Icon: Top-right corner
Button: Disabled
Helper Text: "Only X or Y can access"
```

---

## Recent Reports Panel

### LocalStorage Tracking
```typescript
interface RecentReport {
  id: string                    // timestamp
  type: string                  // report name
  date: string                  // formatted date
  format: string                // 'pdf' | 'excel'
  timestamp: number             // unix ms
}
```

### Storage
```typescript
localStorage.getItem('recentReports')  // JSON array
localStorage.setItem('recentReports', JSON.stringify(updates))
```

### Features
- Track last 5 reports (slice to 5)
- Show type, date, format per row
- "Re-download" button per report
- File icon + metadata display
- Only shown if reports exist

### Data Flow
```
Generate Report
      ↓
Download successful
      ↓
addToHistory(type, format)
      ↓
Update localStorage
      ↓
Re-render Recent Reports panel
```

---

## Role-Based Access Control

### Access Matrix
```
Report Type          | dept_user | risk_officer | admin | executive
─────────────────────┼───────────┼──────────────┼───────┼──────────
Department Risk      |     ✓     |      ✓       |   ✓   |    ✗
Institutional        |     ✗     |      ✓       |   ✓   |    ✗
Executive Summary    |     ✗     |      ✓       |   ✓   |    ✓
Forensic Audit       |     ✗     |      ✓       |   ✓   |    ✗
```

### Implementation
```typescript
const canAccessDeptReport = 
  user?.role === 'dept_user' ||
  user?.role === 'risk_officer' ||
  user?.role === 'admin'

// Apply to button & inputs
disabled={!canAccessDeptReport}
```

---

## Component Hierarchy

```
ReportsPage
├── Department Risk Report Card
│   ├── Department Dropdown
│   ├── Start/End Date Inputs
│   ├── Format Toggle (PDF|Excel)
│   └── Generate Button
├── Institutional Report Card
│   └── Generate Button
├── Executive Summary Card
│   └── Download Button
├── Forensic Audit Report Card
│   ├── Start/End Date Inputs
│   └── Download Button
└── Recent Reports Panel
    └── Report History List (5 items max)
```

---

## State Management

### Form State
```typescript
// Department Report
{
  departmentId: string
  startDate: string        // YYYY-MM-DD
  endDate: string          // YYYY-MM-DD
  format: 'pdf' | 'excel'
  loading: boolean
}

// Forensic Report
{
  startDate: string
  endDate: string
  loading: boolean
}

// Individual flags
execLoading: boolean
instLoading: boolean
```

### Recent Reports
```typescript
recentReports: RecentReport[]  // from localStorage
setRecentReports()            // update state + localStorage
```

---

## Styling

### Card States
- **Enabled:** Full opacity, interactive
- **Disabled:** `opacity-60`, cursor-not-allowed, inputs gray
- **Forensic Alert:** Badge with "Admin & Risk Officer Only"

### Format Toggle
- **Active:** `bg-brand-mid text-white`
- **Inactive:** `bg-gray-200 text-gray-900`

### Recent Reports Row
- **Default:** `bg-gray-50`
- **Hover:** `bg-gray-100` (transition)
- Layout: Icon + metadata | Re-download button

---

## Error Handling

### Validation
```typescript
if (!deptReportState.departmentId) {
  addToast('Please select a department', 'warning')
  return
}
```

### Network Errors
Caught by try/catch, toast notification shown.

### Access Denied
401 redirect to /login handled by Axios interceptor.

---

## Testing with Mock Data

### Mock API Responses
```
GET /api/reports/department → PDF blob (5MB sample)
GET /api/reports/institutional → PDF blob
GET /api/reports/executive-summary → PDF blob
GET /api/reports/forensic-audit → Excel blob
```

### LocalStorage Testing
```javascript
// In browser console
localStorage.setItem('recentReports', JSON.stringify([
  { id: '1', type: 'Department Risk Report', date: '4/21/2025', format: 'pdf', timestamp: 1713710400000 }
]))
```

---

## Performance Considerations

- **Blob download:** Uses native browser API (no streaming)
- **LocalStorage:** 5 items max (minimal footprint)
- **API:** GET requests (no caching needed for file downloads)
- **UI:** Form state local (no global store needed)

---

## Future Enhancements

1. **Scheduled Reports** — Auto-generate on date/time
2. **Email Delivery** — Send reports to recipients
3. **Report Templates** — Custom formats per role
4. **Real-time Preview** — Show report preview before download
5. **Batch Download** — Select multiple reports, zip
6. **Report Library** — Archive all generated reports
