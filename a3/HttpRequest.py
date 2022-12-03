import socket
import argparse
import sys
from urllib.parse import urlparse
import re
import os
from datetime import datetime
from packet import Packet
import ipaddress

# server address: http://127.0.0.1:8080/
router_addr = '127.0.0.1'
router_port = 3000
def parse_commands(args):
    """Given a dict of command line arguments, return a dict with the HTTP req elements"""
    request = {}
    parsed_url = urlparse(args.URL)
    print(parsed_url)
    if parsed_url.scheme == 'http':
        request['host'] = ipaddress.ip_address(parsed_url.hostname)
    else:
        request['host'] = parsed_url.scheme
    # Default web port is 80
    request['port'] = 80 if parsed_url.port is None else parsed_url.port
    request['path'] = parsed_url.path
    print(request['path'])
    if parsed_url.query != '':
        request['path'] += '?' + parsed_url.query
    request['type'] = args.request.upper()
    # If headers in arguments, join them in string dividing by line breaks
    request['headers'] = '\n' + '\n'.join(args.h) if args.h != '' else ''
    request['verbose'] = args.v
    request['outFile'] = '\n'.join(args.o) if args.o != '' else ''
    if args.d:
        request['data'] = '\n'.join(args.d) if args.d != '' else ''
    elif args.f:
        filepath = '\n' + '\n'.join(args.f)
        filepath2 = filepath.split('\n')[1]
        try:
            file = open(filepath2, "r")
            request['data'] = file.read()
            file.close()
        except IOError:
            print("Could not read from file")

    return request


def send_request(req: dict):
    """Sends either GET or POST req to the specified server"""
    print(req)
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # If get request
        if req['type'].casefold() == "get".casefold():
            req_msg = f"{req['type']} {req['path']} HTTP/1.0\nHost: {req['host']}{req['headers']}\n\n"
        # If post request, send content length and data
        elif req['type'].casefold() == "post".casefold():
            req_msg = f"{req['type']} {req['path']} HTTP/1.0\nHost: {req['host']}{req['headers']}\nContent-Length:{(len(str(req['data'])))}\n\n{req['data']}\n"
        else:
            print("""Can not recognize request type keyword
            Please use either get or send""")

        req_msg = req_msg.encode("utf-8")
        p = Packet(0, 1, request['host'], request['port'], req_msg)
        conn.sendto(p.to_bytes(), (router_addr, router_port))
        print(p)
        print('Send "{}" to router'.format(req_msg))
        response = conn.recv(1024)  # Receive response, read up to 1024 bytes
        p = Packet.from_bytes(response)
        print('Packet: ', p)
        print('Payload: ' + p.payload.decode("utf-8"))

        if not request['verbose']:
            response = p.payload.decode().split('\r\n\r\n')[1]  # Get just response body
        if not request['outFile']:
            sys.stdout.write(p.payload.decode())
        # Write output to file
        else:
            outFilename, outFile_extension = os.path.splitext(request['outFile'])

            try:
                outFile = open(request['outFile'], "a")  # append mode
                outFile.write("-----------------------------\n")
                outFile.write(response)
                outFile.write("\n______________________________\n")
                outFile.close()

            except IOError:
                now = datetime.now()

                # dd-mm-YY_H.M.S
                outFilename = now.strftime("%d-%m-%Y_%H.%M.%S.txt")
                try:
                    outFile = open(outFilename, "a")  # append mode
                    outFile.write("-----------------------------\n")
                    outFile.write(response)
                    outFile.write("\n______________________________\n")
                    outFile.close()
                    print(
                        "Unable to write to specified file due to problem in name or extenstion , wrote the out put to  " + outFilename)
                except IOError:
                    print("Could not creat the output file")

    finally:
        conn.close()


help_msg = """
httpc is a curl-like application but supports HTTP protocol only. 
Usage:
    httpc command [arguments]
The commands are:
    get executes a HTTP GET req and prints the response. 
    post executes a HTTP POST req and prints the response. 
    help prints this screen.
Use "httpc --help [command]" for more information about a command.
"""

request_help_msg = """
For GET requests: 
usage: httpc get [-v] [-h key:value] URL
Get executes a HTTP GET request for a given URL.
-v Prints the detail of the response such as protocol, status, and headers. 
-h key:value Associates headers to HTTP Request with the format 'key:value'.

For POST requests:
usage: httpc post [-v] [-h key:value] [-d inline-data] [-f file] URL
Post executes a HTTP POST request for a given URL with inline data or from file.
-v Prints the detail of the response such as protocol, status, and headers. 
-h key:value Associates headers to HTTP Request with the format 'key:value'. 
-d string Associates an inline data to the body HTTP POST request.
-f file Associates the content of a file to the body HTTP POST request.
Either [-d] or [-f] can be used but not both.
"""

parser = argparse.ArgumentParser(description=help_msg, add_help=False)
parser.add_argument("request", help=request_help_msg, choices=['post', 'get'])
parser.add_argument("URL", help="URL for request")
parser.add_argument('-H', '--help', action='help', help="Show help message")
parser.add_argument("-v", help="Return verbose response", action="store_true", default=False)
parser.add_argument("-h", help="Headers for request", nargs='*', default='')
parser.add_argument("-d", "--d", help="inline data for post request", nargs='*', default='')
parser.add_argument("-f", help="file for post request", nargs='*', default='')
parser.add_argument("-o", help="print output to specific file", nargs='*', default='')
arguments = parser.parse_args()

if arguments.request.casefold() == "get".casefold():

    if arguments.f or arguments.d:
        print("-d and -f arguments are only for Post request")
        exit(1)
else:
    if arguments.f == '' and arguments.d == '':
        print("Pass and argument for Post request, Have a look at -v and -f arguments")
    if arguments.f != '' and arguments.d != '':
        print("both -f and -d if arguments can not exist together")
        exit(1)

request = parse_commands(arguments)
send_request(request)
