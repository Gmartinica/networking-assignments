import socket
from datetime import datetime
import threading
import argparse
import time
from time import gmtime, strftime
import os


def run_server(host, port, path, debugging = False):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((host, port))
        listener.listen(5)
        print("**********************************")
        print('Server is listening at', port)
        print('Path is: ', path)
        print("**********************************")
        if debugging:
            print("Debugging is active")
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
    if code == 500:
        return 'Internal Server Error'
    if code == 505:
        return 'HTTP Version Not Supported'


def write_file(path, body):
    status = 201  # Default is file created
    file = None
    if os.path.isfile(path):
        status = 200
    try:
        file = open(path, 'w')
        file.write(body)
        file.close()
    except IOError:
        status = 500
        print("Unable to create/write file.")
    return status


def is_valid_path(basedir, path):
    global args
    requested_path = os.path.realpath(basedir + path)
    if args.v:
        print("REQUEST PATH: " + basedir + path)
        print("Real path: " + requested_path)
    return basedir == os.path.commonpath((basedir, requested_path)) and os.path.isdir(requested_path)


def handle_client(conn, addr, path):
    global args
    print('New client from', addr)
    file = conn.recv(1024)
    data = file.decode("utf-8")
    first_line = data.split(' ')[:2]
    method = first_line[0]
    request_path = first_line[1]
    now = datetime.utcnow()
    date = f"{now.strftime('%a %d %b %Y %H:%M:%S')} GMT"
    if args.v:
        print(f"Date is {date}")
        print("+++++ Request is +++++")
        print(data)
        print("+++++")

    #http_header = data.split('\r\n\r\n')
    #lines = http_header.split('\r\n')
    #TODO: If get request file is empty, return 204 and content length is 0
    #TODO: Add security by avoiding ../../ paths from client
    try:
        if is_valid_path(path, request_path):
            if method.casefold() == "get".casefold():
                status = 200
                bar = data.split(' ')[1]
                wanted_file = path + bar + ".txt"
                f = open(wanted_file, "r")
                content = f.read()
                response = f"HTTP/1.0 {status} {status_phrase(status)}\r\nConnection: close\r\nContent-Length: {len(content)}\r\n{content}\r\n\r\n"
            elif method.casefold() == "post".casefold():
                body = data.split('\n\n')[1]
                path = path + request_path
                status = write_file(path, body)
                response = f"HTTP/1.0 {status} {status_phrase(status)}\r\nDate: {date}\r\nConnection: close\r\n\r\n"
        else:
            status = 403
            if not os.path.isdir(os.path.realpath(path + request_path)):
                status = 400
            response = f"HTTP/1.0 {status} {status_phrase(status)}\r\nDate: {date}\r\nConnection: close\r\n\r\n"
        response = response.encode("utf-8")
        if args.v:
            print(f"+++++ Response sent to {addr} +++++")
            print(response)
            print("+++++")
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
parser.add_argument("-v", help="Prints debugging messages", action="store_true", default=False)
args = parser.parse_args()
run_server('', args.PORT, args.PATH, args.v)
