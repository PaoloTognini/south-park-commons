import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

# Set up the screen
width, height = 400, 400
cell_size = 20
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)

# Function to initialize the game state
def initialize_game():
    snake1 = [(200, 200), (190, 200), (180, 200)]
    snake1_direction = (cell_size, 0)

    snake2 = [(100, 100), (90, 100), (80, 100)]
    snake2_direction = (cell_size, 0)

    food = (random.randrange(0, width, cell_size), random.randrange(0, height, cell_size))

    return snake1, snake1_direction, snake2, snake2_direction, food

# Function to wrap position around the screen edges
def wrap_around(pos):
    x, y = pos
    x = x % width
    y = y % height
    return x, y

# Function to check if two snakes collide
def check_snake_collision(snake1, snake2):
    head1 = snake1[0]
    for segment in snake2:
        if head1 == segment:
            return True
    return False

# Global function to determine who wins
last_mover = -1

# Function to display the winner for a brief period
def display_winner(winner):
    font = pygame.font.Font(None, 72)

    # Render text with a white contour
    text = font.render(f"{winner} Wins!", True, winner)
    text_contour = font.render(f"{winner} Wins!", True, white)

    # Get the rectangle for the main text
    text_rect = text.get_rect(center=(width // 2, height // 2))

    # Draw the contour text slightly offset
    screen.blit(text_contour, (text_rect.x - 2, text_rect.y - 2))
    screen.blit(text_contour, (text_rect.x + 2, text_rect.y + 2))
    screen.blit(text_contour, (text_rect.x - 2, text_rect.y + 2))
    screen.blit(text_contour, (text_rect.x + 2, text_rect.y - 2))

    # Draw the main text
    screen.blit(text, text_rect)

    pygame.display.flip()
    time.sleep(2)  # 2 seconds delay

# Clock to control the frame rate
clock = pygame.time.Clock()

# Game loop
while True:
    snake1, snake1_direction, snake2, snake2_direction, food = initialize_game()

    # Game over flag
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                # Player 1 controls
                if event.key == pygame.K_UP and snake1_direction != (0, cell_size):
                    snake1_direction = (0, -cell_size)
                    last_move = 1
                    #print("last move = ", last_move)
                elif event.key == pygame.K_DOWN and snake1_direction != (0, -cell_size):
                    snake1_direction = (0, cell_size)
                    last_move = 1
                    #print("last move = ", last_move)
                elif event.key == pygame.K_LEFT and snake1_direction != (cell_size, 0):
                    snake1_direction = (-cell_size, 0)
                    last_move = 1
                    #print("last move = ", last_move)
                elif event.key == pygame.K_RIGHT and snake1_direction != (-cell_size, 0):
                    snake1_direction = (cell_size, 0)
                    last_move = 1
                    #print("last move = ", last_move)

                # Player 2 controls
                elif event.key == pygame.K_w and snake2_direction != (0, cell_size):
                    snake2_direction = (0, -cell_size)
                    last_move = 2
                    #print("last move = ", last_move)
                elif event.key == pygame.K_s and snake2_direction != (0, -cell_size):
                    snake2_direction = (0, cell_size)
                    last_move = 2
                    #print("last move = ", last_move)
                elif event.key == pygame.K_a and snake2_direction != (cell_size, 0):
                    snake2_direction = (-cell_size, 0)
                    last_move = 2
                    #print("last move = ", last_move)
                elif event.key == pygame.K_d and snake2_direction != (-cell_size, 0):
                    snake2_direction = (cell_size, 0)
                    last_move = 2
                    #print("last move = ", last_move)

        # Move snake 1
        head1 = (snake1[0][0] + snake1_direction[0], snake1[0][1] + snake1_direction[1])
        head1 = wrap_around(head1)
        snake1.insert(0, head1)

        # Move snake 2
        head2 = (snake2[0][0] + snake2_direction[0], snake2[0][1] + snake2_direction[1])
        head2 = wrap_around(head2)
        snake2.insert(0, head2)

        # Check for collisions with the food for both players
        if head1 == food:
            food = (random.randrange(0, width, cell_size), random.randrange(0, height, cell_size))
        else:
            snake1.pop()

        if head2 == food:
            food = (random.randrange(0, width, cell_size), random.randrange(0, height, cell_size))
        else:
            snake2.pop()

        # Check for collisions with the walls or itself for both players
        if (
            head1 in snake1[1:] or
            head1 == head2 or
            head1[0] < 0 or head1[0] >= width or
            head1[1] < 0 or head1[1] >= height
        ) or (
            head2 in snake2[1:] or
            head2 == head1 or
            head2[0] < 0 or head2[0] >= width or
            head2[1] < 0 or head2[1] >= height
        ):
            game_over = True

        # Check for collisions between the two snakes
        if check_snake_collision(snake1, snake2) or check_snake_collision(snake2, snake1):
            game_over = True

        # Draw everything
        screen.fill(black)

        # Draw snake 1
        for segment in snake1:
            pygame.draw.rect(screen, red, (segment[0], segment[1], cell_size, cell_size))

        # Draw snake 2
        for segment in snake2:
            pygame.draw.rect(screen, blue, (segment[0], segment[1], cell_size, cell_size))

        # Draw food
        pygame.draw.rect(screen, green, (food[0], food[1], cell_size, cell_size))

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(10)  # You can adjust the speed by changing this value

    # Check if the blue head is inside the red body or red head
    if snake2[0] in snake1 and snake1[0] not in snake2:
        display_winner("Red")
    elif (snake2[0] in snake1 and snake1[0] in snake2 and last_move == 2):
        display_winner("Red 2")
    # Check if the red head is inside the blue body or blue head
    elif snake1[0] in snake2 and snake2[0] not in snake1:
        display_winner("Blue")
    elif (snake2[0] in snake1 and snake1[0] in snake2 and last_move == 1):
        display_winner("Blue 2")
    else:
        # Display the winner or a draw for 2 seconds
        if len(snake1) > len(snake2):
            display_winner("Red")
        elif len(snake2) > len(snake1):
            display_winner("Blue")
        else:
            font = pygame.font.Font(None, 72)
            text = font.render("It's a Draw!", True, white)
            text_contour = font.render("It's a Draw!", True, black)
            text_rect = text.get_rect(center=(width // 2, height // 2))
            screen.blit(text_contour, (text_rect.x - 2, text_rect.y - 2))
            screen.blit(text_contour, (text_rect.x + 2, text_rect.y + 2))
            screen.blit(text_contour, (text_rect.x - 2, text_rect.y + 2))
            screen.blit(text_contour, (text_rect.x + 2, text_rect.y - 2))
            screen.blit(text, text_rect)
            pygame.display.flip()
            time.sleep(2)  # 2 seconds delay

    """
    # Display the winner for 2 seconds
    if len(snake1) > len(snake2):
        display_winner("Red")
    elif len(snake2) > len(snake1):
        display_winner("Blue")
"""
"""
    # Check if Blue goes against himself or against Red
    blue_next_cell = (snake2[0][0] + snake2_direction[0], snake2[0][1] + snake2_direction[1])
    if (blue_next_cell in snake2[1:] or blue_next_cell in snake1):
        display_winner("Red")
    else:
        # Display the winner or a draw for 2 seconds
        if len(snake1) > len(snake2):
            display_winner("Red")
        elif len(snake2) > len(snake1):
            display_winner("Blue")
        else:
            # The rest of your draw handling remains unchanged
            font = pygame.font.Font(None, 72)
            text = font.render("It's a Draw!", True, white)
            text_contour = font.render("It's a Draw!", True, black)
            text_rect = text.get_rect(center=(width // 2, height // 2))
            screen.blit(text_contour, (text_rect.x - 2, text_rect.y - 2))
            screen.blit(text_contour, (text_rect.x + 2, text_rect.y + 2))
            screen.blit(text_contour, (text_rect.x - 2, text_rect.y + 2))
            screen.blit(text_contour, (text_rect.x + 2, text_rect.y - 2))
            screen.blit(text, text_rect)
            pygame.display.flip()
            time.sleep(2)  # 2 seconds delay
""" 
