import { describe, expect, it } from 'vitest'
import { queryClient } from '@/lib/queryClient'

describe('queryClient', () => {
  it('uses 30s staleTime for queries', () => {
    const q = queryClient.getDefaultOptions().queries
    expect(q?.staleTime).toBe(30_000)
  })

  it('uses retry 2 for queries and 1 for mutations', () => {
    expect(queryClient.getDefaultOptions().queries?.retry).toBe(2)
    expect(queryClient.getDefaultOptions().mutations?.retry).toBe(1)
  })
})
