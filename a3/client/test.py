import PacketsConverter
from packet import Packet
import math
from threading import Timer

PAYLOAD_SIZE = 1013


# ins = open("demorequest.txt", "r")
# msg = ins.read()
# print(msg)
# num_of_packets = math.ceil(len(msg) / PAYLOAD_SIZE)
# packets = list()
# PacketsConverter.create_packets(msg, num_of_packets, packets, '127.0.0.1', 8000)
# print(packets)
# out = open("msg.txt", "w")
# out.write(PacketsConverter.create_msg(packets))
# def send_packet(lol, lol2):
#     print(lol)
#     print(lol2)
#
#
# syn_thread = Timer(2, send_packet, (1,2)).start()
a = [1,2,3]
d = {x:[False,False] for x in a}
print(d)
for x in d:
    print(x)
    print(d[x][0])
