import pygame
import sys
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 900, 900
PATCH_SIZE = 300
TILE_SIZE = 100
ROWS, COLS = 3, 3
FPS = 60
BLUE = (0, 0, 255) 
RED = (255, 0, 0)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LINE_COLOR = (0, 0, 0)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("my nested Tic Tac Toe")

# Initialize the game board
tile_board = [[[["" for _ in range(COLS)] for _ in range(ROWS)] for _ in range(COLS)] for _ in range(ROWS)]
patch_board = [["" for _ in range(COLS)] for _ in range(ROWS)]
current_player = "O"
winner = None
last_tile_row = -1
last_tile_col = -1
game_ended = False

# Function to check for a winner
def check_winner(board, current_player):
    # Check rows and columns
    for i in range(ROWS):
        if all(board[i][j] == current_player for j in range(COLS)) or all(board[j][i] == current_player for j in range(ROWS)):
            return True

    # Check diagonals
    if all(board[i][i] == current_player for i in range(ROWS)) or all(board[i][ROWS - 1 - i] == current_player for i in range(ROWS)):
        return True

    return False

def is_an_allowed_move(patch_row, patch_col, tile_row, tile_col, last_tile_row, last_tile_col, game_ended):
    # If the game ended, no move is possible
    if game_ended:
        return False

    # At the first move (indicated by having -1 as the last move) and if the patch to be moved is already won,
    # One is free to move wherever he wants.
    if (last_tile_row == -1 and last_tile_col == -1) or patch_board[last_tile_row][last_tile_col] != "":
        if tile_board[patch_row][patch_col][tile_row][tile_col] == "":
            return True
    # Otherwise, one has to move to the patch selected by the tile played last by the other player.
    elif patch_row == last_tile_row and patch_col == last_tile_col:
        if tile_board[patch_row][patch_col][tile_row][tile_col] == "":
            return True
    return False

def update_patch_board(patch_row, patch_col, current_player):
    assert(patch_board[patch_row][patch_col] == "")
    board_of_the_patch = tile_board[patch_row][patch_col]
    if check_winner(board_of_the_patch, current_player):
        patch_board[patch_row][patch_col] = current_player

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and winner is None:
            patch_col = event.pos[0] // PATCH_SIZE
            patch_row = event.pos[1] // PATCH_SIZE

            tile_col = (event.pos[0] % PATCH_SIZE) // TILE_SIZE
            tile_row = (event.pos[1] % PATCH_SIZE) // TILE_SIZE

            if is_an_allowed_move(patch_row, patch_col, tile_row, tile_col, last_tile_row, last_tile_col, game_ended):
                last_tile_row = tile_row
                last_tile_col = tile_col
                tile_board[patch_row][patch_col][tile_row][tile_col] = current_player

                update_patch_board(patch_row, patch_col, current_player)

                if check_winner(patch_board, current_player):
                    winner = "First Player" if current_player == "O" else "Second Player"
                    game_ended = True
                else:
                    # Switch players
                    current_player = "X" if current_player == "O" else "O"

    # Draw background
    screen.fill(WHITE)

    # Draw X and O
    for patch_row in range(ROWS):
        for patch_col in range(COLS):
            for tile_row in range(ROWS):
                for tile_col in range(COLS):
                    tile_upperleft_corner = [patch_col * PATCH_SIZE + tile_col * TILE_SIZE, patch_row * PATCH_SIZE + tile_row * TILE_SIZE]
                    if current_player == "O":
                        COLOR = RED
                    else:
                        COLOR = BLUE
                    if is_an_allowed_move(patch_row, patch_col, tile_row, tile_col, last_tile_row, last_tile_col, game_ended):
                        pygame.draw.rect(screen, COLOR, (tile_upperleft_corner[0], tile_upperleft_corner[1], TILE_SIZE, TILE_SIZE))
                    
                    # Draw the "O" or the "X"
                    if tile_board[patch_row][patch_col][tile_row][tile_col] == "O":
                        pygame.draw.circle(screen, LINE_COLOR, (patch_col * PATCH_SIZE + tile_col * TILE_SIZE + TILE_SIZE // 2, patch_row * PATCH_SIZE + tile_row * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 3, 2)
                    elif tile_board[patch_row][patch_col][tile_row][tile_col] == "X":
                        pygame.draw.line(screen, LINE_COLOR, (patch_col * PATCH_SIZE + tile_col * TILE_SIZE + TILE_SIZE // 4, patch_row * PATCH_SIZE + tile_row * TILE_SIZE + TILE_SIZE // 4),
                                         (patch_col * PATCH_SIZE + tile_col * TILE_SIZE + 3 * TILE_SIZE // 4, patch_row * PATCH_SIZE + tile_row * TILE_SIZE + 3 * TILE_SIZE // 4), 2)
                        pygame.draw.line(screen, LINE_COLOR, (patch_col * PATCH_SIZE + tile_col * TILE_SIZE + TILE_SIZE // 4, patch_row * PATCH_SIZE + tile_row * TILE_SIZE + 3 * TILE_SIZE // 4),
                                         (patch_col * PATCH_SIZE + tile_col * TILE_SIZE + 3 * TILE_SIZE // 4, patch_row * PATCH_SIZE + tile_row * TILE_SIZE + TILE_SIZE // 4), 2)
            patch_upperleft_corner = [patch_col * PATCH_SIZE, patch_row * PATCH_SIZE]
            if patch_board[patch_row][patch_col] == "O":
                pygame.draw.circle(screen, LINE_COLOR, (patch_col * PATCH_SIZE + PATCH_SIZE // 2, patch_row * PATCH_SIZE + PATCH_SIZE // 2), PATCH_SIZE // 3, 6)
            elif patch_board[patch_row][patch_col] == "X":
                pygame.draw.line(screen, LINE_COLOR, (patch_col * PATCH_SIZE + PATCH_SIZE // 4, patch_row * PATCH_SIZE + PATCH_SIZE // 4),
                                 (patch_col * PATCH_SIZE + 3 * PATCH_SIZE // 4, patch_row * PATCH_SIZE + + 3 * PATCH_SIZE // 4), 6)
                pygame.draw.line(screen, LINE_COLOR, (patch_col * PATCH_SIZE + PATCH_SIZE // 4, patch_row * PATCH_SIZE + 3 * PATCH_SIZE // 4),
                                 (patch_col * PATCH_SIZE + 3 * PATCH_SIZE // 4, patch_row * PATCH_SIZE + PATCH_SIZE // 4), 6)
    
    # Draw grid lines
    for i in range(1, ROWS*ROWS):
        pygame.draw.line(screen, LINE_COLOR, (0, i * TILE_SIZE), (WIDTH, i * TILE_SIZE), 2)
        pygame.draw.line(screen, LINE_COLOR, (i * TILE_SIZE, 0), (i * TILE_SIZE, HEIGHT), 2)
    
    for i in range(1, ROWS):
        pygame.draw.line(screen, LINE_COLOR, (0, i * PATCH_SIZE), (WIDTH, i * PATCH_SIZE), 6)
        pygame.draw.line(screen, LINE_COLOR, (i * PATCH_SIZE, 0), (i * PATCH_SIZE, HEIGHT), 6)


    # Display winner
    if winner:
        font = pygame.font.Font(None, 72)
        text = font.render(f"{winner} won!", True, LINE_COLOR)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

        # Update the display
        pygame.display.flip()

        # Wait for 5 seconds
        time.sleep(5)

        # Reset the game for a new match
        tile_board = [[[["" for _ in range(COLS)] for _ in range(ROWS)] for _ in range(COLS)] for _ in range(ROWS)]
        patch_board = [["" for _ in range(COLS)] for _ in range(ROWS)]
        current_player = "O"
        winner = None
        last_tile_row = -1
        last_tile_col = -1
        game_ended = False

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(FPS)

