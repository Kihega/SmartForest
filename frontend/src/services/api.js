
/**
 * api.js — re-exports from config/backends.js for backward compatibility.
 * All URL resolution logic lives in config/backends.js.
 */
export { getAPI, resolveBackend, resetBackend, BACKEND_CANDIDATES } from '../config/backends.js';

import axios from 'axios';
import { resolveBackend } from '../config/backends.js';

export const getAlerts  = async () => (await resolveBackend().then(u => axios.get(u + '/alerts')));
export const getSensors = async () => (await resolveBackend().then(u => axios.get(u + '/sensors')));
export const getHealth  = async () => (await resolveBackend().then(u => axios.get(u + '/health')));
