import pandas as pd
from pandas import DataFrame
from random_word import RandomWords
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display
import socket
import threading
import os


IP_ADD = "192.168.0.101"
PORT = 9000
BUFFER_SIZE=100

word_to_guess=''
guessed_word = ''
result = ''

playersocket = None

def start_conn():
    global playersocket, word_to_guess

    playersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    playersocket.connect(("localhost", PORT))
    word_to_guess = playersocket.recv(100).decode()
    print(F"Guess This Word : {word_to_guess}\n")
    # return playersocket,word_to_guess




def serve_back(guessed_Word):
    global playersocket

    playersocket.send(guessed_word.encode())
    print('Result is being calculated!')
    
    #check to whom we sent
    print(playersocket.getsockname())
    print(playersocket.getpeername())

    result=playersocket.recv(BUFFER_SIZE).decode()
    print('Result : ',result)
    if result == 'You won':
        print("Good Job! You finished first..")
    else:
        print("Better luck next time!")


##########################################################################################



#function that takes input from the user only if word has len 5 and is string
def user_entry(ip = None):
    while True:
        ip = input("Enter your guess : ")
        if ((type(ip) != str) or (len(ip) != 5)):
            print('Guess Invalid! Try again')
            continue
        else:
            return ip.upper()
            

#colormappping for jupyter notebook
def color_map(val):
    if val == val.upper() and len(val)==1:
        color = 'green'
    elif len(val) == 2:
        color = 'orange'
    else:
        color = 'black'   
    return 'color: %s' % color      

#function to turn guesses into dataframe that can be used for checking an indexing
def convert_to_df(attempt,guess_array):
    column = ['1','2','3','4','5']
    indexes = ['Attempt-'+str(attempt+1)]

    df=pd.DataFrame(guess_array).T
    df.columns = column
    df.index = indexes

    return df

#covert the guess values into indexes of verified dataframe
def check_to_index(guess_index):
    check=[]
    for item in guess_index:
        if item[2] == 'Match':#if matches
            check.append(item[0])
        elif item[2] == 'EX':#if exists
            check.append(item[0] + ' ')
        else:#if not present
            check.append(item[0].lower()) 
    return check

        
#actual game logic
def game():
    global word_to_guess

    start_conn()

    guess_word = word_to_guess


    #values to keep track of word guessed rn!
    guess_array = np.array(list(guess_word.upper()))
    guess_index = [[item,index,None] for index,item in enumerate(guess_array)]

    attempt = 0
    guess_store=[]#for logging all the guesses

    while attempt < 6:

        guessing_rn = user_entry()
        guessing_array = np.array(list(guessing_rn))
        guessing_index = [[item,index,None] for index,item in enumerate(guessing_array)]

        matched = []#add if found values
        existing = []#track prev found values
        matching = np.where(guess_array==guessing_array)[0]#checking for matches

        for matches in matching:
            matched.append(guessing_index[matches][0])
            #marking index to check later
            guessing_index[matches][2] = 'Match'
            guess_index[matches][2] = 'Match'

        remaining_guess = [item for item in guessing_index if item[2] !='Match']
        remaining_true = [item for item in guess_index if item[2] != 'Match']

        for guesses in remaining_guess:
            for true in remaining_true:
                if guesses[0] == true[0]:
                    if list(guess_array).count(guesses[0]) > (matched.count(guesses[0]) + existing.count(guesses[0])):
                        existing.append(guesses[0])
                        true[2] = 'EX'
                        guesses[2] = 'EX'
                    else:
                        continue           

        def color_map(val):
            if val == val.upper() and len(val)==1:
                color = 'green'
            elif len(val)==2:
                color = 'orange'
            else:
                color = 'black'   
            return 'color: %s' % color    

        marked = check_to_index(guessing_index)

        guessing_df=convert_to_df(attempt, marked)
        guess_store.append(guessing_df)
        new_df=pd.concat(guess_store)

        g = new_df.style.applymap(color_map)  
        display(g)

        if guessing_rn.lower() == guess_word:
            print('______________________________________________________________')
            print(f'You are right the word is: ',guess_word.upper())
            break
        else:
            attempt += 1
            
            if attempt == 6:
                print(f'Nice try, The word was',guess_word.upper())
                break
    print('From Game() : ', guessing_rn)

    # """
    if(guessing_rn.upper() == guess_word.upper()):
        playersocket.send("W".encode())
    else:
        playersocket.send("L".encode())
    decider=playersocket.recv(BUFFER_SIZE).decode()
    print("\nThe final results: ",decider)


    # """

    # playersocket.send(guessing_rn.encode())
    # decider=playersocket.recv(BUFFER_SIZE).decode()
    # print("\nThe final results: ",decider)
    
        
    


if __name__ == '__main__':
    game()                    

