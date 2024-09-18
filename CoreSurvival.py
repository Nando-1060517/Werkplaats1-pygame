import math
import pygame
import pygame_gui
import random

pygame.init()

#region variables
#main loop
running = True
display_info = pygame.display.Info()
screen = pygame.display.set_mode(pygame.Vector2(display_info.current_w, display_info.current_h))
clock = pygame.time.Clock()

player_coins = 0
player_wood = 0
player_stone = 0

items_list = []

#pos
center = pygame.Vector2(display_info.current_w / 2, display_info.current_h / 2)
random_range_x = 700
random_range_y = 350

#UI
UI_Manager = pygame_gui.UIManager((display_info.current_w, display_info.current_h))
UI_items = pygame_gui.elements.UITextBox('', pygame.Rect(0, 0, 300, 100), UI_Manager)
UI_pos = pygame_gui.elements.UITextBox('', pygame.Rect(300, 0, 300, 100), UI_Manager)

TIMER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, 500)
frame = 0

#region Image import
player_img = pygame.image.load('Sprites/Player/player_stat.png').convert_alpha()
enemy_img = pygame.image.load('Sprites/Enemy/enemy_stat.png').convert_alpha()
#haven't made a bullet img yet
bullet_img = pygame.image.load('Sprites/Items/coin.png')
coin_img = pygame.image.load('Sprites/Items/coin.png').convert_alpha()
#endregion
#endregion

#region Classes and functions
def random_pos():
    return pygame.Vector2(center.x + random.randint(-random_range_x, random_range_x), center.y + random.randint(-random_range_y, random_range_y))

class Player:
    def __init__(self):
        #import
        self.image = player_img

        #base variables
        self.speed = 10

        #pos
        self.move = pygame.Vector2(0, 0)
        self.pos = pygame.Vector2(center.x, center.y)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.image.width, self.image.height)

    def move_pos(self):
        self.pos.x += self.move.x * self.speed
        self.pos.y += self.move.y * self.speed
        self.rect.center = (self.pos.x, self.pos.y)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.move.x = (keys[pygame.K_d] - keys[pygame.K_a])
        self.move.y = (keys[pygame.K_s] - keys[pygame.K_w])

    def collision(self):
        for item in items_list:
            collided = self.rect.colliderect(item)
            if collided:
                items_list.remove(item)

    def draw(self):
        pygame.draw.rect(screen, 'red', self.rect, 5) #border
        screen.blit(self.image, self.rect) #img

    def manager(self):
        self.handle_input()
        self.move_pos()
        self.draw()
        self.collision()

#region Item Classes
class Item:
    def __init__(self):
        self.pos = random_pos()
        self.coin_img = coin_img
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.coin_img.get_width(), self.coin_img.get_height())

class Coins(Item):
    def draw(self):
        pygame.draw.rect(screen, 'red', self.rect, 5)
        screen.blit(self.coin_img, self.pos)

class Wood(Item):
    def draw(self):
        pygame.draw.rect(screen, 'red', self.rect, 5)
        screen.blit(self.coin_img, self.pos)

class Stone(Item):
    def draw(self):
        pygame.draw.rect(screen, 'red', self.rect, 5)
        screen.blit(self.coin_img, self.pos)

for _ in range(10):
    items_list.append(Stone())
    items_list.append(Wood())
    items_list.append(Coins())

def draw_items():
    for item in items_list:
        item.draw()
#endregion

class Enemy:
    def __init__(self):
        #Gets image and scales it down and add rot
        self.original_image = enemy_img
        self.image = self.original_image
        self.image = pygame.transform.rotate(self.image, 0)

        #Get pos
        self.current_pos = random_pos()
        self.rect = pygame.Rect(self.current_pos.x, self.current_pos.y, 1, 1)

        #enemy base stats
        self.enemy_health = 100

    def draw(self):
        #Change this so instead of check player pos compared to enemy, rotate enemy ONLY when chasing
        screen.blit(self.image, self.rect)

    def rot_enemy(self, target_pos):
        #get player pos and change to angle
        direction = pygame.Vector2(target_pos) - pygame.Vector2(self.rect.center)
        angle = math.degrees(math.atan2(direction.y, direction.x))

        #convert img rot to face towards player with offset since wrong front plane
        offset = -90
        self.image = pygame.transform.rotate(self.original_image, -angle + offset)
        self.rect = self.image.get_rect(center=self.rect.center)

    def move_towards(self, target_pos):
        current_pos = pygame.math.Vector2(self.rect.x, self.rect.y)
        distance = current_pos.distance_to(target_pos)
        max_dist = 250
        min_dist = 50
        direction = target_pos - current_pos

        try:
            direction.normalize_ip()
        except ValueError:
            return "Cant normalize vector of zero"

        if distance <= max_dist:
            if distance <= min_dist:
                return
            else:
                self.rot_enemy(target_pos)
                self.rect.topleft += direction * 5

    def manager(self, target_pos):
        self.draw()
        self.move_towards(target_pos)
#endregion

#region --- initialization ---
#region initializing enemies
enemy_amount = 10
enemy_list = [Enemy() for enemies in range(enemy_amount)]
#endregion

#region initializing player
player = Player()
#endregion
#endregion

#region Main loop
while running:
    #region event loop
    #check for exit and refresh screen by filling with background
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == TIMER_EVENT:
            if frame == 3:
                frame = 0
            else: frame += 1
    screen.fill('green')
    #endregion

    #region Objects
    player.manager()
    draw_items()

    for enemies in enemy_list:
        Enemy.manager(enemies, player.pos)
    #endregion

    #region UI
    UI_items.set_text(f'Coins: {player_coins}\nWood: {player_wood}\nStone: {player_stone}')
    UI_pos.set_text(f'posX: {player.pos.x}\nPosY: {player.pos.y}')
    UI_Manager.update(clock.tick(60)/1000.0)
    UI_Manager.draw_ui(screen)
    #endregion

    #region Refresh screen and set fps
    pygame.display.flip()
    clock.tick(60)
    #endregion
#endregion

#Quit if main loop breaks
pygame.quit()