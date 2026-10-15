import { QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/context/AuthContext'
import { AlertProvider } from '@/context/AlertContext'
import { ToastProvider } from '@/context/ToastContext'
import { Router } from '@/router'
import { queryClient } from '@/lib/queryClient'

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AlertProvider>
          <ToastProvider>
            <Router />
          </ToastProvider>
        </AlertProvider>
      </AuthProvider>
    </QueryClientProvider>
  )
}
