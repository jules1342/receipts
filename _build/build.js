const fs = require('fs');
const path = require('path');
const babel = require('@babel/core');

// Paths resolve from this script. Layout: Receipts/receipts.html, Receipts/_build/, Receipts/app/.
const BUILD_DIR = __dirname;
const PROJECT = path.join(BUILD_DIR, '..');
// Optional args: source html and output html, for variant builds (the design copy builds into app/design/).
const SRC = process.argv[2] ? path.resolve(process.argv[2]) : path.join(PROJECT, 'receipts.html');
const OUT = process.argv[3] ? path.resolve(process.argv[3]) : path.join(PROJECT, 'app', 'index.html');
fs.mkdirSync(path.dirname(OUT), { recursive: true });

let html = fs.readFileSync(SRC, 'utf8');
const react = fs.readFileSync(path.join(BUILD_DIR, 'vendor', 'react.js'), 'utf8');
const reactDom = fs.readFileSync(path.join(BUILD_DIR, 'vendor', 'react-dom.js'), 'utf8');

// 1. Extract and precompile the JSX block
const m = html.match(/<script type="text\/babel"[^>]*>([\s\S]*?)<\/script>/);
if (!m) throw new Error('babel script block not found');
const compiled = babel.transformSync(m[1], { cwd: BUILD_DIR, babelrc: false, configFile: false, presets: [['@babel/preset-react', { runtime: 'classic', development: false }]], compact: false, comments: false }).code;

if (/<\/script/i.test(compiled)) throw new Error('compiled code contains </script');
new Function(compiled); // throws if not parseable

// 2. Remove the dev-only CDN script tags
html = html.replace(/\s*<script crossorigin src="https:\/\/unpkg\.com\/react@[^"]*"><\/script>/, '');
html = html.replace(/\s*<script crossorigin src="https:\/\/unpkg\.com\/react-dom@[^"]*"><\/script>/, '');
html = html.replace(/\s*<script src="https:\/\/unpkg\.com\/@babel\/standalone[^"]*"><\/script>/, '');

// 3. Inline React + ReactDOM + compiled app (function replacement: React's code contains `$` sequences)
const inlined =
  '<script>/* React 18.3.1 (inlined, no CDN) */\n' + react + '\n</script>\n' +
  '  <script>/* ReactDOM 18.3.1 (inlined, no CDN) */\n' + reactDom + '\n</script>\n' +
  '  <script>/* Receipts app (precompiled, no Babel) */\n' + compiled + '\n</script>';
html = html.replace(/<script type="text\/babel"[^>]*>[\s\S]*?<\/script>/, () => inlined);

if (/unpkg\.com/.test(html)) throw new Error('unpkg reference still present after build');
if (/—/.test(html)) throw new Error('em dash found in source; remove it before shipping');

const bv = html.match(/const BUILD_VERSION = '([^']+)'/);
fs.writeFileSync(OUT, html);
console.log('built', OUT);
console.log('  bytes:', html.length);
console.log('  BUILD_VERSION:', bv ? bv[1] : '(not found)');
