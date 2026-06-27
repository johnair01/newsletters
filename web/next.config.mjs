/** @type {import('next').NextConfig} */

// Served as a GitHub *Project* Pages site at https://<owner>.github.io/newsletters/,
// so the app lives under the `/newsletters` base path. basePath also prefixes the
// _next assets and public files. (Self-hosted fonts referenced from globals.css are
// prefixed to match — see the note there.) To host at a domain root instead, set
// basePath to '' and drop the /newsletters prefix on the font URLs.
const basePath = '/newsletters';

const nextConfig = {
  output: 'export', // emit a static site (out/) — no Node server needed
  basePath,
  images: { unoptimized: true }, // no Image Optimization server on Pages
  reactStrictMode: true,
};

export default nextConfig;
