# Render + Vercel Deploy Checklist — "Login failed" troubleshooting

You're seeing **"Login failed. Check your credentials."** on the deployed
site even though the Render backend is running. This message is shown for
several different root causes — use this checklist to find which one.

## Step 1 — Confirm Render is using the SAME Supabase project you seeded

Open your deployed backend's health endpoint in a browser:
```
https://your-backend.onrender.com/api/health
```
You should see something like:
```json
{
  "status": "ok",
  "supabaseProject": "abcdefghij",
  "hasServiceKey": true,
  "hasDbUrl": true
}
```

- If `supabaseProject` is `NOT_SET` or `NOT_CONFIGURED` → Render is missing
  `SUPABASE_URL`. Add it in Render Dashboard → your service → Environment.
- If `hasServiceKey` is `false` → `SUPABASE_SERVICE_KEY` is missing on Render.
- **Compare `supabaseProject` (the ref id) against the URL you used when you
  ran `npx prisma db seed` locally.** If they differ, you seeded the WRONG
  project — Render's users table is empty even though your local one isn't.

## Step 2 — Verify the seeded accounts exist in THAT exact project

In Render Dashboard → your service → **Shell**, run:
```bash
node backend/scripts/verify_seed.js
```
This prints whether `admin@smf.tz` / `ranger@smf.tz` actually exist in the
Supabase project Render is currently using, and whether their emails are
confirmed.

If it says "NOT FOUND" → re-run the seed with Render's exact environment:
```bash
npx prisma db seed
```
(Run this from Render's Shell, or copy Render's env vars into a local
`.env` and run it from your machine — either way, it must use the SAME
`SUPABASE_URL` / `SUPABASE_SERVICE_KEY` Render uses at runtime.)

## Step 3 — Confirm the frontend is actually reaching Render

Vite bakes `VITE_*` env vars in at **build time**, not runtime. If you set
`VITE_API_URL_CLOUD` in Vercel's dashboard AFTER the last deploy, it won't
take effect until you **redeploy**.

In Vercel Dashboard → your project → Settings → Environment Variables,
confirm:
```
VITE_API_URL_CLOUD = https://your-backend.onrender.com/api
```
Then trigger a fresh deploy (Vercel → Deployments → Redeploy), since
changing env vars alone does not rebuild the existing deployment.

Open browser DevTools → Console on the live site and reload the login
page. You should see:
```
[Backend] Connected: https://your-backend.onrender.com/api
```
If instead you see `[Backend] Unreachable: ...` for both candidates, the
frontend build never had the right `VITE_API_URL_CLOUD` baked in — go back
and redeploy after fixing the env var.

## Step 4 — Now retry login

With Step 1–3 confirmed, login with:
```
admin@smf.tz  / smf@1234
ranger@smf.tz / smf@1234
```

After this patch, the error message itself will tell you which category
of failure you're hitting (`invalid_credentials`, `supabase_unreachable`,
`profile_sync_failed`, or "cannot reach any backend") instead of one
generic "Login failed" for everything.

## Render free-tier cold start note

Render's free tier spins down after inactivity. The first request after a
period of inactivity can take 30–50 seconds to wake up, during which the
frontend's health probe may time out and look like "backend offline" even
though it's just slow to start. Wait ~1 minute after a long idle period
and try again.
