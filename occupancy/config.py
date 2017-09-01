"""Configuration for server."""
from os import environ
import sys
import binascii

# connectivity
try:
    ENCRYPT_KEY = binascii.unhexlify(environ['ENCRYPT_KEY'].replace(' ', ''))
    AUTH_KEY = binascii.unhexlify(environ['AUTH_KEY'].replace(' ', ''))
    AUTH_IV = binascii.unhexlify(environ['AUTH_IV'].replace(' ', ''))
    assert len(ENCRYPT_KEY) == 16
    assert len(AUTH_KEY) == 16
    assert len(AUTH_IV) == 8
except (KeyError, AssertionError, binascii.Error):
    print('[WARNING] Encryption config not loaded correctly, using default', file=sys.stderr)
    ENCRYPT_KEY = b'testtesttesttest'
    AUTH_KEY = b'testtesttesttest'
    AUTH_IV = b'\0\0\0\0\0\0\0\0'

try:
    DB_URI = environ['DB_URI']
except KeyError:
    print('[WARNING] Database config not loaded correctly, using default', file=sys.stderr)
    DB_URI = 'sqlite:///test.db'

try:
    PROBE_REQUEST_LIFE = int(environ['PROBE_REQUEST_LIFE'])
    OCCUPANCY_UPDATE_INTERVAL = int(environ['OCCUPANCY_UPDATE_INTERVAL'])
    MAINTENANCE_INTERVAL = int(environ['MAINTENANCE_INTERVAL'])
    SNIFFER_MAX_INACTIVE_TIME = int(environ['SNIFFER_MAX_INACTIVE_TIME'])

except (KeyError, ValueError):
    print('[WARNING] Misc config not loaded correctly, using default', file=sys.stderr)
    PROBE_REQUEST_LIFE = 43200 # in seconds
    OCCUPANCY_UPDATE_INTERVAL = 60 # in seconds
    MAINTENANCE_INTERVAL = 43200
    SNIFFER_MAX_INACTIVE_TIME = 300 # in seconds
