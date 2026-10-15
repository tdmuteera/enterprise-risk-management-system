// Form components stubs
// Ready to integrate React Hook Form + Zod

import { ReactNode } from 'react'
import { Button } from '@/components/ui/Button'

export const RiskForm = () => (
  <div className="space-y-4">
    <p className="text-gray-500">RiskForm - to be implemented with React Hook Form + Zod</p>
    <Button>Submit</Button>
  </div>
)

export const MitigationForm = () => (
  <div className="space-y-4">
    <p className="text-gray-500">MitigationForm - to be implemented with React Hook Form + Zod</p>
    <Button>Submit</Button>
  </div>
)

export const LoginForm = () => (
  <div className="space-y-4">
    <p className="text-gray-500">LoginForm - to be implemented with React Hook Form + Zod</p>
    <Button>Sign In</Button>
  </div>
)

export const UserForm = () => (
  <div className="space-y-4">
    <p className="text-gray-500">UserForm - to be implemented with React Hook Form + Zod</p>
    <Button>Save</Button>
  </div>
)

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: ReactNode
}

export const FormModal = ({ isOpen, onClose, title, children }: ModalProps) => {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg max-w-md w-full mx-4">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-lg font-semibold">{title}</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>
        <div className="px-6 py-4">{children}</div>
      </div>
    </div>
  )
}
