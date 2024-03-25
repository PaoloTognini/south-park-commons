import pygame
import random

# Constants
WIDTH, HEIGHT = 400, 400
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# New color for marked tiles
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Initialize Pygame
pygame.init()

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")

# Fonts
font = pygame.font.Font(None, 36)

# Font for larger messages
large_font = pygame.font.Font(None, 48)

# Function to create the game grid
def create_grid():
    grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    mines = random.sample(range(GRID_SIZE * GRID_SIZE), GRID_SIZE)

    for mine in mines:
        row, col = divmod(mine, GRID_SIZE)
        grid[row][col] = -1  # -1 represents a mine
        for i in range(row - 1, row + 2):
            for j in range(col - 1, col + 2):
                if 0 <= i < GRID_SIZE and 0 <= j < GRID_SIZE and grid[i][j] != -1:
                    grid[i][j] += 1  # Increment neighboring cells
    return grid

# Function to draw the grid and messages
def draw_grid(grid, revealed, marked, game_over):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x, y = col * CELL_SIZE, row * CELL_SIZE
            if revealed[row][col]:
                pygame.draw.rect(screen, WHITE, (x, y, CELL_SIZE, CELL_SIZE))
                if grid[row][col] > 0:
                    text = font.render(str(grid[row][col]), True, BLACK)
                    screen.blit(text, (x + CELL_SIZE // 3, y + CELL_SIZE // 3))
                elif grid[row][col] == -1:
                    pygame.draw.circle(screen, BLACK, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), CELL_SIZE // 3)
            else:
                if marked[row][col]:
                    pygame.draw.rect(screen, RED, (x, y, CELL_SIZE, CELL_SIZE))
                else:
                    pygame.draw.rect(screen, GRAY, (x, y, CELL_SIZE, CELL_SIZE))

    if game_over:
        message = large_font.render("Game over!", True, RED)
        screen.blit(message, (WIDTH // 2 - 90, HEIGHT // 2 - 30))
    elif all(all(revealed[row][col] or grid[row][col] == -1 for col in range(GRID_SIZE)) for row in range(GRID_SIZE)):
        message = large_font.render("You win!", True, GREEN)
        screen.blit(message, (WIDTH // 2 - 80, HEIGHT // 2 - 30))


# Function to initialize the game state
def initialize_game():
    return create_grid(), [[False] * GRID_SIZE for _ in range(GRID_SIZE)], [[False] * GRID_SIZE for _ in range(GRID_SIZE)], False

# Main game loop
def main():
    grid, revealed, marked, game_over = initialize_game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = pygame.mouse.get_pos()
                col, row = x // CELL_SIZE, y // CELL_SIZE

                # Left click to reveal the cell
                if event.button == 1 and marked[row][col] == False:
                    revealed[row][col] = True

                    if grid[row][col] == -1:
                        game_over = True

                # Right click to mark/unmark the cell with an "X"
                elif event.button == 3:
                    marked[row][col] = not marked[row][col]

        screen.fill(BLACK)
        draw_grid(grid, revealed, marked, game_over)
        pygame.display.flip()

        if all(all(revealed[row][col] or grid[row][col] == -1 for col in range(GRID_SIZE)) for row in range(GRID_SIZE)):
            print("You win!")
            pygame.time.delay(5000)  # Wait for 5 second before restarting
            grid, revealed, marked, game_over = initialize_game()

        if game_over:
            print("Game over!")
            pygame.time.delay(5000)  # Wait for 5 second before restarting
            grid, revealed, marked, game_over = initialize_game()


# Run the game
if __name__ == "__main__":
    main()

