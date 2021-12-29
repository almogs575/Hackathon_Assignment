import socket
import time
import threading
import random
from _thread import start_new_thread
import colorama
import struct
from select import select
from scapy.arch import get_if_addr
from colors import colors
from random import randrange


name = socket.gethostname()
SERVER_ADDRESS = socket.gethostbyname(name)
# ip = ''  # get_if_addr('eth2')
ip = SERVER_ADDRESS
port = 2025
toBroadcast = True
players = []
# scores = [0, 0]
lock = threading.Lock()
threads_list = []
socket_list = []
# self.player_statistics = []
# self.player_key_press = []
start_game = False
game_finished = False
num_participants = 0
math_result = 0
winner = 0
num1 = 0
num2 = 0

# def start_server():
#     startTCPServer()
# start_new_thread(self.TCPServer)


def start_server():
    # Starts TCP Server via a thread.
    thread = threading.Thread(target=TCPServer)
    thread.start()


def TCPServer():  # Main thread
    global num_participants, threads_list, num1, num2, math_result
    while True:
        # End Game
        default_server()
        # Create TCP server welcome socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((ip, port))  # 2025
        except:
            continue

        print(colors.OKBLUE+"Server started, listening on IP address " +
              ip + "" + colors.ENDC)

        startBroadcasting()  # split to new thread, will be closed after 10 sec
        # start_new_thread(self.broadcast)
        s.listen()
        num1 = randrange(5)
        num2 = randrange(5)
        math_result = num1+num2
        while not start_game:  # while there is no game
            # establish connection with client
            client_coming, _, _ = select([s], [], [], 2)
            if client_coming:
                c, addr = s.accept()
                # set gaming for player
                lock.acquire()
                num_participants += 1

                # th=threading.Thread(target=clientHandler,args=(c,))
                # th.start()

                # threads_list.append(th)
                lock.release()
                # Start a new thread and return its identifier
                # th=threading.Thread(target=clientHandler,args=(c,))
                # th.start()
                # threads_list.append(th)
                # if num_participants==2:

                start_new_thread(clientHandler, (c,))

            # if len(threads_list)==2:
            # for th in threads_list:
            #     th.start()
        # game()
        while num_participants > 0:
            # for th in threads_list:
            #         th.start()
            time.sleep(1)

        s.close()
        # self.pretty_print("Game over, sending out offer requests...")
        print(colors.FAIL + "\nGame over, sending out offer requests...\n" + colors.ENDC)
        # start_game = False


def startBroadcasting():
    # Starts Broadcasting via a thread.
    thread = threading.Thread(target=broadcast)
    thread.start()


def broadcast():
    global start_game
    start_time = time.time()
    server = socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # Enable port reusage
    server.setsockopt(socket.SOL_SOCKET,
                      socket.SO_REUSEADDR, 1)
    # Enable broadcasting mode
    server.setsockopt(socket.SOL_SOCKET,
                      socket.SO_BROADCAST, 1)

    message = struct.pack(">IbH", 0xabcddcba, 0x2, port)
    broadcastIP = ip  # '.'.join(self.ip.split('.')[:2]) + '.255.255'
    while time.time() - start_time < 10:
        server.sendto(message, (broadcastIP, 13117))
        time.sleep(1)
    # if num_participants==2:
    start_game = True


def clientHandler(c):
    global players, winner, num_participants
    try:
        playe_name = str(c.recv(1024), 'utf-8')
    except:
        pass

    players += [playe_name]

    # wait until game will start
    while not start_game:
        time.sleep(0.1)

    # Sending start message to my client
    player1Name = ''
    player2Name = ''
    # for players in players:

    if players[0]:
        player1Name = players[0]

    if len(players) > 1:
        player2Name = players[1]

    # num1 = randrange(5)
    # num2 = randrange(5)
    # math_result = num1+num2
    msg = "Welcome to Quick Maths.\nPlayer 1: " + player1Name \
        + "\nPlayer 2: " + player2Name + \
        "\n==\nPlease answer the following question as fast as you can:\nHow much is " + \
        str(num1) + "+" + str(num2)+"?"
    print(colors.WARNING + msg + colors.ENDC)

    try:
        c.send(msg.encode())

    except ConnectionError:
        pass

    index = players.index(playe_name)
    # team_index = 0 if playe_name in team1 else 1
    # While not past 10 seconds - listen to key presses.
    start_time = time.time()
    while time.time() - start_time < 10:  # play 10 seconds
        try:  # data received from client
            rlist, _, _ = select([c], [], [], 0.1)
            if rlist:
                data = c.recv(1024)  # new key pressings
                if not data:
                    time.sleep(0.1)
                    continue
                if int(data) == math_result:
                    # winner=1
                    if index == 0:

                        # print(player_Num)
                        winner = 1
                        # e.set()
                    elif index == 1:
                        winner = 2
                        # e.set()
                elif int(data) != math_result:
                    if index == 0:

                        winner = 2
                        # e.set()

                    elif index == 1:
                        winner = 1
                        # e.set()
                        # break

        except:
            pass

    # Game Over Message
    msg_end = "Game over!\nThe correct answer was "+str(math_result)+"!\n"
# winner = check_winner()

    if winner == 1:
        msg_end += "\nCongratulations to the winner: " + player1Name
        # print('here')
    elif winner == 2:
        msg_end += "\nCongratulations to the winner: " + player2Name
    elif winner == 0:
        msg_end += "\nThe game finishes with a draw"

    print(colors.OKGREEN + msg_end + colors.ENDC)

    try:
        c.send(msg_end.encode())
    except:
        pass

    # connection closed
    c.close()
    lock.acquire()
    num_participants -= 1
    lock.release()


def default_server():
    """
    Returning Server to default values before new game.
    """
    global players, threads_list, start_game, game_finished, num_participants, math_result, winner

    players = []
    threads_list = []

    start_game = False
    game_finished = False
    num_participants = 0
    math_result = 0
    winner = 0


start_server()
