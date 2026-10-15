import { ReactNode } from 'react'
import clsx from 'clsx'

interface CardProps {
  children: ReactNode
  className?: string
  hover?: boolean
}

export const Card = ({ children, className, hover = false }: CardProps) => {
  return (
    <div
      className={clsx(
        'bg-white rounded-lg shadow-sm border border-gray-100',
        hover && 'hover:shadow-md transition-shadow duration-200 cursor-pointer',
        className
      )}
    >
      {children}
    </div>
  )
}

interface CardHeaderProps {
  children: ReactNode
  className?: string
}

export const CardHeader = ({ children, className }: CardHeaderProps) => {
  return <div className={clsx('px-6 py-4 border-b border-gray-100', className)}>{children}</div>
}

interface CardBodyProps {
  children: ReactNode
  className?: string
}

export const CardBody = ({ children, className }: CardBodyProps) => {
  return <div className={clsx('px-6 py-4', className)}>{children}</div>
}

interface CardFooterProps {
  children: ReactNode
  className?: string
}

export const CardFooter = ({ children, className }: CardFooterProps) => {
  return <div className={clsx('px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-lg', className)}>{children}</div>
}
