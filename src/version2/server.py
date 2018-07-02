# coding: utf-8
# server

import socket
import json
import struct


def send_result(conn, out, result):
    response = json.dumps({"out": out, "result": result})  # 响应消息体
    length_prefix = struct.pack("I", len(response))  # 响应长度前缀
    conn.send(length_prefix)
    conn.sendall(response)  # sendall = send + flush...


def ping(conn, params):
    send_result(conn, "pong", params)


def handle_conn(conn, addr, handlers):
    print(addr, "comes")
    while True: # 循环读写
        length_prefix = conn.recv(4)    # 请求的长度前缀
        if not length_prefix:           # 连接关闭
            print(addr, "Bye")
            conn.close()
            break   # 退出当前连接的循环
        length, = struct.unpack(length_prefix)
        request_body_str = conn.recv(length)
        request = json.loads(request_body_str)
        in_ = request['in']
        params = request['params']
        print(in_, params)
        handler = handlers[in_]
        handler(conn, params)


def loop(sock, handlers):
    while True:
        conn, addr = sock.accept()
        handle_conn(conn, addr, handlers)


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("localhost", 8080)) # 绑定端口
    sock.listen(1)  # 监听客户端连接

    handlers = {    # 注册请求处理器
        "ping": ping
    }

    loop(sock, handlers)

