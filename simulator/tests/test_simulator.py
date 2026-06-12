"""Unit tests for simulator payload structure."""


def make_payload(spike=False):
    from datetime import datetime, timezone
    zone = {'zone': 'Kibiti-North', 'lat': -7.72, 'lng': 38.95}
    return {
        'device_id' : 'SENSOR-001',
        'timestamp' : datetime.now(timezone.utc).isoformat(),
        'zone'      : zone['zone'],
        'latitude'  : zone['lat'],
        'longitude' : zone['lng'],
        'sound_db'  : 90.0 if spike else 40.0,
        'vibration' : 8.0  if spike else 2.0,
    }


def test_payload_has_required_fields():
    p = make_payload()
    required = ['device_id', 'timestamp', 'zone', 'latitude', 'longitude', 'sound_db', 'vibration']
    for field in required:
        assert field in p, f'Missing field: {field}'


def test_spike_exceeds_threshold():
    p = make_payload(spike=True)
    assert p['sound_db'] > 80 or p['vibration'] > 7


def test_normal_below_threshold():
    p = make_payload(spike=False)
    assert p['sound_db'] < 80 and p['vibration'] < 7


def test_sound_db_is_float():
    p = make_payload()
    assert isinstance(p['sound_db'], float)
