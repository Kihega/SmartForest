
'use strict';
/**
 * Prisma Seed — creates real Supabase Auth accounts + DB profile rows.
 *
 * Users created:
 *   admin@smf.tz  / smf@1234  → role: admin
 *   ranger@smf.tz / smf@1234  → role: customer
 *
 * Run:
 *   npx prisma db seed
 *
 * To reset and re-run (removes ALL existing users first):
 *   npx prisma db seed -- --reset
 */
const { PrismaClient } = require('@prisma/client');
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const prisma = new PrismaClient();

// Use the SERVICE KEY (admin privileges) to create auth users
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

const USERS = [
  {
    email:    'admin@smf.tz',
    password: 'smf@1234',
    name:     'System Admin',
    role:     'admin',
  },
  {
    email:    'ranger@smf.tz',
    password: 'smf@1234',
    name:     'Field Ranger',
    role:     'customer',
  },
];

async function deleteAuthUser(email) {
  // List all users and find by email
  const { data, error } = await supabase.auth.admin.listUsers({ perPage: 1000 });
  if (error) { console.warn('[seed] Could not list users:', error.message); return; }
  const found = (data.users || []).find(u => u.email === email);
  if (found) {
    const { error: de } = await supabase.auth.admin.deleteUser(found.id);
    if (de) console.warn('[seed] Delete error for', email, de.message);
    else console.log('[seed] Deleted auth user:', email);
  }
}

async function main() {
  const reset = process.argv.includes('--reset');

  for (const u of USERS) {
    if (reset) {
      // Remove from Supabase Auth
      await deleteAuthUser(u.email);
      // Remove from DB
      await prisma.user.deleteMany({ where: { email: u.email } });
      console.log('[seed] Cleared:', u.email);
    }

    // Create / update Supabase Auth account
    // First check if auth user already exists
    const { data: listData } = await supabase.auth.admin.listUsers({ perPage: 1000 });
    const existingAuth = (listData?.users || []).find(x => x.email === u.email);

    if (existingAuth) {
      // Update password and metadata
      const { error: ue } = await supabase.auth.admin.updateUserById(existingAuth.id, {
        password:      u.password,
        email_confirm: true,
        user_metadata: { name: u.name, role: u.role },
      });
      if (ue) console.warn('[seed] Auth update error for', u.email, ue.message);
      else    console.log('[seed] Auth updated:', u.email);
    } else {
      const { error: ce } = await supabase.auth.admin.createUser({
        email:         u.email,
        password:      u.password,
        email_confirm: true,
        user_metadata: { name: u.name, role: u.role },
      });
      if (ce) console.warn('[seed] Auth create error for', u.email, ce.message);
      else    console.log('[seed] Auth created:', u.email);
    }

    // Upsert DB profile row
    const profile = await prisma.user.upsert({
      where:  { email: u.email },
      update: { name: u.name, role: u.role },
      create: { name: u.name, email: u.email, role: u.role },
    });
    console.log('[seed] DB profile:', profile.email, '| role:', profile.role, '| id:', profile.id);
  }

  // ── Sample sensor readings ──────────────────────────────────────────────
  const readingCount = await prisma.sensorReading.count();
  if (readingCount === 0) {
    const readings = [
      { deviceId:'smt-m01a', sensorType:'microphone', zone:'Kibiti-North',
        latitude:-7.72, longitude:38.95, soundDb:42.5, isAlert:false },
      { deviceId:'smt-m02a', sensorType:'microphone', zone:'Kibiti-South',
        latitude:-7.85, longitude:38.88, soundDb:91.5, isAlert:true  },
      { deviceId:'smt-f01a', sensorType:'flame', zone:'Kibiti-North',
        latitude:-7.72, longitude:38.95, flameDetected:false, temperatureC:28.5, isAlert:false },
      { deviceId:'smt-f02a', sensorType:'flame', zone:'Kibiti-South',
        latitude:-7.85, longitude:38.88, flameDetected:true,  temperatureC:67.3, isAlert:true  },
    ];
    for (const r of readings) await prisma.sensorReading.create({ data: r });
    console.log('[seed] Created', readings.length, 'sample sensor readings');

    await prisma.alert.createMany({
      data: [
        { deviceId:'smt-m02a', sensorType:'microphone', alertType:'illegal_logging',
          zone:'Kibiti-South', latitude:-7.85, longitude:38.88,
          soundDb:91.5, status:'unresolved' },
        { deviceId:'smt-f02a', sensorType:'flame', alertType:'fire',
          zone:'Kibiti-South', latitude:-7.85, longitude:38.88,
          flameDetected:true, temperatureC:67.3, status:'unresolved' },
      ],
      skipDuplicates: true,
    });
    console.log('[seed] Created 2 sample alerts');
  } else {
    console.log('[seed] Skipped readings (already', readingCount, 'rows)');
  }

  console.log('');
  console.log('[seed] Done! Login credentials:');
  console.log('  admin@smf.tz  / smf@1234  (admin dashboard)');
  console.log('  ranger@smf.tz / smf@1234  (user dashboard)');
}

main()
  .catch(e => { console.error('[seed] FATAL:', e.message); process.exit(1); })
  .finally(() => prisma.$disconnect());
