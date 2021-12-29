import socket
import threading
import sys
import os
import struct
import random
import colorama
from select import select
from scapy.arch import get_if_addr
import time
from colors import colors
from pynput.keyboard import Listener

name = socket.gethostname()
SERVER_ADDRESS = socket.gethostbyname(name)
# ip = ''  # get_if_addr('eth2')
ip = SERVER_ADDRESS
port = 13117
player_name = "almog"
broadcastIP = ip
clientSocket=None

def on_press(key):
    pass


def on_release(key):
    print(key)
    try:
        clientSocket.sendall(key.char.encode())
    except ConnectionError:
        pass
    except OSError:
        pass



def start_client():
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        print(colors.OKBLUE +
              "Client started, listening for offer requests..." + colors.ENDC)

        # text = "Client started, listening for offer requests..."
        # self.pretty_print(text)
        try:
            s.bind(('', port))
        except:
            s.close()
            time.sleep(0.2)
            continue

        # Binds client to listen on port self.port. (will be 13117)
        while True:
            try:  # Receives Message
                message, address = s.recvfrom(1024)
                magic_cookie, message_type, port_tcp = struct.unpack(
                    ">IbH", message)

                print(colors.OKGREEN + "Received offer from " +
                      ip + ", attempting to connect..." + colors.ENDC)
                # Drop message if magic cookie is wrong \ not type 2
                # print(bytes.fromhex('0xabcddcba'))
                if magic_cookie == 2882395322 and message_type == 2:
                    s.close()
                    connectTCPServer(address[0], port_tcp)
            except:
                time.sleep(0.2)
                continue
            break


def connectTCPServer(ip_tcp, port_tcp):
    global clientSocket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket=s
    # s.settimeout(11)
    try:  # connect to server via TCP
        s.connect((ip_tcp, port_tcp))
    except:
        pass

    # Sending team name
    s.send(player_name.encode('utf-8'))

    open_game_massage = s.recv(1024).decode()
    if open_game_massage:
        print(colors.WARNING + open_game_massage + colors.ENDC)
    else:
        s.close()
        return

    with Listener(on_press=on_press, on_release=on_release) as listener:
    # waiting for end game message and stop listening to typing
        data = clientSocket.recv(1024)
        print(colors.OKGREEN + data.decode() + colors.ENDC)
        listener.stop()


    # # Playing
    # data = None
    # # s.setblocking(False)  # don't wait while s.recv
    # start_time = time.time()
    # while time.time() - start_time < 11:  # we wan't timeout in case server stops in the middle
    #     try:  # check if EndGame packet received from server
    #         data = s.recv(1024)
    #     except:
    #         pass
    #     if data:
    #         data = str(data, 'utf-8')
    #         print(colors.OKGREEN + data + colors.ENDC)

    #         break
    #     else:  # still typing
    #         try:
    #             character_coming, _, _ = select([sys.stdin], [], [], 0.1)
    #             if character_coming:
    #                 c = sys.stdin.read(1)
    #                 print(c)
    #                 s.send(bytes(c, encoding='utf8'))
    #         except:
    #             pass        
    
    print(colors.FAIL + "Server disconnected, listening for offer requests..."+colors.ENDC)
    s.close()


# name = socket.gethostname()
# SERVER_ADDRESS = socket.gethostbyname(name)
# ip = ''  # get_if_addr('eth2')
start_client()
