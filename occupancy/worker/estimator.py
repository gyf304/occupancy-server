"""Module responsible for estimating occupancy"""
import datetime

ESTIMATORS = {}

def estimate(model=None, probe_requests=None, time=datetime.datetime.utcnow(), **kwargs):
    """Estimate using a model, probe_requests an iterable of dicts"""\
    """Dict contains: rssi, mac_addr, etc"""
    return ESTIMATORS[model](probe_requests, time=time, **kwargs)

def linear_estimator(probe_requests, time, a=1.0, b=0.0, rssi_threshold=-90.0, timespan=60):
    """simple linear estimator"""
    # first deduplicate
    time_threshold = time - datetime.timedelta(seconds=timespan)
    req_dict = {}
    for req in probe_requests:
        rssi = req.get('rssi')
        rssi_adj = req.get('rssi_adjustment')
        adjusted_rssi = rssi + rssi_adj
        req_time = req.get('time')
        if req_time < time_threshold:
            continue
        stored_req = req_dict.get(req['device_mac'])
        if stored_req is None:
            stored_req = []
            req_dict[req['device_mac']] = stored_req
        stored_req.append(adjusted_rssi)
    req_list = req_dict.values()
    # take average on rssi
    rssi_levels = list(map(lambda x: float(sum(x)) / len(x), req_list))
    # drop devices less than threshold
    filtered_rssi_levels = list(filter(lambda x: x >= rssi_threshold, rssi_levels))
    # now get devices
    device_count = float(len(filtered_rssi_levels))
    o_estimate = device_count * a + b
    error = o_estimate**0.4 # made up some random number here
    return {'estimate': o_estimate, 'error': error}

ESTIMATORS['linear'] = linear_estimator
