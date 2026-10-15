### ESLint Configuration
Recommended `.eslintrc.cjs` for React + TypeScript projects:

```javascript
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', '.eslintignore'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
  },
}
```

### Adding More Pages to Router

Update `src/router/index.tsx` to import and use real page components:

```typescript
import { DashboardPage } from '@/pages/DashboardPage'
import { RiskListPage } from '@/pages/RiskListPage'

const router = createBrowserRouter([
  {
    path: '/dashboard',
    element: (
      <ProtectedRoute>
        <DefaultLayout>
          <DashboardPage />
        </DefaultLayout>
      </ProtectedRoute>
    ),
  },
  {
    path: '/risks',
    element: (
      <ProtectedRoute>
        <DefaultLayout>
          <RiskListPage />
        </DefaultLayout>
      </ProtectedRoute>
    ),
  },
  // ... more routes
])
```

### Extending Components

Example: Adding a full RiskTable component with Recharts:

```typescript
// src/components/risk/RiskTable.tsx
import { Risk } from '@/types'

export const RiskTable = ({ risks }: { risks: Risk[] }) => {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 border-b">
          <tr>
            <th className="px-6 py-3 text-left text-sm font-medium">Title</th>
            <th className="px-6 py-3 text-left text-sm font-medium">Severity</th>
            <th className="px-6 py-3 text-left text-sm font-medium">Score</th>
            <th className="px-6 py-3 text-left text-sm font-medium">Status</th>
          </tr>
        </thead>
        <tbody>
          {risks.map((risk) => (
            <tr key={risk.id} className="border-b hover:bg-gray-50">
              <td className="px-6 py-4">{risk.title}</td>
              <td className="px-6 py-4">
                <Badge variant={risk.severity}>{risk.severity}</Badge>
              </td>
              <td className="px-6 py-4">{risk.riskScore}</td>
              <td className="px-6 py-4 capitalize">{risk.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

### Environment Variables

Create `.env.local` in the root:

```env
# API Configuration
VITE_API_URL=http://localhost:8000/api

# Optional: Feature flags
# VITE_ENABLE_FORENSICS=true
# VITE_ANALYTICS_KEY=your-key
```

Access in code:
```typescript
const apiUrl = import.meta.env.VITE_API_URL
```

### Building for Production

```bash
npm run build
```

Output in `dist/` directory. Deploy with any static host (Vercel, Netlify, S3, etc.):

```bash
# Example: Deploy to Vercel
vercel --prod

# Example: Deploy to Netlify
netlify deploy --prod --dir dist
```

### Mobile Optimization

The scaffold is mobile-first. Key breakpoints:
- `<768px` — Mobile (Sidebar hamburger)
- `≥768px (md:)` — Tablet/Desktop (Sidebar visible)
- `≥1024px (lg:)` — Large desktop (Multi-column layouts)

All UI components are touch-friendly with appropriate padding/sizing.
