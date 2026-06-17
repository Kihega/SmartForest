# SmartForest Simulator Tests
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

os.environ.setdefault('BACKEND_URL',    'http://localhost:5000')
os.environ.setdefault('MQTT_BROKER_HOST', 'localhost')
os.environ.setdefault('SEND_INTERVAL',  '180')
os.environ.setdefault('SPIKE_CHANCE',   '0.20')

import mqtt_simulator as sim


class TestPayloadGenerators:
    def test_mic_normal_payload_schema(self):
        p = sim.make_mic(spike=False)
        assert 'device_id'   in p
        assert 'sensor_type' in p
        assert 'zone'        in p
        assert 'sound_db'    in p
        assert 'latitude'    in p
        assert 'longitude'   in p
        assert 'timestamp'   in p
        assert p['sensor_type'] == 'microphone'

    def test_mic_spike_high_db(self):
        for _ in range(20):
            p = sim.make_mic(spike=True)
            assert p['sound_db'] >= 80

    def test_mic_normal_low_db(self):
        for _ in range(20):
            p = sim.make_mic(spike=False)
            assert p['sound_db'] < 80

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
        for _ in range(10):
            p = sim.make_mic(False)
            assert -9.0 < p['latitude']  < -6.5
            assert  37.5 < p['longitude'] < 40.5


class TestDrift:
    def test_drift_stays_within_bounds(self):
        sim._state.clear()
        for _ in range(50):
            p = sim.make_mic(spike=False)
            assert 18 <= p['sound_db'] <= 65

    def test_drift_changes_gradually(self):
        sim._state.clear()
        device = sim.MIC_IDS[0]
        sim._state[device] = 35
        val1 = sim._drift(device, 35, 18, 65, 6)
        val2 = sim._drift(device, 35, 18, 65, 6)
        # consecutive drift steps should differ by at most 2x max_step
        assert abs(val2 - val1) <= 12


class TestSingleBackendUrl:
    def test_backend_url_is_single_string(self):
        assert isinstance(sim.BACKEND_URL, str)
        assert sim.BACKEND_URL.startswith('http')

    def test_no_priority_list_attribute(self):
        # Ensure the old multi-candidate design is gone
        assert not hasattr(sim, 'BACKEND_CANDIDATES')

    def test_probe_returns_bool(self):
        old_url = sim.BACKEND_URL
        sim.BACKEND_URL = 'http://localhost:19999'
        result = sim.probe_backend(timeout=1)
        sim.BACKEND_URL = old_url
        assert result is False


class TestSentinel:
    def test_sentinel_path_is_in_simulator_dir(self):
        import pathlib
        expected_dir = pathlib.Path(__file__).parent.parent
        assert sim.SENTINEL.parent == expected_dir


class TestInterval:
    def test_default_interval_is_three_minutes(self):
        assert sim.INTERVAL == 180
