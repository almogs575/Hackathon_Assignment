import socket
import struct
from select import select
from scapy.arch import get_if_addr
import time
from colors import colors
import time
import sys
import getch
# import msvcrt
import termios
import tty
import atexit




# globals
name = socket.gethostname()
SERVER_ADDRESS = socket.gethostbyname(name)
# ip = ''  # get_if_addr('eth2')
# ip = SERVER_ADDRESS
port = 13117
player_name = "almog"


def start_client():
    print(colors.OKBLUE +
          "Client started, listening for offer requests..." + colors.ENDC)
    while True:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        try:
            udp_socket.bind(('', port))
        except:
            udp_socket.close()
            time.sleep(0.2)
            continue

        # binds client to listen on port
        while True:
            try:  # Receives Message
                # message, address = udp_socket.recvfrom(1024)
                # magic_cookie, message_type, port_tcp = struct.unpack(
                #     ">IbH", message)

                print(colors.OKGREEN + "Received offer from " +
                      SERVER_ADDRESS + ", attempting to connect..." + colors.ENDC)
                # drop message if magic cookie is wrong or not type 2
                # if magic_cookie == 2882395322 and message_type == 2:
                udp_socket.close()
                connectTCPServer(SERVER_ADDRESS, 2025)  # adress[0],#port_tcp
            except:
                time.sleep(0.2)
                # continue
                break


def _getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)  # This number represents the length
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch
# getch = _getch()
# print(getch)


def connectTCPServer(ip_tcp, port_tcp):
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
        open_game_massage = tcp_socket.recv(1024).decode()
        if open_game_massage:
            print(colors.WARNING + open_game_massage + colors.ENDC)
        else:
            tcp_socket.close()
            return

        data = ""
        key = ""
        tcp_socket.setblocking(False)  # don't wait while s.recv

        while not data:
            try:
                # check if end game massege received from server
                data = tcp_socket.recv(1024).decode()
            # break
            except:
                pass
            if data:
                # data = str(data, 'utf-8')
                print(colors.OKGREEN + data + colors.ENDC)
                break
            else:

                if not key:
                    # if kb.kbhit():
                    dr, dw, de = select([sys.stdin], [], [], 0)
                    if dr != []:
                                        # TODO need to change to linux
                        key = _getch()
                        print(key)
                        tcp_socket.send(bytes(key, encoding='utf8'))
                        time.sleep(0.1)

    except:
        pass

    print(colors.FAIL +
          "\nServer disconnected, listening for offer requests..."+colors.ENDC)
    tcp_socket.close()


start_client()
