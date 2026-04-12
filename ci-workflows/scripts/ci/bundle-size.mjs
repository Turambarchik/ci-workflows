#!/usr/bin/env node
// ============================================================
// bundle-size.mjs — Custom Next.js Bundle Analyzer for CI
// ============================================================
// Usage:
//   node bundle-size.mjs analyze --project-dir <path> --output <path>
//   node bundle-size.mjs compare --base <path> --head <path>
//                                --summary-output <path> --comment-output <path>
//
// This script reads Next.js production build output (.next/build-manifest.json
// and .next/app-build-manifest.json) and produces structured JSON reports
// suitable for PR vs base comparison in CI pipelines.
//
// Designed for AI-assisted workflows:
//   - Structured JSON output → easy for agents to parse
//   - Human-readable Markdown → easy for developers to review
//   - Deterministic and reproducible — no external services needed
// ============================================================

import fs from 'fs';
import path from 'path';

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      args[argv[i].slice(2)] = argv[i + 1];
      i++;
    }
  }
  return args;
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'kB', 'MB'];
  const i = Math.floor(Math.log(Math.abs(bytes)) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
}

function formatDiff(diff) {
  if (diff === 0) return '➡️ 0 B';
  const sign = diff > 0 ? '+' : '';
  const emoji = diff > 0 ? '🔺' : '✅';
  return `${emoji} ${sign}${formatBytes(diff)}`;
}

function getFileSize(filePath) {
  try {
    return fs.statSync(filePath).size;
  } catch {
    return 0;
  }
}

function analyze({ 'project-dir': projectDir, output }) {
  if (!projectDir || !output) {
    console.error('analyze requires --project-dir and --output');
    process.exit(1);
  }

  const nextDir = path.join(projectDir, '.next');

  if (!fs.existsSync(nextDir)) {
    console.error(`No .next directory found at: ${nextDir}`);
    console.error('Make sure you run `npm run build` before analyzing.');
    process.exit(1);
  }

  const result = {
    generatedAt: new Date().toISOString(),
    routes: {},
    shared: {},
    totalBytes: 0,
  };

  const manifests = [
    path.join(nextDir, 'build-manifest.json'),
    path.join(nextDir, 'app-build-manifest.json'),
  ];

  const allRoutes = {};

  for (const manifestPath of manifests) {
    if (!fs.existsSync(manifestPath)) continue;

    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    const pages = manifest.pages || {};

    for (const [route, files] of Object.entries(pages)) {
      const normalizedRoute = route === '/_app' ? '(shared)' : route;
      if (!allRoutes[normalizedRoute]) {
        allRoutes[normalizedRoute] = new Set();
      }
      for (const file of files) {
        allRoutes[normalizedRoute].add(file);
      }
    }
  }

  let totalBytes = 0;

  for (const [route, files] of Object.entries(allRoutes)) {
    let routeBytes = 0;
    const fileDetails = [];

    for (const file of files) {
      const filePath = path.join(
        nextDir,
        'static',
        ...file.replace(/^\/_next\/static\//, '').split('/'),
      );
      const size = getFileSize(filePath);
      routeBytes += size;
      if (size > 0) {
        fileDetails.push({ file, size });
      }
    }

    if (route === '(shared)') {
      result.shared = { bytes: routeBytes, files: fileDetails };
    } else {
      result.routes[route] = { bytes: routeBytes, files: fileDetails };
    }

    totalBytes += routeBytes;
  }

  result.totalBytes = totalBytes;

  const outputDir = path.dirname(output);
  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });
  fs.writeFileSync(output, JSON.stringify(result, null, 2));

  console.log(`✅ Analyzed bundle: ${formatBytes(totalBytes)} total`);
  console.log(`   Routes found: ${Object.keys(result.routes).length}`);
  console.log(`   Output: ${output}`);
}

function compare({ base, head, 'summary-output': summaryOutput, 'comment-output': commentOutput }) {
  if (!base || !head || !summaryOutput || !commentOutput) {
    console.error('compare requires --base, --head, --summary-output, --comment-output');
    process.exit(1);
  }

  if (!fs.existsSync(base)) {
    console.error(`Base report not found: ${base}`);
    process.exit(1);
  }
  if (!fs.existsSync(head)) {
    console.error(`Head report not found: ${head}`);
    process.exit(1);
  }

  const baseData = JSON.parse(fs.readFileSync(base, 'utf8'));
  const headData = JSON.parse(fs.readFileSync(head, 'utf8'));

  const allRoutes = new Set([
    ...Object.keys(baseData.routes || {}),
    ...Object.keys(headData.routes || {}),
  ]);

  const rows = [];
  let totalBase = 0;
  let totalHead = 0;

  for (const route of [...allRoutes].sort()) {
    const baseBytes = baseData.routes?.[route]?.bytes ?? 0;
    const headBytes = headData.routes?.[route]?.bytes ?? 0;
    const diff = headBytes - baseBytes;

    totalBase += baseBytes;
    totalHead += headBytes;

    rows.push({ route, baseBytes, headBytes, diff });
  }

  const totalDiff = totalHead - totalBase;

  const totalStatus =
    totalDiff === 0
      ? '✅ No change'
      : totalDiff < 0
        ? `✅ Decreased by ${formatBytes(Math.abs(totalDiff))}`
        : `🔺 Increased by ${formatBytes(totalDiff)}`;

  const tableHeader = `| Route | Base | PR | Diff |
|:------|-----:|---:|-----:|`;

  const tableRows = rows
    .map(
      ({ route, baseBytes, headBytes, diff }) =>
        `| \`${route}\` | ${formatBytes(baseBytes)} | ${formatBytes(headBytes)} | ${formatDiff(diff)} |`,
    )
    .join('\n');

  const totalRow = `| **Total** | **${formatBytes(totalBase)}** | **${formatBytes(totalHead)}** | **${formatDiff(totalDiff)}** |`;

  const table = [tableHeader, tableRows, totalRow].join('\n');

  const commentContent = `<!-- bundle-size-report -->
## 📦 Bundle Size Report

${totalStatus}

${table}

<details>
<summary>ℹ️ How to read this report</summary>

- **Base**: bundle size on the target branch (before your changes)
- **PR**: bundle size after your changes
- **Diff**: size change per route (✅ = smaller or unchanged, 🔺 = larger)
- Sizes reflect uncompressed JS chunks assigned to each route

</details>

_Generated at ${new Date().toISOString()}_`;

  const summaryContent = `## 📦 Bundle Size — PR vs Base

${totalStatus}

${table}`;

  fs.writeFileSync(commentOutput, commentContent);
  fs.writeFileSync(summaryOutput, summaryContent);

  console.log(`✅ Comparison report generated`);
  console.log(`   Base total : ${formatBytes(totalBase)}`);
  console.log(`   PR total   : ${formatBytes(totalHead)}`);
  console.log(`   Diff       : ${formatDiff(totalDiff)}`);
  console.log(`   Summary    : ${summaryOutput}`);
  console.log(`   Comment    : ${commentOutput}`);
}

const [, , command, ...rest] = process.argv;
const args = parseArgs(rest);

switch (command) {
  case 'analyze':
    analyze(args);
    break;
  case 'compare':
    compare(args);
    break;
  default:
    console.error(`Unknown command: ${command}`);
    console.error('Usage: bundle-size.mjs [analyze|compare] [options]');
    process.exit(1);
}