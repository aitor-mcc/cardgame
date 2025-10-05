import pygame  
import random 
import sys 
import time 
import database 
from datetime import datetime 
import singlePlayer as single 
from functions import * 
from gui import * 
from classes import * 
cardX = 180 
cardY = 450 
cardSpace = 62 
pygame.init() 
 

class Play(single.Play): 

    def __init__(self,server,display,username): 

        self.__turn = 0 

        self.__playerList = []#list of players still in the game 

        self.__drawList = []#list of all players (unchanged once players finish their hand) 

        self.__lastCard = None 

        self.__magnitude = 0 

        self.__id = server.id 

        self.__server = server 

        self.__hand = [] 

        self.__text = "" 

        self.__selectedCards = [] 

        self.__rounds = 4 

        self.__display = display 

        if username != None: 

            self.username = username 

        else: 

            self.username = "player " + str(self.__id) 

        self.__usernames = [] 

 

    def loop(self): 

        #fetch whose turn it is from server 

        data = int(self.__server.sendReceive("turn")) 

        if data >= 0: 

            self.__turn = data 

 

        self.getData() 

        if len(self.__playerList) > int(self.__turn): 
            #check to if it is user's turn 
            #self.__playerList[int(self.__turn)].getName() == "player " + str(self.__id) or  
            if (self.__playerList[int(self.__turn)].getName() == "player " + str(self.__id)) and self.__playerList != []: 
                #fetch data/hand 
                self.getData() 
                if self.__hand == []: 
                    self.__hand = self.fetchHand() 

                player = self.__playerList[self.__turn] 
                #play turn 
                self.__selectedCards = player.playTurn(self,self.__selectedCards, self.__display) 
                if self.__selectedCards == None: 
                    self.__selectedCards = []    
            else: 
                self.__hand = self.fetchHand()      

             

 

    def turnPass(self): 
          self.__server.sendReceive("pass") 
 
    def playCard(self,cards): 
        s = "[" 
        for i in cards: 
            s += i.getName() 
            if i != cards[-1]: 
                s += ";" 
        s += "]" 
        self.__server.sendReceive("playCard," + s)  

    def getLastCard(self): 
        return self.__lastCard 

    def getMagnitude(self): 
        return self.__magnitude 

    def getData(self): 
        data = self.__server.sendReceive("data," + str(self.__id)) 
        if data == "error": 
            return "error"    

        data = data.split(",") 
        if len(data) <= 1: 
            return "error"         

        self.__turn = int(data[0]) 

        #get player data from playerList/drawList 
        list = data[1][1:-1].split("+") 
        self.__playerList = [] 

        buffer = int(self.__id)-1 

        for j in list: 
            i = j.replace("[","").replace("]","").split(";") 
            if len(i) < 6: 
                break 

            if i[1] == "False": 
                i[1] = False 

            else: 
                i[1] = True 
            i[2] = int(i[2]) 
            x = int(i[4]) 
            y = int(i[5]) 

            #change positions depending on client  

            if buffer == 1: 
                if j == list[0]: 
                    x = 700  
                    y = 200  

                elif j == list[1]: 
                    x = 500 
                    y = 400 

                elif j == list[2]: 
                    x = 200 
                    y = 200 

                elif j == list[3]: 
                    x = 500 
                    y = 70 
            self.__playerList.append(Player(i[0],i[1],i[2],i[3],x,y)) 

        list = data[2][1:-1].split("+") 
        self.__drawList = [] 

        for j in list: 
            i = j.replace("[","").replace("]","").split(";")           

            if i[1] == "False":
                i[1] = False 
            else: 
                i[1] = True 

            i[2] = int(i[2]) 
            x = int(i[4]) 
            y = int(i[5])  

            #change positions depending on client  

            if buffer == 1: 
                if j == list[0]: 
                    x = 700  
                    y = 200  

                elif j == list[1]: 
                    x = 500 
                    y = 400 

                elif j == list[2]: 
                    x = 200 
                    y = 200 

                elif j == list[3]: 
                    x = 500 
                    y = 70 
            self.__drawList.append(Player(i[0],i[1],i[2],i[3],x,y)) 
         

        if data[3] == "[None]": 
            self.__lastCard = [] 

        else: 
            self.__lastCard = [] 
            cards = data[3] 
            cards = cards.replace("[","") 
            cards = cards.replace("]","") 
            cards = cards.split(";") 

            for i in cards: 
                var = i.replace(" ","").strip() 
                if var == "": 
                    break 

                count = 1 
                num = var[0] 
                if num == "1": 
                    if var[1] =="0": 
                        num = "10" 
                        count += 1 

                if var[count] == "s": 
                    suit = "spades" 

                elif var[count] == "h": 
                    suit = "hearts" 

                elif var[count] == "c": 
                    suit = "clubs" 

                elif var[count] == "d": 
                    suit = "diamonds" 

                else: 
                    print("data received invalid: Last card data invalid") 
                    suit = "spades" 
                self.__lastCard.append(Card(num,suit)) 

        self.__magnitude = data[4] 
        self.__text = data[5] 
        self.__rounds = data[6] 
        
        #usernames list 
        temp = data[7] 
        temp = temp.replace("[","") 
        temp = temp.replace("]","") 
        temp = temp.split(";") 
        self.__usernames = temp 

        return "success!" 

 

         

     

     

    def fetchHand(self): 
        #get hand from server 
        data = self.__server.sendReceive("hand," + str(self.__id)) 
        if data == "error": 
            print("fetch hand error") 
            return [] 

        elif data == "empty" or data == "cannot complete request: not in game": 
            return [] 

        data = data.split(",") 

 

        arr = [] 
        for i in data: 
            if len(i) < 1: 
                pass 

            else: 
                count = 1 
                num = i[0] 
                suit = "" 
                if i[1] == "0": 
                    count += 1 
                    num += i[1] 

                if i[count] == "c": 
                    suit = "clubs" 

                elif i[count] == "s": 
                    suit = "spades" 

                elif i[count] == "h": 
                    suit = "hearts" 

                elif i[count] == "d": 
                    suit = "diamonds" 

                else: 
                    print("error: invalid suit data for hand") 
                    suit = "spades" 
                arr.append(Card(num,suit))  

        return arr 

     

    def getHand(self): 
        return self.__hand 

    def setHand(self,hand): 
        self.__hand = hand     

    def draw(self): 
        #player stats 
        stats("round: " + str(self.__rounds),30,10,self.__display) 
 

        count = 0 
        #loop through each player 
        for i in self.__drawList: 
            x = i.x  
            y = i.y 

            if i.getName() == "player 1" or i.getName() == "player 2": 
                stats(self.__usernames[count],x,y,self.__display) 

            else: 
                stats(i.getName(),x,y,self.__display) 
            stats("cards left: " + str(i.getCardsLeft()),x,y + 12,self.__display) 
            stats(i.getTitle(),x,y + 24,self.__display) 
            if i.getWin() == True: 
                stats("won!",x,y+36,self.__display) 

            if len(self.__playerList) > self.__turn: 
                player = self.__playerList[self.__turn] 
                phase = self.__server.sendReceive() 
                #draw pointer on current turn 

                if i.getName() == player.getName() and phase == "play": 
                    x = i.x  
                    y = i.y 
                    #turn pointer 
                    buffer = int(self.__id) - 1 
                    pointer = pygame.image.load("sprites/pointer.png") 

                    if count == 0 + buffer: 
                        pointer = pygame.transform.rotate(pointer,270) 

                    elif count == 1 + buffer: 
                        pointer = pygame.transform.rotate(pointer,180) 

                    elif count == 2 + buffer: 
                        pointer = pygame.transform.rotate(pointer,90) 

                    a = 45 
                    if x > 500: 
                        x -= a 

                    elif x < 500: 
                        x += a 

                    else: 
                        x -= 15  

                    if y > 300: 
                        y -= a 

                    else: 
                        y += a 
                    self.__display.blit(pointer,(x,y)) 
                count += 1                   

        if len(self.__playerList) > self.__turn and phase == "play":     
            #cards played 
            x = 530 - len(self.__lastCard)*50 
            for i in self.__lastCard: 
                i.draw(self.__display,x,200) 
                x += 50 

        #deck 
        img = pygame.image.load("sprites/back.png") 
        x = 560 
        y = 200 

        for i in range(32): 
            self.__display.blit(img,(x,y)) 
            y -= 0.1 
            x += 0.1         

 

        #text 
        game_texts(self.__text,500-(len(self.__text)),30,self.__display) 
 

        #player cards 
        y = cardY  
        x = cardX 
        big = []#draw over the rest  
 

        for i in self.__hand: 
            if i.getBig(): 
                big.append([i,x,y]) 
                pass 

            else: 
                i.draw(self.__display,x,y) 
            x += cardSpace 

        for i in big: 
            i[0].draw(self.__display,i[1],i[2]) 
            i[0].setBig(False) 

    def getResult(self): 
        result = self.__drawList[int(self.__id) - 1].getTitle() 
        if result == "": 
            return "beggar" 
        return result 

    def setText(self,text): 
        self.text = text 

    def exit(self): 
        sys.exit() 
 

    def getRounds(self): 
        return self.__rounds