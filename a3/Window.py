from packet import Packet


class Window:
    def __init__(self, pkg_list):
        self.pkg_list = pkg_list
        self.num_frames = len(pkg_list)
        self.window_size = int(self.num_frames / 2)


def main():
    p1 = Packet(packet_type=0,
                seq_num=0,
                peer_ip_addr="120.12.12.12",
                peer_port=8000,
                payload="H".encode("utf-8"))
    p2 = Packet(packet_type=0,
                seq_num=1,
                peer_ip_addr="120.12.12.12",
                peer_port=8000,
                payload="E".encode("utf-8"))
    p3 = Packet(packet_type=0,
                seq_num=2,
                peer_ip_addr="120.12.12.12",
                peer_port=8000,
                payload="L".encode("utf-8"))
    p4 = Packet(packet_type=0,
                seq_num=3,
                peer_ip_addr="120.12.12.12",
                peer_port=8000,
                payload="L".encode("utf-8"))
    listpkg = [p1, p2, p3, p4]
    w = Window(listpkg, )


if __name__ == '__main__':
    main()
