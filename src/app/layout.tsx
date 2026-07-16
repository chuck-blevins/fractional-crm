import type { ReactNode } from 'react'

/** App-wide metadata; expanded with real branding in the UI stories (CRB-32). */
export const metadata = {
  title: 'fractional-crm',
  description: 'CRM for a fractional COO/CPO practice',
}

/** Root layout wrapping every route. */
export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
