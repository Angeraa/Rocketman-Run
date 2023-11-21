import random
from secrets import randbelow
import sys
import time
import math
import pygame
from pygame.locals import *

beam_files = ["data\LaserBeamBig_V.png", 
              "data\LaserBeamMed_V.png", 
              "data\LaserBeamMed_V.png",
              "data\LaserBeamMed_H.png", 
              "data\LaserBeamBig_H.png"]

#Create classes and otger methods that will be used in the game up here
class Player:
    sprite = pygame.image.load("data\Harry_Porkchop_Falling.png")
    walking_sprites = ["data\Harry_Porkchop_Running_1.png", 
                       "data\Harry_Porkchop_Running_MID1.png", 
                       "data\Harry_Porkchop_Running_MID2.png", 
                       "data\Harry_Porkchop_Running_2.png",
                       "data\Harry_Porkchop_Running_MID2.png",
                       "data\Harry_Porkchop_Running_MID1.png"]
    position = pygame.Vector2()
    position.xy = 230.0 - sprite.get_width()/2, 725.0
    velocity = pygame.Vector2()
    velocity.xy = 0.0, 0.0
    acceleration = 0.3
    frame = 0

class Background:
    def __init__(self):        
        self.sprite = pygame.image.load("data\RocketmanRunBG.png")
        self.sprite = pygame.transform.scale(self.sprite, (1200, 800))
        self.position = 0

class Laser:
    def __init__(self, bottom):
        if bottom:
            file_path = random.choice(beam_files[1:4])
            self.sprite = pygame.image.load(file_path)
            self.position = pygame.Vector2()
            self.position.xy = 2400.0, 725 - self.sprite.get_size()[1]
        else:
            file_path = random.choice(beam_files)
            self.sprite = pygame.image.load(file_path)
            self.position = pygame.Vector2()
            self.position.xy = 2400.0, random.randrange(80, 600 - self.sprite.get_size()[1])

class Coin:
    def __init__(self, position):
        self.sprite = pygame.image.load("data\Coin.png")
        self.position = pygame.Vector2()
        self.position.xy = position[0], position[1]

def clamp(val, min, max):
    if val < min:
        return min
    if val > max:
        return max
    return val

def load_positions(file, line_number): #requires multiple lines so need sperate files or a way to select only certain sections
    with open(file, "r") as file:
        lines = file.readlines()
        line = lines[line_number - 1].split()
        pair_list = [[int(i) for i in pair.split(":")] for pair in line] 
    return pair_list
    
def main():    
    #init pygame
    pygame.init()

    #Creating variables
    DISPLAY_H = 800
    DISPLAY_W = 1200
    mid_x = DISPLAY_W / 2
    mid_y = DISPLAY_H / 2
    WHITE = (255,255,255)
    BLACK = (0,0,0)
    title = True
    font = pygame.font.get_default_font()
    title_words = pygame.image.load("data\MainTitle.png")

    on_ground = True
    dead = False
    scroll_speed = 5.0
    distance = 0.0
    coins_total = 0
    distance_text = pygame.font.Font(font, 32)
    coin_text = pygame.font.Font(font, 32)
    death_text = pygame.font.Font(font, 72)
    coinCount_Sprite = pygame.image.load("data\Coin.png")
    bg = []
    beams = []
    coins = []
    pos_set_1 = load_positions("data\CoinPositions.txt", 1)
    pos_set_2 = load_positions("data\CoinPositions.txt", 2)
    checkpoint = 100
    last_time = time.time()
    interval = 2
    interval_modifier = 5
    delta_interval = 0
    obs_check = 25
    delta_frame = 0
    player_frame_check = 3
    angle = 0

    deathScreen = pygame.Rect(mid_x-400,mid_y-250,800,500)

    def coin_grouping(pattern):
        if pattern == 0:
            for i in pos_set_1:
                coins.append(Coin(i))
        if pattern == 1:
            for i in pos_set_2:
                coins.append(Coin(i))

    player = Player()

    #creating display
    display = pygame.display.set_mode((DISPLAY_W, DISPLAY_H))
    pygame.display.set_caption("Rocket Pack Ride")
    pygame.mouse.set_visible(False)

    #creating background
    for i in range(2):
        bg.append(Background())
    bg[1].position = bg[0].position + 1200
    for o in bg:
        display.blit(o.sprite, (o.position, 0))
    pygame.display.flip()

    #title screen
    while title:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                title = False
        for o in bg:
            display.blit(o.sprite, (o.position, 0))
        
        #display the title
        display.blit(title_words, (mid_x - 300, mid_y - 200))
        
        pygame.display.update()

    #main game
    while True:
        dt = time.time() - last_time
        if not dead:
            delta_interval += dt
        dt *= 60
        last_time = time.time()

        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if keys[K_ESCAPE]:
            pygame.quit()
            sys.exit()
        
        #vertical movement
        if keys[K_UP] and not dead:
            move_up = True
            if player.position.y < 80.0:
                player.velocity.y = 0.0
            else:
                player.position.y += (player.velocity.y*dt) - 1
                player.velocity.y = clamp(player.velocity.y - player.acceleration*dt, -15.0, 10.0) #the clamp is on the negative
        else:
            move_up = False
        
        #gravity
        if move_up == False and player.position.y < 725.0 - player.sprite.get_height():
            player.position.y += player.velocity.y*dt
            player.velocity.y = clamp(player.velocity.y + 0.5*dt, -10.0, 15.0) #clamp is on the positive
        
        
        #the following two blocks check for out of bounds sprites while not moving up
        if player.position.y < 80.0:
            player.position.y = 80.0
            player.velocity.y = 0
        if player.position.y > 725.0 - player.sprite.get_height() and not dead:
            on_ground = True
            player.position.y = 726.0 - player.sprite.get_height()
            player.velocity.y = 0.0
        elif player.position.y > 725.0 - player.sprite.get_height() and dead:
            player.position.y = 724.0 - player.sprite.get_height()
            if player.velocity.y > 2:
                player.velocity.y = -player.velocity.y + 2
            else:
                player.position.y = 750.0 - player.sprite.get_height()
                player.velocity.y = 0

        #adding dt to delta_frame after on-ground was checked
        if on_ground == True and not dead:
            delta_frame += dt
        else:
            delta_frame = 0

        #updating player hitbox
        player_hitbox = pygame.Rect(player.position.x + 20, player.position.y + 2, player.sprite.get_width() - 25, player.sprite.get_height() - 5)
        
        #Checking obsticle spawn interval
        if delta_interval > interval:
            delta_interval = 0
            obs_check = randbelow(50)
            if obs_check < 3:
                coin_grouping(0)
                interval = 5
            elif obs_check < 6:
                coin_grouping(1)
                interval = 6
            elif obs_check >= 5:
                interval = round(random.random() * interval_modifier + 1, 2)
                beams.append(Laser(False))
        
        #checking frame interval
        if delta_frame > player_frame_check:
            delta_frame = 0
            if player.frame < 5:
                player.frame += 1
                if player.frame == 3:
                    player_frame_check = 10
                else:
                    player_frame_check = 3
            else:
                player.frame = 0
                player_frame_check = 10

        #bliting backgrounds
        display.fill(WHITE)
        for o in bg:
            display.blit(o.sprite, (o.position, 0))     
        
        #Bliting player
        if not dead:
            if on_ground: #make walking animation
                player.sprite = pygame.image.load(player.walking_sprites[player.frame])
                display.blit(player.sprite, (player.position.x, player.position.y))
            elif move_up: #Thruster on
                player.sprite = pygame.image.load("data\Harry_Porkchop_Flying.png")
                display.blit(player.sprite, (player.position.x, player.position.y))
            else: #thruster off
                player.sprite = pygame.image.load("data\Harry_Porkchop_Falling.png")
                display.blit(player.sprite, (player.position.x, player.position.y))
        else: #dead sprite here
            player.sprite = pygame.image.load("data\Harry_Porkchop_Dead.png")             
            rotated_image = pygame.transform.rotate(player.sprite, angle)
            player.position.x = 230 - rotated_image.get_width()/2
            display.blit(rotated_image, (player.position.x, player.position.y))
            if player.velocity.y != 0:
                angle -=  0.2 + abs(player.velocity.y / 100)
                if angle < -360:
                    angle = 0
            elif angle > -90 or (-100 > angle > -270) or angle < -280:
                angle -=  0.5

        #bliting distance
        display.blit(distance_text.render(f"Distance: {math.floor(distance)}m", False, BLACK), (10, 45))

        #Blitting number of coins
        display.blit(coinCount_Sprite, (10, 75))
        display.blit(coin_text.render(f": {coins_total}", False, BLACK), (75, 75))

        #blit obsticles and check for collisions
        for beam in beams:
            beam_hitbox = pygame.Rect(beam.position.x + 10, beam.position.y + 7, beam.sprite.get_size()[0] - 20, beam.sprite.get_size()[1] - 14)
            if pygame.Rect.colliderect(beam_hitbox, player_hitbox):
                dead = True
            if beam.position.x < 0 - beam.sprite.get_size()[0]:
                beams.remove(beam)
                del beam
            else:
                beam.position.x -= scroll_speed*dt  
                display.blit(beam.sprite, (beam.position.x, beam.position.y))

        #bliting coins
        for coin in coins:
            coin_hitbox = pygame.Rect(coin.position.x + 4, coin.position.y + 4, 56, 56)
            if pygame.Rect.colliderect(coin_hitbox, player_hitbox):
                coins.remove(coin)
                del coin
                coins_total += 1
            else:
                if coin.position.x < -70:
                    coins.remove(coin)
                    del coin
                else:
                    coin.position.x -= scroll_speed*dt
                    display.blit(coin.sprite, (coin.position.x, coin.position.y))
            
        #reset moving backgrounds if needed   
        bg[0].position -= scroll_speed*dt
        if bg[0].position <= -1200:
            bg[0].position = 0
            beams.append(Laser(True))
        bg[1].position = bg[0].position + 1200
        
        #increasing distance variable
        distance += scroll_speed/400
        if distance > checkpoint:
            checkpoint += 100
            if scroll_speed < 7.5:
                scroll_speed += 0.1
            if interval_modifier > 3:
                interval_modifier -= 0.05

        if dead:
            if scroll_speed > 0:
                scroll_speed -= 0.005
            else:
                scroll_speed = 0

        #when dead, show death screen and wait for restart
        if dead and scroll_speed == 0:
            #add death screen
            pygame.draw.rect(display, (132, 132, 130), deathScreen)
            display.blit(death_text.render("Damn...You Died", False, BLACK), (mid_x-300,mid_y-200))
            display.blit(distance_text.render(f"Distance: {math.floor(distance)}m", False, BLACK), (mid_x-120, mid_y-50))
            display.blit(coinCount_Sprite, (mid_x-70, mid_y-10))
            display.blit(coin_text.render(f": {coins_total}", False, BLACK), (mid_x, mid_y))
            display.blit(distance_text.render("Press Space to Restart", False, BLACK), (mid_x-200, mid_y+50))
            if keys[K_SPACE]:
                on_ground = True
                dead = False
                scroll_speed = 5.0
                distance = 0.0
                coins_total = 0
                for i in bg:
                    del i
                bg = []
                beams = []
                coins = []
                checkpoint = 100
                last_time = time.time()
                interval = 2
                interval_modifier = 5
                delta_interval = 0
                obs_check = 25
                delta_frame = 0
                player_frame_check = 3
                angle = 0
                del player
                player = Player()
                for i in range(2):
                    bg.append(Background())
                bg[1].position = bg[0].position + 1200
                for o in bg:
                    display.blit(o.sprite, (o.position, 0))
                dead = False
        
        on_ground = False
        pygame.display.flip()
        
if __name__ == "__main__": main()   