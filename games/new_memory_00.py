import pygame
import random

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE_X, GRID_SIZE_Y = 7, 8
CELL_SIZE = WIDTH // (2*GRID_SIZE_X)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)

# Initialize Pygame
pygame.init()

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Game")

# Fonts
font_size = 24
font = pygame.font.Font(None, font_size)

# Generate the game grid
alphabet = [chr(i) for i in range(65, 91)] + ['!','?']  # A-Z
letters = alphabet * 2
print(letters)
random.shuffle(letters)
print(letters)
grid = [[None] * GRID_SIZE_Y for _ in range(GRID_SIZE_X)]

for i in range(GRID_SIZE_X):
    for j in range(GRID_SIZE_Y):
        grid[i][j] = letters.pop()

# Keep track of revealed cells
revealed = [[False] * GRID_SIZE_Y for _ in range(GRID_SIZE_X)]
disappeared = [[False] * GRID_SIZE_Y for _ in range(GRID_SIZE_X)]

# Function to draw the grid
def draw_grid():
    for i in range(GRID_SIZE_X):
        for j in range(GRID_SIZE_Y):
            x, y = j * CELL_SIZE, i * CELL_SIZE
            if revealed[i][j]:
                pygame.draw.rect(screen, WHITE, (x, y, CELL_SIZE, CELL_SIZE))
                text = font.render(grid[i][j], True, BLACK)
                screen.blit(text, (x + CELL_SIZE // 3, y + CELL_SIZE // 3))
            elif disappeared[i][j]:
                pygame.draw.rect(screen, GREEN, (x, y, CELL_SIZE, CELL_SIZE))
                text = font.render(grid[i][j], True, BLACK)
                screen.blit(text, (x + CELL_SIZE // 3, y + CELL_SIZE // 3))
            else:
                pygame.draw.rect(screen, GRAY, (x, y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE),2)

# Main game loop
def main():
    global revealed

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col, row = x // CELL_SIZE, y // CELL_SIZE

                # Check if the cell is within the grid
                if 0 <= row < GRID_SIZE_X and 0 <= col < GRID_SIZE_Y and not revealed[row][col] and not disappeared[row][col]:
                    revealed[row][col] = not revealed[row][col]

                # Check for matching pairs
                revealed_cells = [(i, j) for i in range(GRID_SIZE_X) for j in range(GRID_SIZE_Y) if revealed[i][j]]
                if len(revealed_cells) == 2:
                    (row1, col1), (row2, col2) = revealed_cells
                    if grid[row1][col1] == grid[row2][col2]:
                        # Matching pair found, cells turn green
                        revealed[row1][col1] = revealed[row2][col2] = False
                        disappeared[row1][col1] = disappeared[row2][col2] = True
                elif len(revealed_cells) > 2:
                    for i in range(GRID_SIZE_X):
                        for j in range(GRID_SIZE_Y):
                            revealed[i][j] = False

        screen.fill(BLACK)
        draw_grid()
        pygame.display.flip()

        # Check for game completion
        if all(all(disappeared[i][j] for j in range(GRID_SIZE_Y)) for i in range(GRID_SIZE_X)):
            print("You win!")
            pygame.quit()
            quit()

# Run the game
if __name__ == "__main__":
    main()

