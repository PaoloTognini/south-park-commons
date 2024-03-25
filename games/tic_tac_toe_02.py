import pygame
import sys
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 300, 300
CELL_SIZE = 100
ROWS, COLS = 3, 3
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LINE_COLOR = (0, 0, 0)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe")

# Initialize the game board
board = [["" for _ in range(COLS)] for _ in range(ROWS)]
current_player = "O"
winner = None

# Function to check for a winner
def check_winner():
    # Check rows and columns
    for i in range(ROWS):
        if all(board[i][j] == current_player for j in range(COLS)) or all(board[j][i] == current_player for j in range(ROWS)):
            return True

    # Check diagonals
    if all(board[i][i] == current_player for i in range(ROWS)) or all(board[i][ROWS - 1 - i] == current_player for i in range(ROWS)):
        return True

    return False


# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and winner is None:
            col = event.pos[0] // CELL_SIZE
            row = event.pos[1] // CELL_SIZE

            if board[row][col] == "":
                board[row][col] = current_player

                if check_winner():
                    winner = "First Player" if current_player == "O" else "Second Player"
                else:
                    # Switch players
                    current_player = "X" if current_player == "O" else "O"

    # Draw background
    screen.fill(WHITE)

    # Draw grid lines
    for i in range(1, ROWS):
        pygame.draw.line(screen, LINE_COLOR, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), 2)
        pygame.draw.line(screen, LINE_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT), 2)

    # Draw X and O
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] == "O":
                pygame.draw.circle(screen, LINE_COLOR, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3, 2)
            elif board[row][col] == "X":
                pygame.draw.line(screen, LINE_COLOR, (col * CELL_SIZE + CELL_SIZE // 4, row * CELL_SIZE + CELL_SIZE // 4),
                                 (col * CELL_SIZE + 3 * CELL_SIZE // 4, row * CELL_SIZE + 3 * CELL_SIZE // 4), 2)
                pygame.draw.line(screen, LINE_COLOR, (col * CELL_SIZE + CELL_SIZE // 4, row * CELL_SIZE + 3 * CELL_SIZE // 4),
                                 (col * CELL_SIZE + 3 * CELL_SIZE // 4, row * CELL_SIZE + CELL_SIZE // 4), 2)

    # Display winner
    if winner:
        font = pygame.font.Font(None, 36)
        text = font.render(f"{winner} won!", True, LINE_COLOR)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

        # Update the display
        pygame.display.flip()

        # Wait for 5 seconds
        time.sleep(5)

        # Reset the game for a new match
        board = [["" for _ in range(COLS)] for _ in range(ROWS)]
        current_player = "O"
        winner = None

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(FPS)


"""





# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and winner is None:
            col = event.pos[0] // CELL_SIZE
            row = event.pos[1] // CELL_SIZE

            if board[row][col] == "":
                board[row][col] = current_player

                if check_winner():
                    winner = "First Player" if current_player == "O" else "Second Player"
                else:
                    # Switch players
                    current_player = "X" if current_player == "O" else "O"

    # Draw background
    screen.fill(WHITE)

    # Draw grid lines
    for i in range(1, ROWS):
        pygame.draw.line(screen, LINE_COLOR, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), 2)
        pygame.draw.line(screen, LINE_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT), 2)

    # Draw X and O
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] == "O":
                pygame.draw.circle(screen, LINE_COLOR, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3, 2)
            elif board[row][col] == "X":
                pygame.draw.line(screen, LINE_COLOR, (col * CELL_SIZE + CELL_SIZE // 4, row * CELL_SIZE + CELL_SIZE // 4),
                                 (col * CELL_SIZE + 3 * CELL_SIZE // 4, row * CELL_SIZE + 3 * CELL_SIZE // 4), 2)
                pygame.draw.line(screen, LINE_COLOR, (col * CELL_SIZE + CELL_SIZE // 4, row * CELL_SIZE + 3 * CELL_SIZE // 4),
                                 (col * CELL_SIZE + 3 * CELL_SIZE // 4, row * CELL_SIZE + CELL_SIZE // 4), 2)

    # Display winner
    if winner:
        font = pygame.font.Font(None, 36)
        text = font.render(f"{winner} won!", True, LINE_COLOR)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(FPS)
"""
