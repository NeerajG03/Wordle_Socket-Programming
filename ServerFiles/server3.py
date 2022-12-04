import socket
import threading
import openpyxl
import random
import time

PLAYER_COUNT = 2

IP_ADD = socket.gethostbyname(socket.gethostname())
PORT = 9000
BUFFER_SIZE=100
winner = None
connected_clients = [] #used to know when both the clients are connected
random_word = ''
flag = 0

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #welcoming socket
serversocket.bind((IP_ADD, PORT))



#print details of server socket
print(serversocket.getsockname())

def get_random_word():
#For Grabbing a Random Word from Excel
    global random_word

    random_index = random.randrange(0, 400)
    word_list = openpyxl.load_workbook('Word_List.xlsx')
    curr_sheet = word_list.active
    random_word_cell = curr_sheet.cell(random_index, 1)
    random_word = random_word_cell.value

def start_game():
    print('in start game')
    for each_client in connected_clients:
        each_client.send(random_word.encode())
        print('sent word')      
        threading.Thread(target=winner_declaration, args=(each_client,)).start()        

def winner_declaration(client):
    global winner
    global flag

    print(client.getpeername())
    try:
        win_signal = client.recv(BUFFER_SIZE).decode()
        print('Signal recieved! word output : ',win_signal)
        if(flag == 0 and win_signal == 'W'):
            client.send(('You Won!').encode())
            flag = 1
        else:
            client.send(('You lost! Better luck next time!').encode()) 

        connected_clients.remove(client)

        if(len(connected_clients)==0):
            flag = 0
            start_server()

    except ConnectionAbortedError:
        print('Game Over!')
    except ConnectionResetError:
        print('Game Over!')


def handle_client():
    conn, addr = serversocket.accept()
    print(F"Client {addr} Connected")
    connected_clients.append(conn)
    if(len(connected_clients) == PLAYER_COUNT):
        get_random_word() #Get a random word everytime game starts
        start_game()


def start_server():
    serversocket.listen() #listen for 2 clients only

    for i in range(1, PLAYER_COUNT):
        threading.Thread(target=handle_client).start()

while(True):
    start_server()
