import { ReactNode } from 'react'
import clsx from 'clsx'

interface PageContainerProps {
  children: ReactNode
  className?: string
}

export const PageContainer = ({ children, className }: PageContainerProps) => {
  return (
    <main
      className={clsx(
        'relative min-h-screen md:ml-72 mt-16 px-4 py-8 sm:px-6 sm:py-10 lg:px-10',
        className
      )}
    >
      <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden>
        <div className="absolute -right-24 top-24 h-64 w-64 rounded-full bg-brand-mid/[0.04] blur-3xl" />
        <div className="absolute -left-16 bottom-32 h-48 w-48 rounded-full bg-brand-dark/[0.05] blur-3xl" />
      </div>
      <div className="relative z-[1] mx-auto max-w-7xl">{children}</div>
    </main>
  )
}
