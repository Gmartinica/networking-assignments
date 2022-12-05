import argparse
import socket
import time
from PacketType import PacketType
import PacketsConverter
import os
from packet import Packet
import HttpResponse
import HttpRequest
import math
import udp


def three_way_handshake_server(conn):
    start = time.time()
    print("In three way")
    while True:
        if time.time() - start > 15:
            return False
        data, sender = conn.recvfrom(1024)  # waiting for SYN
        router_addr, router_port = sender
        p = Packet.from_bytes(data)
        if p.packet_type == 3:  # received syn  so we will send synAck
            seq_start = p.seq_num
            syn_ack = Packet(packet_type=PacketType.SYN_ACK.value,
                             seq_num=p.seq_num + 1,
                             peer_ip_addr=p.peer_ip_addr,
                             peer_port=p.peer_port,
                             payload="")
            udp.send_packet(conn, syn_ack, router_addr, router_port)

            # Now wait for ack
            data, sender = conn.recvfrom(1024)  # waiting for ACK
            p = Packet.from_bytes(data)
            if p.packet_type == PacketType.ACK.value and p.seq_num == seq_start + 2:  # received ACK so we are good to go
                return True


def run_server(port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        conn.bind(('', port))
        conn.settimeout(20)
        print('Echo server is listening at', port)
        if three_way_handshake_server(conn):
            while True:
                data, sender = conn.recvfrom(1024)
                handle_client(conn, data, sender)
        else:
            print("Something went wrong with 3 way handshake")
            exit(1)

    finally:
        conn.close()


def sentAll(li):
    rslt = True
    for i in range(0, len(li)):
        if li[i].isRecived == False:
            rslt = False
    return rslt


def handle_client(conn, data, sender):
    try:
        data = [Packet.from_bytes(data)]
        msg = PacketsConverter.create_msg(data)
        print(msg)

        res = HttpResponse.create_response(msg, args.PATH)
        print(res)

        num_of_packets = math.ceil(len(res) / PacketsConverter.PAYLOAD_SIZE)
        res_packets = list()
        PacketsConverter.create_packets(res, num_of_packets, res_packets, data[0].peer_ip_addr, data[0].peer_port)
        print(res_packets)

        # track if packets ack is is received or not
        packets_tracker = list()
        for i in range(0, len(res_packets)):
            packets_tracker.append(False)

        while not (sentAll(protocol_list)):
            for p in res_packets:
                conn.sendto(p.to_bytes(), sender)
                '''
                t1 = Timer(3, resend, ['Timeout:'])
                t1.start()  # run is called
                
                t2 = Timer(3, resend, ['Timeout:'])
                t2.start()  # run is called
                
                if we recive ack  
                t1.cancel()
                '''

            # # TODO msg = creat_msg(type(get/post), )
            # num_of_packets = math.ceil(len(msg) / PAYLOAD_SIZE)
            # packets = list()
            # PacketsConverter.create_packets(msg, num_of_packets, packets, p.peer_ip_addr, p.peer_port)
            # 1         1

            # How to send a reply.
            # The peer address of the packet p is the address of the client already.
            # We will send the same payload of p. Thus we can re-use either `data` or `p`.
            # conn.sendto(p.to_bytes(), sender)

    except Exception as e:
        print("Error: ", e)


# Usage
# python httpfs.py -p port -d path -v verbose
parser = argparse.ArgumentParser()
parser.add_argument("--PORT", "-p", help=HttpResponse.port_help, type=int, default=8080)
parser.add_argument("--PATH", "-d", help=HttpResponse.directory_help, type=HttpResponse.dir_path, default=os.getcwd())
parser.add_argument("-v", help="Prints debugging messages", action="store_true", default=False)
args = parser.parse_args()
# test_msg = 'POST /lol HTTP/1.0\nHost: 127.0.0.1\nContent-Length:6\n\nLolazo\n'
# res = HttpResponse.create_response(test_msg, args.PATH)
# HttpRequest.read_response(res, True, "l.txt")
run_server(args.PORT)
