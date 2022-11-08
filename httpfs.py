import socket

import threading
import argparse
import time
import os


def run_server(host, port, path):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((host, port))
        listener.listen(5)
        print("**********************************")
        print('Time server is listening at', port)
        print('Path is: ', path)
        print("**********************************")

        while True:
            conn, addr = listener.accept()
            threading.Thread(target=handle_client, args=(conn, addr, path)).start()
    finally:
        listener.close()


def status_phrase(code):

    if code == 200:
        return 'OK'
    if code == 201:
        return 'Created'
    if code == 202:
        return 'Accepted'
    if code == 204:
        return 'No Content'
    if code == 301:
        return 'Moved Permanently'
    if code == 302:
        return 'Moved Temporarily'
    if code == 304:
        return 'Not Modified'
    if code == 400:
        return 'Bad Request'
    if code == 403:
        return 'Forbidden'
    if code == 404:
        return 'Not Found'
    if code == 505:
        return 'HTTP Version Not Supported'


def handle_client(conn, addr, path):
    print('New client from', addr)
    file = conn.recv(1024);
    data = file.decode("utf-8")
    print("+++++")
    print(data)
    print("+++++")
    method = data.split(' ')[0]

    #http_header = data.split('\r\n\r\n')
    #lines = http_header.split('\r\n')

    try:
        if method.casefold() == "get".casefold():
            status =200
            bar = data.split(' ')[1]
            wanted_file = path + bar + ".txt"
            f = open(wanted_file, "r")
            content = f.read()
            response =f"HTTP/1.1 {status} {status_phrase(status)}\r\nConnection: close\r\nContent-Length: {len(content)}\r\n{content}\r\n\r\n"
        print("+++++")
        print(response)
        print("+++++")
        if method.casefold() == "post".casefold():
            print("post")
            print('Path is: ', path)
        now = 1

        # Must send uint32 in big-endian
        #conn.sendall(now.to_bytes(4, byteorder='big'))
        response = response.encode("utf-8")
        conn.sendall(response)
    finally:
        conn.close()


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


port_help = """
Specifies the port number that the server will listen and serve at.
Default is 8080.
"""


directory_help = """
Specifies the directory that the server will use to read/write requested
files. 
Default is the current directory when launching the application.
"""

parser = argparse.ArgumentParser()
parser.add_argument("--PORT", "-p", help=port_help, type=int, default=8080)
parser.add_argument("--PATH", "-d", help=directory_help, type=dir_path, default=os.getcwd())
args = parser.parse_args()
run_server('', args.PORT, args.PATH)
