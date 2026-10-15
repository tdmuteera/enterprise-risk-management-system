import { format, formatDistance, isToday, isYesterday, parseISO } from 'date-fns'

export const formatDate = (date: string | Date): string => {
  const d = typeof date === 'string' ? parseISO(date) : date
  return format(d, 'MMM d, yyyy')
}

export const formatDateTime = (date: string | Date): string => {
  const d = typeof date === 'string' ? parseISO(date) : date
  return format(d, 'MMM d, yyyy HH:mm')
}

export const formatTime = (date: string | Date): string => {
  const d = typeof date === 'string' ? parseISO(date) : date
  return format(d, 'HH:mm')
}

export const formatRelative = (date: string | Date): string => {
  const d = typeof date === 'string' ? parseISO(date) : date

  if (isToday(d)) {
    return `today at ${format(d, 'HH:mm')}`
  }

  if (isYesterday(d)) {
    return `yesterday at ${format(d, 'HH:mm')}`
  }

  return formatDistance(d, new Date(), { addSuffix: true })
}

export const formatDueDate = (date: string | Date): string => {
  const d = typeof date === 'string' ? parseISO(date) : date
  return format(d, 'MMM d')
}

export const getDaysSince = (date: string | Date): number => {
  const d = typeof date === 'string' ? parseISO(date) : date
  return Math.floor((new Date().getTime() - d.getTime()) / (1000 * 60 * 60 * 24))
}

export const getDayUntil = (date: string | Date): number => {
  const d = typeof date === 'string' ? parseISO(date) : date
  return Math.ceil((d.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
}
