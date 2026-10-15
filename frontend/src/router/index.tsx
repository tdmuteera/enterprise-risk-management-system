import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import { ProtectedRoute } from '@/components/layout/ProtectedRoute'
import { useAuth } from '@/context/AuthContext'

// Layout
import { Sidebar } from '@/components/layout/Sidebar'
import { Navbar } from '@/components/layout/Navbar'
import { PageContainer } from '@/components/layout/PageContainer'

// Pages
import { Login } from '@/pages/Login'
import { Register } from '@/pages/Register'
import { DeptDashboard } from '@/pages/DeptDashboard'
import { CrossDeptDashboard } from '@/pages/CrossDeptDashboard'
import { ExecutiveDashboard } from '@/pages/ExecutiveDashboard'
import { RiskDetail } from '@/pages/RiskDetail'
import { RiskForm } from '@/components/forms/RiskForm'
import { AlertsPage } from '@/pages/AlertsPage'
import { ForensicPanel } from '@/pages/ForensicPanel'
import { AuditTrail } from '@/pages/AuditTrail'
import { ReportsPage } from '@/pages/ReportsPage'
import { RiskListPage } from '@/pages/RiskListPage'
import { DepartmentsPage } from '@/pages/DepartmentsPage'
import { UsersPage } from '@/pages/UsersPage'
import { SettingsPage } from '@/pages/SettingsPage'

const DefaultLayout = ({ children }: { children: React.ReactNode }) => (
  <div className="min-h-screen">
    <Sidebar />
    <Navbar />
    <PageContainer>{children}</PageContainer>
  </div>
)

const DashboardRedirect = () => {
  const { user } = useAuth()

  if (!user) return <Navigate to="/login" replace />

  switch (user.role) {
    case 'dept_user':
    case 'data_clerk':
    case 'risk_clerk':
    case 'department_head': {
      const deptId = user.departmentId || user.department_id
      if (deptId) return <Navigate to={`/dashboard/department/${deptId}`} replace />
      return <Navigate to="/dashboard/cross-department" replace />
    }
    case 'risk_officer':
    case 'risk_manager':
      return <Navigate to="/dashboard/cross-department" replace />
    case 'admin':
    case 'executive':
    case 'viewer':
    default:
      return <Navigate to="/dashboard/executive" replace />
  }
}

const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/register',
    element: <Register />,
  },
  {
    path: '/',
    element: <Navigate to="/dashboard" replace />,
  },
  // Department Dashboard
  {
    path: '/dashboard/department/:deptId',
    element: (
      <ProtectedRoute>
        <DefaultLayout>
          <DeptDashboard />
        </DefaultLayout>
      </ProtectedRoute>
    ),
  },
  // Cross-Department Dashboard
  {
    path: '/dashboard/cross-department',
    element: (
      <ProtectedRoute>
        <DefaultLayout>
          <CrossDeptDashboard />
        </DefaultLayout>
      </ProtectedRoute>
    ),
  },
  // Executive Dashboard
  {
    path: '/dashboard/executive',
    element: (
      <ProtectedRoute>
        <DefaultLayout>
          <ExecutiveDashboard />
        </DefaultLayout>
      </ProtectedRoute>
    ),
  },
  {
    path: '/dashboard',
    element: (
      <ProtectedRoute>
        <DashboardRedirect />
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
  {
    path: '/risks/new',
    element: (
      <ProtectedRoute>
        <DefaultLayout>
          <RiskForm />
        </DefaultLayout>
      </ProtectedRoute>
    ),
  },
  {
    path: '/risks/:id',
    element: (
      <ProtectedRoute>
        <DefaultLayout>
          <RiskDetail />
        </DefaultLayout>
      </ProtectedRoute>
    ),
  },
  {
    path: '/risks/:id/edit',
    element: (
      <ProtectedRoute>
        <DefaultLayout>
          <RiskForm />
        </DefaultLayout>
      </ProtectedRoute>
    ),
  },
  {
    path: '/departments',
    element: (
      <ProtectedRoute>
        <DefaultLayout>
          <DepartmentsPage />
        </DefaultLayout>
      </ProtectedRoute>
    ),
  },
  {
    path: '/alerts',
    element: (
      <ProtectedRoute>
        <DefaultLayout>
          <AlertsPage />
        </DefaultLayout>
      </ProtectedRoute>
    ),
  },
  {
    path: '/forensic',
    element: (
      <ProtectedRoute>
        <DefaultLayout>
          <ForensicPanel />
        </DefaultLayout>
      </ProtectedRoute>
    ),
  },
  {
    path: '/audit-trail',
    element: (
      <ProtectedRoute>
        <DefaultLayout>
          <AuditTrail />
        </DefaultLayout>
      </ProtectedRoute>
    ),
  },
  {
    path: '/reports',
    element: (
      <ProtectedRoute>
        <DefaultLayout>
          <ReportsPage />
        </DefaultLayout>
      </ProtectedRoute>
    ),
  },
  {
    path: '/users',
    element: (
      <ProtectedRoute requiredRole="admin">
        <DefaultLayout>
          <UsersPage />
        </DefaultLayout>
      </ProtectedRoute>
    ),
  },
  {
    path: '/settings',
    element: (
      <ProtectedRoute>
        <DefaultLayout>
          <SettingsPage />
        </DefaultLayout>
      </ProtectedRoute>
    ),
  },
  {
    path: '/unauthorized',
    element: (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">403</h1>
          <p className="text-xl text-gray-600">You do not have access to this page</p>
        </div>
      </div>
    ),
  },
])

export function Router() {
  return <RouterProvider router={router} future={{ v7_startTransition: true }} />
}
