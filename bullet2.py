import pygame
from pygame import mixer
import os
import random
import csv
import button
import math


mixer.init()
pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

# set framerate
clock = pygame.time.Clock()
FPS = 60

# define game variables

GRAVITY = 0.75
SCROLL_THRESH = 300
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 24
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False

bomb_start_time = None
defuser_start = None
TIME_TO_RELOAD = 1000
sprint = False


# define player action variables
moving_left = False
moving_right = False
shoot_active = False
shoot = False
grenade = False
grenade_thrown = False
reload_active = False

# load music and sounds
# pygame.mixer.music.load('audio/music2.mp3')
# pygame.mixer.music.set_volume(0.3)
# pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.08)
shot_fx = pygame.mixer.Sound('audio/shot.mp3')
shot_fx.set_volume(0.08)
plant_fx = pygame.mixer.Sound('audio/plant.mp3')
plant_fx.set_volume(0.08)
defuse_fx = pygame.mixer.Sound('audio/defuse.wav')
defuse_fx.set_volume(0.08)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.08)
reload_fx = pygame.mixer.Sound('audio/reload.wav')
reload_fx.set_volume(0.18)

# load images
# button images
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
# background
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()
# store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
# bullet
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
# grenade
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
# pick up boxes
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
item_boxes = {
    'Health': health_box_img,
    'Ammo': ammo_box_img,
    'Grenade': grenade_box_img
}

# define colours
BG = (0, 0, 0)
PINK = (252, 81, 125)
WHITE = (255, 255, 255)
GREEN = (81, 252, 153)
BLACK = (0, 0, 0)
PURPLE = (86, 0, 244)

# define font
font = pygame.font.SysFont('Futura', 30)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 450))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 200))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))


# function to reset level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()
    exit_group.empty()
    defuse_group.empty()
    portal_purple_group.empty()
    portal_yellow_group.empty()

    # create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.plant = True
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.y_flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        self.plant_text = 'PLANT THE BOMB'
        self.length = 50
        self.bullet_speed = 15

        # load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death', 'Sprint']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        for position, speed in all_bullets:
            position += speed

        # --- draws ---

        if moving_left or moving_right:
            pass
        else:
            pygame.draw.line(screen, PINK, start, end)

    def move(self, moving_left, moving_right):
        # reset movement variables
        self.plant = False
        screen_scroll = 0
        dx = 0
        dy = 0
        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # sprint
        if sprint:
            self.speed = 10
        else:
            self.speed = 5

        # jump
        if self.jump and not self.in_air:
            self.jump = False
            self.in_air = True
            if sprint:
                self.vel_y = -22
            else:
                self.vel_y = -16

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # check for collision
        for tile in world.obstacle_list:
            # check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # if the ai has hit a wall then make it turn around
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            # self.health += 5
            # if self.health >= 100:
            #     self.health = 100

            # screen_scroll = 0
            # bg_scroll = 0

            # world_data = reset_level()

            # with open(f'level{level}_data.csv', newline='') as csvfile:
            #     reader = csv.reader(csvfile, delimiter=',')
            #     for x, row in enumerate(reader):
            #         for y, tile in enumerate(row):
            #             world_data[x][y] = int(tile)
            # player, health_bar = world.process_data(world_data)

            if bomb_start_time and pygame.sprite.spritecollide(self, water_group, False):
                if self.plant_text == 'DEVICE HAS BEEN DEFUSED':
                    pass
                else:
                    self.plant_text = 'ARMING CODES ENTERED'
                    time_since_enter = pygame.time.get_ticks() - bomb_start_time
                    # screen.blit(FONT.render(message, True, TEXT_COLOR), (20, 20))
                    if time_since_enter >= 5000:
                        self.plant = True
                        self.plant_text = 'DEVICE IS ACTIVE'

        if defuser_start and pygame.sprite.spritecollide(self, defuse_group, True):
            self.plant = False
            self.plant_text = 'DEVICE HAS BEEN DEFUSED'

        if self.plant_text == 'DEVICE IS ACTIVE':
            plant_fx.play()

        if reload_active:
            if self.shoot_cooldown == 0 and player.ammo < 20:
                reload_time_snap = pygame.time.get_ticks() - reload_start_time
                if reload_time_snap >= 1000:
                    whats_left = 20 - self.ammo
                    self.ammo += whats_left

        # check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        portal_purple_complete = False
        if pygame.sprite.spritecollide(self, portal_purple_group, False):
            portal_purple_complete = True

        portal_yellow_complete = False
        if pygame.sprite.spritecollide(self, portal_yellow_group, False):
            portal_yellow_complete = True

        # check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # check if going off the edges of the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # update scroll based on player position
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (
                    world.level_length * TILE_SIZE) - SCREEN_WIDTH) \
                    or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll -= dx

        return screen_scroll, level_complete, portal_purple_complete, portal_yellow_complete

    def shoot(self):
        # add new tiles to the screen
        # get mouse position
        pos = pygame.mouse.get_pos()

        # check that the coordinates are within the tile area
        if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
            # update tile value
            if not reload_active and not sprint and self.shoot_cooldown == 0 and self.ammo > 0:
                self.shoot_cooldown = 8
                # self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction
                bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery,
                                self.direction, pos[0], pos[1])
                print(f'pos[0]: {pos[0]}, pos[1]: {pos[1]} self.rect.centerx: {self.rect.centerx} + (0.75 * self.rect.size[0]: {self.rect.size[0]}), self.direction: {self.direction})')
                bullet_group.add(bullet)
                # reduce ammo
                self.ammo -= 1
                pygame.mixer.stop()
                shot_fx.play()

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)  # 0: idle
                self.idling = True
                self.idling_counter = 50
            # check if the ai in near the player
            if self.vision.colliderect(player.rect):
                # stop running and face the player
                self.update_action(0)  # 0: idle
                # shoot
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1: run
                    self.move_counter += 1
                    # update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # scroll
        self.rect.x += screen_scroll

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        # if moving_up:
        #     screen.blit(pygame.transform.flip(pygame.transform.rotate(self.image, 90), self.flip, False), self.rect)
        # elif moving_down:
        #     screen.blit(pygame.transform.flip(pygame.transform.rotate(self.image, 270), self.flip, False), self.rect)
        # else:
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:  # create player
                        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.2, 5, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:  # create enemies
                        enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:  # create ammo box
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:  # create grenade box
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:  # create health box
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:  # create exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
                    elif tile == 21:
                        defuser = DefuseBox(img, x * TILE_SIZE, y * TILE_SIZE)
                        defuse_group.add(defuser)
                    elif tile == 22:
                        portal_purple = Portal_Purple(img, x * TILE_SIZE, y * TILE_SIZE)
                        portal_purple_group.add(portal_purple)
                    elif tile == 23:
                        portal_yellow = Portal_Yellow(img, x * TILE_SIZE, y * TILE_SIZE)
                        portal_yellow_group.add(portal_yellow)

        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Portal_Purple(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Portal_Yellow(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # scroll
        self.rect.x += screen_scroll
        # check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            # check what kind of box it was
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            # delete the item box
            self.kill()


class DefuseBox(pygame.sprite.Sprite):

    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # scroll
        self.rect.x += screen_scroll


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # update with new health
        self.health = health
        # calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, PINK, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, target_x, target_y):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 30
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.target_x = target_x
        self.target_y = target_y

        self.angle = math.atan2(target_y - y, target_x - x)  # get angle to target in radians
        print('Angle in degrees:', int(self.angle * 180 / math.pi))
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed
        self.x = x
        self.y = y
        # self.position = position

    def update(self):
        # move bullet
        self.x = self.x + self.dx
        self.y = self.y + self.dy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        # check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 35
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        # check for collision with level
        for tile in world.obstacle_list:
            # check collision with walls
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed *= 0.5
                # check if below the ground, i.e. thrown up
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

                    # update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        # countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            # do damage to anyone that is nearby
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        # scroll
        self.rect.x += screen_scroll

        EXPLOSION_SPEED = 4
        # update explosion amimation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            # if the animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:  # whole screen fade
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour,
                             (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour,
                             (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2:  # vertical screen fade down
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete


# create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PURPLE, 4)

# create buttons
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)

# create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
defuse_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
portal_purple_group = pygame.sprite.Group()
portal_yellow_group = pygame.sprite.Group()

# create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
# load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

all_bullets = []

run = True
while run:

    clock.tick(FPS)

    if start_game == False:
        # draw menu
        screen.fill(BG)
        # add buttons
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
        # update background
        draw_bg()
        # draw world map
        world.draw()
        # show player health
        health_bar.draw(player.health)
        # show ammo
        draw_text('AMMO: ', font, WHITE, 10, 35)

        for x in range(player.ammo):
            screen.blit(bullet_img, (90 + (x * 10), 40))
        # show grenades
        draw_text('GRENADES: ', font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img, (135 + (x * 15), 60))

        draw_text(f'BOMB: {player.plant_text} ', font, WHITE, 10, 85)

        # round timers but theyre all fucked up
        # round_total = 90
        #
        # time_since_beginning = pygame.time.get_ticks()
        #
        # time_left = int(round_total - time_since_beginning) / 1000
        #
        # if time_left > 60:
        #     round_output = f'1:{time_left - 60}'
        # elif time_left < 60:
        #     round_output = time_left
        #
        # draw_text(f'TIME: {round_output} ', font, WHITE, 10, 110)


        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        # update and draw groups
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        portal_purple_group.update()
        portal_yellow_group.update()
        defuse_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)
        portal_purple_group.draw(screen)
        portal_yellow_group.draw(screen)
        defuse_group.draw(screen)

        # show intro
        if start_intro:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        # update player actions
        if player.alive:
            # shoot bullets
            if shoot:
                # to be changed for random shots later when determine angles
                # if not moving_right or moving_left:

                player.shoot()

                # start reload
                # if player.ammo < 1:
                #     player.ammo += 25
            # throw grenades
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), player.rect.top, player.direction)
                grenade_group.add(grenade)
                # reduce grenades
                player.grenades -= 1
                grenade_thrown = True
            if player.in_air and not sprint:
                player.update_action(2)  # 2: jump
            elif moving_left and sprint or moving_right and sprint or player.in_air and sprint:
                player.update_action(4)
            elif moving_left or moving_right:
                player.update_action(1)  # 1: run
            elif sprint:
                player.update_action(4)

            else:
                player.update_action(0)  # 0: idle
            screen_scroll, level_complete, portal_purple_complete, portal_yellow_complete = player.move(moving_left,
                                                                                                        moving_right)
            bg_scroll -= screen_scroll
            # check if player has completed the level
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    # load in level data and create world
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)
            if portal_purple_complete:
                # same level portal
                player.rect.center = 975, 870
                screen_scroll -= 975
                bg_scroll += 975

                # up a level portal
                # level += 1
                # bg_scroll = 0
                # world_data = reset_level()
                # if level <= MAX_LEVELS:
                #     # load in level data and create world
                #     with open(f'level{level}_data.csv', newline='') as csvfile:
                #         reader = csv.reader(csvfile, delimiter=',')
                #         for x, row in enumerate(reader):
                #             for y, tile in enumerate(row):
                #                 world_data[x][y] = int(tile)
                #     world = World()
                #     player, health_bar = world.process_data(world_data)
            if portal_yellow_complete:
                level -= 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    # load in level data and create world
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)
        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    # load in level data and create world
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)



    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            run = False
        # keyboard presses
        elif event.type == pygame.MOUSEMOTION:
            try:
                mouse = pygame.mouse.get_pos()
                start = pygame.math.Vector2(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), player.rect.centery + 2)
                end = start + (mouse - start).normalize() * player.length
                # print(f'Start::{start}, end::{end}')
            except ValueError as e:
                pass

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if shoot_active and start_game:
                # all_bullets.append([position, speed])
                shoot = True
            shoot_active = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                sprint = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_r and player.alive:
                pygame.mixer.stop()
                reload_fx.play()
                reload_start_time = pygame.time.get_ticks()
                print(reload_start_time)
                reload_active = True

            if event.key == pygame.K_e:
                print(f'center: {player.rect.center} x: {player.rect.centerx} y: {player.rect.centery}')
                bomb_start_time = pygame.time.get_ticks()
                plant_fx.play()
                print(bg_scroll)
                print(screen_scroll)
            if event.key == pygame.K_x:
                defuser_start = pygame.time.get_ticks()
                print(defuser_start)
                pygame.mixer.stop()
                defuse_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False

        # keyboard button released
        if event.type == pygame.MOUSEBUTTONUP:
            shoot = False
        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                sprint = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

    if reload_active and pygame.time.get_ticks() - reload_start_time > TIME_TO_RELOAD:  # 1000
        reload_active = False

    pygame.display.update()

pygame.quit()
