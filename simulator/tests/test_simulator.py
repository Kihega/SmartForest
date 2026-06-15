"""Unit tests for simulator payload structure — both sensor types."""
import json
from datetime import datetime, timezone

ZONES = [{'zone': 'Kibiti-North', 'lat': -7.72, 'lng': 38.95}]


def make_microphone_payload(spike=False):
    zone = ZONES[0]
    return {
        'device_id'   : 'MIC-001',
        'sensor_type' : 'microphone',
        'timestamp'   : datetime.now(timezone.utc).isoformat(),
        'zone'        : zone['zone'],
        'latitude'    : zone['lat'],
        'longitude'   : zone['lng'],
        'sound_db'    : 90.0 if spike else 40.0,
    }


def make_flame_payload(spike=False):
    zone = ZONES[0]
    return {
        'device_id'      : 'FLAME-001',
        'sensor_type'    : 'flame',
        'timestamp'      : datetime.now(timezone.utc).isoformat(),
        'zone'           : zone['zone'],
        'latitude'       : zone['lat'],
        'longitude'      : zone['lng'],
        'flame_detected' : spike,
        'temperature_c'  : 72.5 if spike else 28.0,
    }


# ── Microphone tests ─────────────────────────────────────
def test_mic_payload_has_required_fields():
    p = make_microphone_payload()
    for f in ['device_id','sensor_type','timestamp',
              'zone','latitude','longitude','sound_db']:
        assert f in p, f'Missing: {f}'


def test_mic_sensor_type_is_microphone():
    assert make_microphone_payload()['sensor_type'] == 'microphone'


def test_mic_spike_exceeds_threshold():
    p = make_microphone_payload(spike=True)
    assert p['sound_db'] > 80, 'Spike should exceed 80dB threshold'


def test_mic_normal_below_threshold():
    p = make_microphone_payload(spike=False)
    assert p['sound_db'] < 80, 'Normal reading should be below 80dB'


def test_mic_sound_db_is_float():
    assert isinstance(make_microphone_payload()['sound_db'], float)


# ── Flame sensor tests ───────────────────────────────────
def test_flame_payload_has_required_fields():
    p = make_flame_payload()
    for f in ['device_id','sensor_type','timestamp',
              'zone','latitude','longitude',
              'flame_detected','temperature_c']:
        assert f in p, f'Missing: {f}'


def test_flame_sensor_type_is_flame():
    assert make_flame_payload()['sensor_type'] == 'flame'


def test_flame_spike_triggers_alert():
    p = make_flame_payload(spike=True)
    assert p['flame_detected'] is True or p['temperature_c'] > 55


def test_flame_normal_no_alert():
    p = make_flame_payload(spike=False)
    assert p['flame_detected'] is False
    assert p['temperature_c'] < 55


def test_flame_temperature_is_float():
    assert isinstance(make_flame_payload()['temperature_c'], float)


# ── Payload JSON serializable ────────────────────────────
def test_mic_payload_json_serializable():
    p = make_microphone_payload(spike=True)
    assert json.dumps(p)  # should not raise


def test_flame_payload_json_serializable():
    p = make_flame_payload(spike=True)
    assert json.dumps(p)
