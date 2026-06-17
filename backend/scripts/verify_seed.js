
'use strict';
/**
 * verify_seed.js — confirms which Supabase project this environment is
 * pointed at, and whether the admin/ranger accounts actually exist there.
 *
 * Run with the SAME environment Render uses (e.g. via Render Shell):
 *   node scripts/verify_seed.js
 *
 * Or locally, after copying Render's exact env vars into backend/.env:
 *   node backend/scripts/verify_seed.js
 */
require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

const url = process.env.SUPABASE_URL;
const key = process.env.SUPABASE_SERVICE_KEY;

console.log('='.repeat(60));
console.log('  SmartForest — Seed Verification');
console.log('='.repeat(60));
console.log();
console.log('SUPABASE_URL        :', url || '(NOT SET)');
console.log('SUPABASE_SERVICE_KEY:', key ? key.slice(0, 12) + '...(set)' : '(NOT SET)');
console.log('DATABASE_URL        :', process.env.DATABASE_URL ? '(set)' : '(NOT SET)');
console.log();

if (!url || !key) {
  console.error('FAIL: SUPABASE_URL or SUPABASE_SERVICE_KEY missing.');
  console.error('      This environment cannot create or verify auth users.');
  process.exit(1);
}

const supabase = createClient(url, key);

async function main() {
  const { data, error } = await supabase.auth.admin.listUsers({ perPage: 1000 });
  if (error) {
    console.error('FAIL: Could not list Supabase Auth users.');
    console.error('      ', error.message);
    console.error('      This usually means SUPABASE_URL or SUPABASE_SERVICE_KEY');
    console.error('      is wrong for this environment.');
    process.exit(1);
  }

  console.log(`Found ${data.users.length} total user(s) in this Supabase project.\n`);

  const targets = ['admin@smf.tz', 'ranger@smf.tz'];
  let allGood = true;

  for (const email of targets) {
    const u = data.users.find(x => x.email === email);
    if (!u) {
      console.log(`  ✗  ${email}  — NOT FOUND in this Supabase project`);
      allGood = false;
    } else {
      console.log(`  ✓  ${email}  — exists (id: ${u.id})`);
      console.log(`       email_confirmed_at: ${u.email_confirmed_at || 'NOT CONFIRMED ⚠️'}`);
      console.log(`       role in metadata  : ${u.user_metadata?.role || '(none)'}`);
      if (!u.email_confirmed_at) allGood = false;
    }
  }

  console.log();
  if (allGood) {
    console.log('RESULT: Seed accounts look correct in THIS Supabase project.');
    console.log('If login still fails from the deployed frontend, the Render');
    console.log('backend likely has DIFFERENT SUPABASE_URL/SUPABASE_SERVICE_KEY');
    console.log('values than the ones used here. Compare them in the Render');
    console.log('dashboard under your service -> Environment.');
  } else {
    console.log('RESULT: Accounts missing or unconfirmed in THIS project.');
    console.log('Fix: run  npx prisma db seed  with these exact env vars loaded.');
  }
  console.log();
}

main().catch(e => { console.error('FATAL:', e.message); process.exit(1); });
