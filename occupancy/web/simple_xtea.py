"""Very simple XTEA CTR + CBC_MAC implementation"""
import struct
# awesome, no manual memory management

def encipher(k, v):
    (v0, v1) = v
    sum = 0
    delta, mask = 0x9e3779b9, 0xffffffff
    for round in range(32):
        v0 = (v0 + (((v1<<4 ^ v1>>5) + v1) ^ (sum + k[sum & 3]))) & mask
        sum = (sum + delta) & mask
        v1 = (v1 + (((v0<<4 ^ v0>>5) + v0) ^ (sum + k[sum>>11 & 3]))) & mask
    return (v0, v1)

def ctr(key, iv, data):
    (c0, c1) = struct.unpack(">2I", iv)
    l = []
    if len(data) % 8 != 0:
        raise ArithmeticError
    blocks = len(data) // 8
    k = struct.unpack(">4I", key)
    for i in range(blocks):
        (v0, v1) = encipher(k, (c0, c1))
        c1 = (c1 + 1) & 0xffffffff
        block = data[i*8:(i+1)*8]
        (b0, b1) = struct.unpack(">2I", block)
        l.append(struct.pack(">2I", v0 ^ b0, v1 ^ b1))
    return b"".join(l)

def cbc_mac(key, iv, data):
    (v0, v1) = struct.unpack(">2I", iv)
    if len(data) % 8 != 0:
        raise ArithmeticError
    blocks = len(data) // 8
    k = struct.unpack(">4I",key)
    for i in range(blocks):
        block = data[i*8:(i+1)*8]
        (b0, b1) = struct.unpack(">2I", block)
        (v0, v1) = (v0 ^ b0, v1 ^ b1)
        (v0, v1) = encipher(k, (v0, v1))
    return struct.pack(">2I", v0, v1)
