from packet import Packet
import socket


def send_packet(conn, p: Packet, router_addr, router_port):
    print(f"Sending packet #{p.seq_num} and type {p.packet_type}")
    conn.sendto(p.to_bytes(), (router_addr, router_port))


class UDP:
    pass
