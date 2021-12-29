import socket
import time
import threading
from _thread import start_new_thread
import struct
from select import select
from scapy.arch import get_if_addr
from colors import colors
from random import randrange
# from threading import Event

# globals
SERVER_ADDRESS = get_if_addr('eth2')
port_tcp = 2025
port_broadcast = 13117
players = {}
lock = threading.Lock()
threads_list = []
num_participants = 0
math_result = 0
winner = ""
num1 = 0
num2 = 0
stop_game = False
stop_broading = False


def start_server():
    """
    starts TCP server with a thread.
    """

    thread = threading.Thread(target=TCPServer)
    thread.start()


def TCPServer():
    """
    the tcp thread get the clients
    """
    global num_participants, num1, num2, math_result, players, stop_broading
    print(colors.OKBLUE+"Server started, listening on IP address " +
          SERVER_ADDRESS + "" + colors.ENDC)
    while True:
        # reset globals
        default_server()
        # Create TCP server welcome socket
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            tcp_socket.bind((SERVER_ADDRESS, port_tcp))  # 2025
        except:
            continue

        startBroadcasting()  # split to new thread
        tcp_socket.listen()
        # random math problem
        num1 = randrange(5)
        num2 = randrange(5)
        math_result = num1+num2
        # start_time = time.time()
        while num_participants != 2: 

            try:
                # establish connection with client
                client_coming, _, _ = select([tcp_socket], [], [], 2)
                if client_coming:
                    conn_socket, addr = tcp_socket.accept()
                    # set num of players
                    lock.acquire()
                    num_participants += 1

                    try:
                        # player_name = str(conn_socket.recv(1024), 'utf-8')
                        player_name = conn_socket.recv(1024).decode()

                    except:
                        break
                    # socket for every client
                    players[player_name] = conn_socket

                    lock.release()

            except:
                stop_broading = True
                break

        if num_participants == 2:
            stop_broading = True
            start_time = time.time()
            while time.time() - start_time < 10:
                time.sleep(1)
            game()
        tcp_socket.close()
        print(colors.FAIL + "\nGame over, sending out offer requests...\n" + colors.ENDC)


def startBroadcasting():
    """
    creating broadcasting thread
    """
    # Starts Broadcasting thread
    thread = threading.Thread(target=broadcast)
    thread.setDaemon(True)
    thread.start()


def broadcast():
    """
    the broadcast thread starting to sends messeges
    """
    # start_time = time.time()
    # global stop_broading
    udp_socket = socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # Enable port reusage
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Enable broadcasting mode
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    message = struct.pack("!IbH", 0xabcddcba, 0x2, port_tcp)
    # broadcastIP = ip
    # start_time = time.time()
    while not stop_broading:
        udp_socket.sendto(message, ('172.99.0.255', port_broadcast))
        time.sleep(1)


def game():
    """
    here all the messages are created and sends to clients
    """
    global players, winner, num_participants, stop_game
    player1Name = ''
    player2Name = ''

    for name in players.keys():
        if not player1Name:
            player1Name = name
        elif not player2Name:
            player2Name = name

    msg = "Welcome to Quick Maths.\nPlayer 1: " + player1Name \
        + "\nPlayer 2: " + player2Name + \
        "\n==\nPlease answer the following question as fast as you can:\nHow much is " + \
        str(num1) + "+" + str(num2)+"?"

    print(colors.WARNING + msg + colors.ENDC)

    # sending welcome message
    for player in players.keys():
        try:
            players[player].sendall(msg.encode())
            start_new_thread(clientHandler, (players[player], player))
        except ConnectionError:
            pass

    start_time = time.time()
    while time.time() - start_time < 10 and not stop_game:
        time.sleep(1)
    # exit_game.wait(9)
    # stop_game=True
    time.sleep(0.1)

    # game over message
    msg_end = "Game over!\nThe correct answer was "+str(math_result)+"!\n"

    if winner == player1Name or winner == ('!'+player2Name):
        msg_end += "\nCongratulations to the winner: " + player1Name
        # print('here')
    elif winner == player2Name or winner == ('!'+player1Name):
        msg_end += "\nCongratulations to the winner: " + player2Name
    elif not winner:
        msg_end += "\nThe game finishes with a draw"

    print(colors.OKGREEN + msg_end + colors.ENDC)
    # sending ending message to clients
    for player in players.keys():
        try:
            players[player].sendall(msg_end.encode())
            players[player].close()
        except:
            print("error")
            pass


def clientHandler(client_socket, playe_name):
    """
    each client send his answer
    Args:
        client_socket 
        playe_name 
    """
    global winner, stop_game, num_participants
    while not stop_game:
        try:
            # data received from client
            rlist, _, _ = select([client_socket], [], [], 0.1)
            if rlist:
                data = client_socket.recv(1024).decode()  # new key pressings
                if not data:
                    time.sleep(0.1)
                    continue
                if int(data) == math_result:
                    lock.acquire()
                    winner = playe_name
                    # time.sleep(0.5)
                    stop_game = True
                    lock.release()
                    # exit_game.set()

                elif int(data) != math_result:
                    lock.acquire()
                    winner = '!' + playe_name
                    # time.sleep(0.5)
                    stop_game = True
                    lock.release()
                    # exit_game.set()

                    # break

        except:
            stop_game = True
            break
    lock.acquire()
    num_participants -= 1
    lock.release()


def default_server():
    """
    returning server to default values before new game
    """
    global players, threads_list, num_participants, math_result, winner, stop_game, stop_broading
    players = {}
    stop_game = False
    num_participants = 0
    math_result = 0
    winner = ""
    stop_broading = False


start_server()
