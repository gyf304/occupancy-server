"""Cleans Probe Requests"""
import datetime
import json
import sys

from . import scheduler
from .. import config, db, model

@scheduler.scheduled_job('interval', seconds=config.PROBE_REQUEST_LIFE)
def clean():
    current_time = datetime.datetime.utcnow()
    session = db.session_factory()
    probe_requests = session.query(model.ProbeRequest).all()
    time_threshold = current_time - datetime.timedelta(hours=config.PROBE_REQUEST_LIFE)
    for probe_request in probe_requests:
        if probe_request.time < time_threshold:
            session.delete(probe_request)
    session.commit()
    session.close()
