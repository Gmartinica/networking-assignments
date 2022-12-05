import argparse
import socket
import PacketsConverter
import os
from PacketType import PacketType
from packet import Packet
import HttpResponse
import HttpRequest
import math

import time
from threading import Timer, Lock
import udp

ack_tracker = list()
all_processes = []


# Todo not tested yet only the overview
# Probably need to change to sth similar to client and we check 1 by 1
def three_way_handshake_server(conn):
    start = time.time()
    conn.settimeout(15)
    print("In three way")
    p = None
    while True:
        if time.time() - start > 20:
            return False
        data, sender = conn.recvfrom(1024)  # waiting for SYN
        router_addr, router_port = sender
        p = Packet.from_bytes(data)
        print("3wayrecived syn")
        if p.packet_type == PacketType.SYN.value:  # received syn  so we will send synAck
            break
    while True:
        try:
            syn_ack = Packet(packet_type=PacketType.SYN_ACK.value,
                             seq_num=p.seq_num + 1,
                             peer_ip_addr=p.peer_ip_addr,
                             peer_port=p.peer_port,
                             payload="")
            udp.send_packet(conn, syn_ack, router_addr, router_port)

            # Now wait for ack
            data, sender = conn.recvfrom(1024)  # waiting for ACK

            p = Packet.from_bytes(data)
            print("3wayrecived ack " + str(p.packet_type) + '  ' + str(PacketType.ACK.value))
            print(p)
            if p.packet_type == PacketType.ACK.value:  # received ACK so we are good to go // and p.seq_num == seq_start + 2
                result = True
                break
        except conn.timeout:
            pass
    return result


def run_server(port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        conn.bind(('', port))
        print('Echo server is listening at', port)
        if three_way_handshake_server(conn):
            conn.settimeout(30)
            while True:
                data, sender = conn.recvfrom(1024)
                handle_client(conn, data, sender)
        else:
            print("Something went wrong with 3 way handshake")
            exit(1)
    except socket.timeout:
        print("client terminated the connection")
        for process in all_processes:
            process.cancel()
        exit(1)

    finally:
        conn.close()


def ack_all(dict):
    rslt = True
    for key in dict:
        if not (dict[key][0]):
            return False
    return rslt


def resend_packets(conn, packet_in_byte, sender, q):
    global all_processes
    if not (ack_tracker[q][1]):
        print("resending packet" + str(q))
        t2 = Timer(3, resend_packets, [conn, packet_in_byte, sender, q])
        all_processes.append(t2)
        conn.sendto(packet_in_byte, sender)
        t2.start()


def handle_client(conn, data, sender):
    global ack_tracker
    global all_processes
    lock = Lock()
    try:
        data = [Packet.from_bytes(data)]
        msg = PacketsConverter.create_msg(data)
        # print(msg)

        res = HttpResponse.create_response(msg, args.PATH)
        # print(res)

        num_of_packets = math.ceil(len(res) / PacketsConverter.PAYLOAD_SIZE)
        res_packets = list()
        PacketsConverter.create_packets(res, num_of_packets, res_packets, data[0].peer_ip_addr, data[0].peer_port)
        print(res_packets)

        # track if packets ack is is received or not
        seq_num_list = [p.seq_num for p in res_packets]
        lock.acquire()
        ack_tracker = {num: [False, False] for num in seq_num_list}
        lock.release()

        a = 0
        b = 1
        if len(ack_tracker) < 4:
            while not (ack_all(ack_tracker)):
                print(ack_all(ack_tracker))
                print("loop : " + str(a))
                # for p in res_packets:
                # for i in range(0, (len(res_packets)-1)):
                print("b" + str(b))
                if b >= len(res_packets):
                    print("HI***********")
                    responseF, senderF = conn.recvfrom(1024)
                    rec_packF = Packet.from_bytes(responseF)
                    print("(4)GOT HERE ACK " + str(rec_packF.seq_num))
                    print(rec_packF)
                    lock.acquire()
                    ack_tracker[rec_packF.seq_num][1] = True
                    lock.release()
                    continue

                p1 = res_packets[a]

                if ack_tracker[p1.seq_num][1]:  # if we already have ack of the left most packet we slide
                    a = a + 1
                    continue

                if ack_tracker[p1.seq_num][0] == True and ack_tracker[p1.seq_num][
                    1] == False:  # if we already have ack of the left most packet we slide
                    responseF, senderF = conn.recvfrom(1024)
                    rec_packF = Packet.from_bytes(responseF)
                    print("(3)GOT HERE ACK " + str(rec_packF.seq_num))
                    print(rec_packF)
                    lock.acquire()
                    ack_tracker[rec_packF.seq_num][1] = True
                    lock.release()
                    if rec_packF.seq_num == p1.seq_num:
                        a = a + 1
                        continue

                t1 = Timer(3, resend_packets, [conn, p1.to_bytes(), sender, p1.seq_num])
                if not (ack_tracker[p1.seq_num][0]):
                    print("sending packet " + str(p1.seq_num))
                    lock.acquire()
                    ack_tracker[p1.seq_num][0] = True
                    lock.release()
                    conn.sendto(p1.to_bytes(), sender)
                    all_processes.append(t1)
                    t1.start()

                response, sender1 = conn.recvfrom(1024)
                rec_pack = Packet.from_bytes(response)
                print("(2) rec ack " + str(rec_pack.seq_num))
                print(rec_pack)
                lock.acquire()
                ack_tracker[rec_pack.seq_num][1] = True
                lock.release()



        else:
            while not (ack_all(ack_tracker)):
                print(ack_all(ack_tracker))
                print("loop : " + str(a))
                # for p in res_packets:
                # for i in range(0, (len(res_packets)-1)):
                print("b" + str(b))
                if b >= len(res_packets):
                    print("HI***********")
                    responseF, senderF = conn.recvfrom(1024)
                    rec_packF = Packet.from_bytes(responseF)
                    print("(4)GOT HERE ACK " + str(rec_packF.seq_num))
                    print(rec_packF)
                    lock.acquire()
                    ack_tracker[rec_packF.seq_num][1] = True
                    lock.release()
                    continue

                p1 = res_packets[a]
                p2 = res_packets[b]

                if ack_tracker[p1.seq_num][1]:  # if we already have ack of the left most packet we slide
                    a = a + 1
                    b = b + 1
                    continue

                if ack_tracker[p1.seq_num][0] == True and ack_tracker[p1.seq_num][
                    1] == False:  # if we already have ack of the left most packet we slide
                    responseF, senderF = conn.recvfrom(1024)
                    rec_packF = Packet.from_bytes(responseF)
                    print("(3)GOT HERE ACK " + str(rec_packF.seq_num))
                    print(rec_packF)
                    lock.acquire()
                    ack_tracker[rec_packF.seq_num][1] = True
                    lock.release()
                    if rec_packF.seq_num == p1.seq_num:
                        a = a + 1
                        b = b + 1
                        continue

                # send the packets if we already havent sent them

                t1 = Timer(3, resend_packets, [conn, p1.to_bytes(), sender, p1.seq_num])
                if not (ack_tracker[p1.seq_num][0]):
                    print("sending packet " + str(p1.seq_num))
                    lock.acquire()
                    ack_tracker[p1.seq_num][0] = True
                    lock.release()
                    conn.sendto(p1.to_bytes(), sender)
                    all_processes.append(t1)
                    t1.start()

                t2 = Timer(3, resend_packets, [conn, p2.to_bytes(), sender, p2.seq_num])
                if not (ack_tracker[p2.seq_num][0]):
                    print("sending packet " + str(p2.seq_num))
                    lock.acquire()
                    ack_tracker[p2.seq_num][0] = True
                    lock.release()
                    conn.sendto(p2.to_bytes(), sender)
                    all_processes.append(t2)
                    t2.start()

                response, sender1 = conn.recvfrom(1024)
                rec_pack = Packet.from_bytes(response)
                print("(2) rec ack " + str(rec_pack.seq_num))
                print(rec_pack)
                lock.acquire()
                ack_tracker[rec_pack.seq_num][1] = True
                lock.release()

                if rec_pack.seq_num == p2.seq_num:
                    t2.cancel()
                    response2, sender2 = conn.recvfrom(1024)
                    rec_pack2 = Packet.from_bytes(response2)
                    print("(1) rec ack " + str(rec_pack2.seq_num))
                    print(rec_pack2)
                    lock.acquire()
                    ack_tracker[rec_pack2.seq_num][1] = True
                    lock.release()
                    if rec_pack.seq_num == p1.seq_num:
                        t1.cancel()
                        a = a + 1
                        b = b + 1
                        continue
                elif rec_pack.seq_num == p1.seq_num:
                    t1.cancel()
                    if b == len(res_packets) - 1:
                        responseF, senderF = conn.recvfrom(1024)
                        rec_packF = Packet.from_bytes(responseF)
                        print("(0) ACK " + str(rec_packF.seq_num))
                        print(rec_packF)
                        lock.acquire()
                        ack_tracker[rec_packF.seq_num][1] = True
                        lock.release()
                    print("************")
                    print(ack_all(ack_tracker))
                    a = a + 1
                    b = b + 1
                    continue

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
test_msg = 'POST /lol HTTP/1.0\nHost: 127.0.0.1\nContent-Length:6\n\nLolazo\n'
res = HttpResponse.create_response(test_msg, args.PATH)
HttpRequest.read_response(res, True, "l.txt")
run_server(args.PORT)
