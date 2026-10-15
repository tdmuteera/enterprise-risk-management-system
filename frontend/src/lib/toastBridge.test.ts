import { describe, expect, it } from 'vitest'
import { registerToastHandler, showAppToast } from './toastBridge'

describe('toastBridge', () => {
  it('invokes registered handler', () => {
    let seen: string | null = null
    registerToastHandler((msg) => {
      seen = msg
    })
    showAppToast('hello', 'info')
    expect(seen).toBe('hello')
    registerToastHandler(null)
  })
})
