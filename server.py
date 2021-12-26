from socket import *
import _thread
import time
from collections import defaultdict
import struct
from colors import colors
# from scapy.arch import get_if_addr
import threading


e = threading.Event()
serverPort = 13117
server_tcp_port = 2025
serverSocket_UDP = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
serverSocket_UDP.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

serverSocket_TCP_Master = socket(AF_INET, SOCK_STREAM)
# server_ip = get_if_addr('eth1')
server_ip = gethostbyname(gethostname())
serverSocket_TCP_Master.bind((server_ip, server_tcp_port))
magic_cookie = 0xfeedbeef
message_type = 0x2

# global stop_game,winner
client_player1 = {}
client_player2 = {}
connection_socket_list = []
stop_game = False
num_of_threads = []
connection_time = 10
game_time = 10
# global winner
winner = 0


def start_server():
    print(colors.OKBLUE+"Server started, listening on IP address " +
          server_ip + "" + colors.ENDC)
    connection = False
    start_time = time.time()
    while time.time() - start_time < connection_time:
        if not connection:
            connection = True
            _thread.start_new_thread(offer_UDP_connection, (start_time,))
            _thread.start_new_thread(TCP_connection, (start_time,))
    game()


def offer_UDP_connection(start_time):
    """
    send broadcast to get udp connection
    :param start_time: when the connection open
    :return: finish after the given time
    """
    while time.time() - start_time < connection_time:
        message = struct.pack('QQQ', magic_cookie,
                              message_type, server_tcp_port)
        serverSocket_UDP.sendto(message, ('<broadcast>', serverPort))
        time.sleep(1)  # send offer every second


def TCP_connection(start_time):
    """
    do tcp connection, get connection_socket and save it for each client
    :param start_time: when the connection open
    :return: finish after the given time
    """
    i = 0
    # client_player1 = {}
    # client_player2 = {}
    # connection_socket_list = []
    while time.time() - start_time < connection_time:
        try:
            serverSocket_TCP_Master.listen()
            connection_socket, client_addr = serverSocket_TCP_Master.accept()
            playe_name = connection_socket.recv(1024).decode('utf-8')

            if i == 0:
                client_player1['player_name'] = playe_name
                client_player1['connection_socket'] = connection_socket
                connection_socket_list.append(connection_socket)
                client_player1['client_addr'] = client_addr
                i += 1
            elif i == 1:
                client_player2['player_name'] = playe_name
                client_player2['connection_socket'] = connection_socket
                connection_socket_list.append(connection_socket)
                client_player2['client_addr'] = client_addr
        except ConnectionError:
            break
        # except socket.timeout:
        #     break
        except OSError:
            break

    serverSocket_TCP_Master.close()


def game():
    """
    start the game and send message to the clients, each client get thread that start the game
    print the score in the end
    :return:
    """
    global winner
    player1Name = ''
    player2Name = ''
    if client_player1:
        player1Name = client_player1['player_name']
    if client_player2:
        player2Name = client_player2['player_name']

    msg = "Welcome to Quick Maths.\nPlayer 1: " + player1Name \
          + "\nPlayer 2: " + player2Name + \
        "\n==\nPlease answer the following question as fast as you can:\nHow much is 2+2?"
    print(colors.WARNING + msg + colors.ENDC)
    for socket in connection_socket_list:
        try:
            socket.sendall(msg.encode())

        except ConnectionError:
            pass

    if client_player1:
        _thread.start_new_thread(
            game_of_client, (1, client_player1['connection_socket']))
    if client_player2:
        _thread.start_new_thread(
            game_of_client, (2, client_player2['connection_socket']))

    # stop_game= False

    e.wait(timeout=game_time)
    # time.sleep(game_time)
    stop_game = True

    msg_end = "Game over!\nThe correct answer was 4!\n"
    # winner = check_winner()

    if winner == 1:
        msg_end += "\nCongratulations to the winner: " + player1Name
        # print('here')
    elif winner == 2:
        msg_end += "\nCongratulations to the winner: " + player2Name
    elif winner == 0:
        msg_end += "\nThe game finishes with a draw"

    print(colors.OKGREEN + msg_end + colors.ENDC)
    # print(msg_end)
    # updating the clients with game summarize
    for socketc in connection_socket_list:
        try:
            socketc.sendall(msg_end.encode())
            # socketc.close()
        except ConnectionError:
            pass

    print(colors.FAIL + "\nGame over, sending out offer requests...\n" + colors.ENDC)
    # serverSocket_TCP_Master.close()


def game_of_client(player_Num, connection_socket):
    """
    each client has separate thread- this is his game
    :param player_Num: 1 or 2
    :param connection_socket: the client socket
    :return:
    """
    global winner

    try:
        while not stop_game:
            # print(player_Num)
            # connection_socket.send(str(stop_game).encode('utf-8'))
            key = connection_socket.recv(1024).decode('utf-8')
            # print(key)
            if not key:
                break
            if key == '4':
                # winner=1
                if player_Num == 1:

                    # print(player_Num)
                    winner = 1
                    e.set()

                elif player_Num == 2:
                    winner = 2
                    e.set()
            else:
                if player_Num == 1:

                    winner = 2
                    e.set()

                elif player_Num == 2:
                    winner = 1
                    e.set()

    except ConnectionError:
        pass

    # connection_socket.close()


while True:
    # client_player1 = {}
    # client_player2 = {}
    # connection_socket_list = []
    start_server()
    # serverSocket_UDP.close()
    # serverSocket_TCP_Master.close()
