
'use strict';
/**
 * backends.js — Backend URL resolver for Node.js services (simulator, seed, etc.)
 *
 * Priority order — all URLs from env vars only, never hardcoded:
 *   1. BACKEND_URL_LOCAL  (default: http://localhost:5000)
 *   2. BACKEND_URL_CLOUD  (Render.com or any hosted backend)
 *   3. BACKEND_URL_EXTRA  (optional third fallback)
 *
 * Usage:
 *   const { resolveBackend, getBackendUrl } = require('./config/backends');
 *   const url = await getBackendUrl();   // -> 'http://localhost:5000'
 */
const http  = require('http');
const https = require('https');
const url   = require('url');

const CANDIDATES = [
  process.env.BACKEND_URL_LOCAL || 'http://localhost:5000',
  process.env.BACKEND_URL_CLOUD || '',
  process.env.BACKEND_URL_EXTRA || '',
].filter(Boolean).filter((v, i, a) => v && a.indexOf(v) === i);

let _resolved = null;

function probe(baseUrl, timeoutMs) {
  return new Promise(resolve => {
    const healthUrl = baseUrl.replace(/\/$/, '') + '/api/health';
    const parsed    = url.parse(healthUrl);
    const lib       = parsed.protocol === 'https:' ? https : http;
    const req       = lib.get(healthUrl, { timeout: timeoutMs }, res => {
      resolve(res.statusCode === 200);
    });
    req.on('error',   () => resolve(false));
    req.on('timeout', () => { req.destroy(); resolve(false); });
    req.setTimeout(timeoutMs);
  });
}

async function resolveBackend() {
  if (_resolved) return _resolved;
  for (const candidate of CANDIDATES) {
    const ms = candidate.includes('localhost') ? 2000 : 5000;
    if (await probe(candidate, ms)) {
      _resolved = candidate.replace(/\/$/, '');
      console.log('[backends] Resolved:', _resolved);
      return _resolved;
    }
    console.warn('[backends] Unreachable:', candidate);
  }
  throw new Error('NO_BACKEND_REACHABLE: tried ' + CANDIDATES.join(', '));
}

function resetBackend() { _resolved = null; }

async function getBackendUrl() { return resolveBackend(); }

module.exports = { resolveBackend, resetBackend, getBackendUrl, CANDIDATES };
