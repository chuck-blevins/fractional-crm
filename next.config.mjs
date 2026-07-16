/** @type {import('next').NextConfig} */
const nextConfig = {
  // `standalone` output is required for the Nexlayer container build (CRB-19).
  output: 'standalone',
  reactStrictMode: true,
}

export default nextConfig
