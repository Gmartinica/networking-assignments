import argparse
import socket
import PacketsConverter
import os
from packet import Packet
import HttpResponse
import HttpRequest
def run_server(port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        conn.bind(('', port))
        print('Echo server is listening at', port)
        while True:
            data, sender = conn.recvfrom(1024)
            handle_client(conn, data, sender)

    finally:
        conn.close()


def handle_client(conn, data, sender):
    try:
        p = Packet.from_bytes(data)
        print("Router: ", sender)
        print("Packet: ", p)
        print("Payload: ", p.payload.decode("utf-8"))
        # TODO msg = creat_msg(type(get/post), )
        num_of_packets = math.ceil(len(msg) / PAYLOAD_SIZE)
        packets = list()
        PacketsConverter.create_packets(msg, num_of_packets, packets, p.peer_ip_addr, p.peer_port)
        # 1         1

        # How to send a reply.
        # The peer address of the packet p is the address of the client already.
        # We will send the same payload of p. Thus we can re-use either `data` or `p`.
        conn.sendto(p.to_bytes(), sender)

    except Exception as e:
        print("Error: ", e)


# Usage
# python httpfs.py -p port -d path -v verbose
parser = argparse.ArgumentParser()
parser.add_argument("--PORT", "-p", help=HttpResponse.port_help, type=int, default=8080)
parser.add_argument("--PATH", "-d", help=HttpResponse.directory_help, type=HttpResponse.dir_path, default=os.getcwd())
parser.add_argument("-v", help="Prints debugging messages", action="store_true", default=False)
args = parser.parse_args()
test_msg = "GET / HTTP/1.0\nHost: 127.0.0.1\n\n"
res = HttpResponse.create_response(test_msg, args.PATH)
HttpRequest.read_response(res.decode("utf-8"))
run_server(args.PORT)
