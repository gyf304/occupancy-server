# Occupancy Server

A part of CMU Library Occupancy project. Written in Python 3.

## Configuration

Configuration is read from environment variables.

### XTEA-CCM Encryption

Please change both `ENCRYPT_KEY` and `AUTH_KEY` environment variables to randomly generated octets. Note that for proper encryption and authentication, two should never be the same. Same values should be used for the sniffers.

Example: 
`ENCRYPT_KEY="74 65 73 74 74 65 73 74 74 65 73 74 74 65 73 74"`

### DB Settings

Change `DB_URI` to point to your DB. If testing locally, use `sqlite:///test.local.db`.

### Sniffer Settings

`SNIFFER_MAX_INACTIVE_TIME` represents the maximum interval in seconds that sniffers should report before considered as inactive.

`OCCUPANCY_UPDATE_INTERVAL` represents the interval in seconds that occupancy information is updated.

`PROBE_REQUEST_LIFE` represents the minimum life of probe requests in DB before wiped.

## Initial System Set-Up

To add locations and sniffers to the system, manual DB editing is required.

TODO: DB editing tutorial.

## Deploy Instructions

### Heroku

  The repository is ready to be deployed to Heroku without further changes.

### Locally

  Copy `app.local.example.json` to `app.local.json`, modify environment variables and run `python3 run_local.py`. Use `Ctrl-C` to kill.
