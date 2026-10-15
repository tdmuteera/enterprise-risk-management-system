# ERM Frontend

Production-grade React 18 + Vite + TypeScript frontend for Enterprise Risk Management.

## Project Structure

```
src/
├── api/                    # API layer with axios + typed functions
│   ├── axiosClient.ts     # Configured axios with interceptors
│   ├── authApi.ts         # Authentication endpoints
│   ├── riskApi.ts         # Risk management endpoints
│   ├── departmentApi.ts   # Department endpoints
│   ├── alertApi.ts        # Alert endpoints
│   ├── mitigationApi.ts   # Mitigation endpoints
│   └── reportApi.ts       # Reports & audit endpoints
├── components/
│   ├── layout/            # Core layouts
│   │   ├── Sidebar.tsx    # Dark navy sidebar with nav
│   │   ├── Navbar.tsx     # Top navigation with search & alerts
│   │   ├── PageContainer.tsx
│   │   └── ProtectedRoute.tsx  # Auth + role-based guards
│   ├── ui/                # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Badge.tsx      # Risk severity badges
│   │   ├── Card.tsx
│   │   ├── Alert.tsx
│   │   └── Spinner.tsx
│   ├── risk/              # Risk-specific components (stubs)
│   ├── charts/            # Chart components (stubs)
│   └── forms/             # Form components (stubs)
├── context/               # State management
│   ├── AuthContext.tsx    # User + token state
│   └── AlertContext.tsx   # Notification alerts
├── hooks/                 # React Query hooks
│   ├── useRisks.ts
│   ├── useAlerts.ts
│   ├── useDepartments.ts
│   └── (others)
├── pages/                 # Page components (stubs)
├── router/                # React Router v6 setup
├── types/                 # TypeScript interfaces
├── utils/                 # Helpers
│   ├── riskColor.ts      # Risk severity color mapping
│   ├── dateFormat.ts     # Date utilities
│   └── exportHelpers.ts  # CSV/JSON export
├── App.tsx               # Root component with providers
├── main.tsx              # Entry point
└── index.css             # Global styles + Tailwind
```

## Tech Stack

- **React 18** — UI framework
- **Vite 5** — Build tool (fast HMR)
- **TypeScript** — Type safety (strict mode)
- **TailwindCSS 3.4** — Utility-first CSS with custom palette
- **React Query v5** — Data fetching & caching
- **React Router v6** — Client-side routing with nested layouts
- **Axios** — HTTP client with interceptors for auth & errors
- **React Hook Form + Zod** — Form validation
- **Recharts** — Chart library (stubs ready)
- **Lucide React** — Icon library

## Color Palette

```
Risk Levels:
  Critical: #D32F2F (red)
  High:     #F57C00 (orange)
  Medium:   #FBC02D (yellow)
  Low:      #388E3C (green)

Brand:
  Dark:  #1F3A6E (sidebar)
  Mid:   #2E75B6 (primary accent)
  Light: #EBF3FB (backgrounds)
```

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Variables

```bash
cp .env.example .env.local
# Edit .env.local with your API URL
```

### 3. Development Server

```bash
npm run dev
```

Opens at `http://localhost:5173`

### 4. Build for Production

```bash
npm run build
```

### 5. Type Check

```bash
npm run type-check
```

## Key Features

### Authentication Flow
- Login page with form validation
- Token persisted in localStorage
- Axios request interceptor attaches Bearer token
- 401 responses auto-redirect to /login

### Protected Routes
- Role-based access control
- Redirect to /unauthorized if role mismatch
- Redirect to /login if not authenticated

### API Layer
- **Typed API functions** per domain (risk, department, alert, etc.)
- **React Query** for caching & refetching
- **Axios interceptors** for automatic token attachment

### Responsive Design
- Sidebar collapses to hamburger on mobile (<768px)
- Tailwind breakpoints built in
- Touch-friendly UI

### Data Fetching
- React Query with 5-minute stale time by default
- Auto-refetch on specific endpoints (alerts every 30s)
- Automatic cache invalidation on mutations

## Development Workflow

### Adding a New Page

1. Create page file in `src/pages/PageName.tsx`
2. Add route in `src/router/index.tsx`
3. Use hooks from `src/hooks/` for data fetching
4. Build UI from `src/components/ui/` and `src/components/layout/`

### Adding a New API Domain

1. Create `src/api/domainApi.ts` with typed functions
2. Create `src/hooks/useDomain.ts` with React Query hooks
3. Use hooks in pages/components

### Styling

- Tailwind classes in JSX
- Custom colors available: `bg-risk-critical`, `text-brand-dark`, etc.
- Global styles in `src/index.css`
- Component-level CSS via Tailwind

## Next Steps

- Implement page components in `src/pages/`
- Add risk-specific components in `src/components/risk/`
- Implement chart components using Recharts in `src/components/charts/`
- Add form components for risk/mitigation creation in `src/components/forms/`
- Connect to backend API (update `VITE_API_URL`)
