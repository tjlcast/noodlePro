# coding: utf-8
# client

import json
import struct
import socket
import time


def rpc(sock, in_, params):
    request_body_str = json.dump({"in": in_, "params": params}) # 请求消息体
    length_prefix = struct.pack("I", len(request_body_str))  # 请求体长度前缀
    sock.send(length_prefix)
    sock.sendall(request_body_str) # sendall = send + flush
    length_prefix = sock.recv(4)  # 响应的长度前缀
    length, = struct.unpack("I", length_prefix)
    response_body_str = sock.recv(length)   # 响应消息体
    response = json.load(response_body_str)
    return response['out'], response['result']  # 返回消息的类型和结果


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 8080))
    for i in range(10): # 连续发送10个 rpc 连接
        out, result = rpc(s, "ping", "ireader %d" % i)
        print(out, result)
        time.sleep(1)
    s.close()
