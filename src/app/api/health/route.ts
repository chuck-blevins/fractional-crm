import { NextResponse } from 'next/server'

/**
 * Liveness probe. Public (unauthenticated) — the auth middleware in CRB-31
 * must keep this route open so the Nexlayer container health check can reach it.
 *
 * @returns 200 with `{ status: "ok" }`.
 */
export function GET(): NextResponse {
  return NextResponse.json({ status: 'ok' })
}
