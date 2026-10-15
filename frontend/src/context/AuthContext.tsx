import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User } from '@/types'

interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (token: string, user: User) => void
  logout: () => void
  /** Replace stored user (e.g. after profile update). Keeps current token. */
  setUser: (user: User) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Restore from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('authToken')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      try {
        setToken(storedToken)
        setUser(JSON.parse(storedUser))
      } catch {
        localStorage.removeItem('authToken')
        localStorage.removeItem('user')
      }
    }
    setIsLoading(false)
  }, [])

  useEffect(() => {
    const onSessionExpired = () => {
      setToken(null)
      setUser(null)
    }
    window.addEventListener('erm:session-expired', onSessionExpired)
    return () => window.removeEventListener('erm:session-expired', onSessionExpired)
  }, [])

  const login = (newToken: string, newUser: User) => {
    localStorage.setItem('authToken', newToken)
    localStorage.setItem('user', JSON.stringify(newUser))
    setToken(newToken)
    setUser(newUser)
  }

  const logout = () => {
    localStorage.removeItem('authToken')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
  }

  const setUserPersist = (next: User) => {
    localStorage.setItem('user', JSON.stringify(next))
    setUser(next)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        isAuthenticated: !!token && !!user,
        login,
        logout,
        setUser: setUserPersist,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
