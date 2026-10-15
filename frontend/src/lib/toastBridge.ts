export type ToastLevel = 'success' | 'error' | 'warning' | 'info'

type ToastFn = (message: string, type?: ToastLevel, duration?: number) => void

let toastImpl: ToastFn | null = null

/** Called from ToastProvider mount so axios/query can show toasts outside React. */
export function registerToastHandler(fn: ToastFn | null) {
  toastImpl = fn
}

export function showAppToast(message: string, type: ToastLevel = 'info', duration = 5000) {
  toastImpl?.(message, type, duration)
}
