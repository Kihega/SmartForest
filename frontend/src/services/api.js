/**
 * api.js — Smart backend resolver
 *
 * Priority:
 *  1. Try VITE_API_URL_CLOUD (Render.com) — 4s timeout
 *  2. Try VITE_API_URL_LOCAL (localhost)  — 2s timeout
 *  3. Both fail -> throw 'NO_BACKEND' error
 *
 * BackendStatus.jsx catches NO_BACKEND and shows a visible banner.
 */
import axios from 'axios';

const CLOUD_URL = import.meta.env.VITE_API_URL_CLOUD;
const LOCAL_URL = import.meta.env.VITE_API_URL_LOCAL || 'http://localhost:5000/api';

let resolvedBaseURL = null;

export async function resolveBackend() {
  if (resolvedBaseURL) return resolvedBaseURL;

  // 1. Try cloud (Render.com)
  if (CLOUD_URL) {
    try {
      await axios.get(CLOUD_URL + '/health', { timeout: 4000 });
      resolvedBaseURL = CLOUD_URL;
      console.log('Backend: cloud (Render)');
      return resolvedBaseURL;
    } catch {
      console.warn('Cloud backend unreachable, trying local...');
    }
  }

  // 2. Try local
  try {
    await axios.get(LOCAL_URL + '/health', { timeout: 2000 });
    resolvedBaseURL = LOCAL_URL;
    console.log('Backend: local');
    return resolvedBaseURL;
  } catch {
    throw new Error('NO_BACKEND');
  }
}

export async function getAPI() {
  const baseURL = await resolveBackend();
  return axios.create({ baseURL });
}

export const getAlerts  = async () => (await getAPI()).get('/alerts');
export const getSensors = async () => (await getAPI()).get('/sensors');
export const getHealth  = async () => (await getAPI()).get('/health');
