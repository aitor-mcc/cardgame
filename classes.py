#the card and deck classes are used in both multiplayer and single player games 
#the server class and the player class in this file are used only in the multiplayer games 
#the corresponding player files can be found in the single player class 
 
import socket 
from threading import * 
import pygame  
import random 
import sys 
import time 
import database 
from datetime import datetime 
import singlePlayer as single 
from functions import * 
from gui import * 

cardX = 180 
cardY = 450 
cardSpace = 62 

pygame.init() 

 

#server class 
class conn: 
    def __init__(self,user,host): 
        self.__host = host   # as both code is running on same pc 
        self.__port = 8888  # socket server port number 
        self.__client_socket = socket.socket()  # instantiate 
        self.__client_socket.connect((self.__host, self.__port))  # connect to the server 
        self.id = self.sendReceive("id, " + str(user)) 
        print("connected with id: " + str(self.id)) 

 

    def sendReceive(self,msg="status"): 

        #used to both send/receive data 
        #a request for data, with the appropriate data is sent to the server and a response will be received depending on reuquest 
        """ 
        List of possible requests: 
        status - phase/status of game 
        data - current game data 
        players - number of players 
        id - receive connection id 
        turn - current turn when in game 
        prevTurn - previous player 
        hand - corresponding hand 
        pass - pass current turn 
        playCard - play card  
        trade - ready up for trade 
        play again - vote to play again 
        see server file for more detail on requests, such as data and formatting needed 
        """ 
        message = msg  # take input 
        self.__client_socket.send(message.encode())  # send message 
        data = self.__client_socket.recv(1024).decode()  # receive response  
        if msg[:4] != "data" and msg != "status" and msg != "turn" and msg[:4] != "hand": 
            print(msg + " >>server response>> " + data) 

        return data 
 

    def close(self): 
        self.__client_socket.close() 
 

    def getSocket(self): 
        return self.__client_socket 
     

    def getPort(self): 
        return self.__port 
     

    def getHost(self): 
        return self.__host 

 

class Card(): 
    def __init__(self,num,suit): 
        self._big = False 
        self._num = num 
        self._suit = suit 
        self._name = str(num) + self._suit 
        self._sprite = pygame.image.load("sprites/" + self._name.lower() + ".png") 
 

        if self._num == "J": 
            self._num = 11 

        if self._num == "Q": 
            self._num = 12 

        if self._num == "K": 
            self._num = 13 

        if self._num == "A": 
            if self._suit == "spades": 
                self._num = 15 

            else: 
                self._num = 14 
        self._num = int(self._num) 

 

    def draw(self,display,x,y): 
        face = pygame.image.load("sprites/front.png") 
        img = self._sprite 

        if self._big: 
            x -= (96*1.5)/8 
            y -= (96*1.5)/8 
            face = pygame.transform.scale_by(face, 1.5) 
            img = pygame.transform.scale_by(img,1.5) 
        display.blit(face,(x,y)) 
        display.blit(img,(x,y)) 

    def getName(self): 
       return self._name 
     

    def getNum(self): 
        return self._num 
     

    def getSuit(self): 
        return self._suit 

    def setBig(self,a): 
        self._big = a 

    def getBig(self): 
        return self._big 

 

class Deck(): 
    def __init__(self): 
        self.newDeck() 
        self.shuffle() 
 
    def newDeck(self): 
        self._arr = [] 

        #create ordered deck of cards starting on diamonds 
        suits = ["diamonds", "clubs", "hearts", "spades"] 

         

        for i in range(13,1,-1): 
            for j in suits: 
                num = str(i) 
                if num == "1": 
                    num = "A" 

                elif num == "11": 
                    num = "J" 

                elif num == "12": 
                    num = "Q" 

                elif num == "13": 
                    num = "K" 

                self._arr.append(Card(num,j)) 

         

    def shuffle(self): 
        self._arr = random.sample(self._arr,len(self._arr)) 

     

    def take(self): 
        #pop the stack, if empty create a new random deck and pop 
        if self.getSize() == 0: 
            self.newDeck() 
            self.shuffle() 

        return self._arr.pop() 

 

    def getSize(self): 
        return len(self._arr) 

 

class Player: 
    def __init__(self,name,win,cardsLeft,title,x,y): 
        self._name = name 
        self._win = win #played all cards? 
        self._cardsLeft = cardsLeft 
        self._title = title #beggar/tycoon etc 
        self.x = x 
        self.y = y 

 

    def playTurn(self,playInst,selectedCards, display, *args): 
        hand = playInst.getHand() 
 
        #get card selected and last card 
        lastCard = playInst.getLastCard() 
        magnitude = int(playInst.getMagnitude()) 
        mouse = pygame.mouse.get_pos() 
        click = pygame.mouse.get_pressed() 

        #collision check for cards and mouse 
        w = 68 
        h = 96 
        x = cardX 
        y = cardY 

 

        if click[2] == True: 
            #deselect card 
            for i in selectedCards: 
                i.setBig(False) 
            selectedCards = [] 

        for i in hand: 
            if x + w > mouse[0] > x and y + h > mouse[1] > y: 
                #card selected 
                i.setBig(True) 

                if click[0] == 1 and i not in selectedCards: 
                    #check whether card playable 
                    if len(lastCard) == 0: 
                        if len(selectedCards) > 0: 
                            if i.getNum() == selectedCards[0].getNum(): 
                                selectedCards.append(i) 

                            else: 
                                selectedCards = [i] 
                        else: 
                            selectedCards.append(i)  

                    #allow selecting of multiple cards of the same number only when start of round or playing double/triples 
                    elif i.getNum() >= lastCard[0].getNum(): 
                        if len(selectedCards) > 0: 
                            if i.getNum() == selectedCards[0].getNum() and len(selectedCards) < magnitude: 
                                selectedCards.append(i) 

                            else: 
                                selectedCards = [i] 
                        else: 
                            selectedCards.append(i) 
            x += cardSpace 

        if selectedCards != None: 
            for i in selectedCards: 
                i.setBig(True) 

        if button("PASS", 375, 550, 150, 50, light_slat, dark_red, click[0], display, playInst.turnPass): 
            return True 

        #play card 
        if button("PLAY", 525, 550, 150, 50, light_slat, dark_red, click[0], display) and len(selectedCards) > 0 : 
            if len(selectedCards) >= int(magnitude) or selectedCards[0].getNum() == 15: 
                for i in selectedCards: 
                    i.setBig(False) 
                    hand.remove(i) 

                playInst.playCard(selectedCards) 
                selectedCards = None 

        return selectedCards 

    def getName(self): 
        return self._name 

    def getCardsLeft(self): 
        return self._cardsLeft 

    def getTitle(self): 
        return self._title 

    def getWin(self): 
        return self._win 

