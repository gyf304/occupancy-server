"""THE app"""
import random
import struct

from flask import jsonify, request

from . import app, rpc
# configure database
from .. import config, db, model

@app.route('/api/v1/locations/')
def location_list():
    """Lists all possible locations"""
    session = db.session_factory()
    locations = list(map(lambda x: {
        'name': x.name,
        'displayNmae': x.display_name,
        'description': x.description
    }, session.query(model.Location).all()))
    session.close()
    return jsonify(locations), 200

@app.route('/api/v1/locations/<location_str>')
def location_info(location_str):
    """HTTP entrypoint for obtaining information of a location"""
    session = db.session_factory()
    location = session.query(model.Location).filter_by(name=location_str).first()
    if location is None:
        return jsonify({'error': 'Location not Found'}), 404
    reply = {
        'name': location.name,
        'displayName': location.display_name,
        'description': location.description
    }
    session.close()
    return jsonify(reply), 200

@app.route('/api/v1/locations/<location_str>/occupancy')
def occupancy(location_str):
    """HTTP entrypoint for getting occupancy of a location"""
    session = db.session_factory()
    count_str = request.args.get('count', '5')
    count = 0
    try:
        count = int(count_str)
    except ValueError:
        return jsonify({'error': 'Invalid Argument'}), 400
    location = session.query(model.Location).filter_by(name=location_str).first()
    if location is None:
        return jsonify({'error': 'Location not Found'}), 404
    occupancy_snapshots = \
        location.occupancy_snapshots.order_by(model.OccupancySnapshot.time)[-count:]
    occupancy_list = list(map(lambda x: {
        'estimate': x.estimate, 'error': x.error,
        'time': x.time, 'degraded': x.degraded
    }, occupancy_snapshots))
    session.close()
    return jsonify(occupancy_list), 200
