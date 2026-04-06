import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow images from any source (for org charts etc served from MCP)
  images: {
    remotePatterns: [
      { protocol: "http", hostname: "localhost", port: "8000" },
    ],
  },
};

export default nextConfig;
