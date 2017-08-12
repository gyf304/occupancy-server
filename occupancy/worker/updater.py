"""Updates occupancy information"""
import datetime
import json
import sys

from . import estimator, scheduler
from .. import config, db, model

@scheduler.scheduled_job('interval', seconds=config.OCCUPANCY_UPDATE_INTERVAL)
def run():
    """runs the update"""
    session = db.session_factory()
    locations = session.query(model.Location).all()
    current_time = datetime.datetime.utcnow()
    sniffer_time_threshold = current_time \
        - datetime.timedelta(seconds=config.SNIFFER_MAX_INACTIVE_TIME)
    for location in locations:
        active_sniffer_count = 0
        try:
            estimator_config = json.loads(str(location.estimator_config))
        except (json.decoder.JSONDecodeError, TypeError):
            print('Update of location {} skipped: No estimator config'.format(location.name),
                  file=sys.stderr)
            continue
        # check if sniffers are online, if not, stop update of that
        # location or mark location as degraded.
        for sniffer in location.sniffers:
            if sniffer.updated >= sniffer_time_threshold:
                active_sniffer_count += 1
        if active_sniffer_count == 0:
            print('Update of location {} skipped: No active sniffer'.format(location.name),
                  file=sys.stderr)
            continue
        probe_requests = []
        for sniffer in location.sniffers:
            for probe_request in sniffer.probe_requests:
                probe_requests.append({
                    'device_mac': probe_request.device_mac,
                    'time': probe_request.time,
                    'rssi': probe_request.rssi,
                    'rssi_adjustment': sniffer.rssi_adjustment,
                })
        ret = estimator.estimate(probe_requests=probe_requests, **estimator_config)
        if ret is None:
            print('Update of location {} skipped: Estimator returned None'.format(location.name),
                  file=sys.stderr)
            continue
        occupancy_snapshot = model.OccupancySnapshot(
            location=location, time=datetime.datetime.utcnow(),
            degraded=(active_sniffer_count < len(location.sniffers)),
            estimate=ret['estimate'], error=ret['error'])
        session.add(occupancy_snapshot)
    session.commit()
    clean = False
    if clean:
        probe_requests = session.query(model.ProbeRequest).all()
        time_threshold = current_time - datetime.timedelta(hours=config.PROBE_REQUEST_LIFE)
        for probe_request in probe_requests:
            if probe_request.time < time_threshold:
                session.delete(probe_request)
        session.commit()
    session.close()
