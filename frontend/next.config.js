/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  typescript: {
    // 生产构建时是否忽略 TypeScript 错误
    ignoreBuildErrors: false,
  },
  eslint: {
    // 生产构建时是否忽略 ESLint 错误
    ignoreDuringBuilds: false,
  },
  images: {
    domains: ['localhost'],
    formats: ['image/webp', 'image/avif'],
  },
  // API 代理配置
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },
  // 环境变量配置
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  // 构建优化
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // 优化 bundle 大小
    if (!dev && !isServer) {
      config.optimization.splitChunks.chunks = 'all';
    }
    
    // 处理 plotly.js
    config.resolve.alias = {
      ...config.resolve.alias,
      'plotly.js': 'plotly.js/dist/plotly.min.js',
    };
    
    return config;
  },
  // 压缩配置
  compress: true,
  // 运行时配置
  poweredByHeader: false,
  generateEtags: false,
  // 国际化配置
  i18n: {
    locales: ['zh-CN', 'en-US'],
    defaultLocale: 'zh-CN',
  },
  // 安全头配置
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;