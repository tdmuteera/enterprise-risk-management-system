import clsx from 'clsx'

interface SkeletonProps {
  className?: string
  count?: number
}

export const Skeleton = ({ className, count = 1 }: SkeletonProps) => {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={clsx('bg-gray-200 rounded-lg animate-pulse', className)}
        />
      ))}
    </>
  )
}

export const SkeletonText = ({ lines = 1 }: { lines?: number }) => (
  <Skeleton className="h-4 w-3/4 mb-2" count={lines} />
)

export const SkeletonCard = () => (
  <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100 space-y-4">
    <Skeleton className="h-8 w-1/2" />
    <Skeleton className="h-12 w-2/3" />
    <Skeleton className="h-4 w-1/3" />
  </div>
)

export const SkeletonTable = ({ rows = 5 }: { rows?: number }) => (
  <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100 space-y-4">
    <Skeleton className="h-6 w-full" />
    {Array.from({ length: rows }).map((_, i) => (
      <Skeleton key={i} className="h-12 w-full" />
    ))}
  </div>
)

export const SkeletonChart = () => (
  <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
    <Skeleton className="h-6 w-1/3 mb-4" />
    <Skeleton className="h-64 w-full" />
  </div>
)
