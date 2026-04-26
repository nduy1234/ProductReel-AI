/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    unoptimized: false,
    remotePatterns: [
      { protocol: "https", hostname: "**.bytepluses.com" },
      { protocol: "https", hostname: "**.volccdn.com" },
      { protocol: "https", hostname: "**.byteimg.com" },
      { protocol: "https", hostname: "images.unsplash.com" },
      { protocol: "https", hostname: "**.pexels.com" },
      { protocol: "https", hostname: "**.atlascloud.ai" },
      { protocol: "https", hostname: "**" },
    ],
  },
  experimental: {
    // Raise body-size limit for base64 image payloads (App Router)
    serverBodySizeLimit: "10mb",
  },
};

module.exports = nextConfig;
