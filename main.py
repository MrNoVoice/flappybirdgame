import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 600
screen_height = 670

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

#define font 
font = pygame.font.SysFont("Bauhaus 93", 60)

#define color
white = (255, 255, 255)

#define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 2000 #milliseconds (increased to reduce the number of pipes)
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipes = False

#load images
bg = pygame.image.load('D:\\Old Projects  code\\Flappy Bird Game -- CodewithRuss\\backgroundimg.png').convert()
ground_img = pygame.image.load('D:\\Old Projects  code\\Flappy Bird Game -- CodewithRuss\\ground.png').convert()
button_img = pygame.image.load('D:\\Old Projects  code\\Flappy Bird Game -- CodewithRuss\\restart.png').convert()

bird_images = []
for num in range(1, 4):
    img = pygame.image.load(f'D:\\Old Projects  code\\Flappy Bird Game -- CodewithRuss\\bird{num}.png').convert_alpha()
    bird_images.append(img)

pipe_image = pygame.image.load('D:\\Old Projects  code\\Flappy Bird Game -- CodewithRuss\\pipe.png').convert_alpha()
flipped_pipe_image = pygame.transform.flip(pipe_image, False, True)

ground_height = ground_img.get_height()  # Get the height of the ground image

def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

def reset_game():
    global score, game_over, flying, last_pipe
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    game_over = False
    flying = False
    last_pipe = pygame.time.get_ticks() - pipe_frequency
    return score

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = bird_images
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        global flying, game_over
        if flying:
            #gravity
            self.vel += 0.5
            if self.vel > 7:
                self.vel = 7
            if self.rect.bottom < screen_height - ground_height:
                self.rect.y += int(self.vel)

        if not game_over:
            #jump
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -8
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            #handle the animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            #rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        if position == 1:
            self.image = flipped_pipe_image
            self.rect = self.image.get_rect()
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.image = pipe_image
            self.rect = self.image.get_rect()
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False

        #check for mouse pose
        pos = pygame.mouse.get_pos()

        # check for mouse over button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]:
                action = True 

        # draw button
        screen.blit(self.image, self.rect)

        return action

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

#recreate button instance 
button = Button(screen_width // 2 - 65 , screen_height // 2 - 55, button_img)

run = True
while run:
    clock.tick(fps)

    #draw background
    screen.blit(bg, (0, 0))

    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)
    draw_text(str(score), font, white, int(screen_width/2), 20 )

    #score checker 
    if len(pipe_group) > 0 and len(bird_group) > 0:
        if (bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left) \
        and (bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right) \
        and not pass_pipes:
            pass_pipes = True

    if pass_pipes and len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
            score += 1
            pass_pipes = False

    #draw the ground
    screen.blit(ground_img, (ground_scroll, screen_height - ground_height))

    #look for collision
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

    #check if bird has hit the ground
    if flappy.rect.bottom >= screen_height - ground_height:
        game_over = True
        flying = False

    if game_over == False and flying == True:
        #generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        #draw and scroll the ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > ground_img.get_width():
            ground_scroll = 0

        pipe_group.update()

    #check for game over and restart 
    if game_over == True:
        if button.draw():
            game_over = False
            score = reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True

    pygame.display.update()

pygame.quit()
