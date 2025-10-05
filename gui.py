#functions for graphical user interface 
import pygame  
import sys 
pygame.init() 

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
 

###text object render 
def text_objects(text, font): 
    textSurface = font.render(text, True, black) 
    return textSurface, textSurface.get_rect() 

 

def end_text_objects(text, font, color): 
    textSurface = font.render(text, True, color) 
    return textSurface, textSurface.get_rect() 

 

#game text display 
def game_texts(text, x, y, display): 
    TextSurf, TextRect = text_objects(text, textfont) 
    TextRect.center = (x, y) 
    display.blit(TextSurf, TextRect) 
 
def game_finish(text, x, y,display, color): 
    TextSurf, TextRect = end_text_objects(text, game_end, color) 
    TextRect.center = (x, y) 
    display.blit(TextSurf, TextRect)     

def stats(text, x, y,display, color = black): 
    TextSurf, TextRect = end_text_objects(text, roboto, color) 
    TextRect.center = (x, y) 
    display.blit(TextSurf, TextRect) 

        
#button display 
def button(msg, x, y, w, h, ic, ac, click, display, action=None): 
    mouse = pygame.mouse.get_pos() 

    if x + w > mouse[0] > x and y + h > mouse[1] > y: 
        pygame.draw.rect(display, ac, (x, y, w, h)) 
        if click == True: 
            pygame.event.clear() 
            if action == None: 
                return True 

            else: 
                action() 

             

    else: 
        pygame.draw.rect(display, ic, (x, y, w, h)) 

 

    TextSurf, TextRect = text_objects(msg, font) 
    TextRect.center = ((x + (w/2)), (y + (h/2))) 
    display.blit(TextSurf, TextRect) 

 
COLOR_INACTIVE = pygame.Color('grey') 
COLOR_ACTIVE = pygame.Color('black') 
FONT = pygame.font.Font(None, 32) 

 

class InputBox: 
    def __init__(self, x, y, w, h, text=''): 
        self.rect = pygame.Rect(x, y, w, h) 
        self.color = COLOR_INACTIVE 
        self.text = text 
        self.txt_surface = FONT.render(text, True, self.color) 
        self.active = False 

    def handle_event(self,events): 
        if pygame.mouse.get_pressed()[0] == 1: 
            # If the user clicked on the input_box rect. 
            if self.rect.collidepoint(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]): 
                # Toggle the active variable. 
                self.active = True 

            else: 
                self.active = False 

            # Change the current color of the input box. 
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE       
      

        for event in events: 
            if event.type == pygame.QUIT: 
                sys.exit() 

            if event.type == pygame.KEYDOWN: 
                if self.active: 
                    if event.key == pygame.K_RETURN: 
                        return True 
                        self.text = '' 

                         

                    elif event.key == pygame.K_BACKSPACE: 
                        self.text = self.text[:-1] 
                    else: 
                        self.text += event.unicode 
                    # Re-render the text. 
                    self.txt_surface = FONT.render(self.text, True, self.color) 

        return False 
 

    def update(self): 
        # Resize the box if the text is too long. 
        width = max(200, self.txt_surface.get_width()+10) 
        self.rect.w = width 

    def draw(self, screen): 
        # Blit the text. 
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5)) 
        # Blit the rect. 
        pygame.draw.rect(screen, self.color, self.rect, 2) 

    def getActive(self): 
        return self.active