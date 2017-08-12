"""Includes RPC routines for sniffer"""
import binascii
import datetime
import random
import struct

import netaddr
from flask import request

from . import simple_xtea as xtea
# configure database
from . import app
from .. import config, db, model

_RPC_FUNCTIONS = dict()

@app.route('/rpc/hxdt', methods=['POST'])
def hxdt_api():
    """"HTTP entrypoint for HXDT rpc calls"""
    hxdt_fmt = '>II8s8s'
    header_size = struct.calcsize(hxdt_fmt)
    if len(request.data) < header_size:
        print('Invalid size!')
        return '', 400
    hxdt_header = struct.unpack(hxdt_fmt, request.data[:header_size])
    cryptogram = request.data[header_size:]
    (ver, cryptogram_len, iv, client_mac) = hxdt_header
    if len(cryptogram) != cryptogram_len:
        print('Cryptogram length mismatch!')
        return '', 400
    if cryptogram_len % 8 != 0:
        print('Cryptogram not padded correctly.')
        return '', 400
    server_mac = xtea.cbc_mac(config.AUTH_KEY, config.AUTH_IV, cryptogram)
    if server_mac != client_mac:
        print('Server Client MAC mismatch!')
        return '', 400
    padded_datagram = xtea.ctr(config.ENCRYPT_KEY, iv, cryptogram)
    (plaintext_len, ) = struct.unpack('>I', padded_datagram[:4])
    padded_plaintext = padded_datagram[4:]
    if plaintext_len < 8 or plaintext_len > len(padded_plaintext):
        print('Illegal Plaintext length')
        return '', 400
    plaintext = padded_plaintext[:plaintext_len]
    rpc_function_name = plaintext[:8].decode('ascii').lower().strip('\0')
    rpc_args = plaintext[8:]
    ret = None
    try:
        ret = run(rpc_function_name, rpc_args)
    except NotImplementedError:
        return '', 501
    except AssertionError:
        return '', 400
    if not ret: # ret is empty
        return '', 200
    # reply back using hxdt
    ret_datagram = b''.join([struct.pack('>I', len(ret)), ret])
    pad_len = (8 - len(ret_datagram) % 8) % 8
    padded_ret_datagram = b''.join([ret, b'\0\0\0\0\0\0\0\0'[:pad_len]])
    ret_iv = struct.pack('>II', random.randint(0, 2**4-1), 0)
    ret_cryptogram = xtea.ctr(config.ENCRYPT_KEY, ret_iv, padded_ret_datagram)
    ret_mac = xtea.cbc_mac(config.AUTH_KEY, config.AUTH_IV, ret_cryptogram)
    ret_header = struct.pack(hxdt_fmt, 0, len(ret_cryptogram), ret_iv, ret_mac)
    return b''.join([ret_header, ret_cryptogram]), 200

def run(name, args):
    """Runs the desired rpc function"""
    try:
        return _RPC_FUNCTIONS[name](args)
    except KeyError:
        raise NotImplementedError

def _discover_1(args):
    if not(len(args) % 8 == 0 and len(args) >= 8):
        raise AssertionError
    (sniffer_mac_bytes, sniffer_time) = struct.unpack('>6sH', args[:8])
    sniffer_mac_hex = binascii.hexlify(sniffer_mac_bytes).decode('ascii')
    sniffer_mac = netaddr.EUI(sniffer_mac_hex)
    current_time = datetime.datetime.utcnow()
    print('Sniffer MAC: {}'.format(sniffer_mac))
    print('Sniff Duration: {}'.format(sniffer_time))
    devices_data = args[8:]
    probe_requests_raw = []
    for i in range(len(devices_data) // 8):
        device_data = devices_data[i*8:(i+1)*8]
        (device_mac_bytes, device_rssi, device_channel) = struct.unpack('>6sbb', device_data)
        device_mac_hex = binascii.hexlify(device_mac_bytes).decode('ascii')
        device_mac = netaddr.EUI(device_mac_hex)
        device_reg = None
        device_org = None
        device_discovery_time = current_time \
            - datetime.timedelta(seconds=random.randint(0, sniffer_time))
        # randomized to make data look better when processing.
        try:
            device_reg = device_mac.oui.registration()
            device_org = device_reg.org
        except netaddr.core.NotRegisteredError:
            pass
        if device_reg is None:
            pass
        else:
            print('Device Manufacturer: {}'.format(device_org))
            probe_requests_raw.append({
                'sniffer_mac': sniffer_mac_hex,
                'device_mac': device_mac_hex,
                'rssi': device_rssi,
                'channel': device_channel,
                'time': device_discovery_time
            })
    if probe_requests_raw:
        session = db.session_factory()
        sniffer = session.query(model.Sniffer).filter_by(mac=sniffer_mac_hex).first()
        if sniffer:
            sniffer.updated = current_time
        probe_requests = \
            list(map(lambda x: model.ProbeRequest(sniffer=sniffer, **x), probe_requests_raw))
        session.add_all(probe_requests)
        session.commit()
        session.close()
    return b''

_RPC_FUNCTIONS['disc1'] = _discover_1
