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
import multiplayer as multi 
 

#randomize seed 
s = random.randint(0,500) 
random.seed(s) 

connection = database.create_connection("sql.sqlite") 
pygame.init() 
clock = pygame.time.Clock() 
 

#pygame variables 
background_color = (34,139,34) 
grey = (220,220,220) 
black = (0,0,0) 
green = (0, 200, 0) 
red = (255,0,0) 
light_slat = (119,136,153) 
dark_slat = (47, 79, 79) 
dark_red = (255, 0, 0) 
font = pygame.font.SysFont("Arial", 20) 
textfont = pygame.font.SysFont('Comic Sans MS', 35) 
game_end = pygame.font.SysFont('dejavusans', 100) 
roboto = pygame.font.SysFont('roboto', 20) 
display_width = 1000 
display_height = 600 
gameDisplay = pygame.display.set_mode((display_width,display_height)) 
gameDisplay.fill(background_color) 
cardX = 180 
cardY = 450 
cardSpace = 62 

 

#menu functions 
def menu(connected): 
    game_texts("TYCOON!", 500, 50,gameDisplay) 
    if connected == False: 
        if button("CONNECT", 430, 120, 150, 50, light_slat, dark_red, click, gameDisplay): 
            return "join server" 

    else: 
        if button("MULTIPLAYER", 430, 120, 150, 50, light_slat, dark_red, click, gameDisplay): 
            server.sendReceive("ready") 
            return "wait"      

        if button("CREATE ACCOUNT", 430, 260, 150, 50, light_slat,dark_red, click, gameDisplay): 
            return "create"       

        if button("LOGIN", 430, 330, 150, 50, light_slat,dark_red, click, gameDisplay): 
            return "login" 

        if button("STATS",430, 400, 150, 50, light_slat,dark_red, click, gameDisplay): 
            return "stats" 

        if button("LEADERBOARD", 430, 470, 150, 50, light_slat, dark_red, click, gameDisplay): 
            return "leaderboard" 

    if button("SINGLE PLAYER", 430, 190, 150, 50, light_slat, dark_red, click, gameDisplay): 
            return "single player"    

    if button("EXIT", 430, 540, 150, 50, light_slat, dark_red, click, gameDisplay): 
        sys.exit() 


    return "menu" 

 

def finishScreen(text): 
    game_texts(text, 500, 200,gameDisplay) 
    if button("NEW ROUND", 430, 300, 150, 50, light_slat, dark_red, click, gameDisplay): 
        try: 
            server.sendReceive("play again") 
            return "wait" 

        except: 
            return "single player" 

     

    if button("MENU",430, 370, 150, 50, light_slat, dark_red, click, gameDisplay): 
        #checks if game is multiplayer or singleplayer 
        try: 
            server.sendReceive("exit") 
        except: 
            pass 

        return "menu" 

    if button("EXIT", 430, 440, 150, 50, light_slat, dark_red, click, gameDisplay): 
        sys.exit() 


    return "finish" 

 

def createAccount(box,box2): 
    inputs = pygame.event.get() 
    click = False 

    for e in inputs: 
        if e.type == pygame.MOUSEBUTTONDOWN: 
            click = True 

    if button("RETURN", 430, 540, 150, 50, light_slat, dark_red, click, gameDisplay): 
        return "menu" 

    game_texts("create account",480,150,gameDisplay) 
    game_texts("username:",480,200,gameDisplay) 
    game_texts("password:",480,280,gameDisplay) 
    box.draw(gameDisplay) 
    box2.draw(gameDisplay) 


    if box.handle_event(inputs) or box2.handle_event(inputs): 
        if box2.text != "" and box.text != "": 
            a = server.sendReceive("create,"+box.text+";"+box2.text) 
            if a != "failed": 
                return "menu" 

            else: 
                import ctypes 
                ctypes.windll.user32.MessageBoxW(0, "Username taken", "error", 1) 

    
    box.update() 
    box2.update() 
    return "create" 

 

def login(box,box2): 
    inputs = pygame.event.get() 
    click = False 

    for e in inputs: 
        if e.type == pygame.MOUSEBUTTONDOWN: 
            click = True 

    if button("RETURN", 430, 540, 150, 50, light_slat, dark_red, click, gameDisplay): 
        return "menu" 

    game_texts("login",480,150,gameDisplay) 
    game_texts("username:",480,200,gameDisplay) 
    game_texts("password:",480,280,gameDisplay) 
    box.draw(gameDisplay) 
    box2.draw(gameDisplay) 

    global user, username, server   
    if box.handle_event(inputs) or box2.handle_event(inputs): 
        var = server.sendReceive("login,"+str(box.text)+";"+str(box2.text)+";"+str(server.id)) 
        if var == "error": 
            import ctypes 
            ctypes.windll.user32.MessageBoxW(0, "User Not Found", "error", 1) 
            box.text = "" 

        else: 
            user = var 
            username = str(box.text) 
            return "menu" 

    box.update() 
    box2.update() 
    return "login" 

 

def joinServer(box, user): 
    game_texts("Enter IP",480,200,gameDisplay) 
    box.draw(gameDisplay) 
    inputs = pygame.event.get() 
    click = False 

    for e in inputs: 
        if e.type == pygame.MOUSEBUTTONDOWN: 
            click = True 

 

    if box.handle_event(inputs) == True: 
        global server 

        try: 
            gameDisplay.fill(background_color) 
            game_texts("connecting...",480,250,gameDisplay) 
            pygame.display.flip() 
            server = conn(user,box.text) 
            return True 

        except: 
            import ctypes 
            ctypes.windll.user32.MessageBoxW(0, "Game Not Found", "error", 1) 
            box.text = "" 
            box.update() 

 

    if button("RETURN", 410, 300, 150, 50, light_slat, dark_red, click, gameDisplay): 
        return "menu" 

 

    box.update() 
    return False 

 

 

def statsPage(): 
    if user == None or connected == False: 
        game_texts("service unavailable!",480,200,gameDisplay) 
        if button("RETURN", 430, 370, 150, 50, light_slat, dark_red, click, gameDisplay): 
            return "menu" 

    else: 
        a = server.sendReceive("stats," + str(user)) 
        a = a.split(",") 
        game_texts("STATS",480,100,gameDisplay) 
        game_texts("games played: " + str(a[0]),480,170,gameDisplay) 
        game_texts("tycoon: " + str(a[1]),480,240,gameDisplay) 
        game_texts("rich man: " + str(a[2]),480,300,gameDisplay) 
        game_texts("poor man: " + str(a[3]),480,360,gameDisplay) 
        game_texts("beggar: " + str(a[4]),480,420,gameDisplay) 
        game_texts("points: " + str(a[5]),480,480,gameDisplay) 
        if button("RETURN", 430, 540, 150, 50, light_slat, dark_red, click,gameDisplay): 
            return "menu" 
    return "stats" 

 

def leaderboard(a): 
    x = 500 
    y = 100 
    rank = 0 
    for i in a: 
        rank += 1 
        stats("#" + str(rank) + " " +  str(i[2]) + ": " + str(i[0]) + " points",x,y,gameDisplay) 
        y += 20 

 

    if button("RETURN", 430, 370, 150, 50, light_slat, dark_red, click, gameDisplay): 
        return "menu" 

    return "leaderboard" 

 

def wait(): 
    game_texts("waiting for players...",480,100,gameDisplay) 
    status = server.sendReceive() 
    if status == "play": 
        return "play" 
     
    return "wait" 

 
global phase 
running = True 
phase = "menu" 
result = "" 
global rounds 
global user, username 
user = None 
username = None 
click = False 
global connected 
connected = False 

 

while running: 
    click = False 
    gameDisplay.fill(background_color) 
    space = False 
    #display username 
    if user != None: 
        stats("playing as: " + str(username),603,10,gameDisplay) 

 

    if phase != "create" and phase != "login" and phase != "join game" and phase != "join server": 
        #get mouse inputs 
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: 
                running = False 

            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_SPACE and phase == "play": 
                    space = True 
                    if game.turn != 0: 
                        game.counter = 0      

            if event.type == pygame.MOUSEBUTTONDOWN: 
                click = True 

     

    #deal with the different game phases 
    if phase == "play" or phase == "trade" or phase == "deal" or phase == "end" or phase == "trade wait" or phase == "single player":      
        button("EXIT", 15, 500, 150, 50, light_slat, dark_red, click, gameDisplay, game.exit) 
        if phase == "play": 
            temp = server.sendReceive() 
            if temp == "play": 
                game.loop() 
            else: 
                phase = temp 

        if phase == "single player": 
            if game.getPhase() == "play": 
                game.loop() 

            elif game.getPhase() == "end": 
                if button("NEXT ROUND", 15, 430, 150, 50, light_slat, dark_red,click, gameDisplay): 
                    game.setPhase("deal") 

 

            elif game.getPhase() == "deal": 
                game.newRound() 
                game.setPhase("trade") 

            elif game.getPhase() == "trade": 

                if button("TRADE", 440, 550, 150, 50, light_slat, dark_red,click,gameDisplay): 
                    game.tradeCard() 
                    game.setPhase("play") 

 

            if game.getPhase() == "finish": 
                phase = "finish" 

        elif phase == "end": 
            if button("NEXT ROUND", 15, 430, 150, 50, light_slat, dark_red, click, gameDisplay): 
                phase = "deal" 

 

        elif phase == "trade": 
            game.setText("New Round!") 
            game.setHand(game.fetchHand()) 

            if button("TRADE", 440, 550, 150, 50, light_slat, dark_red, click, gameDisplay): 
                server.sendReceive("trade") 
                phase = "trade wait" 

                 

         

        elif phase == "trade wait": 
            game.setText("waiting for other players!") 
            temp = server.sendReceive("status") 

            if temp != "trade": 
                phase = temp  
            game.setHand(game.fetchHand()) 
 
        game.draw() 

 

    elif phase == "menu": 
        phase = menu(connected) 
        if phase == "play": 
            rounds = 4 

        if phase == "create" or phase == "login" or phase == "join game" or phase == "join server": 
            #create input boxes 
            box = InputBox(380, 232, 140, 32) 
            if phase != "join game": 
                box2 = InputBox(380,304,140,32) 

 

        if phase == "leaderboard": 
            #fetch data from server 
            copy = server.sendReceive("leaderboard") 
            copy = copy.split(";") 
            arr = [] 
            for i in copy: 

                if len(i) == 0: 
                    break 

                else: 
                    var = i.replace("[","") 
                    var = var.replace("]","") 
                    arr.append(var.split(",")) 

 

        if phase == "single player": 
            game = single.Play(4,gameDisplay) 
            rounds = 4 

 

    elif phase == "finish": 
        phase = finishScreen("You placed " + str(game.getResult()) + "!")     

        if phase == "single player": 
            game = single.Play(4,gameDisplay) 

        elif phase != "finish" and phase != "menu": 
            game = multi.Play(server,gameDisplay,username) 
            rounds = 4 
 

    elif phase == "create": 
        phase = createAccount(box,box2) 

    elif phase == "login": 
        phase = login(box,box2) 

 

    elif phase == "stats": 
        phase = statsPage() 

    elif phase == "leaderboard": 
        phase = leaderboard(arr) 

 

    elif phase == "wait": 
        phase = wait() 

        if phase == "play": 
            game = multi.Play(server,gameDisplay,username) 
            rounds = 4 

 

    elif phase == "join server": 
        connected = joinServer(box, user) 
        if connected == "menu": 
            phase = "menu" 
            connected = False 
        elif connected: 
            phase = "menu" 

     

    pygame.display.flip()