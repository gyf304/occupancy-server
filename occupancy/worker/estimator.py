"""Module responsible for estimating occupancy"""
import datetime

ESTIMATORS = {}

def estimate(model=None, probe_requests=None, **kwargs):
    """Estimate using a model, probe_requests an iterable of dicts"""\
    """Dict contains: rssi, mac_addr, etc"""
    time=datetime.datetime.utcnow()
    return ESTIMATORS[model](probe_requests, time=time, **kwargs)

def linear_estimator(probe_requests, time, a=1.0, b=0.0, rssi_threshold=-90.0, timespan=60, lookback=30):
    """simple linear estimator"""
    # first deduplicate
    time_threshold_low = time - datetime.timedelta(seconds=timespan) - datetime.timedelta(seconds=lookback)
    time_threshold_high = time - datetime.timedelta(seconds=lookback)
    req_dict = {}
    valid_probe_request_count = 0
    for req in probe_requests:
        rssi = req.get('rssi')
        rssi_adj = req.get('rssi_adjustment')
        adjusted_rssi = rssi + rssi_adj
        req_time = req.get('time')
        if adjusted_rssi < rssi_threshold:
            continue
        if req_time < time_threshold_low or req_time > time_threshold_high:
            continue
        stored_req = req_dict.get(req['device_mac'])
        if stored_req is None:
            stored_req = []
            req_dict[req['device_mac']] = stored_req
        stored_req.append(adjusted_rssi)
        valid_probe_request_count += 1
    relative_error = valid_probe_request_count**0.5 / valid_probe_request_count
    req_list = req_dict.values()
    # take average on rssi
    rssi_levels = list(map(lambda x: float(sum(x)) / len(x), req_list))
    # now get devices
    device_count = float(len(rssi_levels))
    o_estimate = max(device_count * a + b, 0)
    error = device_count * a * relative_error
    return {'estimate': o_estimate, 'error': error}

ESTIMATORS['linear'] = linear_estimator
