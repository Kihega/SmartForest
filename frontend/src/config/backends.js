
/**
 * backends.js — centralised backend URL resolver (frontend)
 *
 * Priority order (all URLs come from VITE_ env vars — never hardcoded):
 *   1. VITE_API_URL_LOCAL   (default: http://localhost:5000/api)
 *   2. VITE_API_URL_CLOUD   (Render.com / any hosted backend)
 *   3. VITE_API_URL_EXTRA   (optional third fallback, e.g. staging)
 *
 * The resolver tries each URL in order with a short timeout.
 * The first reachable one is cached for the session.
 *
 * Usage:
 *   import { getAPI } from '../config/backends.js'
 *   const api = await getAPI()
 *   const res = await api.get('/alerts')
 */
import axios from 'axios';

// Pull URLs from Vite env — never hardcode here
const CANDIDATE_URLS = [
  import.meta.env.VITE_API_URL_LOCAL  || 'http://localhost:5000/api',
  import.meta.env.VITE_API_URL_CLOUD  || '',
  import.meta.env.VITE_API_URL_EXTRA  || '',
].filter(Boolean).filter((v, i, a) => v && a.indexOf(v) === i); // dedup + remove empty

let _resolved = null;   // cached after first successful check
let _checking = null;   // in-flight promise (prevents parallel races)

async function probe(url, timeoutMs) {
  try {
    await axios.get(url.replace(/\/api$/, '') + '/api/health', { timeout: timeoutMs });
    return true;
  } catch {
    return false;
  }
}

export async function resolveBackend() {
  if (_resolved) return _resolved;
  if (_checking) return _checking;

  _checking = (async () => {
    for (const url of CANDIDATE_URLS) {
      const timeout = url.includes('localhost') ? 2000 : 5000;
      if (await probe(url, timeout)) {
        _resolved = url;
        console.info('[Backend] Connected:', url);
        _checking = null;
        return url;
      }
      console.warn('[Backend] Unreachable:', url);
    }
    _checking = null;
    throw new Error('NO_BACKEND');
  })();

  return _checking;
}

/** Reset cache — forces re-probe on next call (useful after network change) */
export function resetBackend() {
  _resolved = null;
  _checking = null;
}

/** Get an axios instance pointed at the resolved backend */
export async function getAPI(token) {
  const baseURL = await resolveBackend();
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  return axios.create({ baseURL, headers });
}

/** Raw list of candidates (for debug/status display) */
export const BACKEND_CANDIDATES = CANDIDATE_URLS;
