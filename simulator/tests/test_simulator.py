"""
SmartForest Simulator Tests
"""

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set env vars BEFORE importing simulator so config reads them
os.environ.setdefault('BACKEND_URL_LOCAL', 'http://localhost:5000')
os.environ.setdefault('MQTT_BROKER_HOST',  'localhost')
os.environ.setdefault('SEND_INTERVAL',     '5')
os.environ.setdefault('SPIKE_CHANCE',      '0.20')

import mqtt_simulator as sim


class TestPayloadGenerators:
    def test_mic_normal_payload_schema(self):
        p = sim.make_mic(spike=False)
        assert 'device_id'    in p
        assert 'sensor_type'  in p
        assert 'zone'         in p
        assert 'sound_db'     in p
        assert 'latitude'     in p
        assert 'longitude'    in p
        assert 'timestamp'    in p
        assert p['sensor_type'] == 'microphone'

    def test_mic_spike_high_db(self):
        for _ in range(20):
            p = sim.make_mic(spike=True)
            assert p['sound_db'] >= 80, f"spike reading {p['sound_db']} below threshold"

    def test_mic_normal_low_db(self):
        for _ in range(20):
            p = sim.make_mic(spike=False)
            assert p['sound_db'] < 80, f"normal reading {p['sound_db']} above threshold"

    def test_flame_normal_payload_schema(self):
        p = sim.make_flame(spike=False)
        assert 'device_id'      in p
        assert 'sensor_type'    in p
        assert 'flame_detected' in p
        assert 'temperature_c'  in p
        assert p['sensor_type'] == 'flame'
        assert p['flame_detected'] == False

    def test_flame_spike_detected(self):
        p = sim.make_flame(spike=True)
        assert p['flame_detected'] == True
        assert p['temperature_c'] >= 55

    def test_payload_json_serializable(self):
        for fn, s in [(sim.make_mic, False), (sim.make_mic, True),
                      (sim.make_flame, False), (sim.make_flame, True)]:
            p = fn(s)
            j = json.dumps(p)
            assert isinstance(j, str)
            assert len(j) > 10

    def test_device_ids_format(self):
        for _ in range(10):
            mic_p = sim.make_mic(False)
            assert mic_p['device_id'].startswith(sim.PREFIX + '-m')
            flm_p = sim.make_flame(False)
            assert flm_p['device_id'].startswith(sim.PREFIX + '-f')

    def test_zone_is_valid(self):
        valid_zones = {z['zone'] for z in sim.ZONES}
        for _ in range(10):
            p = sim.make_mic(False)
            assert p['zone'] in valid_zones

    def test_coordinates_near_kibiti(self):
        """Coordinates should be within ~1 degree of Kibiti, Tanzania"""
        for _ in range(10):
            p = sim.make_mic(False)
            assert -9.0 < p['latitude']  < -6.5
            assert  37.5 < p['longitude'] < 40.5


class TestBackendCandidates:
    def test_candidates_list_not_empty(self):
        assert len(sim.BACKEND_CANDIDATES) >= 1

    def test_local_candidate_present(self):
        assert any('localhost' in c for c in sim.BACKEND_CANDIDATES)

    def test_probe_returns_bool(self):
        # Probe a definitely-closed port — should return False quickly
        result = sim.probe('http://localhost:19999', timeout=1)
        assert result is False

    def test_resolve_returns_none_when_all_down(self, monkeypatch):
        # Patch probe to always fail
        monkeypatch.setattr(sim, 'probe', lambda url, t=3: False)
        sim._resolved = None  # reset cache if module-level
        result = sim.resolve_backend()
        assert result is None


class TestSentinel:
    def test_sentinel_path_is_in_simulator_dir(self):
        import pathlib
        expected_dir = pathlib.Path(__file__).parent.parent
        assert sim.SENTINEL.parent == expected_dir
