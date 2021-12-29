import socket
import struct
from scapy.arch import get_if_addr
import time
from colors import colors
from KBHit import KBHit


# globals

SERVER_ADDRESS = get_if_addr('eth2')
port_broadcast = 13117
# tcp_port = 2025
player_name = "TheLastRound"
kb = KBHit()


def start_client():
    """
    create and run client sockets
    """
    print(colors.OKBLUE +
          "Client started, listening for offer requests..." + colors.ENDC)
    while True:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        try:
            udp_socket.bind(('', port_broadcast))
        except:
            udp_socket.close()
            time.sleep(0.2)
            continue

        # binds client to listen on port
        while True:
            try:  # Receives Message
                message, address = udp_socket.recvfrom(1024)
                magic_cookie, message_type, port_tcp = struct.unpack(
                    ">IbH", message)

                # drop message if magic cookie is wrong or not type 2
                if magic_cookie == 2882395322 and message_type == 2:
                    print(colors.OKGREEN + "Received offer from " +
                          SERVER_ADDRESS + ", attempting to connect..." + colors.ENDC)
                    udp_socket.close()
                    connect_TCP_server(address[0], port_tcp)
            except:
                time.sleep(0.2)
                # continue
                break


def connect_TCP_server(ip_tcp, port_tcp):
    """
    connect to the tcp server
    Args:
        ip_tcp 
        port_tcp 
    """
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tcp_socket.settimeout(0.2)
    try:
        # connect to server TCP
        tcp_socket.connect((ip_tcp, port_tcp))
    except:
        pass

    # sending team name
    tcp_socket.send(player_name.encode())

    try:
        open_game_message = tcp_socket.recv(1024).decode()
        time.sleep(0.5)
        # print(colors.OKGREEN + "Received offer from " +
        #       SERVER_ADDRESS + ", attempting to connect..." + colors.ENDC)
        if open_game_message:
            print(colors.WARNING + open_game_message + colors.ENDC)
        else:
            tcp_socket.close()
            return

        data = ""
        key = ""
        tcp_socket.setblocking(False)  # don't wait while s.recv

        while not data:
            try:
                # check if end game messege received from server
                data = tcp_socket.recv(1024).decode()
            # break
            except:
                pass
            if data:
                print(colors.OKGREEN + data + colors.ENDC)
                break
            else:

                if not key:
                    if kb.kbhit():
                        key = kb.getch()
                        print(key)
                        tcp_socket.send(bytes(key, encoding='utf8'))
                        time.sleep(0.1)

    except:
        pass

    print(colors.FAIL +
          "\nServer disconnected, listening for offer requests..."+colors.ENDC)
    tcp_socket.close()


start_client()
