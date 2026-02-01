/** @type {import('next').NextConfig} */
const nextConfig = {
  // Note: 'standalone' output is only for Docker/self-hosted deployments
  // Vercel handles the build automatically, so we don't set output here
  // output: 'standalone',  // Uncomment for Docker deployments
  serverExternalPackages: ['better-auth'],
};

module.exports = nextConfig;