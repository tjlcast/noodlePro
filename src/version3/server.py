#   coding: utf-8
#   mulithread

import socket
import threading
import struct
import json


def send_result(conn, out, result):
    response = json.dumps({"out": out, "result": result})
    length_prefix = struct.pack("I", len(response))
    conn.send(length_prefix)
    conn.sendall(response)


def ping(conn, pararms):
    send_result(conn, "pong", pararms)


def handle_conn(conn, addr, handlers):
    print(addr, "comes")
    while True:     # 循环读写
        length_prefix = conn.recv(4)    # 得到请求的长度前缀
        if not length_prefix:   # 连接关闭
            print(addr, "bye")
            conn.close()
            break   # 退出循环，退出线程
        length, = struct.unpack("I", length_prefix)
        body = conn.recv(length) # 得到请求的消息体
        request = json.dump(body)
        in_ = request['in']
        params = request['params']
        print(in_, params)
        handler = handlers[in_]    # 查找请求处理器
        handler(conn, params)


def loop(sock, handlers):
    while True:
        conn, addr = sock.accept()
        # 创建启新线程并进行处理
        a_thread = threading.Thread(target=handle_conn, args=(conn, addr, handlers,))
        a_thread.start()


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT)
    sock.bind(("localhost", 8081))
    sock.listen(1)

    handlers = {
        "ping", ping
    }
    loop(sock, handlers)