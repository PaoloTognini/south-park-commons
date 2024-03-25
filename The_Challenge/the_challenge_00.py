# This code, "challenge_00", is the first complete version.
#
# Things to solve: (1) add some levels, (2) add more complex combinations of tiles.

import pygame
import pygame.gfxdraw
import sys
import time
import random
import copy
import math
from levels import levels

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 32
VISIBLE_GRID_SIZE = 9
TILE_SIZE = 30  # Adjust the tile size as needed
DELTA_T = 0.25  # in seconds
SCALE_FACTOR = 2  # Adjust the scale factor as needed

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
DARK_GREY = (64, 64, 64)
VERY_DARK_GREY = (32, 32, 32)
LIGHT_GREY = (223, 223, 223)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
DARK_RED = (128, 0, 0)
ORANGE = (251, 139, 35)
DARK_GREEN = (0, 128, 0)
GREEN = (0, 255, 0)
LIGHT_GREEN = (128, 255, 128)
YELLOW = (255, 255, 0)
LIGHT_BLUE = (0, 255, 255)
VERY_LIGHT_BLUE = (128, 255, 255)
PURPLE = (255, 0, 255)
BROWN = (165, 42, 42)
DARK_BROWN = (92, 64, 51)

# Initialize the display
visible_grid_pixel_size = VISIBLE_GRID_SIZE * TILE_SIZE * SCALE_FACTOR
screen_size = (visible_grid_pixel_size*14/9, visible_grid_pixel_size)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Chip's Challenge")

# Function to get the visible grid coordinates
def get_visible_grid_coords(chip_pos):
    x, y = chip_pos

    # Calculate the top-left corner of the visible grid
    visible_grid_top_left_x = max(min(x - (VISIBLE_GRID_SIZE // 2), GRID_SIZE - VISIBLE_GRID_SIZE), 0)
    visible_grid_top_left_y = max(min(y - (VISIBLE_GRID_SIZE // 2), GRID_SIZE - VISIBLE_GRID_SIZE), 0)

    return visible_grid_top_left_x, visible_grid_top_left_y

# Check where is Chip
def check_where_is_Chip(chip_pos, downworld):
    x, y = chip_pos
    return downworld[x][y]

direction_chars = ['U', 'R', 'D', 'L']
monster_chars = ['f', 'g', 'o', 'q', 'b', 'a', 'p', 't', 'm']
moving_chars = monster_chars + ['c', 'n']
color_chars = ['r', 'y', 'g', 'b']
element_chars = ['F', 'W', 'I', 'E']
button_chars = ['g', 'b', 'r', 'n']

def angle_from_direction(direction):
    direction_dict = {'U': 0, 'R': 1, 'D': 2, 'L': 3}
    return direction_dict.get(direction, None)

def direction_from_angle(direction):
    direction_dict = {0: 'U', 1: 'R', 2: 'D', 3: 'L'}
    return direction_dict.get(direction, None)

def reverse_direction_char(direction):
    direction_dict = {'U': 'D', 'R': 'L', 'D': 'U', 'L': 'R'}
    return direction_dict.get(direction, None)

def full_direction(direction):
    direction_dict = {'U': 'up', 'R': 'right', 'D': 'down', 'L': 'left'}
    return direction_dict.get(direction, None)

def color_from_char(color_char):
    color_dict = {'r': RED, 'y': YELLOW, 'g': GREEN, 'b': BLUE, 'F': ORANGE, 'W': BLUE, 'I': LIGHT_GREY, 'E': LIGHT_GREEN}
    return color_dict.get(color_char, None)

def color_from_button_char(button_char):
    color_dict = {'g': GREEN, 'b': BLUE, 'r': RED, 'n': BROWN}
    return color_dict.get(button_char, None)

def is_new_pos_inside_the_grid(new_pos):
    if new_pos[0] < 0 or new_pos[0] > GRID_SIZE - 1 or new_pos[1] < 0 or new_pos[1] > GRID_SIZE - 1:
        return False
    else:
        return True

def chip_can_press_keys(downworld, i, j, tools_acquired):
    if downworld[i][j] == 'TA':
        return False
    if downworld[i][j][0] == 'I' and downworld[i][j][1] in ['_','U','R','D','L'] and tools_acquired.get('I')==0:
        return False
    return True

def object_can_pass_through(downworld, overworld, i, j, object_char, direction_char, tools_acquired, lost_time, current_time, cloner_list,teleport_list, already_moved):
    assert(direction_char in direction_chars)

    c = downworld[i][j]
    
    if c[0] == 'C' and c[1] in ['_','U','R','D','L']:
        return False, lost_time
    if c=='DC':
        return False, lost_time

    # The Lines. I can't get there if I go towards an edge.
    if c[0] == 'L':
        if c[1] == 'X':
            if direction_char == 'U' or direction_char == 'L':
                return False, lost_time
        elif c[1] in direction_chars:
            #print("I passed a ", c, "cell!")
            if angle_from_direction(c[1])==(angle_from_direction(direction_char) + 2)%4:
                return False, lost_time

    # The Ice. I can't get there if I go towards an edge.
    if c[0] == 'I' and c[1] in direction_chars:
        #print("c[1] is ", c[1], " and direction_char is ", direction_char)
        if c[1] == 'U' and direction_char in ['R','D']:
            return False, lost_time
        if c[1] == 'R' and direction_char in ['D','L']:
            return False, lost_time
        if c[1] == 'D' and direction_char in ['L','U']:
            return False, lost_time
        if c[1] == 'L' and direction_char in ['U','R']:
            return False, lost_time
    
    # Now chip_can_pass_through is the only one of the three functions that returns lost_time.
    # As there is the case, using teleports, in which Chip moves a block and kills itself...!
    # It happens if Chip is over the first teleport, on the right there is a block, and on the right there is the
    # second and last teleport.
    if object_char == 'c':
        return chip_can_pass_through(downworld, overworld, i, j, direction_char, tools_acquired, lost_time, current_time, cloner_list, teleport_list, already_moved)
    elif object_char in monster_chars:
        return monster_can_pass_through(downworld, overworld, i, j, object_char, direction_char), lost_time
    elif object_char == 'n':
        return block_can_pass_through(downworld, overworld, i, j), lost_time

# Check if the Tile is like a wall for a monster
def monster_can_pass_through(downworld, overworld, i, j, monster_char, direction_char):
    for c in (downworld[i][j], overworld[i][j]):
        if c=='E_' or c=='SF' or c=='th':
            return False
        if c=='WL' or c=='IW' or c=='1p' or c=='DI' or c=='FK' or c=='FF' or c=='so' or c=='ch':
            return False
        if c[0] == 'd' and c[1] in color_chars:
            return False
        if c[0] == 's' and c[1] in element_chars:
            return False
        if c[0] == 'n' and c[1] in ['_','U','R','D','L']:
            return False
        for other_monster_char in monster_chars:
            for other_direction_char in direction_chars:
                if c==other_monster_char+other_direction_char:
                    return False
        if monster_char == 'a':
            if c=='F_':
                return False
    return True

def block_can_pass_through(downworld, overworld, i, j):
    for c in (downworld[i][j], overworld[i][j]):
        if c=='WL' or c=='IW' or c=='1p' or c=='DI' or c=='FK' or c=='FF' or c=='so' or c=='ch':
            return False
        if c[0] == 'd' and c[1] in color_chars:
            return False
        if c[0] == 's' and c[1] in element_chars:
            return False
        if c[0] == 'n' and c[1] in ['_','U','R','D','L']:
            return False
        for monster_char in monster_chars:
            for direction_char in direction_chars:
                if c==monster_char+direction_char:
                    return False
    return True


def chip_can_pass_through(downworld, overworld, i, j, direction_char, tools_acquired, lost_time, current_time, cloner_list, teleport_list, already_moved):
    # A Chip tries to pass through a Fake, the true nature of the Fake reveals itself.
    if overworld[i][j] == 'FK':
        overworld[i][j] = '__'

    for c in (downworld[i][j], overworld[i][j]):
        # Chip may encounter a Block which may or may not be moved!
        if c[0] == 'n' and c[1] in ['_','U','R','D','L']:
            it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char, downworld, overworld, i, j, 'n', tools_acquired, lost_time, current_time, cloner_list, teleport_list, already_moved)
            return it_moved, lost_time

        # The Wall.
        if c=='WL' or c=='IW':
            return False, lost_time

        # The Fake Floor.
        if downworld[i][j] == 'FF':
            downworld[i][j] = 'WL'
            return False, lost_time

        # Open and Closed Doors.
        if c=='DC':
            return False, lost_time
        
        # The One Pass.
        if c=='1p':
            downworld[i][j] = 'WL'

        # The Socket.
        if c=='so':
            # If I did not obtain all chips left, it's a wall.
            if tools_acquired['c'] > 0:
                #print("There are ", tools_acquired['c'], " Chips left!")
                return False, lost_time
            else:
                # If probed with all the chips required, the socket disappears.
                # I assume the socket is in the overworld.
                overworld[i][j] == '__'

        # The Door.
        for color_char in color_chars:
            if c=='d'+color_char:
                # If I do not have the key, it is like a wall.
                if tools_acquired[color_char] == 0:
                    #print("My tools are ", tools_acquired)
                    return False, lost_time
                else:
                    # Else I loose a key (except for the green key which cannot be lost):
                    if color_char != 'g':
                        tools_acquired[color_char]-=1
                    #print("My tools are ", tools_acquired)
    return True, lost_time

def monster_is_dead(downworld, overworld, i, j, monster_char):
    c = downworld[i][j]
    over_c = overworld[i][j]
    
    # The bomb kills all monsters and disappears.
    if c == 'bo':
        downworld[i][j] = '__'
        overworld[i][j] = '__'
        return True
    
    if monster_char == 'f':
        if c == 'W_' or over_c == 'W_':
            return True
        return False
    if monster_char == 'g':
        if c == 'F_':
            return True
        return False
    if monster_char == 'o' or monster_char == 'q' or monster_char == 'b' or monster_char == 'p' or monster_char == 'm':
        if c == 'F_' or c == 'W_':
            return True
        return False
    if monster_char == 'a':
        if c == 'W_':
            return True
        return False

def kills_chip_if_over_it(c):
    for monster_char in monster_chars:
        for direction_char in direction_chars:
            if c == monster_char + direction_char:
                #print("chip is killed!")
                return True
    if c == 'W_':
        #print("chip is killed!")
        return True
    return False

def transposed(world):
    return list(map(list, zip(*world)))

# i, j are the positions from where the movement starts.
def object_can_go_and_goes(direction_char, downworld, overworld, i, j, moving_char, tools_acquired, lost_time, current_time, cloner_list, teleport_list, already_moved):
    the_object_will_move = False
    # The condition with the cloner is to avoid an object to be cloned goes in a direction different from the original one.
    if (
            (direction_char == 'U' and j > 0 and downworld[i][j]!='LU' and (downworld[i][j][0]!='C' or downworld[i][j][1]=='U')) or
            (direction_char == 'R' and i < GRID_SIZE - 1 and downworld[i][j]!='LR' and downworld[i][j]!='LX' and (downworld[i][j][0]!='C' or downworld[i][j][1]=='R')) or
            (direction_char == 'D' and j < GRID_SIZE - 1 and downworld[i][j]!='LD' and downworld[i][j]!='LX' and (downworld[i][j][0]!='C' or downworld[i][j][1]=='D')) or
            (direction_char == 'L' and i > 0 and downworld[i][j]!='LL' and (downworld[i][j][0]!='C' or downworld[i][j][1]=='L'))
    ):
        new_positions = new_position_with_teleport(i,j,direction_char,downworld,teleport_list)
        index_new_pos = 0
        while index_new_pos < len(new_positions) and the_object_will_move == False:
            new_i = new_positions[index_new_pos][0]
            new_j = new_positions[index_new_pos][1]
            can_pass, lost_time = object_can_pass_through(downworld,overworld,new_i,new_j,moving_char,direction_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
            if can_pass:
                overworld[i][j] = '__'
                the_object_will_move = True
                # If chip goes over a monster, it is killed
                if moving_char == 'c':
                    if kills_chip_if_over_it(overworld[new_i][new_j]):
                        #print("Chip moves on to a monster!")
                        if lost_time == 0:
                            lost_time = current_time
                elif moving_char != 'c':
                    if overworld[new_i][new_j][0] == 'c' and overworld[new_i][new_j][1] in ['_','U','R','D','L']:
                        #print("An object is over Chip!")
                        if lost_time == 0:
                            lost_time = current_time
            index_new_pos += 1
        if the_object_will_move == False:
            direction_char = reverse_direction_char(direction_char)
    if the_object_will_move == True:
        new_moving_name = moving_char + direction_char
        if moving_char == 'n':
            overworld[i][j] = '__' 
            # The block is assumed to be in the overworld.
            # The block removes water and converts it into dirt.
            if downworld[new_i][new_j] == 'W_':
                downworld[new_i][new_j] = 'DI'
            # The block removes the bomb and disappears.
            elif downworld[new_i][new_j] == 'bo':
                downworld[new_i][new_j] = '__'
            # The block presses a button.
            elif downworld[new_i][new_j][0] == '.':
                button_color = downworld[new_i][new_j][1]
                a_button_was_pressed(button_color, new_i, new_j, downworld, overworld, tools_acquired, lost_time, current_time, cloner_list, teleport_list, already_moved)
                #print("The Block just pressed a button")
                new_block_name = 'n' + direction_char
                overworld[new_i][new_j] = new_block_name
            else:
                new_block_name = 'n' + direction_char
                overworld[new_i][new_j] = new_block_name
        if moving_char in monster_chars:
            if not monster_is_dead(downworld,overworld,new_i,new_j,moving_char):
                overworld[new_i][new_j] = new_moving_name
            # Water in the overworld is the only cause of death of monsters from the overworld!
            if overworld[new_i][new_j] == 'W_' and monster_char != 'g':
                overworld[new_i][new_j] = '__'
        if moving_char == 'c':
            overworld[new_i][new_j] = new_moving_name
        # Chip removes the dirt which is under him.
        if moving_char == 'c' and downworld[new_i][new_j] == 'DI':
            downworld[new_i][new_j] = '__'
        
        # If the object presses a button.
        if downworld[new_i][new_j][0] == '.':
            button_color = downworld[new_i][new_j][1]
            a_button_was_pressed(button_color, new_i, new_j, downworld, overworld, tools_acquired, lost_time, current_time, cloner_list, teleport_list, already_moved)
            #print("A monster or Chip just pressed a button")
        return True, new_i, new_j, lost_time
    else:
        return False, 0, 0, lost_time
    
def direction_changed_by_ice(last_direction_char, type_of_ice):
    # I make heavy use of last_direction_char which is the direction_char of the last move!
    if type_of_ice == '_':
        direction_char = last_direction_char
    # Cases in which I go UP:
    elif (type_of_ice == 'D' and last_direction_char == 'R') or (type_of_ice == 'L' and last_direction_char == 'L'):
        direction_char = 'U'
    # Cases in which I go RIGHT:
    elif (type_of_ice == 'U' and last_direction_char == 'U') or (type_of_ice == 'L' and last_direction_char == 'D'):
        direction_char = 'R'
    # Cases in which I go DOWN:
    elif (type_of_ice == 'U' and last_direction_char == 'L') or (type_of_ice == 'R' and last_direction_char == 'R'):
        direction_char = 'D'
    # Cases in which I go LEFT:
    elif (type_of_ice == 'R' and last_direction_char == 'U') or (type_of_ice == 'D' and last_direction_char == 'D'):
        direction_char = 'L'
    else:
        direction_char = last_direction_char
        #print("ILLEGAL MOVE!")
        #print("type_of_ice = ", type_of_ice)
        #print("last_direction_char = ", last_direction_char)
        quit()
    return direction_char

def align_cloners_with_objects_above(downworld, overworld):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if downworld[i][j][0] == 'C' and downworld[i][j][1] in ['_','U','R','D','L']:
                if overworld[i][j][0] in moving_chars and overworld[i][j][0] != 'c' and overworld[i][j][1] in direction_chars:
                    if downworld[i][j][1] != overworld[i][j][1]:
                        downworld[i][j] = 'C' + overworld[i][j][1]
                        #print("The Cloner at position i, j = ", i, j, " was corrected!")

def cloner_from_red_button(i, j, cloner_list):
    for index in range(len(cloner_list)):
        red_button = cloner_list[index][0]
        if red_button == [i,j]:
            return cloner_list[index][1]
    #print("ERROR! In position i, j = ", i, j, " there is no red button of the cloner list!")
        
def red_button_from_cloner(i, j, cloner_list):
    for index in range(len(cloner_list)):
        cloner = cloner_list[index][1]
        if cloner == [i,j]:
            return cloner_list[index][0]
    #print("ERROR! In position i, j = ", i, j, " there is no cloner of the cloner list!")

def a_button_was_pressed(button_color, i, j, downworld, overworld, tools_acquired, lost_time, current_time, cloner_list, teleport_list, already_moved):
    if button_color in 'g':
        #print("A green button was pressed!")
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if downworld[x][y] == 'DC':
                    downworld[x][y] = 'DO'
                elif downworld[x][y] == 'DO':
                    downworld[x][y] = 'DC'
    elif button_color in 'b':
        #print("A blue button was pressed!")
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if overworld[x][y][0] == 't' and overworld[x][y][1] in direction_chars:
                    overworld[x][y] = 't' + reverse_direction_char(overworld[x][y][1])
    if button_color in 'r':
        #print("A red button was pressed!")
        #print("ANOTHER PRINT Cloner list = ", cloner_list)
        #print("i, j = ", i, j)
        x, y = cloner_from_red_button(i, j, cloner_list)
        #print("LAST PRINT: x, y = ", x, y)
        #print("already_moved = ", already_moved)
        already_moved[x][y] = False

def get_index_of_teleport(i,j,teleport_list):
    for n in range(len(teleport_list)):
        if teleport_list[n] == [i,j]:
            return n
    #print("ERROR! GIVEN POSITION i, j = ", i, j, " IS NOT A TELEPORT!")
    quit()

def new_position(i, j, direction_char):
    if direction_char == 'U': 
        return i, j-1
    if direction_char == 'R': 
        return i+1, j
    if direction_char == 'D': 
        return i, j+1
    if direction_char == 'L': 
        return i-1, j

def new_position_with_teleport(i, j, direction_char, downworld, teleport_list):
    new_positions = []
    
    new_i, new_j = new_position(i, j, direction_char)
    # If the new position has a teleport
    if downworld[new_i][new_j] == 'TP':
        n = get_index_of_teleport(new_i, new_j, teleport_list)
        n_teleports = len(teleport_list)
        for index in range(n_teleports):
            new_i, new_j = teleport_list[(n+1+index)%n_teleports]
            new_i, new_j = new_position(new_i, new_j, direction_char)
            new_positions.append([new_i, new_j])
        return new_positions
    else:
        return [[new_i, new_j]]

def draw_text(screen, text, color, position):
    font = pygame.font.Font(None, 60)  # You can adjust the font size
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=position)
    screen.blit(text_surface, text_rect)

def draw_filled_pie(surface, color, center, radius, start_angle, stop_angle):
    points = [center]
    num_points = 100

    for i in range(num_points + 1):
        angle = math.radians(start_angle + (stop_angle - start_angle) * i / num_points)
        x = center[0] + int(radius * math.cos(angle))
        y = center[1] + int(radius * math.sin(angle))
        points.append((x, y))

    pygame.draw.polygon(surface, color, points)


def draw_the_tile(c, draw_position, current_time):
    side = TILE_SIZE * SCALE_FACTOR // 2.0
    size = side

    if c == 'E_':
        pygame.draw.rect(screen, BLUE, (draw_position[0] * TILE_SIZE * SCALE_FACTOR, draw_position[1] * TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR))
        pygame.draw.rect(screen, WHITE, ((draw_position[0]+0.1) * TILE_SIZE * SCALE_FACTOR, (draw_position[1]+0.1) * TILE_SIZE * SCALE_FACTOR, 0.8*TILE_SIZE * SCALE_FACTOR, 0.8*TILE_SIZE * SCALE_FACTOR))
        pygame.draw.rect(screen, BLUE, ((draw_position[0]+0.2) * TILE_SIZE * SCALE_FACTOR, (draw_position[1]+0.2) * TILE_SIZE * SCALE_FACTOR, 0.6*TILE_SIZE * SCALE_FACTOR, 0.6*TILE_SIZE * SCALE_FACTOR))
        pygame.draw.rect(screen, WHITE, ((draw_position[0]+0.3) * TILE_SIZE * SCALE_FACTOR, (draw_position[1]+0.3) * TILE_SIZE * SCALE_FACTOR, 0.4*TILE_SIZE * SCALE_FACTOR, 0.4*TILE_SIZE * SCALE_FACTOR))
        pygame.draw.rect(screen, BLUE, ((draw_position[0]+0.4) * TILE_SIZE * SCALE_FACTOR, (draw_position[1]+0.4) * TILE_SIZE * SCALE_FACTOR, 0.2*TILE_SIZE * SCALE_FACTOR, 0.2*TILE_SIZE * SCALE_FACTOR))
    if c == 'F_':
        pygame.draw.rect(screen, ORANGE, (draw_position[0] * TILE_SIZE * SCALE_FACTOR, draw_position[1] * TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR))
    if c[0] == 'I' and c[1] in ['_', 'U', 'R', 'D', 'L']:
        x_left = draw_position[0]*TILE_SIZE*SCALE_FACTOR
        x_right = x_left + TILE_SIZE*SCALE_FACTOR
        y_up = draw_position[1]*TILE_SIZE*SCALE_FACTOR
        y_down = y_up + TILE_SIZE*SCALE_FACTOR
        pygame.draw.rect(screen, VERY_LIGHT_BLUE, (x_left, y_up, TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR))
        
        short_side = TILE_SIZE * SCALE_FACTOR * 0.1
        if c[1] == 'U':
            pygame.draw.rect(screen, DARK_GREY, (x_left, y_up, TILE_SIZE * SCALE_FACTOR, short_side))
            pygame.draw.rect(screen, DARK_GREY, (x_left, y_up, short_side, TILE_SIZE * SCALE_FACTOR))
            triangle_vertices = [(x_left, y_up), (x_left, y_up+3*short_side), (x_left+3*short_side, y_up)]
        if c[1] == 'R':
            pygame.draw.rect(screen, DARK_GREY, (x_left, y_up, TILE_SIZE * SCALE_FACTOR, short_side))
            pygame.draw.rect(screen, DARK_GREY, (x_left + TILE_SIZE * SCALE_FACTOR - short_side, y_up, short_side, TILE_SIZE * SCALE_FACTOR))
            triangle_vertices = [(x_right, y_up), (x_right, y_up+3*short_side), (x_right-3*short_side, y_up)]
        if c[1] == 'D':
            pygame.draw.rect(screen, DARK_GREY, (x_left, y_up + TILE_SIZE * SCALE_FACTOR - short_side, TILE_SIZE * SCALE_FACTOR, short_side))
            pygame.draw.rect(screen, DARK_GREY, (x_left + TILE_SIZE * SCALE_FACTOR - short_side, y_up, short_side, TILE_SIZE * SCALE_FACTOR))
            triangle_vertices = [(x_right, y_down), (x_right, y_down-3*short_side), (x_right-3*short_side, y_down)]
        if c[1] == 'L':
            pygame.draw.rect(screen, DARK_GREY, (x_left, y_up + TILE_SIZE * SCALE_FACTOR - short_side, TILE_SIZE * SCALE_FACTOR, short_side))
            pygame.draw.rect(screen, DARK_GREY, (x_left, y_up, short_side, TILE_SIZE * SCALE_FACTOR))
            triangle_vertices = [(x_left, y_down), (x_left, y_down-3*short_side), (x_left+3*short_side, y_down)]
        if c[1] != '_':
            pygame.draw.polygon(screen, DARK_GREY, triangle_vertices)
    
    # Draw the Energy.
    if c[0] == 'E' and c[1] in ['U','R','D','L','X']:
        if c[1] != 'X':
            direction_char = c[1]
        center = (
            draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
            draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
        )
        pygame.draw.rect(screen, GREEN, (draw_position[0] * TILE_SIZE * SCALE_FACTOR, draw_position[1] * TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR))

        relative_vertices = [
            (-size,size/2),
            (0,0),
            (size,size/2),
            (size,0),
            (0,-size/2),
            (-size,0)
        ]


        if c[1] != 'X':
            # Rotate the polygon according to the direction_char
            if direction_char == 'U':
                relative_rotated_vertices = relative_vertices
            elif direction_char == 'L':
                relative_rotated_vertices = [
                    (vertex[1], -vertex[0]) for vertex in relative_vertices
                ]
            elif direction_char == 'D':
                relative_rotated_vertices = [
                    (-vertex[0], -vertex[1]) for vertex in relative_vertices
                ]
            elif direction_char == 'R':
                relative_rotated_vertices = [
                    (-vertex[1], vertex[0]) for vertex in relative_vertices
                ]
            rotated_vertices = [
                (vertex[0]+center[0], vertex[1]+center[1]) for vertex in relative_rotated_vertices
            ]
            # Draw the rotated triangle
            pygame.draw.polygon(screen, WHITE, rotated_vertices)

        if c[1] == 'X':
            # Draw different circles inside the blob
            num_circles = random.randint(2, 5)  # You can adjust the range as needed
            for _ in range(num_circles):
                circle_radius = random.uniform(TILE_SIZE * 0.1, TILE_SIZE * 0.4)
                circle_position = (
                    random.uniform(center[0] - TILE_SIZE * SCALE_FACTOR / 2, center[0] + TILE_SIZE * SCALE_FACTOR / 2),
                    random.uniform(center[1] - TILE_SIZE * SCALE_FACTOR / 2, center[1] + TILE_SIZE * SCALE_FACTOR / 2)
                )
                pygame.draw.circle(screen, WHITE, (int(circle_position[0]), int(circle_position[1])), int(circle_radius))

    
    if c == 'WL':
        pygame.draw.rect(screen, DARK_GREY, (draw_position[0] * TILE_SIZE * SCALE_FACTOR, draw_position[1] * TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR))
    if c == 'SF':
        #pygame.draw.rect(screen, VERY_DARK_GREY, (draw_position[0] * TILE_SIZE * SCALE_FACTOR, draw_position[1] * TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR))
        rect = pygame.Rect(draw_position[0] * TILE_SIZE * SCALE_FACTOR,
            draw_position[1] * TILE_SIZE * SCALE_FACTOR,
            TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR)
        pygame.draw.rect(screen, VERY_DARK_GREY, rect)

        dot_radius = 1
        dot_color = WHITE
        dot_spacing = 5  # Adjust dot spacing as needed

        for y in range(rect.top, rect.bottom, dot_spacing):
            for x in range(rect.left, rect.right, dot_spacing):
                pygame.draw.circle(screen, dot_color, (x, y), dot_radius)

    if c == 'DC' or c == 'DO':
        door_is_closed = (c == 'DC')
        if c == 'DC':
            outer_color, inner_color = [DARK_GREEN, DARK_GREY]
        else:
            outer_color, inner_color = [GREEN, BLACK]
            
        center = (
            draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
            draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
        )

        # Calculate the size and position of the filled GREEN / DARK_GREEN tile
        green_tile_rect = pygame.Rect(
            center[0] - TILE_SIZE * SCALE_FACTOR / 2,
            center[1] - TILE_SIZE * SCALE_FACTOR / 2,
            TILE_SIZE * SCALE_FACTOR,
            TILE_SIZE * SCALE_FACTOR
        )
        
        # Draw the filled GREEN / DARK_GREEN tile
        pygame.draw.rect(screen, outer_color, green_tile_rect)
        
        # Calculate the size and position of the centered DARK_GREY square
        dark_grey_square_size = TILE_SIZE * SCALE_FACTOR * 0.8  # Adjust as needed
        dark_grey_square_rect = pygame.Rect(
            center[0] - dark_grey_square_size / 2,
            center[1] - dark_grey_square_size / 2,
            dark_grey_square_size,
            dark_grey_square_size
        )
        
        # Draw the centered DARK_GREY square
        pygame.draw.rect(screen, inner_color, dark_grey_square_rect)

        
    # Draw the shoes and the thief.
    if (c.startswith('s') and c[1] in element_chars) or c=='th':
        if True:
            if c=='th':
                pygame.draw.rect(screen, RED, ((draw_position[0])*2*side, (draw_position[1])*2*side, 2*side, 2*side))
                pygame.draw.rect(screen, WHITE, ((draw_position[0]+0.1)*2*side, (draw_position[1]+0.1)*2*side, 0.8*2*side, 0.8*2*side))
                shoe_color = BLACK
            else:
                element_char = c[1]
                shoe_color = color_from_char(element_char)
            
            shoe_center = (
                draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
                draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
            )
            
            # Define the size of the shoe rectangles
            rectangle1_width = TILE_SIZE * 0.4*1.5
            rectangle1_height = TILE_SIZE * 0.6*2.0
            
            rectangle2_width = TILE_SIZE * 0.5*1.5
            rectangle2_height = TILE_SIZE * 0.3*1.5
            
            # Draw the first rectangle
            pygame.draw.rect(screen, shoe_color, (shoe_center[0] - rectangle1_width / 2 + TILE_SIZE * 0.2, shoe_center[1] - rectangle1_height / 2, rectangle1_width, rectangle1_height))
            
            # Draw the second rectangle forming an "L" shape
            pygame.draw.rect(screen, shoe_color, (shoe_center[0] - rectangle1_width / 2 - rectangle2_width + TILE_SIZE * 0.5, shoe_center[1] - rectangle2_height / 2 + TILE_SIZE * 0.4, rectangle2_width, rectangle2_height))
            if c=='th':
                polygon_vertices = (
                    (draw_position[0]*2*side,draw_position[1]*2*side+0.07*2*side),
                    (draw_position[0]*2*side,draw_position[1]*2*side),
                    (draw_position[0]*2*side+0.07*side,draw_position[1]*2*side),
                    (draw_position[0]*2*side+2*side,draw_position[1]*2*side+0.93*2*side),
                    (draw_position[0]*2*side+2*side,draw_position[1]*2*side+2*side),
                    (draw_position[0]*2*side+0.93*2*side,draw_position[1]*2*side+2*side),
                    )
                pygame.draw.polygon(screen, RED, polygon_vertices)

    # Draw the Keys.
    for color_char in color_chars:
        if c == 'k' + color_char:
            color = color_from_char(color_char)
            circle_center = ((draw_position[0]+0.2)*TILE_SIZE*SCALE_FACTOR,(draw_position[1]+0.5)*TILE_SIZE*SCALE_FACTOR)
            pygame.draw.circle(screen, color, circle_center, TILE_SIZE*SCALE_FACTOR *0.15)
            pygame.draw.circle(screen, BLACK, circle_center, TILE_SIZE*SCALE_FACTOR *0.10)
            pygame.draw.rect(screen, color, ((draw_position[0]+0.3)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.475)*TILE_SIZE*SCALE_FACTOR, 0.6*TILE_SIZE*SCALE_FACTOR, 0.05*TILE_SIZE*SCALE_FACTOR))
            pygame.draw.rect(screen, color, ((draw_position[0]+0.7)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.5)*TILE_SIZE*SCALE_FACTOR, 0.05*TILE_SIZE*SCALE_FACTOR, 0.15*TILE_SIZE*SCALE_FACTOR))
            pygame.draw.rect(screen, color, ((draw_position[0]+0.8)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.5)*TILE_SIZE*SCALE_FACTOR, 0.05*TILE_SIZE*SCALE_FACTOR, 0.15*TILE_SIZE*SCALE_FACTOR))


    # Draw the Bomb.
    if c == 'bo':
        bomb_center = (
            draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
            draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
        )
        circle1_radius = TILE_SIZE * 0.5
        pygame.draw.circle(screen, GREY, (int(bomb_center[0]), int(bomb_center[1])), int(circle1_radius))
        
        pygame.draw.rect(screen, GREY, ((draw_position[0]+0.46)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.2)*TILE_SIZE*SCALE_FACTOR, 0.1*TILE_SIZE*SCALE_FACTOR, 0.1*TILE_SIZE*SCALE_FACTOR))

    # Draw the button
    if c[0] == '.' and c[1] in button_chars:
        button_char = c[1]
        circle_center = (
            draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
            draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
        )
        pygame.draw.circle(screen, color_from_button_char(button_char), (circle_center[0], circle_center[1]), TILE_SIZE // 3.5)
    
    # Draw the One Pass.
    if c == '1p':
        center = (
            draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
            draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
        )

        # Define the size of the bomb circles
        circle2_radius = TILE_SIZE * 0.8

        # Draw the second circle forming an "X" shape
        pygame.draw.line(screen, GREY, (center[0] - circle2_radius, center[1] - circle2_radius), (center[0] + circle2_radius, center[1] + circle2_radius), 2)
        pygame.draw.line(screen, GREY, (center[0] - circle2_radius, center[1] + circle2_radius), (center[0] + circle2_radius, center[1] - circle2_radius), 2)

    # Draw the Trap.
    if c == 'TA' or c == 'TI':
        center = (
            draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
            draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
        )

        # Define the size of the trap
        circle2_radius = TILE_SIZE * 0.8

        # Draw the second circle forming an "X" shape
        pygame.draw.line(screen, BROWN, (center[0] - circle2_radius, center[1] - circle2_radius), (center[0] + circle2_radius, center[1] + circle2_radius), 6)
        pygame.draw.line(screen, BROWN, (center[0] - circle2_radius, center[1] + circle2_radius), (center[0] + circle2_radius, center[1] - circle2_radius), 6)

    # Draw the Teleport
    if c == 'TP':
        center = (
            draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
            draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
        )
        pygame.draw.circle(screen, WHITE, center, int(TILE_SIZE * SCALE_FACTOR * 0.45))
        pygame.draw.circle(screen, BLUE, center, int(TILE_SIZE * SCALE_FACTOR * 0.375))

    # Draw the Cloner
    if c[0] == 'C' and c[1] in ['_','U','R','D','L']:
        center = (
            draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
            draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
        )
        pygame.draw.rect(screen, DARK_GREY, (draw_position[0] * TILE_SIZE * SCALE_FACTOR, draw_position[1] * TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR))
        pygame.draw.circle(screen, WHITE, center, int(TILE_SIZE * SCALE_FACTOR * 0.45))
        pygame.draw.circle(screen, DARK_GREY, center, int(TILE_SIZE * SCALE_FACTOR * 0.375))
        pygame.draw.circle(screen, WHITE, center, int(TILE_SIZE * SCALE_FACTOR * 0.3))
        pygame.draw.circle(screen, DARK_GREY, center, int(TILE_SIZE * SCALE_FACTOR * 0.225))
    
    # Draw the Hint
    if c == 'hi':
        center = (
            draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
            draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
        )
        pygame.draw.circle(screen, WHITE, center, int(TILE_SIZE * SCALE_FACTOR * 0.45))
        pygame.draw.circle(screen, BLACK, center, int(TILE_SIZE * SCALE_FACTOR * 0.375))
        draw_text(screen, '?', WHITE, center)  # Change '?' to the character you want
    
    # Draw an arbitrary character.
    # Characters in the overworld can be erased; those in the downworld cannot.
    if c[0] == 'w':
        center = (
            draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
            draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
        )
        draw_text(screen, c[1], WHITE, center)

    # Draw the chips and the socket.
    if c == 'ch' or c == 'so': 
        if c=='so':
            side = TILE_SIZE*SCALE_FACTOR
            pygame.draw.rect(screen, DARK_GREY, ((draw_position[0])*TILE_SIZE*SCALE_FACTOR, (draw_position[1])*TILE_SIZE*SCALE_FACTOR, TILE_SIZE*SCALE_FACTOR, TILE_SIZE*SCALE_FACTOR))
            polygon_vertices = (
                ((draw_position[0]+0.2)*side,(draw_position[1]+0.1)*side),
                ((draw_position[0]+0.2)*side,(draw_position[1]+0.9)*side),
                ((draw_position[0]+0.35)*side,(draw_position[1]+0.9)*side),
                ((draw_position[0]+0.35)*side,(draw_position[1]+0.75)*side),
                ((draw_position[0]+0.65)*side,(draw_position[1]+0.75)*side),
                ((draw_position[0]+0.65)*side,(draw_position[1]+0.9)*side),
                ((draw_position[0]+0.8)*side,(draw_position[1]+0.9)*side),
                ((draw_position[0]+0.8)*side,(draw_position[1]+0.1)*side),
                ((draw_position[0]+0.65)*side,(draw_position[1]+0.1)*side),
                ((draw_position[0]+0.65)*side,(draw_position[1]+0.25)*side),
                ((draw_position[0]+0.35)*side,(draw_position[1]+0.25)*side),
                ((draw_position[0]+0.35)*side,(draw_position[1]+0.1)*side),
                )
            pygame.draw.polygon(screen, VERY_DARK_GREY, polygon_vertices)
            #pygame.draw.rect(screen, DARK_GREY, (draw_position[0] * TILE_SIZE * SCALE_FACTOR, draw_position[1] * TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR))
            pygame.draw.rect(screen, BLUE, ((draw_position[0]+0.35)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.35)*TILE_SIZE*SCALE_FACTOR, 0.3*TILE_SIZE*SCALE_FACTOR, 0.3*TILE_SIZE*SCALE_FACTOR))
        else:
            chip_color = GREY
        chip_center = (
            draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
            draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
        )
        
        # Define the size of the chip
        chip_width = 0.8 * TILE_SIZE
        chip_height = 1.6 * TILE_SIZE
        
        # Draw the main grey rectangle for Chip
        if c=='ch':
            pygame.draw.rect(screen, chip_color, (chip_center[0] - chip_width / 2, chip_center[1] - chip_height / 2, chip_width, chip_height))
        
        # Define the size and position of the rectangular pins
        pin_size = chip_width / 8
        pin_positions = [
            (chip_center[0] - chip_width / 2 - pin_size, chip_center[1] + chip_height * 3/8),
            (chip_center[0] - chip_width / 2 - pin_size, chip_center[1] + chip_height * 1/8),
            (chip_center[0] - chip_width / 2 - pin_size, chip_center[1] - chip_height * 1/8),
            (chip_center[0] - chip_width / 2 - pin_size, chip_center[1] - chip_height * 3/8),
            
            (chip_center[0] + chip_width / 2, chip_center[1] + chip_height * 3/8),
            (chip_center[0] + chip_width / 2, chip_center[1] + chip_height * 1/8),
            (chip_center[0] + chip_width / 2, chip_center[1] - chip_height * 1/8),
            (chip_center[0] + chip_width / 2, chip_center[1] - chip_height * 3/8)
        ]
        
        # Draw the 8 rectangular pins
        for pin_position in pin_positions:
            pygame.draw.rect(screen, GREY, (pin_position[0], pin_position[1], pin_size, pin_size))

    # Draw the Separation Lines.
    if c[0] == 'L' and (c[1] in direction_chars or c[1] == 'X'):
        if c[1] == 'X':
            line_direction_chars = ['D','R']
        else:
            line_direction_chars = c[1]

        for direction_char in line_direction_chars:
            center = (
                draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
                draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
            )
            
            small_side_rectangle = TILE_SIZE * 0.1
            if direction_char == 'U':
                x_upper_left = center[0] - TILE_SIZE * SCALE_FACTOR / 2
                y_upper_left = center[1] - TILE_SIZE * SCALE_FACTOR / 2
                height_rectangle = small_side_rectangle
                width_rectangle = TILE_SIZE*SCALE_FACTOR
            if direction_char == 'D':
                x_upper_left = center[0] - TILE_SIZE * SCALE_FACTOR / 2
                y_upper_left = center[1] + TILE_SIZE * SCALE_FACTOR / 2 - TILE_SIZE * 0.1
                height_rectangle = small_side_rectangle
                width_rectangle = TILE_SIZE*SCALE_FACTOR
            if direction_char == 'L':
                x_upper_left = center[0] - TILE_SIZE * SCALE_FACTOR / 2
                y_upper_left = center[1] - TILE_SIZE * SCALE_FACTOR / 2
                height_rectangle = TILE_SIZE*SCALE_FACTOR
                width_rectangle = small_side_rectangle
            if direction_char == 'R':
                x_upper_left = center[0] + TILE_SIZE * SCALE_FACTOR / 2 - TILE_SIZE * 0.1
                y_upper_left = center[1] - TILE_SIZE * SCALE_FACTOR / 2
                height_rectangle = TILE_SIZE*SCALE_FACTOR
                width_rectangle = small_side_rectangle
            pygame.draw.rect(screen, GREY, (x_upper_left, y_upper_left, width_rectangle, height_rectangle))

    # The Overworld
    if c == 'W_':
        pygame.draw.rect(screen, BLUE, (draw_position[0] * TILE_SIZE * SCALE_FACTOR, draw_position[1] * TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR))
    if c == 'DI':
        pygame.draw.rect(screen, DARK_RED, (draw_position[0] * TILE_SIZE * SCALE_FACTOR, draw_position[1] * TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR))
    if c[0] == 'n' and c[1] in ['_','U','R','D','L']:
        pygame.draw.rect(screen, BROWN, (draw_position[0] * TILE_SIZE * SCALE_FACTOR, draw_position[1] * TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR))
    if c == 'FK':
        pygame.draw.rect(screen, DARK_GREEN, (draw_position[0] * TILE_SIZE * SCALE_FACTOR, draw_position[1] * TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR))
    if c[0] == 'c' and c[1] in direction_chars:
        pygame.draw.rect(screen, WHITE, (draw_position[0] * TILE_SIZE * SCALE_FACTOR, draw_position[1] * TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR))
    

    # Draw the Doors.
    for color_char in color_chars:
        if c == 'd' + color_char:
            # First, draw a wall like it were a wall.
            pygame.draw.rect(screen, DARK_GREY, (draw_position[0] * TILE_SIZE * SCALE_FACTOR, draw_position[1] * TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR))
            
            # Inside your drawing loop for the red door with a keyhole
            door_center = (
                draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
                draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
            )
            
            # Define the vertices of the red door shape
            door_width = TILE_SIZE
            door_height = TILE_SIZE * 4 // 3
            door_vertices = [
                (door_center[0] - door_width / 2, door_center[1] - door_height / 2),
                (door_center[0] + door_width / 2, door_center[1] - door_height / 2),
                (door_center[0] + door_width / 2, door_center[1] + door_height / 2),
                (door_center[0] - door_width / 2, door_center[1] + door_height / 2),
            ]

            # Draw the red door shape
            pygame.draw.polygon(screen, color_from_char(color_char), door_vertices)
            
            # Draw the black keyhole at the center of the red door
            keyhole_size = TILE_SIZE // 6
            pygame.draw.circle(screen, BLACK, (int(door_center[0]+TILE_SIZE*0.2), int(door_center[1])), keyhole_size)
            

    for direction_char in direction_chars:
        # Draw the Fireball
        if c == 'f' + direction_char:
            if direction_char == 'U':
                pygame.draw.ellipse(screen, RED, ((draw_position[0]+0.25)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.05)*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR, 0.95*TILE_SIZE*SCALE_FACTOR))
                pygame.draw.ellipse(screen, ORANGE, ((draw_position[0]+0.25)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.05)*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR, 0.8*TILE_SIZE*SCALE_FACTOR))
                pygame.draw.ellipse(screen, YELLOW, ((draw_position[0]+0.25)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.05)*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR, 0.65*TILE_SIZE*SCALE_FACTOR))
                pygame.draw.ellipse(screen, WHITE, ((draw_position[0]+0.25)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.05)*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR))
            if direction_char == 'R':
                pygame.draw.ellipse(screen, RED, ((draw_position[0]+0.0)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.25)*TILE_SIZE*SCALE_FACTOR, 0.95*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR))
                pygame.draw.ellipse(screen, ORANGE, ((draw_position[0]+0.15)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.25)*TILE_SIZE*SCALE_FACTOR, 0.8*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR))
                pygame.draw.ellipse(screen, YELLOW, ((draw_position[0]+0.3)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.25)*TILE_SIZE*SCALE_FACTOR, 0.65*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR))
                pygame.draw.ellipse(screen, WHITE, ((draw_position[0]+0.45)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.25)*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR))
            if direction_char == 'D':
                pygame.draw.ellipse(screen, RED, ((draw_position[0]+0.25)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0)*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR, 0.95*TILE_SIZE*SCALE_FACTOR))
                pygame.draw.ellipse(screen, ORANGE, ((draw_position[0]+0.25)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.15)*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR, 0.8*TILE_SIZE*SCALE_FACTOR))
                pygame.draw.ellipse(screen, YELLOW, ((draw_position[0]+0.25)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.3)*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR, 0.65*TILE_SIZE*SCALE_FACTOR))
                pygame.draw.ellipse(screen, WHITE, ((draw_position[0]+0.25)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.45)*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR))
            if direction_char == 'L':
                pygame.draw.ellipse(screen, RED, ((draw_position[0]+0.05)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.25)*TILE_SIZE*SCALE_FACTOR, 0.95*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR))
                pygame.draw.ellipse(screen, ORANGE, ((draw_position[0]+0.05)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.25)*TILE_SIZE*SCALE_FACTOR, 0.8*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR))
                pygame.draw.ellipse(screen, YELLOW, ((draw_position[0]+0.05)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.25)*TILE_SIZE*SCALE_FACTOR, 0.65*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR))
                pygame.draw.ellipse(screen, WHITE, ((draw_position[0]+0.05)*TILE_SIZE*SCALE_FACTOR, (draw_position[1]+0.25)*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR, 0.5*TILE_SIZE*SCALE_FACTOR))

        # Draw the Glider
        if c == 'g' + direction_char:
            glider_center = (
                draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
                draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
            )

            # Define the vertices of the equilateral triangle (rhombus)
            triangle_size = TILE_SIZE // 1.2
            relative_vertices = [
                (0, -triangle_size),
                (triangle_size * math.sqrt(3) / 2, triangle_size / 2),
                (-triangle_size * math.sqrt(3) / 2, triangle_size / 2)
            ]
    
            # Rotate the triangle based on the direction_char
            if direction_char == 'U':
                relative_rotated_vertices = relative_vertices
            elif direction_char == 'L':
                relative_rotated_vertices = [
                    (vertex[1], -vertex[0]) for vertex in relative_vertices
                ]
            elif direction_char == 'D':
                relative_rotated_vertices = [
                    (-vertex[0], -vertex[1]) for vertex in relative_vertices
                ]
            elif direction_char == 'R':
                relative_rotated_vertices = [
                    (-vertex[1], vertex[0]) for vertex in relative_vertices
                ]
            rotated_vertices = [
                (vertex[0]+glider_center[0], vertex[1]+glider_center[1]) for vertex in relative_rotated_vertices
            ]

            # Draw the rotated triangle
            pygame.draw.polygon(screen, GREY, rotated_vertices)
        
        # Draw the Ball
        if c == 'o' + direction_char:
            center = (
                draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
                draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
            )
            pygame.draw.circle(screen, PURPLE, (center[0], center[1]), TILE_SIZE // 1.5)

        # Draw the Saturn
        if c == 'q' + direction_char:
            center = (
                draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
                draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
            )
            pygame.draw.circle(screen, LIGHT_BLUE, (center[0], center[1]), TILE_SIZE // 1.5)

        # Draw the Blob
        if c == 'b' + direction_char:
            center = (
                draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
                draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
            )

            # Draw the random blob shape in green
            pygame.draw.ellipse(screen, GREEN, (center[0] - TILE_SIZE * SCALE_FACTOR / 2, center[1] - TILE_SIZE * SCALE_FACTOR / 2, TILE_SIZE * SCALE_FACTOR / 1.5, TILE_SIZE * SCALE_FACTOR / 1.5))

            # Draw different circles inside the blob
            num_circles = random.randint(2, 5)  # You can adjust the range as needed
            for _ in range(num_circles):
                circle_radius = random.uniform(TILE_SIZE * 0.1, TILE_SIZE * 0.4)
                circle_position = (
                    random.uniform(center[0] - TILE_SIZE * SCALE_FACTOR / 2, center[0] + TILE_SIZE * SCALE_FACTOR / 2),
                    random.uniform(center[1] - TILE_SIZE * SCALE_FACTOR / 2, center[1] + TILE_SIZE * SCALE_FACTOR / 2)
                )
                pygame.draw.circle(screen, GREEN, (int(circle_position[0]), int(circle_position[1])), int(circle_radius))
        
        # Draw the Paramecia.
        if c == 'p' + direction_char:
            rectangle_center = (
                draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
                draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
            )
            
            # Define the size of the rectangle
            smaller_size = TILE_SIZE * SCALE_FACTOR * 0.25
            bigger_size = TILE_SIZE * SCALE_FACTOR * 0.75
            
            if direction_char == 'U' or direction_char == 'D':
                rectangle_width = smaller_size
                rectangle_height = bigger_size
            elif direction_char == 'R' or direction_char == 'L':
                rectangle_width = bigger_size
                rectangle_height = smaller_size
            
            # Draw the rectangle centered within the TILE
            pygame.draw.rect(
                screen,
                BROWN,
                (
                    rectangle_center[0] - rectangle_width / 2,
                    rectangle_center[1] - rectangle_height / 2,
                    rectangle_width,
                    rectangle_height
                )
            )

        # Draw the Ants.
        if c == 'a' + direction_char:
            ant_center = (
                draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
                draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
            )
            
            length = TILE_SIZE * SCALE_FACTOR * 0.4
            
            # Draw the first line forming an "X" shape
            x_left = ant_center[0] - length
            x_right = ant_center[0] + length
            x = ant_center[0]
            y_left = ant_center[1] - length
            y_right = ant_center[1] + length
            y = ant_center[1]

            if direction_char == 'U' or direction_char == 'D':
                pygame.draw.line(screen, WHITE, (x_left, y_left), (x_right, y_right), 2)
                pygame.draw.line(screen, WHITE, (x_left, y), (x_right, y), 2)
                pygame.draw.line(screen, WHITE, (x_left, y_right), (x_right, y_left), 2)
            elif direction_char == 'R' or direction_char == 'L':
                pygame.draw.line(screen, WHITE, (x_left, y_left), (x_right, y_right), 2)
                pygame.draw.line(screen, WHITE, (x, y_left), (x, y_right), 2)
                pygame.draw.line(screen, WHITE, (x_left, y_right), (x_right, y_left), 2)
            
            # Define the sizes of the ant circles
            small_circle_radius = TILE_SIZE * 0.2
            medium_circle_radius = TILE_SIZE * 0.3
            large_circle_radius = TILE_SIZE * 0.4
            
            # Draw three circles aligned vertically
            x_left = ant_center[0] - TILE_SIZE * SCALE_FACTOR / 4
            x = ant_center[0]
            x_right = ant_center[0] + TILE_SIZE * SCALE_FACTOR / 4
            y_left = ant_center[1] - TILE_SIZE * SCALE_FACTOR / 4
            y = ant_center[1]
            y_right = ant_center[1] + TILE_SIZE * SCALE_FACTOR / 4
            
            if direction_char == 'U':
                pygame.draw.circle(screen, YELLOW, (int(x), int(y_left)), int(small_circle_radius))
                pygame.draw.circle(screen, YELLOW, (int(x), int(y)), int(medium_circle_radius))
                pygame.draw.circle(screen, YELLOW, (int(x), int(y_right)), int(large_circle_radius))
            if direction_char == 'D':
                pygame.draw.circle(screen, YELLOW, (int(x), int(y_right)), int(small_circle_radius))
                pygame.draw.circle(screen, YELLOW, (int(x), int(y)), int(medium_circle_radius))
                pygame.draw.circle(screen, YELLOW, (int(x), int(y_left)), int(large_circle_radius))
            if direction_char == 'R':
                pygame.draw.circle(screen, YELLOW, (int(x_right), int(y)), int(small_circle_radius))
                pygame.draw.circle(screen, YELLOW, (int(x), int(y)), int(medium_circle_radius))
                pygame.draw.circle(screen, YELLOW, (int(x_left), int(y)), int(large_circle_radius))
            if direction_char == 'L':
                pygame.draw.circle(screen, YELLOW, (int(x_left), int(y)), int(small_circle_radius))
                pygame.draw.circle(screen, YELLOW, (int(x), int(y)), int(medium_circle_radius))
                pygame.draw.circle(screen, YELLOW, (int(x_right), int(y)), int(large_circle_radius))

            # Define the size of the bomb circles
        
            # Specify the rotation angle in degrees
            #rotation_angle_degrees = 90
            
        # Draw the Tanks.
        if c == 't' + direction_char:
            rectangle_center = (
                draw_position[0] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2,
                draw_position[1] * TILE_SIZE * SCALE_FACTOR + TILE_SIZE * SCALE_FACTOR // 2
            )
            
            # Define the size of the rectangle
            smaller_size = TILE_SIZE * SCALE_FACTOR * 0.45
            bigger_size = TILE_SIZE * SCALE_FACTOR * 0.65
            
            if direction_char == 'U' or direction_char == 'D':
                rectangle_width = smaller_size
                rectangle_height = bigger_size
            elif direction_char == 'R' or direction_char == 'L':
                rectangle_width = bigger_size
                rectangle_height = smaller_size
            
            # Draw the rectangle centered within the TILE
            pygame.draw.rect(
                screen,
                BLUE,
                (
                    rectangle_center[0] - rectangle_width / 2,
                    rectangle_center[1] - rectangle_height / 2,
                    rectangle_width,
                    rectangle_height
                )
            )
            
            # Calculate the size and position of the smaller rectangle (cannon)
            smaller_size = TILE_SIZE * SCALE_FACTOR * 0.1
            bigger_size = TILE_SIZE * SCALE_FACTOR * 0.4
            if direction_char == 'U' or direction_char == 'D':
                cannon_width = smaller_size
                cannon_height = bigger_size
            elif direction_char == 'R' or direction_char == 'L':
                cannon_width = bigger_size
                cannon_height = smaller_size
            
            if direction_char == 'D':
                delta_x = - cannon_width // 2
                delta_y = + cannon_height // 2
            if direction_char == 'U':
                delta_x = - cannon_width // 2
                delta_y = - cannon_height * 3 // 2
            if direction_char == 'R':
                delta_x = + cannon_width // 2
                delta_y = - cannon_height // 2
            if direction_char == 'L':
                delta_x = - cannon_width * 3 // 2
                delta_y = - cannon_height // 2

            cannon_rect = pygame.Rect(
                rectangle_center[0] + int(delta_x),
                rectangle_center[1] + int(delta_y),  # Move up from the tank body
                cannon_width,
                cannon_height
            )
            
            # Draw the smaller rectangle (cannon)
            pygame.draw.rect(screen, BLUE, cannon_rect)

        # Draw the piranhas Monsters.
        if c == 'm' + direction_char:
            if (int(current_time*2)%2) == 0:
                pygame.draw.circle(screen, RED, ((draw_position[0]+0.5) * 2*size, (draw_position[1]+0.5) * 2*size), int(0.45*2*size))
                pygame.draw.rect(screen, WHITE, ((draw_position[0]+0.2) * 2*size, (draw_position[1]+0.1) * 2*size, 0.6*2*size, 0.8*2*size))
                pygame.draw.rect(screen, BLACK, ((draw_position[0]+0.2) * 2*size, (draw_position[1]+0.3) * 2*size, 0.6*2*size, 0.4*2*size))
            else:
                pygame.draw.rect(screen, RED, (draw_position[0] * 2*size, (draw_position[1]+0.2) * 2*size, 2*size, 0.6*2*size))
                pygame.draw.rect(screen, WHITE, ((draw_position[0]+0.1) * 2*size, (draw_position[1]+0.3) * 2*size, 0.8*2*size, 0.4*2*size))

def display_message(message, big=False):
    if big == False:
        horizontal_side = 6.8
        vertical_side = 4.8
        color = BLACK
    else:
        horizontal_side = 11.8
        vertical_side = 6.8
        color = BLUE

    x_left = TILE_SIZE*SCALE_FACTOR*1.1
    y_up = TILE_SIZE*SCALE_FACTOR*1.1
    pygame.draw.rect(screen, WHITE, (x_left, y_up, TILE_SIZE * SCALE_FACTOR * horizontal_side, TILE_SIZE * SCALE_FACTOR * vertical_side))
    x_left = TILE_SIZE*SCALE_FACTOR*1.2
    y_up = TILE_SIZE*SCALE_FACTOR*1.2
    pygame.draw.rect(screen, BLUE, (x_left, y_up, TILE_SIZE * SCALE_FACTOR * (horizontal_side - 0.2), TILE_SIZE * SCALE_FACTOR * (vertical_side - 0.2)))

    font_size = 40
    font = pygame.font.SysFont(None, font_size)
    # Render each line of the text
    lines = message.split('\n')
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, YELLOW)
        text_rect = text_surface.get_rect()
        if big == False:
            text_rect.center = (TILE_SIZE*SCALE_FACTOR*4.5, TILE_SIZE*SCALE_FACTOR*(3.5+i/2-len(lines)/4))
        else:
            text_rect.center = (TILE_SIZE*SCALE_FACTOR*7, TILE_SIZE*SCALE_FACTOR*(4.5+i/2-len(lines)/4))
        screen.blit(text_surface, text_rect)
    pygame.display.flip()

# The cloner list and trap list must be given as a list, of lists of the positions of
# the (red or brown) button and the corresponding cloner or trap (respectively).
# The button is before the cloner / trap.
# The coordinates must be given by (column, row) which corresponds (x, y).
# The default for chips left at start is the number of chips of the board.
class Level:
    def __init__(self, level_number, downworld, overworld, time_limit=-1, chips_left_at_start=-1, cloner_list=[], trap_list=[], hint_text="No hint. \nKeep it up!", level_title=""):
        self.downworld = downworld
        self.overworld = overworld
        self.level_number = level_number
        self.time_limit = time_limit
        self.chips_left_at_start = chips_left_at_start
        self.cloner_list = cloner_list
        self.trap_list = trap_list
        self.hint_text = hint_text
        self.level_title = level_title


# Main game loop
def game_loop(level, last_level, repetition_level, max_level, is_the_challenge_starting):
    # Initialize the Level 
    level_number = copy.deepcopy(level.level_number)
    if (level_number == last_level):
        repetition_level += 1
    else:
        last_level = level_number
        repetition_level = 0

    # Initialize the Level 
    level_number = copy.deepcopy(level.level_number)
    downworld = copy.deepcopy(level.downworld)
    overworld = copy.deepcopy(level.overworld)
    chips_left_at_start = copy.deepcopy(level.chips_left_at_start)
    cloner_list = copy.deepcopy(level.cloner_list)
    trap_list = copy.deepcopy(level.trap_list)
    time_limit = copy.deepcopy(level.time_limit)
    hint_text = copy.deepcopy(level.hint_text)
    level_title = copy.deepcopy(level.level_title)

    if level_title == "":
        level_title = f"Level {level_number}"

    if chips_left_at_start == -1:
        chips_left_at_start = 0
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if downworld[i][j] == 'ch':
                    chips_left_at_start += 1
    #print("chips left at start = ", chips_left_at_start)

    # The teleport list is in reversed reading order
    teleport_list = []
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if downworld[i][j] == 'TP':
                teleport_list.append([i,j])
    teleport_list.reverse()
    #print("teleport list is ", teleport_list)

    #print(cloner_list)
    # The direction of the object above the cloner is adjusted to be equal to the direction of the cloner below.
    # If they were by mistake unequal, they now become equal.
    align_cloners_with_objects_above(downworld, overworld)
    tools_acquired = {'r': 0, 'y': 0, 'g': 0, 'b': 0, 'F': 0, 'W': 0, 'I': 0, 'E': 0, 'c': chips_left_at_start}
    
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if overworld[i][j][0] == 'c' and overworld[i][j][1] in direction_chars:
                chip_pos = [i,j]
                last_direction_char = overworld[i][j][1]    # I can't make it work better

    # Initialize clock for controlling speed
    clock = pygame.time.Clock()
    last_move_time = 0    # The last time Chip moved.
    won_time = 0
    lost_time = 0
    go_to_time = False
    ready_to_go_to = False
    ready_to_go_to_time = 0
    level_to_go_to = 0
    first_time_try_to_go_to = True
    first_iteration_of_while_loop = True
    any_key_was_pressed = False
    we_are_asking_yes_no_question = False
    var = []
    # Until the player presses a key to start the game.
    start_time = -1
    
    # This variable allows to avoid to move twice in the same turn an object, or to move an object just cloned.
    already_moved = []
    for i in range(GRID_SIZE):
        new_row = []
        for j in range(GRID_SIZE):
            if (downworld[i][j][0] == 'C' and downworld[i][j][1] in direction_chars):
                # The reason for this condition is that monsters on top of "cloner" will be treated
                # as if the have "already" moved! So they are freezed. Except the red button is pushed.
                new_row.append(True)
            else:
                new_row.append(False)
        already_moved.append(new_row)

    #print("I start again!")
    #print("My tools are ", tools_acquired)

    while True:
        # Handle current and last times
        current_time = time.time()
        if first_iteration_of_while_loop == True:
            last_time = current_time
            first_iteration_of_while_loop = False
        
        # If the cloner created an object, I reinitialize the object on top of the cloner
        for index in range(len(cloner_list)):
            # Get the position of each cloner
            i, j = cloner_list[index][1]
            if overworld[i][j] != level.overworld[i][j]:
                overworld[i][j] = level.overworld[i][j]
                already_moved[i][j] = True
        
        # If the brown button associated to a trap is pressed (/ not pressed), the trap becomes inactive i.e. 'TI'
        # (/ active i.e. 'TA')
        for index in range(len(trap_list)):
            # Get the position of each trap
            # If a button is pressed, it changes the result.
            button_x, button_y = trap_list[index][0]
            trap_x, trap_y = trap_list[index][1]
            if overworld[button_x][button_y][0] in moving_chars and overworld[button_x][button_y][1] in ['_','U','R','D','L']:
                downworld[trap_x][trap_y] = 'TI'
            else:
                downworld[trap_x][trap_y] = 'TA'
       
        # DISPLAY THE BOARD
        # Update the display
        screen.fill(BLACK)

        # Get the top-left corner of the visible grid
        visible_grid_top_left_x, visible_grid_top_left_y = get_visible_grid_coords(chip_pos)
        
        # Display the Displayer of the tools acquired
        for i in range(5):
            for j in range(10):
                draw_position = (VISIBLE_GRID_SIZE + i, VISIBLE_GRID_SIZE - j)
                pygame.draw.rect(screen, WHITE, (draw_position[0] * TILE_SIZE * SCALE_FACTOR, draw_position[1] * TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR))
        
        tools_draw_position = (VISIBLE_GRID_SIZE + 1.5, VISIBLE_GRID_SIZE - 8)
        font = pygame.font.SysFont(None, 50)
        text = font.render("LEVEL", True, RED)
        text_rect = text.get_rect(center=((tools_draw_position[0]+1)*TILE_SIZE*SCALE_FACTOR, (tools_draw_position[1]-0.5)*TILE_SIZE*SCALE_FACTOR))
        screen.blit(text, text_rect)
        
        pygame.draw.rect(screen, BLACK, (tools_draw_position[0] * TILE_SIZE * SCALE_FACTOR, tools_draw_position[1] * TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR * 2, TILE_SIZE * SCALE_FACTOR))
        font = pygame.font.SysFont(None, 50)
        text = font.render(str(level_number), True, RED)
        text_rect = text.get_rect(center=((tools_draw_position[0]+1)*TILE_SIZE*SCALE_FACTOR, (tools_draw_position[1]+0.5)*TILE_SIZE*SCALE_FACTOR))
        screen.blit(text, text_rect)
        
        tools_draw_position = (VISIBLE_GRID_SIZE + 1.5, VISIBLE_GRID_SIZE - 6)
        font = pygame.font.SysFont(None, 50)
        text = font.render("TIME", True, RED)
        text_rect = text.get_rect(center=((tools_draw_position[0]+1)*TILE_SIZE*SCALE_FACTOR, (tools_draw_position[1]-0.5)*TILE_SIZE*SCALE_FACTOR))
        screen.blit(text, text_rect)
        
        pygame.draw.rect(screen, BLACK, (tools_draw_position[0] * TILE_SIZE * SCALE_FACTOR, tools_draw_position[1] * TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR * 2, TILE_SIZE * SCALE_FACTOR))
        font = pygame.font.SysFont(None, 50)
        
        if time_limit == -1:
            time_in_seconds = "---"
        else:
            if start_time == -1:
                time_in_seconds = time_limit
            else:
                if lost_time == 0 and won_time == 0:
                    time_in_seconds = max(0,int(time_limit - (current_time-start_time)))
                elif lost_time != 0 and won_time == 0:
                    time_in_seconds = max(0,int(time_limit - (lost_time-start_time)))
                elif won_time != 0 and lost_time == 0:
                    time_in_seconds = max(0,int(time_limit - (won_time-start_time)))
                else:
                    #print("ERROR! Chip both lost and won the game!")
                    quit()
        if time_in_seconds == 0 and lost_time == 0:
            lost_time = current_time
        time_in_seconds_str = str(time_in_seconds)
        text = font.render(time_in_seconds_str, True, RED)
        text_rect = text.get_rect(center=((tools_draw_position[0]+1)*TILE_SIZE*SCALE_FACTOR, (tools_draw_position[1]+0.5)*TILE_SIZE*SCALE_FACTOR))
        screen.blit(text, text_rect)
        
        tools_draw_position = (VISIBLE_GRID_SIZE + 1.5, VISIBLE_GRID_SIZE - 4)
        font = pygame.font.SysFont(None, 50)
        text = font.render("CHIPS LEFT", True, RED)
        text_rect = text.get_rect(center=((tools_draw_position[0]+1)*TILE_SIZE*SCALE_FACTOR, (tools_draw_position[1]-0.5)*TILE_SIZE*SCALE_FACTOR))
        screen.blit(text, text_rect)
        
        pygame.draw.rect(screen, BLACK, (tools_draw_position[0] * TILE_SIZE * SCALE_FACTOR, tools_draw_position[1] * TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR * 2, TILE_SIZE * SCALE_FACTOR))
        font = pygame.font.SysFont(None, 50)
        chips_left = str(max(0, tools_acquired.get('c')))
        text = font.render(chips_left, True, RED)
        text_rect = text.get_rect(center=((tools_draw_position[0]+1)*TILE_SIZE*SCALE_FACTOR, (tools_draw_position[1]+0.5)*TILE_SIZE*SCALE_FACTOR))
        screen.blit(text, text_rect)

        if downworld[chip_pos[0]][chip_pos[1]] == 'hi':
            hint_activated = True
        else:
            hint_activated = False

        for i in range(4):
            for j in range(2):
                tools_draw_position = (VISIBLE_GRID_SIZE + 0.5 + i, VISIBLE_GRID_SIZE - 2.5 + j)
                pygame.draw.rect(screen, BLACK, (tools_draw_position[0] * TILE_SIZE * SCALE_FACTOR, tools_draw_position[1] * TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR))
                if not hint_activated:
                    if j == 0:
                        if tools_acquired.get(element_chars[i]) != 0:
                            shoe_name = 's' + element_chars[i]
                            draw_the_tile(shoe_name, tools_draw_position, current_time)
                    if j == 1:
                        if tools_acquired.get(color_chars[i]) != 0:
                            key_name = 'k' + color_chars[i]
                            draw_the_tile(key_name, tools_draw_position, current_time)
        if hint_activated:
            #print("hint activated!")
            font_size = 30
            font = pygame.font.SysFont(None, font_size)
            text_rect = pygame.Rect((VISIBLE_GRID_SIZE+0.6)*TILE_SIZE*SCALE_FACTOR, (VISIBLE_GRID_SIZE-2.3)*TILE_SIZE*SCALE_FACTOR, TILE_SIZE*SCALE_FACTOR*4, TILE_SIZE*SCALE_FACTOR*2)
            # Render each line of the text
            lines = hint_text.split('\n')
            #print("lines = ", lines)
            for i, line in enumerate(lines):
                text_surface = font.render(line, True, RED)
                screen.blit(text_surface, text_rect)
                text_rect.y += TILE_SIZE*SCALE_FACTOR*0.3 # Adjust the vertical position for each line

        # Draw the 9 x 9 Board as seen by Chip
        for i in range(visible_grid_top_left_x, visible_grid_top_left_x + VISIBLE_GRID_SIZE, 1):
            for j in range(visible_grid_top_left_y, visible_grid_top_left_y + VISIBLE_GRID_SIZE, 1):
                draw_position = (i - visible_grid_top_left_x, j - visible_grid_top_left_y)
                draw_the_tile(downworld[i][j], draw_position, current_time)
                draw_the_tile(overworld[i][j], draw_position, current_time)
                #print("current_time = ", current_time)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # Handle key presses
        keys = pygame.key.get_pressed()

        if won_time > 0 and go_to_time == False:
            x_left = TILE_SIZE*SCALE_FACTOR*3.1
            y_up = TILE_SIZE*SCALE_FACTOR*4.1
            alpha_value = 50  # Adjust the alpha (transparency) as needed
            transparent_green = (0, 255, 0, alpha_value)  # Assuming RGB color with alpha channel
            pygame.draw.rect(screen, transparent_green, (x_left, y_up, TILE_SIZE * SCALE_FACTOR * 2.8, TILE_SIZE * SCALE_FACTOR * 0.8))

            font = pygame.font.SysFont(None, 50)
            text = font.render("You Won!", True, BLUE)
            text_rect = text.get_rect(center=(visible_grid_pixel_size // 2, visible_grid_pixel_size // 2))
            screen.blit(text, text_rect)

            # Show the message for 3 seconds
            if current_time - won_time >= 3:
                return True, False, False, 0, last_level, repetition_level

        if lost_time > 0 and go_to_time == False:
            n_repetitions_to_skip_level = 8
            if (repetition_level%(n_repetitions_to_skip_level+1) != n_repetitions_to_skip_level):
                x_left = TILE_SIZE*SCALE_FACTOR*3.1
                y_up = TILE_SIZE*SCALE_FACTOR*4.1
                alpha_value = 50  # Adjust the alpha (transparency) as needed
                transparent_red = (255, 0, 0, alpha_value)  # Assuming RGB color with alpha channel
                pygame.draw.rect(screen, transparent_red, (x_left, y_up, TILE_SIZE * SCALE_FACTOR * 2.8, TILE_SIZE * SCALE_FACTOR * 0.8))

                font = pygame.font.SysFont(None, 50)
                text = font.render("You Lost!", True, BLACK)
                text_rect = text.get_rect(center=(visible_grid_pixel_size // 2, visible_grid_pixel_size // 2))
                screen.blit(text, text_rect)

                last_level = level_number
                # Show the message for 3 seconds
                if current_time - lost_time >= 3:
                    return False, False, False, 0, last_level, repetition_level
            else:
                display_message("You seem to have trouble\n with this level. Would you\n prefer skipping to the\n next one? \n \n Press Y or N")
                we_are_asking_yes_no_question = True
                if keys[pygame.K_y]:
                    #print("Y was pressed meaning Yes")
                    return False, True, False, 0, last_level, repetition_level
                elif keys[pygame.K_n]:
                    #print("N was pressed meaning No")
                    return False, False, False, 0, last_level, repetition_level

        #print("go_to_time = ", go_to_time)
        #print("we_are_asking_yes_no_question = ", we_are_asking_yes_no_question)
        if keys[pygame.K_n] and keys[pygame.K_LCTRL]:
            #print("are we asking yes no questions? ", we_are_asking_yes_no_question)
            lost_time = current_time
            #print("N was pressed meaning Next Level")
            if actual_level != max_level:
                ready_to_go_to = True
                ready_to_go_to_time = current_time
                level_to_go_to = actual_level+1

        if keys[pygame.K_p] and keys[pygame.K_LCTRL]:
            lost_time = current_time
            #print("P was pressed meaning Previous Level")
            if actual_level != 0:
                ready_to_go_to = True
                ready_to_go_to_time = current_time
                level_to_go_to = actual_level-1
        
        if keys[pygame.K_g] or go_to_time:
            go_to_time = True
            lost_time = current_time
            if first_time_try_to_go_to:
                display_message("Write the level you want\n to go to and press Enter. \n\nAll the levels beyond " + str(max_level) + " \nare inaccessible: if you try \nto reach them, you will be \nredirected to level " + str(max_level))

        a_digit_was_pressed = False
        # Append the pressed digit to the var list
        for key in range(pygame.K_0, pygame.K_9 + 1):
            #print("key = ", key, " and var = ", var)
            if keys[key] and go_to_time:
                a_digit_was_pressed = True
                new_var = (chr(key - pygame.K_0 + ord('0')))
                #print("new_var = ", new_var)
                if var == [] or var[-1] != new_var:
                    var.append(new_var)
        if not a_digit_was_pressed:
            new_var = 0
            if var == [] or var[-1] != new_var:
                var.append(new_var)
    
        if go_to_time and keys[pygame.K_RETURN]:
            list_level_to_go_to = []
            #print("var = ", var)
            for char in var:
                if char == 0:
                    pass
                else:
                    list_level_to_go_to.append(char)
                    level_to_go_to = int(''.join(list_level_to_go_to))
                    #print("level_to_go_to = ", level_to_go_to)
            #print("level_to_go_to = ", level_to_go_to, " and type = ", type(level_to_go_to))
            #print("max_level = ", max_level, " and type = ", type(max_level))
            ready_to_go_to = True
            ready_to_go_to_time = current_time
            if level_to_go_to >= max_level:
                level_to_go_to = max_level

        if ready_to_go_to and current_time - ready_to_go_to_time >= 0.5:
            #print("I go to")
            return True, False, True, level_to_go_to, last_level, repetition_level
        # ROUTINE OF EACH TURN. REINITIALIZE THINGS.
        # This stops the level from starting if the player did not press any key. 
        #print("any_key_was_pressed = ", any_key_was_pressed)
        #print("go_to_time = ", go_to_time)
        if (any_key_was_pressed == False):
            if not(keys[pygame.K_UP] or keys[pygame.K_RIGHT] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_q] or keys[pygame.K_RETURN]):
                x_left = TILE_SIZE*SCALE_FACTOR*1.1
                y_up = TILE_SIZE*SCALE_FACTOR*6.1
                pygame.draw.rect(screen, WHITE, (x_left, y_up, TILE_SIZE * SCALE_FACTOR * 6.8, TILE_SIZE * SCALE_FACTOR * 1.8))
                x_left = TILE_SIZE*SCALE_FACTOR*1.2
                y_up = TILE_SIZE*SCALE_FACTOR*6.2
                pygame.draw.rect(screen, BLACK, (x_left, y_up, TILE_SIZE * SCALE_FACTOR * 6.6, TILE_SIZE * SCALE_FACTOR * 1.6))
                
                font_size = 48
                font = pygame.font.SysFont(None, font_size)
                # Render each line of the text
                lines = level_title.split('\n')
                for i, line in enumerate(lines):
                    text_surface = font.render(line, True, YELLOW)
                    text_rect = text_surface.get_rect()
                    text_rect.center = (TILE_SIZE*SCALE_FACTOR*4.5, TILE_SIZE*SCALE_FACTOR*(7+i*0.5))
                    screen.blit(text_surface, text_rect)
                pygame.display.flip()
                continue
            else:
                #print("Any key was pressed")
                is_the_challenge_starting = False
                start_time = current_time
                any_key_was_pressed = True

        pygame.display.flip()
        
        # I reinitialize the already_moved variable, to allow object to move after being freeze for a turn
        if won_time == 0 and lost_time == 0:
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    if not (downworld[i][j][0] == 'C' and downworld[i][j][1] in direction_chars):
                        # The reason for this condition is that monsters on top of "cloner" will be treated
                        # as if the have "already" moved! So they remain freezed. Except if the red button is pushed.
                        already_moved[i][j] = False
        
        if keys[pygame.K_q]:
            #print("You surrendered the match by pressing the letter Q!")
            lost_time = current_time

        # MOVEMENT OF CHIP DUE TO KEY PRESSED
        x_chip_old = chip_pos[0]
        y_chip_old = chip_pos[1]

        # Reinitialize the chip_moved variable
        chip_moved = False

        if current_time - last_move_time >= DELTA_T and won_time == 0 and lost_time == 0:
            a_key_was_pressed = False

            # Chip can press keys if it is not in an Active Trap or in Ice without Ice shoes.
            if chip_can_press_keys(downworld, chip_pos[0], chip_pos[1], tools_acquired):
                if keys[pygame.K_UP]:
                    direction_char = 'U'
                    a_key_was_pressed = True
                elif keys[pygame.K_RIGHT]:
                    direction_char = 'R'
                    a_key_was_pressed = True
                elif keys[pygame.K_DOWN]:
                    direction_char = 'D'
                    a_key_was_pressed = True
                elif keys[pygame.K_LEFT]:
                    direction_char = 'L'
                    a_key_was_pressed = True
                if a_key_was_pressed:
                    # This eliminates the Boost going forward in the Energy. Now, if I'm on the Energy going to a
                    # direction, I cannot accelerate further in that direction.
                    if (
                        downworld[chip_pos[0]][chip_pos[1]][0] == 'E' and
                        downworld[chip_pos[0]][chip_pos[1]][1] in direction_chars and
                        tools_acquired.get('E') == 0 and
                        direction_char == downworld[chip_pos[0]][chip_pos[1]][1]
                        ):
                        pass
                    else:
                        chip_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char, downworld, overworld, chip_pos[0], chip_pos[1], 'c', tools_acquired, lost_time, current_time, cloner_list, teleport_list, already_moved)
                if chip_moved:
                    chip_pos = [new_i,new_j]
                    last_move_time = current_time
                    # This will guarantee that you can plant yours feet down going aganst the Energy!
                    # BE CAREFUL! I retrodated the pressing of the key so that it is allowed to press the key
                    # every DELTA_T/2 time instead of DELTA_T, so that the maximum speed becomes 2/DELTA_T which
                    # compensates the speed imposed on Chip by the Energy.
                    if (
                        downworld[chip_pos[0]][chip_pos[1]][0] == 'E' and
                        downworld[chip_pos[0]][chip_pos[1]][1] in direction_chars and
                        tools_acquired.get('E') == 0 and
                        direction_char == reverse_direction_char(downworld[chip_pos[0]][chip_pos[1]][1])
                        ):
                        last_move_time = current_time - DELTA_T/2

        # INVOLUNTARY MOVEMENT ON ICE AND ENERGY OF ALL OBJECTS: CHIP, MONSTERS, BLOCKS
        # It excludes the voluntary movement of Chip in Energy, which is accounted for in the previous section.
        is_time_for_ice_and_energy_movement = (won_time == 0 and lost_time == 0 and (current_time // (DELTA_T/2)) != (last_time // (DELTA_T/2)))

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                # I check if I can move the object, if it is the right time, and if the game did not end.
                if (already_moved[x][y] == False and is_time_for_ice_and_energy_movement and won_time == 0 and lost_time == 0):
                    # If I'm Chip, or a monster, or a block
                    if overworld[x][y][0] in moving_chars and overworld[x][y][1] in direction_chars:
                        moving_char = overworld[x][y][0]

                        # ICE
                        # If the object is on Ice without the Ice shoes.
                        # The main idea is that the Ice cn change the direction of the object. Then the object tries
                        # to move. If it can't, it reverses its direction. And its direction is changed again by the ice.
                        if downworld[x][y][0] == 'I' and downworld[x][y][1] in ['U','R','D','L','_'] and (moving_char != 'c' or tools_acquired.get('I') == 0):
                            # The object is on Ice and the object does not have the Ice shoes!
                            last_direction_char = overworld[x][y][1]
                            type_of_ice = downworld[x][y][1]
                            
                            it_moved = False
                            old_x = x
                            old_x = y
                            
                            # The direction to be taken is still to be calculated! The Ice could change it!
                            direction_char = direction_changed_by_ice(last_direction_char, type_of_ice)

                            it_moved, new_x, new_y, lost_time = object_can_go_and_goes(direction_char, downworld, overworld, x, y, moving_char, tools_acquired, lost_time, current_time, cloner_list, teleport_list, already_moved)
                            if not it_moved:
                                # The direction is reversed due to the obstacle
                                direction_char = reverse_direction_char(direction_char)
                                # The direction is changed by the Ice again!
                                direction_char = direction_changed_by_ice(direction_char, type_of_ice)
                                # The object tries to move
                                it_moved, new_x, new_y, lost_time = object_can_go_and_goes(direction_char, downworld, overworld, x, y, moving_char, tools_acquired,lost_time,current_time, cloner_list, teleport_list, already_moved)
                            
                            if it_moved:
                                if moving_char == 'c':
                                    chip_pos = [new_x,new_y]
                                    last_move_time = current_time
                            already_moved[new_x][new_y] = True

                        # ENERGY
                        # If the object is on Energy without the Energy shoes.
                        # The main idea is that the Energy imposes the direction on the object.
                        # (Chip can also press keys on Energy, but this section deals only with the involuntary
                        # movements on Energy)
                        elif downworld[x][y][0] == 'E' and downworld[x][y][1] in ['U','R','D','L','X'] and (moving_char != 'c' or tools_acquired.get('E') == 0):
                            # The object is on Energy and the object does not have the Energy shoes!
                            last_direction_char = overworld[x][y][1]
                            type_of_energy = downworld[x][y][1]
                            
                            it_moved = False
                            old_x = x
                            old_x = y
                            
                            # The direction to be taken is determined by the type of energy
                            if type_of_energy == 'X':
                                random_n = random.randint(0, 3)
                                # I try to go forward, or left, or right, or back - at random.
                                direction_char = direction_from_angle((angle_from_direction(direction_char)+random_n)%4)
                            else:
                                direction_char = type_of_energy

                            it_moved, new_x, new_y, lost_time = object_can_go_and_goes(direction_char, downworld, overworld, x, y, moving_char, tools_acquired, lost_time, current_time, cloner_list, teleport_list, already_moved)
                            
                            if it_moved:
                                if moving_char == 'c':
                                    chip_pos = [new_x,new_y]
                                    # If I'm on Energy, I can press keys normally, as if my last move was only
                                    # that given by the last time I pressed a key.
                                    #last_move_time = current_time
                            already_moved[new_x][new_y] = True

        # MONSTERS AND BLOCK MOVEMENTS (EXCEPT ON ICE AND ON ENERGY) AND CLONING

        if won_time == 0 and lost_time == 0 and (current_time // DELTA_T) != (last_time // DELTA_T):
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    if already_moved[i][j] == True:
                        continue
                    if downworld[i][j][0] == 'I' and downworld[i][j][1] in ['_','U','R','D','L']:
                        continue
                    if downworld[i][j][0] == 'E' and downworld[i][j][1] in ['X','U','R','D','L']:
                        continue
                    if downworld[i][j] == 'TA':    # Trap Active
                        continue

                    if True:
                        #This is for the fireballs.
                        monster_char = 'f'
                        if overworld[i][j][0] == monster_char and overworld[i][j][1] in direction_chars:
                            direction_char = overworld[i][j][1]
                            # First I try to go to the direction I point to.
                            it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired, lost_time, current_time, cloner_list, teleport_list, already_moved)
                            if it_moved == False:
                                # If I can't, I try to go to my right.
                                direction_char = direction_from_angle((angle_from_direction(direction_char)+1)%4)
                                it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired, lost_time, current_time, cloner_list, teleport_list, already_moved)
                                if it_moved == False:
                                    # If I can't, I try to go my left.
                                    direction_char = direction_from_angle((angle_from_direction(direction_char)+2)%4)
                                    it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired, lost_time, current_time, cloner_list, teleport_list, already_moved)
                                    if it_moved == False:
                                        # If I can't, I try to go back.
                                        direction_char = direction_from_angle((angle_from_direction(direction_char)+3)%4)
                                        it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired, lost_time, current_time, cloner_list, teleport_list, already_moved)
                                        if it_moved == False:
                                            #If I can't, I do not do anything.
                                            new_i = i
                                            new_j = j
                                            pass
                            already_moved[new_i][new_j] = True
                    
                        #This is for the gliders.
                        monster_char = 'g'
                        if overworld[i][j][0] == monster_char and overworld[i][j][1] in direction_chars:
                            direction_char = overworld[i][j][1]
                            # First I try to go to the direction I point to.
                            it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                            if it_moved == False:
                                # If I can't, I try to go to my left.
                                direction_char = direction_from_angle((angle_from_direction(direction_char)+3)%4)
                                it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                                if it_moved == False:
                                    # If I can't, I try to go my right.
                                    direction_char = direction_from_angle((angle_from_direction(direction_char)+2)%4)
                                    it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                                    if it_moved == False:
                                        # If I can't, I try to go back.
                                        direction_char = direction_from_angle((angle_from_direction(direction_char)+1)%4)
                                        it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                                        if it_moved == False:
                                            #If I can't, I do not do anything.
                                            new_i = i
                                            new_j = j
                                            pass
                            already_moved[new_i][new_j] = True

                        #This is for the pink balls.
                        monster_char = 'o'
                        if overworld[i][j][0] == monster_char and overworld[i][j][1] in direction_chars:
                            direction_char = overworld[i][j][1]
                            # First I try to go to the direction I point to.
                            it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char, downworld, overworld, i, j, monster_char, tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                            if it_moved == False:
                                # If I can't, I try to go to back.
                                direction_char = direction_from_angle((angle_from_direction(direction_char)+2)%4)
                                it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char, downworld, overworld, i, j, monster_char, tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                                if it_moved == False:
                                    #If I can't, I do not do anything.
                                    new_i = i
                                    new_j = j
                                    pass
                            already_moved[new_i][new_j] = True

                        #This is for the saturns.
                        monster_char = 'q'
                        if overworld[i][j][0] == monster_char and overworld[i][j][1] in direction_chars:
                            direction_char = overworld[i][j][1]
                            # First I try to go to the direction I point to.
                            it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                            if it_moved == False:
                                move_attempts = 0
                                while it_moved == False and move_attempts < 20:
                                    random_n = random.randint(0, 3)
                                    # If I can't, I try to go left, or right, or back - at random.
                                    direction_char = direction_from_angle((angle_from_direction(direction_char)+random_n)%4)
                                    it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                                    move_attempts += 1
                                if it_moved == False:
                                    #If I can't, I do not do anything.
                                    new_i = i
                                    new_j = j
                                    pass
                            already_moved[new_i][new_j] = True

                        #This is for the Blobs.
                        monster_char = 'b'
                        if (current_time // (DELTA_T*4)) != (last_time // (DELTA_T*4)):
                            if overworld[i][j][0] == monster_char and overworld[i][j][1] in direction_chars:
                                direction_char = overworld[i][j][1]
                                move_attempts = 0
                                it_moved = False
                                while it_moved == False and move_attempts < 20:
                                    random_n = random.randint(0, 3)
                                    # I try to go forward, or left, or right, or back - at random.
                                    direction_char = direction_from_angle((angle_from_direction(direction_char)+random_n)%4)
                                    it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                                    move_attempts += 1
                                if it_moved == False:
                                    #If I can't, I do not do anything.
                                    new_i = i
                                    new_j = j
                                    pass
                                already_moved[new_i][new_j] = True
                    
                        #This is for the Ants.
                        monster_char = 'a'
                        if overworld[i][j][0] == monster_char and overworld[i][j][1] in direction_chars:
                            direction_char = overworld[i][j][1]
                            # First I try to go to the direction to the left I point to.
                            direction_char = direction_from_angle((angle_from_direction(direction_char)+3)%4)
                            it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                            if it_moved == False:
                                # If I can't, I try to go forward.
                                direction_char = direction_from_angle((angle_from_direction(direction_char)+1)%4)
                                it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                                if it_moved == False:
                                    # If I can't, I try to go to the right.
                                    direction_char = direction_from_angle((angle_from_direction(direction_char)+1)%4)
                                    it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                                    if it_moved == False:
                                        # If I can't, I try to go back.
                                        direction_char = direction_from_angle((angle_from_direction(direction_char)+1)%4)
                                        it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                                        if it_moved == False:
                                            #If I can't, I do not do anything.
                                            new_i = i
                                            new_j = j
                                            pass
                            already_moved[new_i][new_j] = True
                    
                        #This is for the Paramecia.
                        monster_char = 'p'
                        if overworld[i][j][0] == monster_char and overworld[i][j][1] in direction_chars:
                            direction_char = overworld[i][j][1]
                            # First I try to go to the direction to the right I point to.
                            direction_char = direction_from_angle((angle_from_direction(direction_char)+1)%4)
                            it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                            if it_moved == False:
                                # If I can't, I try to go forward.
                                direction_char = direction_from_angle((angle_from_direction(direction_char)+3)%4)
                                it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                                if it_moved == False:
                                    # If I can't, I try to go to the left.
                                    direction_char = direction_from_angle((angle_from_direction(direction_char)+3)%4)
                                    it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                                    if it_moved == False:
                                        # If I can't, I try to go back.
                                        direction_char = direction_from_angle((angle_from_direction(direction_char)+3)%4)
                                        it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                                        if it_moved == False:
                                            #If I can't, I do not do anything.
                                            new_i = i
                                            new_j = j
                                            pass
                            already_moved[new_i][new_j] = True

                        #This is for the Tanks
                        monster_char = 't'
                        if overworld[i][j][0] == monster_char and overworld[i][j][1] in direction_chars:
                            direction_char = overworld[i][j][1]
                            # First I try to go to the direction I point to.
                            it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,monster_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                            if it_moved == False:
                                #If I can't, I do not do anything.
                                new_i = i
                                new_j = j
                                pass
                            already_moved[new_i][new_j] = True
                        
                        #This is for the piranhas Monsters
                        monster_char = 'm'
                        if (current_time // (DELTA_T*4)) != (last_time // (DELTA_T*4)):
                            if overworld[i][j][0] == monster_char and overworld[i][j][1] in direction_chars:
                                direction_char = overworld[i][j][1]
                                # First I calculate what is the quickest path to the player.
                                delta_x = chip_pos[0]-i
                                delta_y = chip_pos[1]-j
                                # Define new coordinates
                                delta_x_new = - delta_y + delta_x
                                delta_y_new = - delta_y - delta_x
    
                                if delta_x_new >= 0 and delta_y_new > 0:
                                    new_direction_char = 'U'
                                elif delta_x_new > 0 and delta_y_new <= 0:
                                    new_direction_char = 'R'
                                elif delta_x_new <= 0 and delta_y_new < 0:
                                    new_direction_char = 'D'
                                elif delta_x_new < 0 and delta_y_new >= 0:
                                    new_direction_char = 'L'
                                else:
                                    # The player was already eaten.
                                    continue
        
                                # Now I try to go towards the player along the direction chosen
                                it_moved, new_i, new_j, lost_time = object_can_go_and_goes(new_direction_char,downworld,overworld,i,j,monster_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                                if it_moved == False:
                                    #If I can't, I do not do anything.
                                    new_i = i
                                    new_j = j
                                    overworld[i][j] = monster_char + new_direction_char
                                    pass
                                already_moved[new_i][new_j] = True
                        
                        # This is for the directional Blocks
                        # (this applies only when a Block is released by a Trap, and when a Block is cloned)
                        block_char = 'n'
                        if overworld[i][j][0] == block_char and overworld[i][j][1] in ['_','U','R','D','L']:
                            if (downworld[i][j][0] == 'C' and downworld[i][j][1] in direction_chars) or downworld[i][j] == 'TI':
                                # I try to go to the direction I point to.
                                #if downworld[i][j][0] == 'C':
                                direction_char = overworld[i][j][1]
                                it_moved, new_i, new_j, lost_time = object_can_go_and_goes(direction_char,downworld,overworld,i,j,block_char,tools_acquired,lost_time,current_time,cloner_list, teleport_list, already_moved)
                                # We want to avoid a block that continues to move autonomously
                                if it_moved == True:
                                    overworld[i][j] = level.overworld[i][j]
                                elif it_moved == False:
                                    #If I can't, I do not do anything.
                                    new_i = i
                                    new_j = j
                                    pass
                                already_moved[new_i][new_j] = True
                        
        
        # CHECK IF CHIP ACQUIRED TOOLS
        # Check if Chip captured keys or shoes or chips, or find a thief.
        
        # Useful variables to know where is chip in the downworld and his company in the overworld.
        where_is_chip = downworld[chip_pos[0]][chip_pos[1]]
        company = overworld[chip_pos[0]][chip_pos[1]]
        
        # This checks if Chip found a key
        # (The green keys cannot be lost by opening a door, but they are acquired as the other keys)
        if where_is_chip[0] == 'k' and where_is_chip[1] in color_chars:
            color_char = where_is_chip[1]
            downworld[chip_pos[0]][chip_pos[1]] = '__'
            tools_acquired[color_char] += 1
            #print("My tools are ", tools_acquired)
    
        # This checks if Chip found a shoe
        if where_is_chip[0] == 's' and where_is_chip[1] in element_chars:
            element_char = where_is_chip[1]
            downworld[chip_pos[0]][chip_pos[1]] = '__'
            tools_acquired[element_char] += 1
            #print("My tools are ", tools_acquired)
        
        # The thief robs all the shoes.
        if where_is_chip == 'th':
            for element_char in element_chars:
                tools_acquired[element_char] = 0
            #print("My tools are ", tools_acquired)

        # The variable tools_acquired['c'] accounts for the number of chips left.
        if where_is_chip == 'ch':
            downworld[chip_pos[0]][chip_pos[1]] = '__'
            tools_acquired['c'] -= 1
            #print("My tools are ", tools_acquired)


        # CHECK IF GAME ENDED
        # Check if Chip won or lost
        # Win through the Exit.
        if where_is_chip == 'E_':
            if won_time == 0:
                won_time = current_time
        
        # Death by Bomb.
        if where_is_chip == 'bo':
            #print("You were killed by a Bomb!")
            if lost_time == 0:
                lost_time = current_time

        # Death by Fire.
        if where_is_chip == 'F_' and tools_acquired.get('F') == 0:
            #print("You were killed by the Fire!")
            if lost_time == 0:
                lost_time = current_time
        
        # Death by Water.
        if where_is_chip == 'W_' and tools_acquired.get('W') == 0:
            #print("You drowned in the Water!")
            if lost_time == 0:
                lost_time = current_time
        if kills_chip_if_over_it(company):
            #print("You were killed by ", company, "!")
            if lost_time == 0:
                lost_time = current_time

        # I save the time to be used in the next iteration.
        last_time = current_time

        # Cap the frame rate
        clock.tick(60)
        

# Call the game loop

actual_level = 0
# Global variables
last_level = 0
repetition_level = 0
max_level = actual_level
is_the_challenge_starting = True

#introduction_text = "Welcome to the Challenge!\nCollect chips, avoid monsters, reach the Exit!\n\n\nUse CTRL + P or CTRL + N to go to previous\nor next levels (if accessible).\nUse G to go to an accessible level!"
introduction_text = "Welcome to The Challenge!\nCollect chips, avoid monsters, reach the Exit!\n\nUse the arrow keys to move.\n\n\nGood Luck!\nby PAXT"
display_message(introduction_text, big=True)
time.sleep(8)

while actual_level < len(levels):
    if max_level < actual_level:
        max_level = actual_level
    the_level_was_passed, skip_level, use_go_to, level_to_go_to, last_level, repetition_level = game_loop(levels[actual_level], last_level, repetition_level, max_level, is_the_challenge_starting)
    is_the_challenge_starting = False
    if the_level_was_passed or skip_level:
        actual_level += 1
    if use_go_to:
        last_level = actual_level
        actual_level = level_to_go_to
    else:
        pass

pygame.quit()
sys.exit()

