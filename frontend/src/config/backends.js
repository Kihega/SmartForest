
/**
 * backends.js — single source of truth for the backend URL (frontend).
 *
 * ONE env var, no priority list, no hardcoded fallback list:
 *   VITE_API_URL   — set this in frontend/.env to whatever is running:
 *                     local  -> http://localhost:5000/api
 *                     cloud  -> https://your-app.onrender.com/api
 *
 * The app doesn't care which one it is — it just uses whatever URL is
 * configured. Switching environments means changing ONE line in .env
 * and rebuilding (Vite bakes env vars in at build time).
 *
 * Usage:
 *   import { getAPI } from '../config/backends.js'
 *   const api = await getAPI()
 *   const res = await api.get('/alerts')
 */
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

let _checked = false;
let _reachable = null;

async function probe() {
  try {
    await axios.get(API_URL.replace(/\/api$/, '') + '/api/health', { timeout: 6000 });
    return true;
  } catch {
    return false;
  }
}

/** Resolves to the configured API_URL. Throws NO_BACKEND if unreachable. */
export async function resolveBackend() {
  if (_checked && _reachable) return API_URL;
  const ok = await probe();
  _checked = true;
  _reachable = ok;
  if (!ok) {
    console.warn('[Backend] Unreachable:', API_URL);
    throw new Error('NO_BACKEND');
  }
  console.info('[Backend] Connected:', API_URL);
  return API_URL;
}

/** Forces a fresh reachability check on next call. */
export function resetBackend() {
  _checked = false;
  _reachable = null;
}

/** Returns an axios instance pointed at the configured backend. */
export async function getAPI(token) {
  const baseURL = await resolveBackend();
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  return axios.create({ baseURL, headers });
}

/** The single configured URL (for status display / debugging). */
export const BACKEND_URL = API_URL;
