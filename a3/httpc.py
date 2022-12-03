import argparse
import ipaddress
import socket
from urllib.parse import urlparse

from packet import Packet


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
            exit(1)

    return request

def run_client(router_addr, router_port, server_addr, server_port):
    peer_ip = ipaddress.ip_address(socket.gethostbyname(server_addr))
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    timeout = 5
    try:
        msg = "Hello World"
        p = Packet(packet_type=0,
                   seq_num=1,
                   peer_ip_addr=peer_ip,
                   peer_port=server_port,
                   payload=msg.encode("utf-8"))
        conn.sendto(p.to_bytes(), (router_addr, router_port))
        print('Send "{}" to router'.format(msg))

        # Try to receive a response within timeout
        conn.settimeout(timeout)
        print('Waiting for a response')
        response, sender = conn.recvfrom(1024)
        p = Packet.from_bytes(response)
        print('Router: ', sender)
        print('Packet: ', p)
        print('Payload: ' + p.payload.decode("utf-8"))

    except socket.timeout:
        print('No response after {}s'.format(timeout))
    finally:
        conn.close()


# Usage:
# python echoclient.py --routerhost localhost --routerport 3000 --serverhost localhost --serverport 8007

parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description=help_msg, add_help=False)
parser.add_argument("request", help=request_help_msg, choices=['post', 'get'])
parser.add_argument("URL", help="URL for request")
parser.add_argument('-H', '--help', action='help', help="Show help message")
parser.add_argument("-v", help="Return verbose response", action="store_true", default=False)
parser.add_argument("-h", help="Headers for request", nargs='*', default='')
parser.add_argument("-d", "--d", help="inline data for post request", nargs='*', default='')
parser.add_argument("-f", help="file for post request", nargs='*', default='')
parser.add_argument("-o", help="print output to specific file", nargs='*', default='')
parser.add_argument("--routerhost", help="router host", default="127.0.0.1")
parser.add_argument("--routerport", help="router port", type=int, default=3000)
parser.add_argument("--serverhost", help="server host", default="127.0.0.1")
parser.add_argument("--serverport", help="server port", type=int, default=8080)
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
args = parser.parse_args()

run_client(args.routerhost, args.routerport, args.serverhost, args.serverport)
