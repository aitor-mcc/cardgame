import pygame
import random
import sys
import time
import database
from datetime import datetime
import singlePlayer as single
from functions import *
from gui import *
from classes import Card, Deck

cardX = 180
cardY = 450
cardSpace = 62

connection = database.create_connection("sql.sqlite")

pygame.init()
clock = pygame.time.Clock()

background_color = (34, 139, 34)
grey = (220, 220, 220)
black = (0, 0, 0)
green = (0, 200, 0)
red = (255, 0, 0)
light_slat = (119, 136, 153)
dark_slat = (47, 79, 79)
dark_red = (255, 0, 0)
font = pygame.font.SysFont("Arial", 20)
textfont = pygame.font.SysFont('Comic Sans MS', 35)
game_end = pygame.font.SysFont('dejavusans', 100)
roboto = pygame.font.SysFont('roboto', 20)
display_width = 1000
display_height = 600

class Player:
    def __init__(self, name, x=100, y=100):
        self.x = x
        self.y = y
        self._name = name
        self._title = ""  # tycoon/beggar etc
        self._win = False
        self._hand = None

    def setHand(self, hand):
        hand = mergeSort(hand, 0, len(hand) - 1, 0)[::-1]
        self._hand = hand

    def getName(self):
        return self._name

    def getCardsLeft(self):
        return len(self._hand)

    def getHand(self):
        return self._hand

    def getType(self):
        return -1

    def getTitle(self):
        return self._title

    def setTitle(self, a):
        self._title = a

    def getWin(self):
        return self._win

    def setWin(self, a):
        self._win = a

    def playTurn(self, *args):
        pass

    def tradeCards(self):
        cards = []
        if self._title == "tycoon":
            recipient = 3
        elif self._title == "rich":
            recipient = 2
        elif self._title == "poor":
            recipient = 1
        else:
            recipient = 0

        if self._title in ["tycoon", "beggar"]:
            n = 2
        else:
            n = 1

        if self._title in ["tycoon", "rich"]:
            for i in range(1, n + 1):
                cards.append(self._hand[-i])
        else:
            for i in range(n):
                cards.append(self._hand[i])

        for i in cards:
            self._hand.remove(i)

        return [cards, recipient]

    def give(self, card):
        self._hand.append(card)
        self._hand = mergeSort(self._hand, 0, len(self._hand) - 1, 0)[::-1]


class HumanPlayer(Player):
    def getType(self):
        return 0

    def playTurn(self, playInst, selectedCards, display, *args):
        # get card selected
        lastCard = playInst.getLastCard()
        magnitude = playInst.getMagnitude()
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        w = 68
        h = 96
        x = cardX
        y = cardY

        if click[2]:
            for i in selectedCards:
                i.setBig(False)
            selectedCards = []

        for i in self._hand:
            if x + w > mouse[0] > x and y + h > mouse[1] > y:
                i.setBig(True)
                if click[0] and i not in selectedCards:
                    if len(lastCard) == 0:
                        if len(selectedCards) > 0:
                            if i.getNum() == selectedCards[0].getNum():
                                selectedCards.append(i)
                            else:
                                selectedCards = [i]
                        else:
                            selectedCards.append(i)
                    elif i.getNum() >= lastCard[0].getNum():
                        if len(selectedCards) > 0:
                            if i.getNum() == selectedCards[0].getNum() and len(selectedCards) < magnitude:
                                selectedCards.append(i)
                            else:
                                selectedCards = [i]
                        else:
                            selectedCards.append(i)
            x += cardSpace

        if selectedCards is not None:
            for i in selectedCards:
                i.setBig(True)

        if button("PASS", 375, 550, 150, 50, light_slat, dark_red, click[0], display, playInst.turnPass):
            return True

        if button("PLAY", 525, 550, 150, 50, light_slat, dark_red, click[0], display) and len(selectedCards) > 0:
            if len(selectedCards) >= magnitude or selectedCards[0].getNum() == 15:
                for i in selectedCards:
                    i.setBig(False)
                    self._hand.remove(i)
                playInst.playCard(selectedCards)
                selectedCards = None

        return selectedCards


class CpuPlayer(Player):
    def getType(self):
        return 1

    def playTurn(self, playInst, *args):
        hand = self._hand[::-1]
        cards = []
        magnitude = playInst.getMagnitude()
        lastCard = playInst.getLastCard()

        if len(lastCard) == 0:
            n = 1
        else:
            n = lastCard[0].getNum()

        for i in range(len(hand)):
            card = hand[i]
            if card.getNum() >= n:
                cards.append(card)
                if card.getNum() == 15:
                    break
                if i + magnitude < len(hand):
                    for j in range(1, magnitude):
                        if hand[i + j].getNum() == card.getNum():
                            cards.append(hand[i + j])
                        else:
                            cards = []
                            break

            if len(cards) == magnitude:
                break
            else:
                cards = []
        if cards:
            if len(cards) == magnitude or cards[0].getNum() == 15:
                for i in cards:
                    self._hand.remove(i)
                playInst.playCard(cards)
        else:
            playInst.turnPass()


class Play:
    def __init__(self, players, display):
        self.__cards = 9  # num of cards
        self.__players = players
        self.__deck = Deck()
        self.__deck.shuffle()
        self.__playerList = []
        self.__winCount = 0
        self.__titles = ["tycoon", "rich", "poor", "beggar"]
        self.__winOrder = []
        self.__display = display
        self.rounds = 4
        self.__playerList.append(HumanPlayer("player 1", 500, 400))
        x = 200
        y = 200
        for i in range(2, 2 + players - 1):
            self.__playerList.append(CpuPlayer(f"player {i}", x, y))
            x += 300
            if y == 200:
                y = 70
            else:
                y = 200

        self.drawList = self.__playerList.copy()  # player list but doesn't get changed
        self.deal(self.__cards, self.__playerList)
        self.__deck = Deck()
        self.__turn = 0
        self.__prevPlayer = self.__playerList[0]  # player that previously played a card
        self.__lastCard = []

        self.__counter = 0
        self.__text = ""
        self.__passCount = 0  # counts how many people have passed in a row

        self.__selectedCards = []
        self.__magnitude = 1  # whether pairs are played or trios or singles etc....

        self.__phase = "play"
        self.__result = ""

    def takeCard(self):
        return self.__deck.take()

    def deal(self, n, players):
        for i in players:
            l = []
            for j in range(n):
                l.append(self.takeCard())
            i.setHand(l)

    def loop(self):
        if self.__counter == 0:
            if self.__lastCard:
                if self.__lastCard[0].getNum() == 15:
                    self.__lastCard = []
                    self.__passCount = 0
                    self.__magnitude = 1
            if self.__passCount >= len(self.__playerList) - 1:
                self.__lastCard = []
                self.__passCount = 0
                self.__magnitude = 1
                try:
                    self.__turn = self.__playerList.index(self.__prevPlayer)
                except Exception:
                    pass

            player = self.__playerList[self.__turn]
            self.__selectedCards = player.playTurn(self, self.__selectedCards, self.__display)

            if self.__selectedCards is None:
                self.__selectedCards = []

            if self.__turn != 0:
                self.__selectedCards = []
                self.__counter += 1
        else:
            self.__counter += 1
            if self.__counter >= 60:
                self.__counter = 0

    def newRound(self):
        self.__playerList = self.drawList.copy()
        self.__deck = Deck()
        self.__deck.shuffle()
        self.__winCount = 0
        self.__titles = ["tycoon", "rich", "poor", "beggar"]
        self.deal(self.__cards, self.__playerList)
        self.__deck = Deck()
        self.__deck.shuffle()
        self.__turn = 0
        self.__prevPlayer = self.__playerList[0]
        self.__lastCard = []

        self.__counter = 0
        self.__text = "trade!"
        self.__passCount = 0

        self.__selectedCards = []
        self.__magnitude = 1

        for i in self.__playerList:
            i._win = False

        self.__players = len(self.__playerList)

    def tradeCard(self):
        self.__playerList = self.drawList.copy()
        for i in self.__playerList:
            m = i.tradeCards()
            self.giveCards(m[0], self.__winOrder[m[1]])

        self.__text = "play!"
        self.__winOrder = []

    def giveCards(self, cards, recipient):
        for i in cards:
            recipient.give(i)

    def playCard(self, cards):
        self.__text = ""
        card = cards[0]
        self.__passCount = 0

        p = self.__playerList[self.__turn]
        self.__prevPlayer = p

        if p.getCardsLeft() == 0:
            self.__players -= 1
            self.__winCount += 1
            self.__winOrder.append(p)

            if self.__players > 0:
                next = self.__turn + 1
                if next > self.__players:
                    next -= self.__players
                self.__prevPlayer = self.__playerList[next]
            else:
                self.setPhase("end")
                self.rounds -= 1
                if self.rounds == 0:
                    self.__result = self.drawList[0].getTitle()
                    self.setPhase("finish")

            self.__playerList.remove(p)
            self.__turn -= 1
            p.setWin(True)
            p.setTitle(self.__titles[self.__winCount - 1])

        if self.__lastCard:
            if self.__lastCard[0].getNum() == card.getNum():
                self.__turn += 1
                self.__text = "skipped!"

        if not (card.getNum() == 15 and not p.getWin()):
            self.__turn += 1
            if self.__turn >= self.__players:
                self.__turn -= self.__players
        elif card.getNum() == 15:
            self.__text = "Ace of spades!"

        self.__magnitude = len(cards)
        self.__lastCard = cards

    def turnPass(self, *args):
        self.__text = ""
        self.__turn += 1
        self.__passCount += 1
        self.__text = "pass"
        if self.__passCount > 1:
            self.__text += " x" + str(self.__passCount) + "!"
        if self.__turn >= self.__players:
            self.__turn -= self.__players

        return True

    def getLastCard(self):
        return self.__lastCard

    def getMagnitude(self):
        return self.__magnitude

    def draw(self):
        # player stats
        stats("round: " + str(self.rounds), 30, 10, self.__display)
        for i in self.drawList:
            x = i.x
            y = i.y
            stats(i.getName(), x, y, self.__display)
            stats("cards left: " + str(i.getCardsLeft()), x, y + 12, self.__display)
            stats(i.getTitle(), x, y + 24, self.__display)
            if i.getWin():
                stats("won!", x, y + 36, self.__display)

        if len(self.__playerList) > self.__turn:
            x = self.__playerList[self.__turn].x
            y = self.__playerList[self.__turn].y

            # turn pointer
            pointer = pygame.image.load("sprites/pointer.png")
            if x == 500 and y == 400:
                pointer = pygame.transform.rotate(pointer, 270)
            elif x == 200 and y == 200:
                pointer = pygame.transform.rotate(pointer, 180)
            elif x == 500 and y == 70:
                pointer = pygame.transform.rotate(pointer, 90)

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

            self.__display.blit(pointer, (x, y))

            # cards played
            x = 530 - len(self.__lastCard) * 50
            for i in self.__lastCard:
                i.draw(self.__display, x, 200)
                x += 50

        # deck
        img = pygame.image.load("sprites/back.png")
        x = 560
        y = 200
        for i in range(self.__deck.getSize()):
            self.__display.blit(img, (x, y))
            y -= 0.1
            x += 0.1

        # text
        game_texts(self.__text, 500 - (len(self.__text)), 30, self.__display)

        # player cards
        y = cardY
        x = cardX
        big = []  # draw over the rest

        for i in self.drawList[0].getHand():
            if i.getBig():
                big.append([i, x, y])
            i.draw(self.__display, x, y)
            x += cardSpace

        for i in big:
            i[0].draw(self.__display, i[1], i[2])
            i[0].setBig(False)

    def exit(self):
        sys.exit()

    def getPhase(self):
        return self.__phase

    def setPhase(self, phase):
        self.__phase = phase

    def getResult(self):
        return self.__result