// Jest setup - mock Supabase and database models
jest.mock('./src/config/supabase', () => ({
  auth: {
    signInWithPassword: jest.fn().mockResolvedValue({
      data: {
        user: {
          id: 'test-user-123',
          email: 'test@example.com',
          user_metadata: { 
            name: 'Test User', 
            role: 'ranger' 
          }
        },
        session: {
          access_token: 'test-token-xyz',
          expires_at: Math.floor(Date.now() / 1000) + 3600
        }
      },
      error: null
    }),
    signOut: jest.fn().mockResolvedValue({ error: null }),
    getUser: jest.fn().mockResolvedValue({
      data: {
        user: {
          id: 'test-user-123',
          email: 'test@example.com'
        }
      },
      error: null
    })
  }
}));

jest.mock('./src/models/userModel', () => ({
  create: jest.fn().mockResolvedValue({
    id: 'user-123',
    email: 'test@example.com',
    role: 'ranger',
    name: 'Test User'
  }),
  getByEmail: jest.fn().mockResolvedValue({
    id: 'user-123',
    email: 'test@example.com',
    role: 'ranger',
    name: 'Test User'
  }),
  getById: jest.fn().mockResolvedValue({
    id: 'user-123',
    email: 'test@example.com',
    role: 'ranger',
    name: 'Test User'
  })
}));

jest.mock('./src/config/database', () => ({
  query: jest.fn().mockResolvedValue({ rows: [] }),
  execute: jest.fn().mockResolvedValue({ success: true })
}));

// Suppress console noise during tests
global.console.error = jest.fn();
global.console.warn = jest.fn();
