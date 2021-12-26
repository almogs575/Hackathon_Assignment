from colors import colors
from pynput.keyboard import Listener
import time
from socket import *
import struct
# import getchמ
import keyboard
message_code = 2882395322


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


def UDP_connection():
    """
    :return: ip of the server and tcp port of server
    """
    clientSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    clientSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    serverPort = 13117
    clientSocket.bind(('', serverPort))
    # print("Client started, listening for offer requests...")
    while True:
        # try:

        message, serverAddress = clientSocket.recvfrom(1024)
        unpacked_message = struct.unpack('QQQ', message)
        # print(str(unpacked_message[0]))
        if unpacked_message[0] == message_code and unpacked_message[1] == 2:
            clientSocket.close()
            server_tcp_port = unpacked_message[2]
            (ip, port) = serverAddress
            print(colors.OKGREEN + "Received offer from " +
                  ip + ", attempting to connect..." + colors.ENDC)
            break
    return ip, server_tcp_port
    # except:
    # continue


def TCP_connection(ip, server_tcp_port, clientSocket):
    """
    :param ip: ip of the server
    :param server_tcp_port: tcp port of server
    :return: brake when server crash
    """
    # print("Received offer from ", ip, " attempting to connect...")

    clientSocket.connect((ip, server_tcp_port))
    # team_name = input("enter name:")
    clientSocket.send("almog".encode('utf-8'))
    return True


def game(clientSocket):
    """
    game: read key and then write to socket
    """
    # while True:  # receive welcome message
    open_game_massage = clientSocket.recv(1024).decode()
    if open_game_massage:
        print(colors.WARNING + open_game_massage + colors.ENDC)
        # break

    # while True:

        # thread listener, recives characters input from the user
    with Listener(on_press=on_press, on_release=on_release) as listener:
        # waiting for end game message and stop listening to typing
        data = clientSocket.recv(1024)
        print(colors.OKGREEN + data.decode() + colors.ENDC)
        listener.stop()

    print(colors.FAIL + "Server disconnected, listening for offer requests..."+colors.ENDC)

    # stop_message = clientSocket.recv(1024).decode()
    # print(stop_message)
    # break
    # clientSocket.close()
    # if stop_message == "game over":
    #     print(stop_message)
    #     break

    clientSocket.close()


print(colors.OKBLUE + "Client started, listening for offer requests..." + colors.ENDC)
while True:
    ip, server_tcp_port = UDP_connection()
    clientSocket = socket(AF_INET, SOCK_STREAM)
    try:
        ans = TCP_connection(ip, server_tcp_port, clientSocket)
        if ans:
            game(clientSocket)
        clientSocket.close()
    # except socket.timeout:
    #     pass
    except ConnectionError:
        pass
