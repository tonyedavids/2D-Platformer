import os       #TD: Operating System Module that lets us connect to computer
import random   #TD: Random Module for numbers
import math     #TD: Math Module for numbers
import pygame
from os import listdir 
from os.path import isfile, join
pygame.init()       #TD: Starts the Pygame Window

pygame.display.set_caption("Platformer")    #TD: caption for out display window


WIDTH, HEIGHT = 1000, 800                                           #TD: Dimensions of our game window
FPS = 60                                                           #TD: Refresh rate of our game window
PLAYER_VEL = 6                                                      #TD: Player Velocty, the higher the faster the character 

PATH = r'C:\Coding Projects\2D-Platformer\assets'                   #TD: The directory that I used inorder to collect objects for game

window = pygame.display.set_mode((WIDTH, HEIGHT))                   #TD: Using the Width & Height variables


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]       


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join(PATH, dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join(PATH, "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 64, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):                         #TD: We are using the built in pygame Sprite Class to animate and move our character
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "VirtualGuy", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):                #TD: This is the the first function that gets initialized as soon as the game begins
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)        #TD: Basically the players rectangle hitbox, lots of built in Pygame functions are being used
        self.x_vel = 0                                      #TD: Speed in the x direction
        self.y_vel = 0                                      #TD: Speed in the y direction
        self.mask = None                                    #TD: 
        self.direction = "left"                             #TD: When the game gets initialized, the characters direction begins by facing the left
        self.animation_count = 0                            #TD: When the game gets initialized, the characcters animation count begins at 0
        self.fall_count = 0                                 #TD: When the game begins, the fall count starts at zero 
        self.jump_count = 0                                 #TD: When the game begins, the jump count is also zero  
        self.hit = False                                    #TD: When the game starts the character is NOT being hit
        self.hit_count = 0                                  #TD: When the game starts the character hit count is at zero

    def jump(self):                                         
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx                                   #TD: Some calculus, basically adding a change in the X direction
        self.rect.y += dy                                   #TD: Adding Some change in the Y direction

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel                                   #TD: Some Physics, essentially a left movement is a negative velocity movement
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel                                    #TD: Movement in the right
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):                                    #TD: Movements are doing to
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):                                       #TD: Background Function thats going to return how many tiles we need to draw 
    image = pygame.image.load(join(PATH, "Background", name))   #TD: collects the assets path, within the background subfolder and name variable representing filename
    _, _, width, height = image.get_rect()                      #TD: get_rect() Collects the X & Y values needed for each tile
    tiles = []

    for i in range(WIDTH // width + 1):         
        for j in range(HEIGHT // height + 1):       #TD: Basically divides the number tiles needed in the X & Y and adds 1 so there is no empy space
            pos = (i * width, j * height)           #TD: Creates a tuple of the x,y and needed for the entire window 
            tiles.append(pos)                       #TD: inserts the amount of tiles needed from the position calculation variable

    return tiles, image                             #TD: now we can use the image and tiles outside of the function
                                                    #TD: In summary the function will take a background image from my computers memory and divides it into tiles. The function will also calculate the position of these tiles in order to be used later on

def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:                         #TD: loops through the back ground and gets an emount of tiles oer background
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()


def main(window):       #TD: Main code for the actual game
    clock = pygame.time.Clock()
    background, bg_image = get_background("Gray.png")

    block_size = 96

    player = Player(100, 100, 50, 50)

    # Add a staircase and extend the map space
    staircase_width = 5  # Width of the staircase
    staircase_height = 5  # Height of the staircase

    floor = [
        Block(i * block_size, HEIGHT - block_size, block_size)
        for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)
    ]

# Add a staircase to the floor
    for i in range(staircase_width):
        for j in range(staircase_height):
            floor.append(Block(i * block_size + j * block_size, HEIGHT - block_size * (j + 1), block_size))

    for i in range(5):
        floor.append(Block((i + staircase_width) * block_size, HEIGHT - block_size * 6, block_size))

    objects = [*floor]

    fire = Fire((staircase_width + 5) * block_size, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    objects.append(fire)

    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)