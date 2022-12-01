import socket
from datetime import datetime
import threading
import argparse
import os
from packet import Packet

def run_server(host, port, path, debugging=False):
    listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        #listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((host, port))
        print("**********************************")
        print('Server is listening at', port)
        print('Path is: ', path)
        print("**********************************")
        if debugging:
            print("Debugging is active")
        while True:
            data, sender = listener.recvfrom(1024)
            handle_client(listener, sender, data, path)
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
    global args
    path = path + ".txt"
    status = 201  # Default is file created
    if os.path.isfile(path):
        status = 200
    try:
        if path == args.PATH:
            raise FileNotFoundError
        file = open(path, 'w')
        file.write(body)
        file.close()
    except FileNotFoundError:
        status = 404
        print("File was not found")
    except IOError:
        status = 500
        print("Unable to create/write file.")
    return status


def is_valid_path(basedir, path, request_type):
    global args
    requested_path = os.path.realpath(basedir + path)
    if args.v:
        print("REQUEST PATH: " + basedir + path)
        print("Real path: " + requested_path)
    print("Is path file====>>> " + str(os.path.isfile(requested_path)))
    print("Is dir file====>>> " + str(os.path.isdir(requested_path)))
    valid = True
    if request_type == "get":
        if not (os.path.isfile(requested_path + ".txt") or os.path.isdir(requested_path)):
            valid = False
    return basedir == os.path.commonpath((basedir, requested_path)) and valid


def handle_client(conn, sender, data, path):
    global args
    print('New client from', sender)
    p = Packet.from_bytes(data)
    data = p.payload.decode()
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

    try:
        if args.v:
            print("____________>>>>>>>>>>>>>>" + str(is_valid_path(path, request_path, method)))
        if is_valid_path(path, request_path, method):
            print("{{{{{{{{{}}}}}}}}}}}}}}}}}}}}}")

            if method.casefold() == "get".casefold():
                status = 200
                bar = data.split(' ')[1]

                if os.path.isfile(path + bar + ".txt"):
                    wanted_file = path + bar + ".txt"
                    f = open(wanted_file, "r")
                    content = f.read()
                    response = f"HTTP/1.0 {status} {status_phrase(status)}\r\nConnection: close\r\nContent-Length: {len(content)}\r\n\n{content}\r\n\r\n"
                elif os.path.isdir(path + bar):
                    content = os.listdir(path+bar)
                    if args.v:
                        print("Contents of directory are:")
                        print(content)
                    response = f"HTTP/1.0 {status} {status_phrase(status)}\r\nConnection: close\r\nContent-Length: {len(str(content))}\r\n\n{content}\r\n\r\n"
                else:
                    status = 400
                    response = f"HTTP/1.0 {status} {status_phrase(status)}\r\nDate: {date}\r\nConnection: close\r\n\r\n"

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
        p.payload = response
        if args.v:
            print(f"+++++ Response sent to {sender} +++++")
            print(response)
            print("+++++")
        conn.sendto(p.to_bytes(), sender)
    except Exception as e:
        print("Error: ", e)


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
