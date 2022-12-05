from packet import Packet
from PacketType import PacketType


class ReceiverWindow:
    def __init__(self):
        self.rec_packets = []
        self.ready = False

    def insert(self, packet):
        """Inserts packet of type Packet to the list in order"""
        if packet.seq_num not in self.rec_packets:
            self.rec_packets.append([packet.seq_num, packet])
            tmp = sorted(self.rec_packets, key=lambda x: x[0])
            self.rec_packets = tmp

    def all_packets_received(self, fin_packet):
        print("HOT HERE")
        print(len(self.rec_packets))
        end = fin_packet.seq_num
        if len(self.rec_packets) == 0 or len(self.rec_packets) == end:
            self.ready = True
            return True
        else:
            return False

    def get_packets(self):
        packets = []
        for x in self.rec_packets:
            packets.append(x[1])
        return packets


def main():
    pass


if __name__ == main():
    main()
