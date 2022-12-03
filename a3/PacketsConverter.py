import math
import sys
from packet import Packet

PAYLOAD_SIZE = 1013


def create_packets(msg, num_of_packets, packets, ip_addr, port):
    for i in range(0, num_of_packets):
        if i == num_of_packets - 1:
            p = Packet(packet_type=0,
                       seq_num=i+1,
                       peer_ip_addr=ip_addr,
                       peer_port=port,
                       payload=msg[i * PAYLOAD_SIZE:].encode("utf-8"))
            # last chunck of the packets
            packets.append(p)
        else:
            p = Packet(packet_type=0,
                       seq_num=i+1,
                       peer_ip_addr=p.peer_ip_addr,
                       peer_port=p.peer_port,
                       payload=msg[i * PAYLOAD_SIZE:(i + 1) * PAYLOAD_SIZE].encode("utf-8"))
            packets.append(p)


def create_msg(packets):
    msg = ""
    for i in range(0, len(packets)):
        msg = msg + packets[i].payload.decode("utf-8")
    return msg
