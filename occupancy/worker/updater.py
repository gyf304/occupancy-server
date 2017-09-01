"""Updates occupancy information"""
import datetime
import json
import sys

from . import estimator, scheduler
from .. import config, db, model

@scheduler.scheduled_job('interval', seconds=config.OCCUPANCY_UPDATE_INTERVAL)
def update():
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
            print('[ERROR] Updater: Update of {} skipped: Estimator config error'.format(repr(location)),
                  file=sys.stderr)
            continue
        # check if sniffers are online, if not, stop update of that
        # location or mark location as degraded.
        for sniffer in location.sniffers:
            if sniffer.updated and sniffer.updated >= sniffer_time_threshold:
                active_sniffer_count += 1
            else:
                print('[WARNING] Updater: {} missing'.format(repr(sniffer)),
                      file=sys.stderr)
        if active_sniffer_count == 0:
            print('[ERROR] Updater: Update of {} skipped: No active sniffer'.format(repr(location)),
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
            print('[ERROR] Updater: Update of {} skipped: Estimator returned None'.format(repr(location)),
                  file=sys.stderr)
            continue
        occupancy_snapshot = model.OccupancySnapshot(
            location=location, time=datetime.datetime.utcnow(),
            degraded=(active_sniffer_count < len(location.sniffers)),
            estimate=ret['estimate'], error=ret['error'])
        session.add(occupancy_snapshot)
    session.commit()
    session.close()
