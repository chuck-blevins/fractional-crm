import { describe, it, expect } from 'vitest'
import { GET } from '@/app/api/health/route'

describe('GET /api/health', () => {
  it('responds 200 with { status: "ok" }', async () => {
    const res = GET()
    expect(res.status).toBe(200)
    await expect(res.json()).resolves.toEqual({ status: 'ok' })
  })
})
