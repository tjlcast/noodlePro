#   coding: utf-8
#   multi process

import socket
import struct
import json
import os


def ping(conn, params):
    send_result(conn, "pong", params)


def send_result(conn, out, result):
    response = json.dumps({"out": out, "result": result})
    length_prefix = struct.pack("I", response)
    conn.send(length_prefix)
    conn.sendall(response)


def handle_conn(conn, addr, handlers):
    print(addr, "comes")
    while True:
        length_prefix = conn.recv(4)    # 接收4个字节
        if not length_prefix:
            print(addr, "bye")
            conn.close()
            break
        length, = struct.unpack("I", length_prefix)
        body = conn.recv(length)
        request = json.load(body)

        in_ = request["in"]
        params = request["params"]
        print(in_, params)
        handler = handlers[in_]
        handler(conn, params)


def loop(sock, handlers):
    while True:
        conn, addr = sock.accept()
        pid = os.fork() # fork 调用后，父子进程都将会从这里开始，区别是返回的pid不同
        if pid < 0: # fork error
            return
        if pid > 0: # 此时的pid表示父进程的pid
            conn.close()# 关闭父进程的客户端套接字引用
            continue
        if pid == 0:    # 关闭子进程的服务套接字引用
            sock.close()
            handle_conn(conn, addr, handlers)
            break       # 子进程处理结束后退出循环.


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("localhost", 8080))
    sock.listen(1)
    handlers = {
        "ping": ping
    }
    loop(sock, handlers)
