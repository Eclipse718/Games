import pygame
import os
import math
import random

pygame.init()

# Ensure you are in the correct directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

screen_width = 500
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))

# Load and scale images
spaceship_image = pygame.transform.scale(pygame.image.load('spaceship.png'), (50, 50))
start_button_image = pygame.transform.scale(pygame.image.load('startButton.png'), (200, 50))
background_image = pygame.transform.scale(pygame.image.load('starry sky background.jpg'), (screen_width, screen_height))
laser_image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load('laser.png'), (20, 20)), 90)
heart_image = pygame.transform.scale(pygame.image.load('heart.png'), (30, 30))
game_over_image = pygame.transform.scale(pygame.image.load('GameOver.png'), (250, 250))
upgraded_ship = pygame.transform.scale(pygame.image.load('upgradedShip.png'), (50, 50))
rotated_upgraded_ship = pygame.transform.rotate(pygame.transform.scale(pygame.image.load('upgradedShip.png'), (50, 50)), 180)
arrow_image_green = pygame.transform.scale(pygame.image.load('Arrow.png'), (50, 50))
upgraded_laser_image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load('upgraded_laser.png'), (20, 20)), 90)
miniGunner_item_image = pygame.transform.scale(pygame.image.load('MiniGunner.png'), (50, 50))
miniGunner_image = pygame.transform.scale(pygame.image.load('MiniGunner.png'), (30, 30))

lasers = []
explosions = []
enemies = []
global background_y
background_y = -screen_height
global background_y_2
background_y_2 = 0

global win_tick
win_tick = 0

global wave
wave = 0
scroll_speed = 0.02

global win_color
global continue_color
win_color = (255, 255, 0)
continue_color = (255, 255, 255)

is_homescreen = True

font = pygame.font.Font('arcadefont.ttf', 72)

global score
score = 0

global health
health = 3

global in_shop
in_shop = False

game_over = False

global win
win = False

global upgraded_ship_purchased
upgraded_ship_purchased = False
global mini_gunner_available
mini_gunner_available = False
global shop_items
shop_items = []
global shop_positions
shop_positions = [] 
global mini_gunners
mini_gunners = []
global insufficient_funds_ticks
insufficient_funds_ticks = 0



class ShopItem:
    def __init__(self, image, price, buy_function):
        self.image = image
        self.price = price
        self.buy_function = buy_function


class Laser:
    def __init__(self, x, y, laser_image):
        self.image = laser_image
        self.x = x
        self.y = y
        self.speed = 1

    def move(self):
        self.y -= self.speed

    def is_collision(self, x, y, width, height):
        return self.x >= x and self.x <= x + width and self.y >= y and self.y <= y + height

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

class Explosion:
    def __init__(self, x, y, width, height, frames):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.frames = frames
        self.image = pygame.image.load('explode.png')
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

    def draw(self):
            screen.blit(self.image, (self.x, self.y))

    def tick(self):
        self.frames -= 1
        if self.frames <= 0:
            explosions.remove(self)

class Player:
    def __init__(self, spaceship_image, laser_blast_image):
        self.spaceship_image = spaceship_image
        self.laser_blast_image = laser_blast_image
        self.spaceship_x = 0
        self.damage = 1

    def upgrade_spaceship(self, upgraded_spaceship_image, upgraded_laser_blast_image):
        self.spaceship_image = upgraded_spaceship_image
        self.laser_blast_image = upgraded_laser_blast_image
        self.damage = 2

    def move_spaceship(self, mouse_x, screen_width):
        self.spaceship_x = mouse_x - self.spaceship_image.get_width() / 2
        if self.spaceship_x < 0 - self.spaceship_image.get_width() / 3:
            self.spaceship_x = 0 - self.spaceship_image.get_width() / 3
        elif self.spaceship_x > screen_width - self.spaceship_image.get_width() * 2 / 3:
            self.spaceship_x = screen_width - self.spaceship_image.get_width() * 2 / 3

    def blit_spaceship(self, screen, screen_height):
        screen.blit(self.spaceship_image, (self.spaceship_x, screen_height - self.spaceship_image.get_height()))
    
    def shoot_laser(self, lasers):
        lasers.append(Laser(self.spaceship_x + self.spaceship_image.get_width() / 2 - 10, screen_height - self.spaceship_image.get_height() - 2, self.laser_blast_image))

class Enemy:
    def __init__(self, x, y):
        self.initial_x = x
        self.x = x
        self.y = y
        self.health = 1
        self.speed = 0.03
        self.amplitude = 25
        self.frequency = 0.002
        self.phase = 0
        self.score_value = 0
        self.damage = 1  

    def move(self):
        self.y += self.speed
        self.x = self.initial_x + self.amplitude * math.sin(self.frequency * self.phase)
        self.phase += 1

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def is_collision(self, x, y, width, height):
        image_rect = self.image.get_rect()
        image_rect.topleft = (self.x, self.y)
        return image_rect.colliderect(pygame.Rect(x, y, width, height))

    def explode(self):
        if self.health <= 0:
            global score
            score += self.score_value
            explosions.append(Explosion(self.x, self.y, self.image.get_width(), self.image.get_height(), 60))
            if self in enemies:
                enemies.remove(self)
    
    def take_damage(self):
        self.health -= player.damage
        if self.health <= 0:
            self.explode()

    def deal_damage(self):
        global health
        health -= self.damage
        enemies.remove(self)


class Grunt(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.transform.scale(pygame.image.load('grunt_image.png'), (50, 50))
        self.health = 1
        self.speed = 0.05
        self.amplitude = 30
        self.frequency = 0.003
        self.score_value = 100


class Greeny(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.transform.scale(pygame.image.load('Greeny.png'), (50, 60))
        self.health = 2
        self.speed = 0.03
        self.amplitude = 40
        self.frequency = 0.001
        self.score_value = 150
        self.damage = 2

class FlyingSaucer(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.transform.scale(pygame.image.load('flying_saucer.png'), (30, 30))
        self.health = 6
        self.speed = 0.1
        self.move_down = True
        self.move_left = False
        self.move_right = False
        self.move_count = 0
        self.score_value = 1000
    
    def move(self):
        if self.move_down:
            self.y += self.speed
            if self.y >= 35:
                self.move_down = False
                self.move_left = True
        elif self.move_left:
            self.x -= self.speed
            if self.x <= 0:
                self.move_left = False
                self.move_right = True
        elif self.move_right:
            self.x += self.speed
            if self.x >= screen_width - self.image.get_width():
                self.move_right = False
                self.move_left = True

class Speeder(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.transform.scale(pygame.transform.rotate(pygame.image.load('speeder.png'), 180), (50, 50))
        self.health = 2
        self.speed = 0.25
        self.move_down = True
        self.move_left = False
        self.move_right = False
        self.score_value = 200

    def move(self):
        if self.move_down:
            self.y += self.speed
            
class Reddy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.transform.scale(pygame.image.load('Reddy.png'), (60, 60))
        self.health = 6
        self.speed = 0.1
        self.amplitude = 50
        self.frequency = 0.002
        self.score_value = 250
        self.damage = 2
        self.tick = random.randint(1400, 2000)  

    def move(self):
        self.y += self.speed
        self.x = self.initial_x + self.amplitude * math.sin(self.frequency * self.phase)
        self.phase += 1
        self.tick -= 1
        if self.tick <= 0:
            self.tick = random.randint(1500, 2000)  
            new_mini_reddy = MiniReddy(self.x, self.y + self.image.get_height())
            enemies.append(new_mini_reddy)  

class MiniReddy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.transform.scale(pygame.image.load('Reddy.png'), (30, 30))
        self.health = 1
        self.speed = .45
        self.amplitude = 0
        self.frequency = 0
        self.score_value = 50
        self.damage = 1

class Ghosty(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.transform.scale(pygame.image.load('Ghosty.png'), (40, 40))
        self.health = 3
        self.speed = 0.12
        self.amplitude = 20
        self.tick = random.randint(600, 800)
        self.invisible = False

    def move(self):
        self.y += self.speed
        self.x = self.initial_x + self.amplitude * math.sin(self.frequency * self.phase)
        self.phase += 1
        self.tick -= 1
        if self.tick <= 0:
            if self.invisible:
                self.image = pygame.transform.scale(pygame.image.load('Ghosty.png'), (40, 40))
                self.invisible = False
            else:
                self.image = pygame.transform.scale(pygame.image.load('Ghosty_invisible.png'), (40, 40))
                self.invisible = True
            self.tick = random.randint(600, 800)
            
class MrGloop(Enemy):
    def __init__(self, x, y, divisions=0):
        super().__init__(x, y)
        scale = {0: (80, 80), 1: (40, 40), 2: (20, 20)}
        self.image = pygame.transform.scale(pygame.image.load('MrGloop.png'), scale[divisions])
        self.divisions = divisions
        
        if self.divisions == 0:
            self.health = 8
            self.damage = 4
            self.score_value = 300
            self.speed = 0.06
        elif self.divisions == 1:
            self.health = 4
            self.damage = 2
            self.score_value = 100
            self.speed = 0.09
        else:
            self.health = 2
            self.damage = 1
            self.score_value = 50
            self.speed = 0.12
        
        self.spawned_divisions = False

    def explode(self):
        super().explode()
        if self.divisions < 2 and not self.spawned_divisions:
            self.spawn_divisions()

    def spawn_divisions(self):
        if not self.spawned_divisions:
            left_x = self.x - self.image.get_width() / 2 - 5
            right_x = self.x + self.image.get_width() / 2 + 5
            enemies.append(MrGloop(left_x, self.y, divisions=self.divisions + 1))
            enemies.append(MrGloop(right_x, self.y, divisions=self.divisions + 1))
            self.spawned_divisions = True

    def take_damage(self):
        super().take_damage()
        if self.health <= 0 and self.divisions < 2 and not self.spawned_divisions:
            self.explode()

class Mothership(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.transform.scale(pygame.image.load('Mothership.png'), (110, 110))
        self.speed = 0.11
        self.tick = 1500
        self.x_direction = 1
        self.y_direction = 1
        self.health = 50
        self.score_value = 1500
        
    def move(self):
        if self.y < 50:
            self.y += self.speed
        else:
            self.x += self.speed * self.x_direction
            if self.x <= 0 or self.x + self.image.get_width() >= 500:
                self.x_direction = -self.x_direction
        self.tick -= 1
        if self.tick <= 0:
            self.tick = 2000
            self.spawn_wave()
                
    def spawn_wave(self):
        if random.randint(1, 6) == 1:
            for i in range(5):
                x = random.randint(0, 500 - 50)  # Grunt
                y = 0
                enemies.append(Grunt(x, y))
        elif random.randint(1, 6) == 2:
            for i in range(4):
                x = random.randint(40, 500 - 90)  # Greeny (40 offset due to movement)
                y = -50
                enemies.append(Greeny(x, y))
        elif random.randint(1, 6) == 3:
            for i in range(5):
                x = random.randint(0, 500 - 50)  # Speeder
                if i == 0 or i == 4:
                    y = -250
                elif i == 1 or i == 3:
                    y = -150
                else:
                    y = -50
                enemies.append(Speeder(x, y))
        elif random.randint(1, 6) == 4:
            for i in range(2):
                x = random.randint(50, 500 - 130)  # Reddy
                y = -50
                enemies.append(Reddy(x, y))
            for i in range(2):
                x = random.randint(150, 500 - 130)  # Reddy (offset to separate the pairs)
                y = -50
                enemies.append(Reddy(x, y))
        elif random.randint(1, 6) == 5:
            for i in range(5):
                x = random.randint(40, 500 - 40)  # Ghosty
                y = 0
                enemies.append(Ghosty(x, y))
        else:
            x = random.randint(120, 500 - 120)  # MrGloop
            enemies.append(MrGloop(x, -20))

def next_wave(wave):
    if wave == 1:
        for i in range(5):
            x = 30 + (i * 100)
            y = 0
            enemies.append(Grunt(x, y))
    elif wave == 2:
        for i in range(5):
            x = 30 + (i * 100)
            y = 0
            enemies.append(Grunt(x, y))
        for i in range(4):
            x = 80 + (i * 100)
            y = -100
            enemies.append(Grunt(x, y))
    elif wave == 3:
        global in_shop
        setup_shop()
        in_shop = True
    elif wave == 4:
        for i in range(5):
            x = 30 + (i * 100)
            y = 0
            enemies.append(Grunt(x, y))
        for i in range(4):
            x = 80 + (i * 100)
            y = -100
            enemies.append(Greeny(x, y))
    elif wave == 5:
        for i in range(5):
            x = 30 + (i * 100)
            y = 0
            enemies.append(Grunt(x, y))
        for i in range(4):
            x = 80 + (i * 100)
            y = -100
            enemies.append(Greeny(x, y))
        enemies.append(FlyingSaucer(50, -50))
        
    elif wave == 6:
        for i in range(3):
            x = 25 + (i * 200)
            y = 0
            enemies.append(Grunt(x, y))
        for i in range(2):
            x = 125 + (i * 200)
            y = -60
            enemies.append(Grunt(x, y))
        for i in range(5):
            x = 25 + (i * 100)
            if i == 0 or i == 4:
                y = -250
            elif i == 1 or i == 3:
                y = -150
            else:
                y = -50
            enemies.append(Speeder(x, y))
        enemies.append(FlyingSaucer(50, -50))
    elif wave == 7:
        setup_shop()
        in_shop = True
    elif wave == 8:
        for i in range(3):
            if i == 0:
                x = 75
            if i == 1:
                x = 225
            if i == 2:
                x = 375
            y = -50
            enemies.append(Reddy(x, y))
        for i in range(5):
            x = 50 + (i * 100)
            y = 0
            enemies.append(Greeny(x, y))
        enemies.append(Speeder(20, -60))
        enemies.append(Speeder(440, -60))
    elif wave == 9:
        for i in range(3):
            if i == 0:
                x = 75
            if i == 1:
                x = 225
            if i == 2:
                x = 375
            y = -50
            enemies.append(Ghosty(x, y))
        for i in range(5):
            x = 50 + (i * 100)
            y = 0
            enemies.append(Greeny(x, y))
        enemies.append(Speeder(20, -60))
        enemies.append(Speeder(440, -60))
    elif wave == 10:
        enemies.append(MrGloop(210, -20))
    elif wave == 11:
        setup_shop()
        in_shop = True
    elif wave == 12:
        enemies.append(Mothership(200, -20))
    elif wave == 13:
        global win, lasers, win_tick, win_color, continue_color
        if(not win):
            lasers = []
            win_tick = 0
            win = True
    elif wave == 14:
        enemies.append(Mothership(random.randint(0, 380), -20))
    elif wave > 14:
        if(wave - 14)%4 == 0:
            setup_shop()
            in_shop = True
        else:
            for i in range(wave - 12):
                enemies.append(Mothership(random.randint(0, 380), -20))

def draw_background():
    global background_y, background_y_2  

    screen.blit(background_image, (0, background_y))
    screen.blit(background_image, (0, background_y_2))

    background_y += scroll_speed
    background_y_2 += scroll_speed  

    if background_y >= 0:
        background_y = -screen_height
    if background_y_2 >= screen_height:
        background_y_2 = 0

class MiniGunner:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0.3
        self.direction = 1
        self.tick = random.randint(1000, 2000)
    
    def move(self):
        if self.x <= 0 or self.x + 30 >= screen_width:
            self.direction *= -1
        self.x += self.direction * self.speed
        self.tick -= 1
        if self.tick <= 0:
            self.fire_laser()
            self.tick = random.randint(1000, 2000)

    def fire_laser(self):
        if(not in_shop):
            lasers.append(Laser(self.x + 15, self.y - 3, laser_image))

    def draw(self):
        screen.blit(miniGunner_image, (self.x, self.y))

class ShopItem:
    def __init__(self, image, price, buy_function, stock):
        self.image = image
        self.price = price
        self.buy_function = buy_function
        self.stock = stock
    def move(self):
        if self.x <= 0 or self.x + 30 >= screen_width:
            self.direction *= -1
        self.x += self.direction * self.speed

    def draw(self):
        screen.blit(miniGunner_image, (self.x, self.y))

class HeartItem(ShopItem):
    def __init__(self, image, price, buy_function, stock):
        super().__init__(image, price, buy_function, stock)

class UpgradedShipItem(ShopItem):
    def __init__(self, image, price, buy_function, stock):
        super().__init__(image, price, buy_function, stock)

class ArrowItem(ShopItem):
    def __init__(self, image, price, buy_function, stock):
        super().__init__(image, price, buy_function, stock)

class MiniGunnerItem(ShopItem):
    def __init__(self, image, price, buy_function, stock):
        super().__init__(image, price, buy_function, stock)

def setup_shop():
    global shop_items, upgraded_ship_purchased, shop_positions, lasers
    heart_item = HeartItem(heart_image, 750, buy_heart, 2)
    arrow_item = ArrowItem(arrow_image_green, 0, buy_arrow, float('inf'))
    shop_items = [heart_item, arrow_item]
    if not upgraded_ship_purchased:
        upgraded_ship_item = UpgradedShipItem(rotated_upgraded_ship, 3500, buy_ship_upgrade, 1)
        shop_items.insert(1, upgraded_ship_item)
    else:
        mini_gunner_item = MiniGunnerItem(miniGunner_item_image, 3000, buy_mini_gunner, 4)
        shop_items.insert(1, mini_gunner_item)
    shop_positions = [(125-(shop_items[0].image.get_width()/2), 250), (250-(shop_items[0].image.get_width()/2), 250) , (375-(shop_items[0].image.get_width()/2), 250)] 
    lasers = []


def create_shop(screen_width, screen_height):
    global wave, health, score, lasers, shop_items, shop_positions, insufficient_funds_ticks, upgraded_ship_purchased
    arcadefont = pygame.font.Font('arcadefont.ttf', 20)
    for i, (item, position) in enumerate(zip(shop_items, shop_positions)):
        screen.blit(item.image, position)
        if item.price > 0 and item.image.get_alpha() == 255:
            price_text = arcadefont.render(str(item.price), True, (255, 255, 255))
            text_rect = price_text.get_rect(center=(position[0] + item.image.get_width() // 2, position[1] + item.image.get_height() + price_text.get_height() // 2))
            screen.blit(price_text, text_rect)

    for i, (item, position) in enumerate(zip(shop_items, shop_positions)):
        item_rect = pygame.Rect(position[0], position[1], item.image.get_width(), item.image.get_height())
        for laser in list(lasers):
            if item_rect.collidepoint(laser.x, laser.y):
                lasers.remove(laser)
                if item.price > score:
                    insufficient_funds(300)
                else:
                    if isinstance(item, HeartItem):
                        item.stock -= 1  
                        if item.stock <= 0:  
                            shop_items.pop(i)  
                            shop_positions.pop(i)
                    elif isinstance(item, UpgradedShipItem):
                        item.stock -= 1
                        if item.stock <= 0:
                            shop_items.pop(i)  
                            shop_positions.pop(i)
                            upgraded_ship_purchased = True
                    elif isinstance(item, MiniGunnerItem):
                        item.stock -= 1
                        if item.stock <= 0:
                            shop_items.pop(i)  
                            shop_positions.pop(i)
                    item.buy_function(score, wave)
                    score -= item.price
                break

    if insufficient_funds_ticks > 0:
        arcadefont = pygame.font.Font('arcadefont.ttf', 18)
        text = arcadefont.render("INSUFFICIENT FUNDS", True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen_width // 2, 60))
        screen.blit(text, text_rect)
        insufficient_funds_ticks -= 1

def insufficient_funds(frames):
    global insufficient_funds_ticks
    insufficient_funds_ticks = frames

def buy_heart(score, wave):
    global health
    health += 1

def buy_ship_upgrade(score, wave):
    global player, upgraded_ship_purchased, shop_items
    player.upgrade_spaceship(upgraded_ship, upgraded_laser_image)

def buy_arrow(score, wave):
    wave += 1
    global in_shop
    in_shop = False
    shop_items = []

def win_screen():
    global win, win_tick, wave, laser, win_color, continue_color
    
    if win_tick == 0:
        win_color = (255, 255, 255)
        continue_color = (255, 255, 0)

    if win_tick % 800 == 0:
        win_color = (255, 255, 255) if win_color == (255, 255, 0) else (255, 255, 0)
        continue_color = (255, 255, 0) if continue_color == (255, 255, 255) else (255, 255, 255)
    win_tick += 1  

    font = pygame.font.Font('arcadefont.ttf', 50)
    win_text = font.render('YOU WIN!!', True, win_color)
    text_rect = win_text.get_rect(center=(250, 200))
    screen.blit(win_text, text_rect)

    font = pygame.font.Font('arcadefont.ttf', 40)
    continue_text = font.render('CONTINUE?', True, continue_color)
    c_text_rect = continue_text.get_rect(center=(250, 325))
    pygame.draw.rect(screen, continue_color, c_text_rect.inflate(10, 10), 2)
    screen.blit(continue_text, c_text_rect)

    for laser in list(lasers):
        if laser.is_collision(c_text_rect.x, c_text_rect.y, c_text_rect.width, c_text_rect.height):
            lasers.remove(laser)
            explosions.append(Explosion(c_text_rect.x, c_text_rect.y, c_text_rect.width, c_text_rect.height, 100))
            wave += 1
            win = False




def buy_mini_gunner(score, wave):
    global mini_gunners
    mini_gunners.append(MiniGunner(screen_width // 2, screen_height - 30))

def always_draw():
    global spaceship_x, is_homescreen, wave, in_shop

    draw_background()
    
    if(win):
        win_screen()

    font = pygame.font.Font('arcadefont.ttf', 18)
    score_text = font.render(f"SCORE: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10)) 
    comma_font = pygame.font.SysFont('Arial', 27, bold = True)
    comma_text = comma_font.render(":", True, (255, 255, 255))  
    screen.blit(comma_text, (102, 3)) 
    
    for enemy in enemies:
        if(enemy.y >= screen_height):
            enemy.deal_damage()
    
    for enemy in enemies:
        enemy.draw()
        
    for mini_gunner in mini_gunners:
        mini_gunner.move()
        mini_gunner.draw()
    
    start_x = 10
    start_y = screen_height - 30

    for i in range(health):
        screen.blit(heart_image, (screen_width - 10 - (20 + 15) * (i + 1), screen_height - 15 - 20))
        
    mouse_x, mouse_y = pygame.mouse.get_pos()
    player.move_spaceship(mouse_x, screen_width)
    player.blit_spaceship(screen, screen_height)

    start_button_x = screen_width / 2 - start_button_image.get_width() / 2
    start_button_y = screen_height / 3 - start_button_image.get_height() / 2

    if is_homescreen:
        screen.blit(start_button_image, (start_button_x, start_button_y))

    if in_shop:
        create_shop(screen_width, screen_height)
    
    for laser in list(lasers):
        laser.move()
        laser.draw()
        if is_homescreen:
            if laser.is_collision(start_button_x, start_button_y, start_button_image.get_width(), start_button_image.get_height()):
                lasers.remove(laser)
                explosions.append(Explosion(start_button_x, start_button_y, start_button_image.get_width(), start_button_image.get_height(), 100))
                is_homescreen = False
                next_wave(1)

    for explosion in list(explosions):
        explosion.draw()
        explosion.tick()

    if len(enemies) == 0 and not is_homescreen and not in_shop and not win:
        wave += 1
        next_wave(wave)
    
    pygame.display.update()




player = Player(spaceship_image, laser_image)
running = True
while running:
    
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    if health <= 0:
        game_over = True

    if game_over:
        screen.fill((0,0,0))
        game_over_rect = game_over_image.get_rect()
        game_over_rect.center = (screen_width // 2+10, int(screen_height * 1/3)+50)
        screen.blit(game_over_image, game_over_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and (event.button == 1 or event.button == 3):
                pygame.QUIT()
        pygame.display.update()
    else:

        always_draw()
        for enemy in list(enemies):
            enemy.move()
            enemy.draw()
            for laser in list(lasers):
                if enemy.y+enemy.image.get_height() > 0 and enemy.y < screen_height:
                    if laser.x > enemy.x and laser.x < enemy.x + enemy.image.get_width():
                        if laser.y > enemy.y and laser.y < enemy.y + enemy.image.get_height():
                            if not (isinstance(enemy, Ghosty) and enemy.invisible): 
                                lasers.remove(laser)
                                enemy.take_damage()

                        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and (event.button == 1 or event.button == 3):
                player.shoot_laser(lasers)