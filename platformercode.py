import os       #TD: Operating System Module that lets us connect to the computer
import random   #TD: Random Module for numbers
import math     #TD: Math Module for numbers
import pygame
from os import listdir 
from os.path import isfile, join
pygame.init()       #TD: Starts the Pygame Window
pygame.display.set_caption("Best Platformer")    #TD: caption for our display window

"""
TD as Tonye Davids
CG as Caleb Gourzong
"""
WIDTH, HEIGHT = 1000, 800                                           #TD: Dimensions of our game window
FPS = 60                                                            #TD: Refresh rate of our game window
PLAYER_VEL = 6                                                      #TD: Player Velocty, the higher the faster the character 

PATH = r'C:\Coding Projects\2D-Platformer\assets'                   #TD: The directory that I used to collect objects for the game

window = pygame.display.set_mode((WIDTH, HEIGHT))                   #TD: Using the Width & Height variables


def flip(sprites):                                                             #CG: Sprites originally all face the right so this function will flip the sprites so they will face the left if the player is facing the left
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]  #CG: Built-in function which checks the direction of the character, which way to flip depending on if it is true or false and will do this for every sprite image per player sprite   

    
def load_sprite_sheets(dir1, dir2, width, height, direction=False):            #CG: This function will load all of the different sprite sheets for each character. Direction determines if the sprite is flipped or not
    path = join(PATH, dir1, dir2)                                              #CG: Built-in function that creates a path to the directory of images 
    images = [f for f in listdir(path) if isfile(join(path, f))]               #CG: Will load every file in that directory allowing them to be loaded in and manipulated

    all_sprites = {}                                                           #CG: A dictionary that will have each sprite sheet's individual images added to it 

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()    #CG: Will load a transparent background image from the needed image directory for each image in the directory

        sprites = []                                                           #CG: Creates anempty list to collect each individual image in a given sprite sheet
        for i in range(sprite_sheet.get_width() // width):                     #CG: This will chop up the sprite sheets containing the entire animation cycles into each individual frame of the animation by dividing the length of the sprite sheet by the width of each individual animation frame.
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)     #CG: Creates surface that an image can be blitted (drawn) on and is the size of an individual animation frame
            rect = pygame.Rect(i * width, 0, width, height)                    #CG: Determines where in the sprite sheet the image is pulled from in this case the top left corner of each animation frame is the "starting point" of the sprite
            surface.blit(sprite_sheet, (0, 0), rect)                           #CG Draws specific sprite frame needed which is determined by rect onto the surface which is a given size of the sprite
            sprites.append(pygame.transform.scale2x(surface))                  #CG: Adds this sprite to the list of sprites while scaling it up by a factor of 2 

        if direction:                                                          #CG: Adds a mirror image of each type of sprite sheet ie. falling, jumping to the master dictionary of all_sprites depending on direction
            all_sprites[image.replace(".png", "") + "_right"] = sprites        #CG: The next two lines will add to all_sprite sheets depending on the direction and will use the flip function if player is facing left
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites                   #CG: Otherwise just use base sprites facing right

    return all_sprites                                                         #CG: Allows all sprites that have been stripped and chopped up to now be called and applied to whatever object requires a sprite in the game 


def get_block(size):                                                           #CG: A function that will create blocks to be called in other functions
    path = join(PATH, "Terrain", "Terrain.png")                                #CG: Creates a path to the sprite sheet for terrain
    image = pygame.image.load(path).convert_alpha()                            #CG: Using the path loads the sprites from terrain file
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)                #CG: Creates a transparent surface for the image to be applied to 
    rect = pygame.Rect(96, 64, size, size)                                      #CG: Creates the rectangular hitbox the blocks will be using 
    surface.blit(image, (0, 0), rect)                                          #CG: Pastes the image onto the surface and onto the rectangular hitbox of the block
    return pygame.transform.scale2x(surface)                                   #CG: Returns the block with its graphics and hitbox while also scaling it up by a factor of two 


class Player(pygame.sprite.Sprite):                                           #TD: We are using the built-in pygame Sprite Class to animate and move our character. CG: We use a class to define the player so that a multitude of functions can be called upon while interacting with the player
    COLOR = (255, 0, 0)                                                       #CG: Sets a basic colour to the character but will not be seen once the sprite is loaded and covers it up
    GRAVITY = 1                                                               #CG: This is the base velocity of gravity downwards
    SPRITES = load_sprite_sheets("MainCharacters", "VirtualGuy", 32, 32, True) #CG: loads the sprite sheets for a specific character in this case ninja frog and call it true so that the sprite can face both left and right as shown in previous code of load_sprite_sheets
    ANIMATION_DELAY = 3                                                       #CG: The length of time it takes for the frame of a sprite to change

    def __init__(self, x, y, width, height):                #TD: This is the first function that gets initialized once the game begins CG: self is used for all functions under the class player to refer to functions and variables only accessible by the player class
        super().__init__()                                  #CG: This initializes the parent class
        self.rect = pygame.Rect(x, y, width, height)        #TD: This is the player's rectangle hitbox, lots of built-in Pygame functions are being used
        self.x_vel = 0                                      #TD: Speed in the x direction per frame
        self.y_vel = 0                                      #TD: Speed in the y direction per frame
        self.mask = None                                    
        self.direction = "left"                             #TD: When the game gets initialized, the character's direction begins by facing the left
        self.animation_count = 0                            #TD: When the game gets initialized, the character's animation count begins at 0
        self.fall_count = 0                                 #TD: When the game begins, the fall count starts at zero CG: is a variable set to track how long the character has been falling
        self.jump_count = 0                                 #CG: Jump count starts at zero to allow the player to jump when the game first begins
        self.hit = False                                    #TD: When the game starts the character is NOT being hit
        self.hit_count = 0                                  #TD: When the game starts the character hit count is at zero

    def jump(self):                                         #CG: Function that will alter the player's coordinates to jump
        self.y_vel = -self.GRAVITY * 8                      #CG: This will change the player y velocity. The reason it is negative and a multiple of gravity is to make the character jump upward and to make sure the velocity is changed by enough to not be instantly dragged down by gravity
        self.animation_count = 0                            #CG: This will restart the character's animation frame
        self.jump_count += 1                                #CG: When jumping increase jump count this will be later used to allow double jumps but nothing more than that
        if self.jump_count == 1:                            #CG: These two lines say that if it is the player's first jump then erase all accumulated extra gravity but the accumulated gravity will affect the second jump
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx                                   #TD: Some calculus, basically adding a change in the X direction
        self.rect.y += dy                                   #TD: Adding Some change in the Y direction

    def make_hit(self):                                     #Function determines if player has hit fire object                      
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel                                   #TD: Some Physics, essentially a left movement is a negative velocity movement CG: it is negative because you must subtract from the x and y coordinates of the player to move them left
        if self.direction != "left":                        #CG: Tells the computer which version of the sprite it should pull
            self.direction = "left"
            self.animation_count = 0                        #CG: Resets the player's animation

    def move_right(self, vel):
        self.x_vel = vel                                    #TD: Movement in the right is positive velocity
        if self.direction != "right":                       #CG: Tells the computer which version of the sprite it should pull
            self.direction = "right"
            self.animation_count = 0                        #CG: Resets the player's animation

    def loop(self, fps):                                                    #CG: Will be called every frame and will check which direction the player is facing and update the animation accordingly as well as move the player
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)        #CG: This will make the player be affected by gravity. It works by making the player fall at the specified unit of gravity which is 1 but will increase the speed at which you fall depending on how long you are falling. This is done by dividing fall_count by fps to track how many seconds character has been falling and the adding additional acceleration downwards
        self.move(self.x_vel, self.y_vel)                                   #CG: This will move the character left and right if the variables are changed

        if self.hit:                                                        #CG: These five lines start your hit animation when hit and then after two seconds turn off your hit animation and you return to normal state
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1                                                #CG: This will make you fall permanently unless you are colliding with an object simulating gravity in the game
        self.update_sprite()                                                #CG: Will update sprite needed and draw function will display needed sprite

    def landed(self):                                                       #YM: Function that handles the players' properties when landed
        self.fall_count = 0                                                 #YM: This erases any accumulated gravity once the player has landed
        self.y_vel = 0                                                      #YM. Sets the player's y velocity to zero so they do not keep falling 
        self.jump_count = 0                                                 #YM: Resets the player's jump count so they can jump 

    def hit_head(self):                                                     #YM: A function that handles players' properties when hitting the undersides of objects
        self.count = 0                                                      
        self.y_vel *= -1                                                    #YM: This will push the player off the bottom of the block allowing them to begin falling again

    def update_sprite(self):                                                #CG: This function will change what sprite is appearing by calling different images from the sprite dictionary depending on the player's current position or action
        sprite_sheet = "idle"                                               #CG: If the player is not moving or doing anything it will call a frame of the idle sprite sheet
        if self.hit:                                                        #CG: If the player is hit it will call a frame of the hit sprite sheet
            sprite_sheet = "hit" 
        elif self.y_vel < 0:                                                #CG: Checks if the player is going upwards
            if self.jump_count == 1:                                        #CG: If the player is accelerating upwards and it is the first jump display the frames from the jump sprite sheet
                sprite_sheet = "jump"
            elif self.jump_count == 2:                                      #CG: If the player is accelerating upwards and it is the second jump display the frames from the double jump sprite sheet    
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:                                 #CG If the player is accelerating downwards display a falling sprite. The reason it has to be accelerating downwards faster than gravity is because gravity is always being applied so fall would always be displayed so instead a significant amount of downwards acceleration must be accumulated before the fall sprite is displayed
            sprite_sheet = "fall"
        elif self.x_vel != 0:                                               #CG: If the player is moving meaning it has a velocity greater or less than zero it will call a frame of the run sprite sheet
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction             #CG: This will get what sprite sheet is needed and then more specifically which direction of the sprite sheet is needed depending on player orientation
        sprites = self.SPRITES[sprite_sheet_name]                           #CG: Possible sprites in a given sprite sheet 
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)                #CG: Will change which sprite is being shown by iterating through the index of sprites at the rate of animation_delay and dividing by the number of animation frames in the sprite sheet to cycle through the animation
        self.sprite = sprites[sprite_index]                                 #CG: The next three lines update and call the given index of the given sprite sheet at a given time while constantly changing the animation count to allow a change in the sprite index and updating it
        self.animation_count += 1
        self.update()

    def update(self):                                                       #YM: Updates rectangle that is the player depending on the sprite that is currently being displayed
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))#YM: If the sprite is slightly larger or smaller this will update the rectangle that is acting as the player's hitbox
        self.mask = pygame.mask.from_surface(self.sprite)                   #YM: Mask is a map of every pixel in the sprite and with this, it will allow pixel collision instead of collision with the entirety of the player rectangle

    def draw(self, win, offset_x):                                          #CG: Will draw all visual changes
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))        #CG: Will draw the sprites as they are updated

    def handle_collision(self, trophy):
        if pygame.sprite.collide_mask(self, trophy):
            print("Player touched the trophy! Game Over!")
            pygame.quit()
            quit()




class Object(pygame.sprite.Sprite):                                         #CL: Object class used to define dimensions and properties of objects to be later used to allow player collision
    def __init__(self, x, y, width, height, name=None):
        super().__init__()                                                  #CL: This initializes the parent class
        self.rect = pygame.Rect(x, y, width, height)                        #CL: Used to define the rectangle of space the object will take up
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)       #CL: Makes the surface the sprites will be loaded on transparent
        self.width = width                                                  #CL: declares the width of the object
        self.height = height                                                #CL: declares the height of the object
        self.name = name                                                    #CL: declares the name of the object to be called

    def draw(self, win, offset_x):                                          #CL: This function will draw the objects in the game and will change them when the screen scrolls or the players change position
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Trophy(Object):                                                       #TD: Trophy Class 
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "trophy")
        trophy_image = pygame.image.load(join(PATH, "Checkpoints", "Trophy.png")).convert_alpha()
        self.image.blit(trophy_image, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        self.touched = False                                                # TD: False if the trophy is touched

    def handle_collision(self, player):
        if pygame.sprite.collide_mask(player, self):
            print("Player touched the trophy! Game Over!")
            self.touched = True                                             # TD: Set the flag when trophy is touched
            pygame.quit()
            quit()

class Block(Object):                                                        #CG: Class for the blocks/terrain the player will stand on using the properties from the object class above
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)                                  #CG: Initializes parent class. Uses size twice to make the block a square
        block = get_block(size)                                             #CG: Will get a block of whatever size is inputted
        self.image.blit(block, (0, 0))                                      #CG: Will put the block at the top left of the image we are displaying our block on
        self.mask = pygame.mask.from_surface(self.image)                    #CG: Also for pixel perfect collision on the block


class Fire(Object):                                                         #CG: This class will act as an obstacle for the player
    ANIMATION_DELAY = 3                                                     #CG determines how long it takes for the animation to cycle

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")                       #CG: Initializes parent class
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)      #CG: Loads images for the traps
        self.image = self.fire["off"][0]                                    #CG: Fire starts as off
        self.mask = pygame.mask.from_surface(self.image)                    #CG: Creates pixel-perfect collision between the player and trap
        self.animation_count = 0                                            #CG: Starts at the beginning of the animation
        self.animation_name = "off"                                         #CG: Names starting animation as off. This will later be used to only hit players if fire is "on"

    def on(self):                                                           #CG: On and off function used to determine animations and property of the fire at a specific instance
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):                                                           #CG: This function is used to animate frames. I will give general commenting as step-by-step commenting is the same as the player update sprite function. In general, this function divides sprite sheets into images and iterates through them at a given rate
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):        #CG: Resets animation count after it gets longer than the length of the sprites so the number does not get too large and cause lag on the computer
            self.animation_count = 0


def get_background(name):                                           #TD: Background Function that is going to return how many tiles we need to draw CG: name is used to change the type of tile that is called to change background if needed
    image = pygame.image.load(join(PATH, "Background", name))       #TD: collects the assets path, within the background subfolder and name variable representing the filename
    _, _, width, height = image.get_rect()                          #TD: get_rect() Collects the X & Y values needed for each tile
    tiles = []                                                      #CG: creates an empty list and following for loops will add the tiles needed to this list and will then display the list

    for i in range(WIDTH // width + 1):         
        for j in range(HEIGHT // height + 1):                       #TD: Basically divides the number tiles needed in the X & Y and adds 1 so there is no empty space
            pos = (i * width, j * height)                           #TD: Creates a tuple of the x,y and needed for the entire window 
            tiles.append(pos)                                       #TD: inserts the number of tiles needed from the position calculation variable

    return tiles, image                                             #TD: now we can use the image and tiles outside of the function
                                                                    #TD: In summary, the function will take a background image from my computers memory and divides it into tiles. The function will also calculate the position of these tiles to be used later on

def draw(window, background, bg_image, player, objects, offset_x):  #CG: This function will draw the background onto the game screen in combination with the get_background function and draw the player
    for tile in background:                                         #TD: loops through the background and gets a number of tiles per background
        window.blit(bg_image, tile)                                 #CG: This line will loop for each tile and draw the background at the position of the tile variable which contains the x and y coordinates of every tile that needs to be drawn

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x) 

    pygame.display.update()                                         #CG: This updates the screen at every frame and will reload the images each frame so old drawings don't stay on the screen


def handle_vertical_collision(player, objects, dy):                 #CG: Function that handles vertical collision
    collided_objects = []                                           #CG: Empty list of blocks being collided with vertically
    for obj in objects:    
        if pygame.sprite.collide_mask(player, obj):                 #CG: Using mask properties allows for pixel-perfect collisions
            if dy > 0:                                              #CG: The next three line says if the player is accelerating downward when colliding to place the bottom of the player model to the top of the object and to call the properties of the land function
                player.rect.bottom = obj.rect.top    
                player.landed()
            elif dy < 0:                                            #CG: The next three line says if the player is accelerating upward when colliding to place the top of the player model to the bottom of the object and to call the properties of the hit head function
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)                            #CG: Add all collided objects to the list 

    return collided_objects                                         #CG: Return which objects were collided with


def collide(player, objects, dx):                                   #CG: Function that handles horizontal collision
    player.move(dx, 0)                                              #CG: These two lines check if it is colliding horizontally and update the player rectangle and mask 
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):                #CG: Using updated masks checks if there is a horizontal collision and if not break out of the loop
            collided_object = obj
            break

    player.move(-dx, 0)                                            #CG: If it is colliding with the updated mask it will move the player back the exact amount it moves forward to simulate the appearance of stopping
    player.update()                                                #CG: It will then update the player mask and rectangle and return what objects are being collided with and what happens if there is collision   
    return collided_object


def handle_move(player, objects):                              #WD: This function will change the coordinates of the player based on the keys pressed
    keys = pygame.key.get_pressed()                            #WD: A built-in function that checks which keys are being pressed

    player.x_vel = 0                                           #WD: Must set velocity to initial of 0 so that the x velocity isn't permanently set to the direction you move in and will be reset to zero so you stop moving when a key is not being pressed
    collide_left = collide(player, objects, -PLAYER_VEL * 2)   #WD: Checks if it is being collided with on the left and moves them to the right at the same rate as they are moving left
    collide_right = collide(player, objects, PLAYER_VEL * 2)   #WD: Checks if it is being collided with on the right and moves them to the left at the same rate as they are moving right

    if keys[pygame.K_LEFT] and not collide_left:               #WD: checks if the left arrow keys are being pressed and that the player is not currently colliding with anything to the left of it
        player.move_left(PLAYER_VEL)                           #WD: If true makes the character move to the left at the speed previously chosen by Player_vel
    if keys[pygame.K_RIGHT] and not collide_right:             #WD: checks if the right arrow keys are being pressed and that the player is not currently colliding with anything to the right of it
        player.move_right(PLAYER_VEL)                          #WD: If true makes the character move to the right at the speed previously chosen by Player_vel

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel) #CG: Calls vertical collision to be used in another variable
    to_check = [collide_left, collide_right, *vertical_collide]                 #CG: This is a master list of all three collision functions so that the handle move function knows how to alter player position based on collision            

    for obj in to_check:                                                        #CG This for loop checks through the list of every object you are colliding with and if one of those objects is the fire object then it will execute the being hit animation 
        if obj and obj.name == "fire":
            player.make_hit()


def main(window):       #TD: Main code for the actual game
    clock = pygame.time.Clock()
    background, bg_image = get_background("Gray.png")

    block_size = 96

    player = Player(100, 100, 50, 50)

    # TD: Add a staircase and extend the map space
    staircase_width = 5  # TD: Width of the staircase
    staircase_height = 5  # TD: Height of the staircase

    floor = [
        Block(i * block_size, HEIGHT - block_size, block_size)
        for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)
    ]

# TD: Add a staircase to the floor
    for i in range(staircase_width):
        for j in range(staircase_height):
            floor.append(Block(i * block_size + j * block_size, HEIGHT - block_size * (j + 1), block_size))

    for i in range(5):
        floor.append(Block((i + staircase_width) * block_size, HEIGHT - block_size * 6, block_size))

    objects = [*floor]

    fire = Fire((staircase_width + 5) * block_size, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    objects.append(fire)

    trophy = Trophy((staircase_width + 14) * block_size, HEIGHT - block_size - 64, 75, 75)
    objects.append(trophy)

    offset_x = 0
    scroll_area_width = 200
    
    run = True

    # TD: Inside the game loop
    game_over = False  # TD: I tried to make a flag to detect if the player colllides with the character, I spent like all day trying to figure it out and it just doesnt work unfortunately 
    while run and not game_over:
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

    # TD: Check for trophy collision and set the game_over flag
        if player.handle_collision(trophy):
            game_over = True

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

# TD: Tried to end the game after the game loop
    pygame.quit()
    quit()





if __name__ == "__main__":
    main(window)