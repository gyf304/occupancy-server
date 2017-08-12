"""Configuration for server."""
from os import environ
import sys

# connectivity

try:
    ENCRYPT_KEY = environ['ENCRYPT_KEY'].encode('ascii')
    AUTH_KEY = environ['AUTH_KEY'].encode('ascii')
    AUTH_IV = environ['AUTH_IV'].encode('ascii')
    assert len(ENCRYPT_KEY) == 16
    assert len(AUTH_KEY) == 16
except (KeyError, AssertionError):
    print('Encryption config not loaded correctly, using default', file=sys.stderr)
    ENCRYPT_KEY = b'testtesttesttest'
    AUTH_KEY = b'testtesttesttest'
    AUTH_IV = b'\0\0\0\0\0\0\0\0'

try:
    DB_URI = environ['DB_URI']
except KeyError:
    print('Database config not loaded correctly, using default', file=sys.stderr)
    DB_URI = 'sqlite:///test.db'

try:
    PROBE_REQUEST_LIFE = int(environ['PROBE_REQUEST_LIFE'])
    OCCUPANCY_UPDATE_INTERVAL = int(environ['OCCUPANCY_UPDATE_INTERVAL'])
    SNIFFER_MAX_INACTIVE_TIME = int(environ['SNIFFER_MAX_INACTIVE_TIME'])
except (KeyError, ValueError):
    print('Misc config not loaded correctly, using default', file=sys.stderr)
    PROBE_REQUEST_LIFE = 12 # in hours
    OCCUPANCY_UPDATE_INTERVAL = 60 # in seconds
    SNIFFER_MAX_INACTIVE_TIME = 300 # in seconds
# misc

ESTIMATOR_CONFIG = {
    'sorrells': {
        'model': 'linear',
        'a': 1.0,
        'b': 0.0,
        'rssi_threshold': -90.0,
        'timespan': 120
    }
}
