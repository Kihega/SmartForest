'use strict';
/**
 * Singleton PrismaClient.
 *
 * In development, Next.js/Vite hot-reload can create many instances.
 * The global singleton pattern prevents that.
 *
 * In test (NODE_ENV=test), we export a mock-friendly instance.
 * Jest mocks this whole module in jest.setup.js.
 */
const { PrismaClient } = require('@prisma/client');

let prisma;

if (process.env.NODE_ENV === 'production') {
  prisma = new PrismaClient({
    log: ['error'],
  });
} else {
  // Reuse across HMR/nodemon restarts
  if (!global.__prisma) {
    global.__prisma = new PrismaClient({
      log: process.env.NODE_ENV === 'test' ? [] : ['warn', 'error'],
    });
  }
  prisma = global.__prisma;
}

module.exports = prisma;
