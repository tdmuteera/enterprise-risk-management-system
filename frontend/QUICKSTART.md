# ERM Frontend - Quick Start Guide

## 📦 Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Start development server
npm run dev
```

Visit `http://localhost:5173`

## 🏗️ Architecture Overview

### API Layer (`src/api/`)
- **Axios client** with automatic Bearer token injection
- **Request interceptor** — attaches token from localStorage
- **Response interceptor** — redirects to /login on 401
- **Typed API functions** per domain (auth, risk, department, alert, mitigation, report)

```typescript
// Usage example
const { data: risks } = useRisks()
const createRisk = useCreateRisk()
```

### State Management (`src/context/`)
- **AuthContext** — user, token, auth methods
- **AlertContext** — notification counts

### Data Fetching (`src/hooks/`)
- React Query v5 with sensible defaults
- 5-minute stale time for queries
- Auto-refetch on mutations
- Unread alerts refresh every 30s

### UI Components (`src/components/`)
- **Layout** — Sidebar, Navbar, PageContainer, ProtectedRoute
- **UI** — Button, Badge, Card, Alert, Spinner
- **Risk** — RiskCard, RiskBadge, RiskTable, RiskHeatmap, RiskChainGraph
- **Charts** — Stubs ready for Recharts integration
- **Forms** — Stubs for React Hook Form + Zod

### Pages (`src/pages/`)
- Login (fully implemented)
- Dashboard (stats dashboard stub)
- RiskList (grid view stub)
- Others as stubs ready for expansion

## 🎨 Design System

### Colors
```
Risk Levels:
  bg-risk-critical (#D32F2F)
  bg-risk-high     (#F57C00)
  bg-risk-medium   (#FBC02D)
  bg-risk-low      (#388E3C)

Brand:
  bg-brand-dark    (#1F3A6E)  ← Sidebar
  bg-brand-mid     (#2E75B6)  ← Primary accent
  bg-brand-light   (#EBF3FB)  ← Backgrounds
```

### Responsive
- Sidebar: Hamburger on mobile, fixed on desktop
- Grid layouts use Tailwind breakpoints (md:, lg:)
- Touch-friendly padding & button sizes

## 🔐 Authentication

**Login Flow:**
1. User enters email/password on /login
2. API returns token + user data
3. Token stored in localStorage
4. Axios adds Bearer token to all requests
5. 401 errors redirect to /login

**Protected Routes:**
```typescript
<ProtectedRoute requiredRole="admin">
  <Dashboard />
</ProtectedRoute>
```

## 📡 API Integration

**Backend Expected:**
- `POST /api/auth/login` — returns `{ token, user }`
- `GET /api/risks` — returns `Risk[]`
- `GET /api/departments` — returns `Department[]`
- `GET /api/alerts` — returns `Alert[]`
- (All with Bearer token auth)

**Environment:**
```bash
VITE_API_URL=http://localhost:8000/api
```

## 🚀 Next Steps

### 1. Connect to Backend
```bash
# Update .env.local with your API URL
VITE_API_URL=http://your-backend:8000/api
```

### 2. Implement Pages
- Fill in `src/pages/` with full page implementations
- Import components from `src/components/`
- Use hooks from `src/hooks/` for data

### 3. Add Charts
```typescript
// In src/components/charts/index.tsx
import { LineChart, BarChart } from 'recharts'

export const TrendLineChart = ({ data }) => (
  <LineChart data={data}>
    {/* ... */}
  </LineChart>
)
```

### 4. Add Forms
```typescript
// In src/components/forms/index.tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'

export const RiskForm = () => {
  const { register, handleSubmit } = useForm({
    resolver: zodResolver(riskSchema),
  })
  // ...
}
```

### 5. Deploy
```bash
npm run build
# Output in dist/ — ready for production
```

## 📚 Key Files

| File | Purpose |
|------|---------|
| `src/App.tsx` | Root component, providers setup |
| `src/main.tsx` | Entry point |
| `src/index.css` | Global styles + Tailwind |
| `src/api/axiosClient.ts` | HTTP client with interceptors |
| `src/context/AuthContext.tsx` | Auth state & methods |
| `src/router/index.tsx` | Route definitions |
| `src/components/layout/Sidebar.tsx` | Main navigation |
| `src/types/index.ts` | TypeScript interfaces |

## 🧪 Testing

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Build
npm run build
```

## 📖 Documentation

- **Vite** — https://vitejs.dev
- **React Query** — https://tanstack.com/query
- **React Hook Form** — https://react-hook-form.com
- **TailwindCSS** — https://tailwindcss.com
- **Recharts** — https://recharts.org
- **Zod** — https://zod.dev
