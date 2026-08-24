import type { NextConfig } from "next";

// "localhost" costs two seconds per request on Windows while IPv6 is tried first
const API_URL = process.env.API_URL ?? "http://127.0.0.1:3001";

const nextConfig: NextConfig = {
  // The browser only ever talks to this server. The API stays bound to the loopback
  // interface even when the web app is opened from another device on the network.
  rewrites() {
    return [{ source: "/api/:path*", destination: `${API_URL}/:path*` }];
  },
  // lets a phone on the same private network load the dev server
  allowedDevOrigins: ["192.168.*.*", "10.*.*.*"],
};

export default nextConfig;
