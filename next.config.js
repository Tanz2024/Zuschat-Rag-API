/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    BACKEND_URL: process.env.BACKEND_URL || 'https://zuschat-rag-api.onrender.com',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.BACKEND_URL || 'https://zuschat-rag-api.onrender.com'}/:path*`,
      },
    ];
  },
  images: {
    domains: ['localhost', 'zuschat-rag-api.onrender.com'],
  },
};

module.exports = nextConfig;
