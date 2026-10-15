import { createContext, useContext, useState, ReactNode } from 'react'

interface AlertNotification {
  id: string
  unreadCount: number
}

interface AlertContextType {
  notifications: AlertNotification | null
  updateUnreadCount: (count: number) => void
  incrementUnread: () => void
  decrementUnread: () => void
}

const AlertContext = createContext<AlertContextType | undefined>(undefined)

export const AlertProvider = ({ children }: { children: ReactNode }) => {
  const [notifications, setNotifications] = useState<AlertNotification | null>(null)

  const updateUnreadCount = (count: number) => {
    setNotifications({
      id: Date.now().toString(),
      unreadCount: count,
    })
  }

  const incrementUnread = () => {
    setNotifications((prev) =>
      prev ? { ...prev, unreadCount: prev.unreadCount + 1 } : { id: Date.now().toString(), unreadCount: 1 }
    )
  }

  const decrementUnread = () => {
    setNotifications((prev) =>
      prev ? { ...prev, unreadCount: Math.max(0, prev.unreadCount - 1) } : null
    )
  }

  return (
    <AlertContext.Provider
      value={{
        notifications,
        updateUnreadCount,
        incrementUnread,
        decrementUnread,
      }}
    >
      {children}
    </AlertContext.Provider>
  )
}

export const useAlertNotifications = () => {
  const context = useContext(AlertContext)
  if (!context) {
    throw new Error('useAlertNotifications must be used within AlertProvider')
  }
  return context
}
