"""Configuration for server."""

# connectivity
ENCRYPT_KEY = b'testtesttesttest'
AUTH_KEY = b'testtesttesttest'
AUTH_IV = b'\0\0\0\0\0\0\0\0'
DB_URI = 'sqlite:///test.db'

# misc
PROBE_REQUEST_LIFE = 12 # in hours
OCCUPANCY_UPDATE_INTERVAL = 60 # in seconds
SNIFFER_MAX_INACTIVE_TIME = 300 # in seconds
ESTIMATOR_CONFIG = {
    'sorrells': {
        'model': 'linear',
        'a': 1.0,
        'b': 0.0,
        'rssi_threshold': -90.0,
        'timespan': 120
    }
}
