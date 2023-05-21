from enum import Enum


class PacketType(Enum):
    DATA = 0
    ACK = 1
    NAK = 2
    SYN = 3
    SYN_ACK = 4
    FIN = 5


# Test for class enum
def main():
    p = PacketType.DATA
    x = 1
    print(PacketType(x).name)
    print(p.value)
    print(p.name)


if __name__ == '__main__':
    main()
