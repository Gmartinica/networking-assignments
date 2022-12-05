import argparse
import ipaddress
import socket
from urllib.parse import urlparse
import HttpRequest
from packet import Packet
from PacketType import PacketType
import math
from udp import UDP, send_packet
import PacketsConverter
from threading import Timer
from ReceiverWindow import ReceiverWindow

PAYLOAD_SIZE = 1013


def parse_commands(args):
    """Given a dict of command line arguments, return a dict with the HTTP req elements"""
    request = {}
    parsed_url = urlparse(args.URL)
    print(parsed_url)
    if parsed_url.scheme == 'http':
        request['host'] = parsed_url.hostname
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


# Share only one conn among functions
def three_way_handshake(router_addr, router_port, server_addr, server_port):
    peer_ip = ipaddress.ip_address(socket.gethostbyname(server_addr))
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    timeout = 5
    syn = Packet(packet_type=PacketType.SYN.value,
                 seq_num=1,
                 peer_ip_addr=peer_ip,
                 peer_port=server_port,
                 payload="")

    # syn_thread = Timer(send_packet, (conn, syn, router_addr, router_port))

    send_packet(conn, syn, router_addr, router_port)
    # Try to receive a response within timeout
    conn.settimeout(timeout)
    print('Waiting for a response')
    timeout_count = 0
    while True:
        try:
            response, sender = conn.recvfrom(1024)
            p = Packet.from_bytes(response)
            print(p)
            if p.packet_type == PacketType.SYN_ACK.value:  # Received SYN ACK
                ack = Packet(packet_type=PacketType.ACK.value,
                             seq_num=3,
                             peer_ip_addr=peer_ip,
                             peer_port=server_port,
                             payload="")
                send_packet(conn, ack, router_addr, router_port)
                return True
        except socket.timeout:
            timeout_count += 1
            if timeout_count > 6:
                return False
            send_packet(conn, syn, router_addr, router_port)
            continue


def run_client(router_addr, router_port, server_addr, server_port, request):
    peer_ip = ipaddress.ip_address(socket.gethostbyname(server_addr))
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    timeout = 30
    try:
        p = Packet(packet_type=0,
                   seq_num=1,
                   peer_ip_addr=peer_ip,
                   peer_port=server_port,
                   payload=request)
        conn.sendto(p.to_bytes(), (router_addr, router_port))
        print('Send "{}" to router'.format(request))

        # Try to receive a response within timeout
        conn.settimeout(timeout)
        print('Waiting for a response')
        receiver = ReceiverWindow()
        while not receiver.ready:
            response, sender = conn.recvfrom(1024)
            p = Packet.from_bytes(response)
            print(" packet :")
            print(p)

            if p.packet_type == PacketType.DATA.value:
                receiver.insert(p)
                ack = Packet(packet_type=PacketType.ACK.value,
                             seq_num=p.seq_num,
                             peer_ip_addr=p.peer_ip_addr,
                             peer_port=p.peer_port,
                             payload="")
                conn.sendto(ack.to_bytes(), sender)
            elif p.packet_type == PacketType.FIN.value:
                print("FIN PACKET")                
                print(receiver.get_packets())
                
                if receiver.all_packets_received(p):
                    receiver.insert(p)
                    fin_ack = Packet(packet_type=PacketType.ACK.value,
                                     seq_num=p.seq_num,
                                     peer_ip_addr=p.peer_ip_addr,
                                     peer_port=p.peer_port,
                                     payload="")
                    conn.sendto(fin_ack.to_bytes(), sender)
            '''
                # sending back the ack
                p_ack = p
                p_ack.packet_type = 1
                p_ack.peer_port = server_port
                p_ack.peer_ip_addr = peer_ip
                conn.sendto(p_ack.to_bytes(), (router_addr, router_port))
                '''
        print("RECEIVED EVERYTHING")
        #print(receiver.get_packets())
        #     # append to our receiveer list
        #     packets_received.append(p)
        #     if p.packet_type == 5:
        #         break
        # print(packets_received)
        # print(PacketsConverter.create_msg(packets_received))
        # # print('Router: ', sender)
        # # print('Packet: ', p)
        # # print('Payload: ' + p.payload.decode("utf-8"))
        msg = PacketsConverter.create_msg(receiver.get_packets())
        print(msg)

    except socket.timeout:
        print('No response after {}s'.format(timeout))
    finally:
        conn.close()


# Help and usage
# python httpc.py --help

parser = argparse.ArgumentParser(description=HttpRequest.help_msg, add_help=False)
parser.add_argument("request", help=HttpRequest.request_help_msg, choices=['post', 'get'])
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
args = parser.parse_args()
request = parse_commands(args)
if args.request.casefold() == "get".casefold():
    if args.f or args.d:
        print("-d and -f arguments are only for Post request")
        exit(1)
else:
    if args.f == '' and args.d == '':
        print("Pass an argument for Post request, Have a look at -v and -f arguments")
        exit(1)
    if args.f != '' and args.d != '':
        print("both -f and -d if arguments can not exist together")
        exit(1)
http_request = HttpRequest.create_request(request)
print(http_request)
# if three_way_handshake(args.routerhost, args.routerport, args.serverhost, args.serverport):
#     print("Got through handshake")
# else:
#     exit(4)
run_client(args.routerhost, args.routerport, args.serverhost, args.serverport, http_request)
