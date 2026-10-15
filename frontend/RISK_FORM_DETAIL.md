# Risk Form & Detail Implementation Guide

## Overview

The Risk Form and Risk Detail page are the core interaction points for creating, editing, and viewing risk assessments.

## Risk Form Component

**Location:** `src/components/forms/RiskForm.tsx`  
**Routes:**
- Create: `/risks/new`
- Edit: `/risks/:id/edit`

### Features

#### 1. **Dual-Mode Form** (Create/Edit)
- Automatically loads existing data when editing
- Shows "Create New Risk" header for create mode
- Shows "Edit Risk" header for edit mode

#### 2. **Field Validation** (Zod Schema)
All fields validated on blur and submit:
```typescript
- Title: 5-100 chars (required)
- Description: 20-500 chars (required)
- Category: enum, required
- Department: dropdown, required (auto-selected for dept_user)
- Owner: dropdown from selected department users, required
- Status: dropdown, required
- Likelihood: 1-5, required
- Impact: 1-5, required
- Velocity: 1-5, required
- Detectability: 1-5, required
```

#### 3. **Live Score Preview**
- Right sidebar with live-updating score
- Pure client-side math: `Raw = L × I × V × D`, then `Normalized = Raw / 625`
- Color band badge (Critical/High/Medium/Low)
- Speedometer-style filled bar
- Hint text with mitigation recommendation

#### 4. **Score Sliders**
Four interactive range sliders (1-5):
- **Likelihood**: "How probable?" (Rare → Almost Certain)
- **Impact**: "How severe?" (Negligible → Catastrophic)
- **Velocity**: "How fast?" (Slow → Immediate)
- **Detectability**: "How hidden?" (Easily Detected → Very Hidden)

Each has:
- Tooltip on hover
- Current value display
- Scale labels (1-5)
- Error message if invalid

#### 5. **Submit Behavior**
- **Success**: Toast notification + redirect to `/risks/:id`
- **Validation Error**: Scroll to first error, focus field
- **API Error**: Show error banner with backend message
- **Loading**: Button shows spinner

### Schema & Scoring

**File:** `src/forms/riskSchema.ts`

```typescript
calculateRiskScore(likelihood, impact, velocity, detectability)
  → Raw = L × I × V × D (range: 1-625)
  → Normalized = (Raw / 625) × 100 (range: 0-100)
  → Min(100) to cap at 100

getSeverityBand(score)
  → score >= 75: 'critical' (#D32F2F)
  → score >= 50: 'high' (#F57C00)
  → score >= 25: 'medium' (#FBC02D)
  → else: 'low' (#388E3C)
```

### Components Used

- **Slider** (`src/components/ui/Slider.tsx`)
  - Interactive sliders with gradient fill
  - Read-only bars for detail page
  - Tooltips on hover

- **ScorePreview** (`src/components/ui/Slider.tsx`)
  - Sticky sidebar component
  - Live-updating score display
  - Severity badge & hint
  - Calculation breakdown

- **RiskForm** (`src/components/forms/RiskForm.tsx`)
  - React Hook Form integration
  - Zod validation
  - Responsive 2-col layout (1-col on mobile)

## Risk Detail Page

**Location:** `src/pages/RiskDetail.tsx`  
**Route:** `/risks/:id`

### Sections

#### 1. **Risk Header**
- Title (large, bold)
- Department badge
- Category chip
- Severity color badge
- Risk score (large display)
- Days open
- Edit/Delete buttons

#### 2. **Score Breakdown Card**
Four read-only sliders showing:
- Likelihood, Impact, Velocity, Detectability
- Each displayed as a filled bar (no interaction)

#### 3. **Description Card**
Full risk description text

#### 4. **Tabs: Overview / Audit Trail**

**Overview Tab:**

**Smart Recommendations Card**
- Bulleted list from `/risks/:id/recommendations` endpoint
- 5-6 actionable items based on risk factors
- Example: "Implement segregation of duties", "Conduct quarterly training"

**Mitigation Actions Table**
- List of all linked mitigations
- Columns: Title, Description, Owner, Due Date, Status, Effectiveness
- Add Mitigation button (opens modal)
- Status badges (In-Progress, Completed)
- Effectiveness score

**Audit Trail Tab**
- Vertical timeline of all changes
- Each entry shows:
  - User avatar/name
  - Action (e.g., "Changed Likelihood")
  - Old → New values
  - Timestamp
  - Description/reason

#### 5. **Linked Risks Panel** (Sidebar)
- Chips for each linked risk
- Click to navigate
- Shows link type (Dependency, Related)
- Link Another Risk button

#### 6. **Status Card** (Sidebar)
- Current status badge
- Owner name
- Created date
- Last updated date

#### 7. **Quick Info Card** (Sidebar)
- Probability (1-5)
- Impact (1-5)
- Days open

### Data Fetching

```typescript
useRiskById(id)              // Main risk data
// Expected endpoints:
GET /api/risks/:id/recommendations
GET /api/risks/:id/audit-trail
GET /api/risks/:id/mitigations
GET /api/risks/:id/linked-risks
```

## Risk Heatmap Component

**Location:** `src/components/risk/RiskHeatmap.tsx`

### Features

#### 1. **5×5 CSS Grid**
- X-axis: Likelihood (1→5, bottom labels)
- Y-axis: Impact (1→5, left labels)
- Cells show count of risks at (L, I)

#### 2. **Color Gradient**
```
0 risks:  white
1 risk:   light yellow
2-3:      yellow
4-6:      orange
7+:       red
```

Based on cell count relative to max count in dataset.

#### 3. **Interactions**

**Hover:**
- Cell scales up slightly
- Border becomes darker
- Tooltip shows risk titles

**Click:**
- Cell highlights with ring
- Side panel opens showing risks in mini-table
- Clicking same cell deselects

#### 4. **Legend**
Color scale indicator at bottom:
- White (0 risks)
- Yellow (Low)
- Orange (High)
- Red (Critical)

### Props & Usage

```typescript
<RiskHeatmap risks={riskArray} />

// Where riskArray is Risk[]
// Component groups by (risk.probability, risk.impact)
```

### Styling

- Responsive grid gap
- Aspect ratio squares (1:1)
- Smooth transitions
- Drop shadow text for visibility
- Tailwind colors + custom palette

## API Endpoints Required

### Risk Operations
```
GET /api/risks/:id                    // Fetch risk detail
POST /api/risks                       // Create risk
PATCH /api/risks/:id                 // Update risk
DELETE /api/risks/:id                // Delete risk
```

### Recommendations & History
```
GET /api/risks/:id/recommendations   // Smart recommendations
GET /api/risks/:id/audit-trail       // Audit trail events
GET /api/risks/:id/mitigations       // Linked mitigations
GET /api/risks/:id/linked-risks      // Linked risk relationships
```

## Form Validation Errors

All errors displayed inline:
- Below each field
- Text color: #D32F2F (red)
- Emoji: ⚠️
- Example: "Title must be at least 5 characters"

On submit with errors:
1. Scroll to first error
2. Focus input field
3. Prevent submission

## Hooks

```typescript
useRiskById(id)          // Fetch single risk
useCreateRisk()          // Create mutation
useUpdateRisk()          // Update mutation
useDepartments()         // Fetch departments for dropdown
```

## Next Steps

1. Connect `/api/risks/*` endpoints
2. Implement department user fetching
3. Add recommendation engine logic
4. Implement audit trail backend
5. Test form validation edge cases
6. Optimize heatmap rendering for large datasets
