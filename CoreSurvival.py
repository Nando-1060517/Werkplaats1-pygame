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

#pos
center = pygame.Vector2(display_info.current_w / 2, display_info.current_h / 2)
random_range_x = 700
random_range_y = 350

#UI
player_coins = 0
player_wood = 0
player_stone = 0

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
        for item in items_list[:]:
            collide = self.rect.colliderect(item)
            if collide:
                print(f'collision: {collide}')
                items_list.remove(item)

    def draw(self):
        pygame.draw.rect(screen, 'red', self.rect, 5)
        screen.blit(self.image, self.rect)

    def shoot(self):
        #get player pos
        #instantiate bullet
        #move bullet towards current mouse pos
        #if hits object damage it if has health
        #delete bullet oncollision or dist passed
        screen.blit(bullet_img, self.rect)

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
        self.radius = 10
        self.size = 20


    def draw(self, layer):
        raise NotImplementedError("woops")

class Coins(Item):
    def draw(self, layer):
        pygame.draw.rect(screen, 'red', self.rect, 5)
        screen.blit(self.coin_img, self.pos)

class Wood(Item):
    def draw(self, layer):
        pygame.draw.rect(screen, 'red', self.rect, 5)
        screen.blit(self.coin_img, self.pos)

class Stone(Item):
    def draw(self, layer):
        pygame.draw.rect(screen, 'red', self.rect, 5)
        screen.blit(self.coin_img, self.pos)

items_list = []

for _ in range(5):
    items_list.append(Stone())
    items_list.append(Wood())
    items_list.append(Coins())

def draw_items(layer):
    for item in items_list:
        item.draw(layer)
#endregion

class Enemy:
    def __init__(self):
        #Gets image and scales it down and add rot
        self.image = enemy_img

        #Get pos
        self.current_pos = random_pos()
        self.pos = pygame.Rect(self.current_pos.x, self.current_pos.y, 1, 1)

        #enemy base stats
        self.enemy_health = 100

    def draw(self):
        #Change this so instead of check player pos compared to enemy, rotate enemy ONLY when chasing
        if player.rect.x < self.pos.x:
            if player.rect.y < self.pos.y:
                screen.blit(pygame.transform.flip(self.image, True, False), self.pos)
            else:
                screen.blit(pygame.transform.flip(self.image, True, True), self.pos)
        else:
            if player.rect.y < self.pos.y:
                screen.blit(pygame.transform.flip(self.image, False, False), self.pos)
            else:
                screen.blit(pygame.transform.flip(self.image, False, True), self.pos)

    def move_towards(self):
        target_pos = pygame.math.Vector2(player.rect.x, player.rect.y)
        current_pos = pygame.math.Vector2(self.pos.x, self.pos.y)
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
            self.pos.topleft += direction * 5

    def manager(self):
        ...

#region --- initialization ---
#region initializing enemies
enemy_amount = 10
enemy_list = [Enemy() for enemies in range(enemy_amount)]
enemy_list_flipped = [Enemy() for enemies in range(enemy_amount)]
#endregion

#region initializing player
player = Player()
#endregion
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
                f'frame: {frame}'
                frame = 0
            else: frame += 1
            print(f'frame: {frame}')
    screen.fill('green')
    #endregion

    #calling player
    player.manager()

    #region instantiation
    for enemies in enemy_list:
        Enemy.draw(enemies)
        Enemy.move_towards(enemies)

    draw_items(screen)

    #loop through items and check for collision with player
    #Mostly works but gotta fix the problem where it only works
    # with rect types so not circle or ellipse


    #endregion

    UI_items.set_text(f'Coins: {player_coins}\nWood: {player_wood}\nStone: {player_stone}')
    UI_pos.set_text(f'posX: {player.pos.x}\nPosY: {player.pos.y}')
    UI_Manager.update(clock.tick(60)/1000.0)
    UI_Manager.draw_ui(screen)

    pygame.display.flip()
    clock.tick(60)
#endregion

#Quit if main loop breaks
pygame.quit()