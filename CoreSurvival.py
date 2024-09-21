import math
import pygame
import pygame_gui
import random

pygame.init()

#region --- variables ---
#main loop
running = True
display_info = pygame.display.Info()
screen = pygame.display.set_mode(pygame.Vector2(display_info.current_w, display_info.current_h))
clock = pygame.time.Clock()

player_coins = 0
player_wood = 0
player_stone = 0

items_list = []
bullet_list = []
enemy_list = []

#pos
center = pygame.Vector2(display_info.current_w / 2, display_info.current_h / 2)
random_range_x = 700
random_range_y = 350

#UI
UI_Manager = pygame_gui.UIManager((display_info.current_w, display_info.current_h))
UI_items = pygame_gui.elements.UITextBox('', pygame.Rect(0, 0, 300, 100), UI_Manager)
UI_pos = pygame_gui.elements.UITextBox('', pygame.Rect(300, 0, 300, 100), UI_Manager)
UI_mouse_pos = pygame_gui.elements.UITextBox('', pygame.Rect(0, 0, 100, 75))

TIMER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, 500)
frame = 0

#region Image import

def scale_image(img, image_scale):
    scaled = pygame.Vector2(img.get_width() * image_scale, img.get_height() * image_scale)
    scaled_img = pygame.transform.scale(img, scaled)
    return scaled_img

IMAGE_OFFSET = -90
idle_player_image = pygame.image.load('Sprites/Player/player_stat.png').convert_alpha()
shooting_player_image = pygame.image.load('Sprites/Player/player_aim.png').convert_alpha()

enemy_img = pygame.image.load('Sprites/Enemy/enemy_stat.png').convert_alpha()
bullet_img = scale_image(pygame.image.load('Sprites/Items/bullet.png').convert_alpha(), 0.3)
coin_img = pygame.image.load('Sprites/Items/coin.png').convert_alpha()
#endregion
#endregion

#region --- Classes and functions ---

def random_pos():
    return pygame.Vector2(center.x + random.randint(-random_range_x, random_range_x), center.y + random.randint(-random_range_y, random_range_y))

def get_mouse_pos():
    pos = pygame.mouse.get_pos()
    return pos

def get_direction(target, current):
    return pygame.Vector2(target) - current

def rotate_img(target_pos, current_pos, offset):
    # get angle by taking direction converting that in radians and then the radian to degrees
    # offset want sprites zijn richting boven gemaakt terwijl default rechts is

    direction = get_direction(target_pos, current_pos)
    # calculate direction by subtracting current pos from mouse pos
    # mouse_pos [1500, 700] - current_pos [700, 450] = direction [800, 250]

    angle = math.degrees(math.atan2(direction.y, direction.x))
    # [direction.y / direction.x] [250 / 800] = arc tangent is 0.3125
    # 0.3125 * (180 / pi) = angle is 17,9 graden

    return -angle + offset

class Player:
    def __init__(self):
        self.speed = 10

        self.original_idle_img = idle_player_image
        self.idle_img = self.original_idle_img

        self.original_shooting_img = shooting_player_image
        self.shooting_img = self.original_shooting_img

        self.current_state = 'idle'
        self.current_image = self.idle_img
        self.current_original_image = self.original_idle_img

        #pos
        self.move = pygame.Vector2(0, 0)
        self.pos = pygame.Vector2(center.x, center.y)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.current_original_image.get_width(), self.current_original_image.get_height())

    def move_pos(self):
        self.pos.x += self.move.x * self.speed
        self.pos.y += self.move.y * self.speed
        self.rect.center = (self.pos.x, self.pos.y)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if pygame.key.get_just_pressed()[pygame.K_SPACE]:
            bullet_list.append(Bullet())
        self.move.x = (keys[pygame.K_d] - keys[pygame.K_a])
        self.move.y = (keys[pygame.K_s] - keys[pygame.K_w])

    def collision(self):
        for item in items_list:
            collided = self.rect.colliderect(item)
            if collided:
                items_list.remove(item)

    def draw(self):
        pygame.draw.rect(screen, 'red', self.rect, 5)
        screen.blit(self.current_image, (
        self.rect.centerx - self.current_image.get_width() / 2, self.rect.centery - self.current_image.get_height() / 2))

    def manager(self):
        self.handle_input()

        if self.move:
            self.current_state = 'shooting'
            self.current_original_image = self.original_shooting_img
            self.current_image = self.shooting_img
        else:
            self.current_state = 'idle'
            self.current_original_image = self.original_idle_img
            self.current_image = self.idle_img

        self.move_pos()
        self.current_image = pygame.transform.rotate(self.current_image, rotate_img(get_mouse_pos(), self.rect.center, IMAGE_OFFSET))
        self.draw()
        self.collision()

class Bullet:
    def __init__(self):
        self.is_alive = True
        self.speed = 5

        self.original_image = bullet_img
        self.image = self.original_image

        self.rect = self.original_image.get_rect()
        self.rect.center = player.rect.center

        self.direction = get_direction(get_mouse_pos(), self.rect.center)
        print(f'mousepos: {get_mouse_pos()} - current_pos: {self.rect.center} = direction: {self.direction}')
        self.direction.normalize_ip()
        print(f'normalized direciton: {self.direction}')
        self.image = pygame.transform.rotate(self.original_image, rotate_img(get_mouse_pos(), self.rect.center, IMAGE_OFFSET))

    def move_self(self):
        #print(self.rect.center)
        self.rect.center += self.direction * self.speed
        #self.rect.center = [x, y]
        #self.target_pos = [mouse_pos [x, y], []]
        #self.speed = [int speed = 5]

    def collision(self):
        for enemy in enemy_list:
            collided = self.rect.colliderect(enemy)
            if collided:
                enemy_list.remove(enemy)
                self.is_alive = False
            if self.rect.x <= 0 or self.rect.x >= display_info.current_w or self.rect.y <= 0 or self.rect.y > display_info.current_h:
                for bul in bullet_list:
                    print(f'[{bullet_list.index(bul)}]: {bul.rect}')
                self.is_alive = False

    def draw(self):
        pygame.draw.rect(screen, 'red', self.rect, 2) #border
        screen.blit(self.image, self.rect)

    def manager(self):
        self.move_self()
        self.collision()
        self.draw()

class Enemy:
    def __init__(self):
        self.max_dist = 250
        self.min_dist = 50
        self.original_image = enemy_img
        self.image = self.original_image

        self.current_pos = random_pos()
        self.rect = pygame.Rect(self.current_pos.x, self.current_pos.y, self.image.width, self.image.height)

        #enemy base stats
        self.enemy_health = 100

    def rot_enemy(self, target_pos):
        direction = pygame.Vector2(target_pos) - pygame.Vector2(self.rect.center)
        angle = math.degrees(math.atan2(direction.y, direction.x))

        #convert img rot to face towards player with offset since wrong front plane
        offset = -90
        self.image = pygame.transform.rotate(self.original_image, -angle + offset)
        self.rect = self.image.get_rect(center=self.rect.center)

    def move_towards(self, target_pos):
        current_pos = pygame.math.Vector2(self.rect.x, self.rect.y)
        distance = current_pos.distance_to(target_pos)
        direction = target_pos - current_pos

        try:
            direction.normalize_ip()
        except ValueError:
            return "Cant normalize vector of zero"

        if distance <= self.max_dist:
            if distance <= self.min_dist:
                return
            else:
                self.rot_enemy(target_pos)
                self.rect.topleft += direction * 5

    def draw(self):
        pygame.draw.rect(screen, 'red', self.rect, 5) #border
        screen.blit(self.image, self.rect)

    def manager(self, target_pos):
        self.draw()
        self.move_towards(target_pos)

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

#region --- Main loop ---
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

    for bullet in bullet_list:
        if bullet.is_alive:
            Bullet.manager(bullet)
        else:
            bullet_list.remove(bullet)

    draw_items()
    for enemies in enemy_list:
        Enemy.manager(enemies, player.pos)
    #endregion

    #region UI
    mousex, mousey = get_mouse_pos()
    UI_mouse_pos.rect = pygame.Rect(mousex, mousey, 200, 100)
    UI_items.set_text(f'Coins: {player_coins}\nWood: {player_wood}\nStone: {player_stone}')
    UI_pos.set_text(f'posX: {player.pos.x}\nPosY: {player.pos.y}')
    anle = rotate_img(get_mouse_pos(), player.rect.center, IMAGE_OFFSET)
    UI_mouse_pos.set_text(f' mousepos: {mousex}, {mousey}\n angle: {-anle:.2f}')
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