/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone', // For Docker - creates optimized standalone build
  
  // Performance optimizations
  swcMinify: true, // Use SWC for faster minification
  
  experimental: {
    optimizePackageImports: ['gsap', '@gsap/react', 'framer-motion'],
  },
  
  // Compression
  compress: true,
  
  // Enable PWA and security headers
  async headers() {
    return [
      {
        source: '/manifest.json',
        headers: [
          {
            key: 'Content-Type',
            value: 'application/manifest+json',
          },
        ],
      },
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on',
          },
          {
            key: 'X-Frame-Options',
            value: 'ALLOWALL', // Required for Telegram WebApp
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ];
  },
  
  // Telegram WebApp optimization
  images: {
    unoptimized: true, // Required for Telegram WebApp
    formats: ['image/webp'],
  },
  
  // Asset prefix disabled for Railway (causes issues with relative paths)
  // assetPrefix: process.env.NODE_ENV === 'production' ? process.env.NEXT_PUBLIC_BASE_URL : '',
  
  // Reduce bundle size
  webpack: (config, { isServer }) => {
    // Optimize for smaller bundle size
    if (!isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          default: false,
          vendors: false,
          commons: {
            name: 'commons',
            chunks: 'all',
            minChunks: 2,
          },
          lib: {
            test: /[\\/]node_modules[\\/]/,
            name(module) {
              const packageName = module.context.match(
                /[\\/]node_modules[\\/](.*?)([\\/]|$)/
              )?.[1];
              return `npm.${packageName?.replace('@', '')}`;
            },
          },
        },
      };
    }
    
    return config;
  },
  
  // Production source maps (disabled for smaller build)
  productionBrowserSourceMaps: false,
}

module.exports = nextConfig
