/** @type {import('next').NextConfig} */

// The web app deploys as a labeled design preview UNDER the corpus site
// (https://<owner>.github.io/newsletters/web/ — the root URL belongs to the rendered
// record, DEF-13). basePath is env-driven so one build serves every context:
//   - local dev / plain `npm run build`: no env → no basePath
//   - Pages build (deploy-pages.yml):    NEXT_BASE_PATH=/newsletters/web
// Fonts need no syncing — globals.css uses relative url()s the bundler rewrites.
const basePath = process.env.NEXT_BASE_PATH ?? '';

const nextConfig = {
  output: 'export', // emit a static site (out/) — no Node server needed
  basePath,
  trailingSlash: true, // folder/index.html URLs — required for gh-pages subpath serving
  images: { unoptimized: true }, // no Image Optimization server on Pages
  reactStrictMode: true,
};

export default nextConfig;
