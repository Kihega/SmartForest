'use strict';
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  const admin = await prisma.user.upsert({
    where:  { email: 'admin@smartforest.tz' },
    update: { role: 'admin' },
    create: { name: 'System Admin', email: 'admin@smartforest.tz', role: 'admin' },
  });
  console.log('[seed] Admin:', admin.email, 'id:', admin.id);

  const ranger = await prisma.user.upsert({
    where:  { email: 'john@smartforest.tz' },
    update: {},
    create: { name: 'John Ranger', email: 'john@smartforest.tz', role: 'customer' },
  });
  console.log('[seed] Ranger:', ranger.email, 'id:', ranger.id);

  const readings = [
    { deviceId:'MIC-001',   sensorType:'microphone', zone:'Kibiti-North',
      latitude:-7.72, longitude:38.95, soundDb:42.5,  isAlert:false },
    { deviceId:'MIC-002',   sensorType:'microphone', zone:'Kibiti-South',
      latitude:-7.85, longitude:38.88, soundDb:91.5,  isAlert:true  },
    { deviceId:'FLAME-001', sensorType:'flame', zone:'Kibiti-North',
      latitude:-7.72, longitude:38.95, flameDetected:false, temperatureC:28.5, isAlert:false },
    { deviceId:'FLAME-002', sensorType:'flame', zone:'Kibiti-South',
      latitude:-7.85, longitude:38.88, flameDetected:true,  temperatureC:67.3, isAlert:true  },
  ];
  for (const r of readings) {
    await prisma.sensorReading.create({ data: r });
  }
  console.log('[seed] Created', readings.length, 'sensor readings');

  await prisma.alert.createMany({
    data: [
      { deviceId:'MIC-002',   sensorType:'microphone', alertType:'illegal_logging',
        zone:'Kibiti-South', latitude:-7.85, longitude:38.88,
        soundDb:91.5, status:'unresolved' },
      { deviceId:'FLAME-002', sensorType:'flame', alertType:'fire',
        zone:'Kibiti-South', latitude:-7.85, longitude:38.88,
        flameDetected:true, temperatureC:67.3, status:'unresolved' },
    ],
    skipDuplicates: true,
  });
  console.log('[seed] Created 2 alerts');
  console.log('[seed] Done');
}

main()
  .catch(e => { console.error('[seed] ERROR:', e.message); process.exit(1); })
  .finally(() => prisma.$disconnect());
