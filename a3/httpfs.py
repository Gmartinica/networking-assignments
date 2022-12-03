import argparse
import socket
import math
import sys
from packet import Packet

PAYLOAD_SIZE = 1013

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


def create_packets(msg, num_of_packets, packets):
    for i in range(0, num_of_packets):
        if i == num_of_packets - 1:
            # last chunck of the packets
            packets.append(msg[i * PAYLOAD_SIZE:])
        else:
            packets.append(msg[i * PAYLOAD_SIZE:(i + 1) * PAYLOAD_SIZE])

            
def handle_client(conn, data, sender):
    try:
        p = Packet.from_bytes(data)
        print("Router: ", sender)
        print("Packet: ", p)
        print("Payload: ", p.payload.decode("utf-8"))

        # TODO msg = creat_msg()
        num_of_packets = math.ceil(len(msg) / PAYLOAD_SIZE)
        packets = list()
        create_packets(msg, num_of_packets, packets)

        # How to send a reply.
        # The peer address of the packet p is the address of the client already.
        # We will send the same payload of p. Thus we can re-use either `data` or `p`.
        conn.sendto(p.to_bytes(), sender)

    except Exception as e:
        print("Error: ", e)







# Usage python httpfs.py [--port port-number]
parser = argparse.ArgumentParser()
parser.add_argument("--port", help="echo server port", type=int, default=8007)
args = parser.parse_args()
run_server(args.port)
