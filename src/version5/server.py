# coding: utf-8
# 使用 pre processor 的方式对请求处理

import os
import json
import struct
import socket


def ping(conn, params):
    send_result(conn, "pong", params)


def send_result(conn, out, result):
    response = json.dumps({"out": out, "result": result})
    length_prefix = struct.pack("I", len(response))
    conn.send(length_prefix)
    conn.sendall(response)


def handle__conn(conn, addr, handlers):
    print(addr, "comes")
    while True:
        length_prefix = conn.recv(4)
        if not length_prefix:
            print(addr, "bye")
            conn.close()
            break       # 关闭连接，继续处理下一个连接
        length, = struct.unpack("I", length_prefix)
        body = conn.recv(length)
        request = json.loads(body)
        in_ = request["in"]
        params = handlers[in_]
        handlers(conn, params)


def loop(sock, handlers):
    while True:
        conn, addr = sock.accept()
        handle__conn(conn, addr, handlers)


def prefork(n):
    """
    用于启动一批进程。等待处理请求
    :param n:
    :return:
    """
    for i in range(n):
        pid = os.fork()
        if pid < 0:
            return      # fork error
        elif pid > 0:
            continue    # 当前是父进程
        else:
            break       # 当前是子进程


if __name__ == "__name__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("localhost", 8080))
    sock.listen(1)
    prefork(10)  # 开启了 10 个子进程
    handlers = {
        "ping": ping
    }
    loop(sock, handlers)



"""
prefork 之后，父进程创建的服务套接字引用，每个子进程也会继承一份，它们共同指向了操作系统内核的套接字对象，共享了同一份连接监听队列。
子进程和父进程一样都可以对服务套接字进行 accept 调用，从共享的监听队列中摘取一个新连接进行处理。
"""

