import { MutationCache, QueryCache, QueryClient } from '@tanstack/react-query'
import { AxiosError } from 'axios'
import { showAppToast } from '@/lib/toastBridge'

function isAxiosError(error: unknown): error is AxiosError {
  return Boolean(error && typeof error === 'object' && 'isAxiosError' in error)
}

function shouldSkipAxiosHandledError(error: unknown): boolean {
  if (!isAxiosError(error)) {
    return false
  }
  const s = error.response?.status
  if (s === 401 || s === 403 || s === 422 || s === 500) {
    return true
  }
  if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
    return true
  }
  return false
}

function onQueryError(error: unknown) {
  if (shouldSkipAxiosHandledError(error)) {
    return
  }
  const msg = error instanceof Error ? error.message : 'Something went wrong'
  showAppToast(msg, 'error')
}

export const queryClient = new QueryClient({
  queryCache: new QueryCache({ onError: onQueryError }),
  mutationCache: new MutationCache({
    onError: onQueryError,
    onSuccess(_data, _variables, _onMutateResult, mutation) {
      const key = mutation.options.mutationKey
      if (!Array.isArray(key)) {
        return
      }
      if (key[0] === 'risks') {
        void queryClient.invalidateQueries({ queryKey: ['risks'] })
        void queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      }
      if (key[0] === 'forensic-scan') {
        void queryClient.invalidateQueries({ queryKey: ['alerts'] })
        void queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      }
    },
  }),
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 2,
    },
    mutations: {
      retry: 1,
    },
  },
})
