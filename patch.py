#!/usr/bin/env python3
"""
patch_ci_secrets.py — Fix CI: inject GitHub Secrets as env vars + mock Supabase in tests
Run from SmartForest ROOT: python3 patch_ci_secrets.py
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

def overwrite(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    print("  [UPDATE] " + path)

if not os.path.isdir(os.path.join(ROOT, "backend")):
    print("ERROR: Run from SmartForest ROOT folder.")
    exit(1)

# ── 1. Updated CI yml — inject secrets as env vars ───────────
CI_YML = (
    "name: CI - Test, Build & Auto-Merge to Main\n\n"
    "on:\n"
    "  push:\n"
    "    branches: [develop]\n"
    "  pull_request:\n"
    "    branches: [main]\n\n"
    "permissions:\n"
    "  contents: write\n\n"
    "jobs:\n\n"
    "  test-backend:\n"
    "    name: Backend Tests\n"
    "    runs-on: ubuntu-latest\n"
    "    env:\n"
    "      NODE_ENV: test\n"
    "      PORT: 5000\n"
    "      SUPABASE_URL: ${{ secrets.SUPABASE_URL }}\n"
    "      SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}\n"
    "      SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}\n"
    "      DATABASE_URL: ${{ secrets.DATABASE_URL }}\n"
    "      JWT_SECRET: ${{ secrets.JWT_SECRET }}\n"
    "      MQTT_BROKER: mqtt://localhost:1883\n"
    "      MQTT_TOPIC: forest/sensor/data\n"
    "      SOUND_THRESHOLD_DB: 80\n"
    "      TEMP_THRESHOLD_C: 55\n"
    "      DEDUP_MINUTES: 5\n"
    "    steps:\n"
    "      - uses: actions/checkout@v4\n"
    "      - name: Setup Node.js\n"
    "        uses: actions/setup-node@v4\n"
    "        with:\n"
    "          node-version: '20'\n"
    "          cache: 'npm'\n"
    "          cache-dependency-path: backend/package-lock.json\n"
    "      - name: Install dependencies\n"
    "        working-directory: ./backend\n"
    "        run: npm ci\n"
    "      - name: Run tests\n"
    "        working-directory: ./backend\n"
    "        run: npm test\n\n"
    "  test-frontend:\n"
    "    name: Frontend Lint & Build\n"
    "    runs-on: ubuntu-latest\n"
    "    steps:\n"
    "      - uses: actions/checkout@v4\n"
    "      - name: Setup Node.js\n"
    "        uses: actions/setup-node@v4\n"
    "        with:\n"
    "          node-version: '20'\n"
    "          cache: 'npm'\n"
    "          cache-dependency-path: frontend/package-lock.json\n"
    "      - name: Install dependencies\n"
    "        working-directory: ./frontend\n"
    "        run: npm ci\n"
    "      - name: Lint\n"
    "        working-directory: ./frontend\n"
    "        run: npm run lint\n"
    "      - name: Build\n"
    "        working-directory: ./frontend\n"
    "        run: npm run build\n"
    "        env:\n"
    "          VITE_API_URL_CLOUD: ${{ secrets.VITE_API_URL_CLOUD }}\n"
    "          VITE_API_URL_LOCAL: http://localhost:5000/api\n\n"
    "  test-simulator:\n"
    "    name: Simulator Tests\n"
    "    runs-on: ubuntu-latest\n"
    "    steps:\n"
    "      - uses: actions/checkout@v4\n"
    "      - name: Setup Python\n"
    "        uses: actions/setup-python@v5\n"
    "        with:\n"
    "          python-version: '3.11'\n"
    "      - name: Install dependencies\n"
    "        run: pip install -r simulator/requirements.txt\n"
    "      - name: Run tests\n"
    "        run: pytest simulator/tests/ -v\n\n"
    "  docker-build:\n"
    "    name: Docker Build Check\n"
    "    runs-on: ubuntu-latest\n"
    "    needs: [test-backend, test-frontend]\n"
    "    steps:\n"
    "      - uses: actions/checkout@v4\n"
    "      - name: Build backend Docker image\n"
    "        run: docker build ./backend -t smartforest-backend\n\n"
    "  auto-merge-to-main:\n"
    "    name: Auto-merge to Main\n"
    "    runs-on: ubuntu-latest\n"
    "    needs: [test-backend, test-frontend, test-simulator, docker-build]\n"
    "    if: github.ref == 'refs/heads/develop' && github.event_name == 'push'\n"
    "    steps:\n"
    "      - uses: actions/checkout@v4\n"
    "        with:\n"
    "          fetch-depth: 0\n"
    "          token: ${{ secrets.GITHUB_TOKEN }}\n"
    "      - name: Configure Git\n"
    "        run: |\n"
    "          git config user.name \"github-actions[bot]\"\n"
    "          git config user.email \"github-actions[bot]@users.noreply.github.com\"\n"
    "      - name: Merge develop into main\n"
    "        run: |\n"
    "          git checkout main\n"
    "          git merge develop --no-ff -m \"ci: auto-merge develop into main [skip ci]\"\n"
    "          git push origin main\n"
)

# ── 2. Jest setup file — mock Supabase + pg pool for tests ───
JEST_SETUP = (
    "// jest.setup.js\n"
    "// Runs before every test file.\n"
    "// Mocks external services so tests never need a live DB or Supabase.\n\n"
    "// ── Mock pg Pool (Supabase PostgreSQL) ──────────────────\n"
    "jest.mock('./src/config/db', () => {\n"
    "  return {\n"
    "    query: jest.fn().mockResolvedValue({ rows: [], rowCount: 0 }),\n"
    "  };\n"
    "});\n\n"
    "// ── Mock Supabase client ─────────────────────────────────\n"
    "jest.mock('./src/config/supabase', () => {\n"
    "  return {\n"
    "    auth: {\n"
    "      signInWithPassword: jest.fn().mockResolvedValue({\n"
    "        data: null,\n"
    "        error: { message: 'Invalid credentials' },\n"
    "      }),\n"
    "      signOut: jest.fn().mockResolvedValue({ error: null }),\n"
    "      getUser: jest.fn().mockResolvedValue({\n"
    "        data: null,\n"
    "        error: { message: 'Invalid token' },\n"
    "      }),\n"
    "    },\n"
    "  };\n"
    "});\n\n"
    "// ── Mock MQTT (no broker needed in tests) ────────────────\n"
    "jest.mock('mqtt', () => ({\n"
    "  connect: jest.fn().mockReturnValue({\n"
    "    on         : jest.fn(),\n"
    "    subscribe  : jest.fn(),\n"
    "    publish    : jest.fn(),\n"
    "    disconnect : jest.fn(),\n"
    "  }),\n"
    "}));\n"
)

# ── 3. Updated package.json — point to jest setup file ───────
PACKAGE_JSON = (
    '{\n'
    '  "name": "backend",\n'
    '  "version": "1.0.0",\n'
    '  "description": "SmartForest illegal logging detection backend",\n'
    '  "main": "src/index.js",\n'
    '  "type": "commonjs",\n'
    '  "scripts": {\n'
    '    "start": "node src/index.js",\n'
    '    "dev": "nodemon src/index.js",\n'
    '    "test": "jest",\n'
    '    "test:verbose": "jest --verbose"\n'
    '  },\n'
    '  "jest": {\n'
    '    "testEnvironment": "node",\n'
    '    "forceExit": true,\n'
    '    "silent": true,\n'
    '    "testTimeout": 10000,\n'
    '    "setupFiles": ["./jest.setup.js"]\n'
    '  },\n'
    '  "dependencies": {\n'
    '    "@supabase/supabase-js": "^2.49.0",\n'
    '    "cors": "^2.8.6",\n'
    '    "dotenv": "^17.4.2",\n'
    '    "express": "^5.2.1",\n'
    '    "mqtt": "^5.15.1",\n'
    '    "pg": "^8.21.0"\n'
    '  },\n'
    '  "devDependencies": {\n'
    '    "jest": "^30.4.2",\n'
    '    "nodemon": "^3.1.14",\n'
    '    "supertest": "^7.2.2"\n'
    '  }\n'
    '}\n'
)

print("\nApplying CI secrets fix...\n")
overwrite(".github/workflows/ci.yml", CI_YML)
overwrite("backend/jest.setup.js",    JEST_SETUP)
overwrite("backend/package.json",     PACKAGE_JSON)

print("""
Done! Now:
  git add .
  git commit -m "ci: inject secrets as env vars, mock supabase+db in tests"
  git push origin develop
""")
