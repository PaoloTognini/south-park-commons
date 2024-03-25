import pygame
import sys
import time

# Initialize Pygame
pygame.init()

# Set up the screen
width, height = 600, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pong")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)

# Paddle A
paddle_a = pygame.Rect(50, height // 2 - 30, 10, 60)

# Paddle B
paddle_b = pygame.Rect(width - 60, height // 2 - 30, 10, 60)

# Ball
ball = pygame.Rect(width // 2 - 10, height // 2 - 10, 20, 20)
ball_speed = [4, 4]

# Timer variables
start_time = time.time()
reset_time = 2  # seconds

# Clock to control the frame rate
clock = pygame.time.Clock()

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    # Paddle A controls
    if keys[pygame.K_w] and paddle_a.top > 0:
        paddle_a.y -= 5
    if keys[pygame.K_s] and paddle_a.bottom < height:
        paddle_a.y += 5

    # Paddle B controls
    if keys[pygame.K_UP] and paddle_b.top > 0:
        paddle_b.y -= 5
    if keys[pygame.K_DOWN] and paddle_b.bottom < height:
        paddle_b.y += 5

    # Move the ball
    ball.x += ball_speed[0]
    ball.y += ball_speed[1]

    # Ball collisions with walls
    if ball.top <= 0 or ball.bottom >= height:
        ball_speed[1] = -ball_speed[1]

    # Ball collisions with paddles
    if ball.colliderect(paddle_a) or ball.colliderect(paddle_b):
        ball_speed[0] = -ball_speed[0]

    # Check if the ball is off the screen for more than 2 seconds
    if ball.right < 0 or ball.left > width:
        elapsed_time = time.time() - start_time
        if elapsed_time > reset_time:
            ball.x = width // 2 - 10
            ball.y = height // 2 - 10
            start_time = time.time()

    # Draw everything
    screen.fill(black)
    pygame.draw.rect(screen, white, paddle_a)
    pygame.draw.rect(screen, white, paddle_b)
    pygame.draw.ellipse(screen, white, ball)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

