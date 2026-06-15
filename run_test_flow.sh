#!/usr/bin/env bash
# ============================================================
# SmartForest Daily Testing Flow
# Run from SmartForest ROOT: bash run_test_flow.sh
# ============================================================
# Flow:
#  1. Check backend (Render cloud first, local fallback)
#  2. Run backend unit tests
#  3. Run simulator pytest tests
#  4. Start MQTT broker (if not running)
#  5. Start backend locally (if cloud not available)
#  6. Start simulator -> triggers MQTT -> backend -> Supabase
#  7. Verify data in DB via API calls
# ============================================================

set -e

CLOUD_URL="${CLOUD_BACKEND_URL:-}"
LOCAL_URL="http://localhost:5000"
BACKEND_URL=""

echo ""
echo "============================================================"
echo " SmartForest Daily Test Flow"
echo "============================================================"

# ── Step 1: Detect active backend ───────────────────────
echo ""
echo "[1/5] Detecting active backend..."
if [ -n "$CLOUD_URL" ]; then
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
             --connect-timeout 4 "$CLOUD_URL/api/health" || echo "000")
    if [ "$STATUS" = "200" ]; then
        BACKEND_URL="$CLOUD_URL"
        echo "  Backend: CLOUD (Render) -> $CLOUD_URL"
    else
        echo "  Cloud backend not reachable (status: $STATUS)"
    fi
fi

if [ -z "$BACKEND_URL" ]; then
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
             --connect-timeout 2 "$LOCAL_URL/api/health" || echo "000")
    if [ "$STATUS" = "200" ]; then
        BACKEND_URL="$LOCAL_URL"
        echo "  Backend: LOCAL -> $LOCAL_URL"
    else
        echo "  Local backend not running. Starting it..."
        echo "  Run in a new terminal: cd backend && npm run dev"
        echo "  Then re-run this script."
        exit 1
    fi
fi

# ── Step 2: Backend unit tests ───────────────────────────
echo ""
echo "[2/5] Running backend tests..."
cd backend && npm test && cd ..
echo "  Backend tests: PASSED"

# ── Step 3: Simulator pytest ─────────────────────────────
echo ""
echo "[3/5] Running simulator tests..."
cd simulator
if [ ! -d venv ]; then
    echo "  Creating venv..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt -q
else
    source venv/bin/activate
fi
pytest tests/ -v
cd ..
echo "  Simulator tests: PASSED"

# ── Step 4: Verify API endpoints ─────────────────────────
echo ""
echo "[4/5] Verifying API endpoints..."
echo ""

echo "  GET /api/health"
curl -s "$BACKEND_URL/api/health" | python3 -m json.tool

echo ""
echo "  GET /api/sensors (last 3)"
curl -s "$BACKEND_URL/api/sensors" | \
    python3 -c "import sys,json; d=json.load(sys.stdin); \
    [print('   ',r.get('device_id'),r.get('sensor_type'),\
    r.get('sound_db',''),r.get('temperature_c','')) for r in d[:3]]"

echo ""
echo "  GET /api/alerts/count"
curl -s "$BACKEND_URL/api/alerts/count" | python3 -m json.tool

echo ""
echo "  GET /api/alerts (last 3)"
curl -s "$BACKEND_URL/api/alerts" | \
    python3 -c "import sys,json; d=json.load(sys.stdin); \
    [print('   ',a.get('alert_type'),a.get('device_id'),\
    a.get('zone'),a.get('status')) for a in d[:3]]"

# ── Step 5: Start simulator ───────────────────────────────
echo ""
echo "[5/5] Starting simulator (Ctrl+C to stop)..."
echo "      Watch Supabase Table Editor for new rows:"
echo "      https://supabase.com/dashboard/project/mcnhuvfbtsddtnuwatkj/editor"
echo ""
cd simulator
source venv/bin/activate
CLOUD_BACKEND_URL="$CLOUD_URL" python mqtt_simulator.py
