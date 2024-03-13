import pygame
import random

# Initialize Pygame
pygame.init()

# Define some colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Set the width and height of the screen (width, height).
size = (700, 700)
screen = pygame.display.set_mode(size)

# Set the size of the grid
grid_size = 10

# Set the number of pixels per grid
pixel_per_grid = size[0] // grid_size

# Create a clock object to help track time.
clock = pygame.time.Clock()

# Set up the food
food_x = random.randint(0, grid_size - 1)
food_y = random.randint(0, grid_size - 1)
food_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Set up the snake
snake_x = random.randint(0, grid_size - 1)
snake_y = random.randint(0, grid_size - 1)
snake_color = WHITE  # Off white
snake_body = [(snake_x, snake_y)]

# Set up the direction of the snake
snake_direction = "RIGHT"

# Speed of the snake
speed = 5  # Increase or decrease this value to change the game's speed

# Game loop
running = True
while running:

    # Process input (events)
    for event in pygame.event.get():
        # Check for closing window
        if event.type == pygame.QUIT:
            running = False

    # Get a list of all keys currently being pressed down
    keys = pygame.key.get_pressed()

    # Change direction of the snake if a key is pressed
    if keys[pygame.K_w] and snake_direction != "DOWN":
        snake_direction = "UP"
    if keys[pygame.K_s] and snake_direction != "UP":
        snake_direction = "DOWN"
    if keys[pygame.K_a] and snake_direction != "RIGHT":
        snake_direction = "LEFT"
    if keys[pygame.K_d] and snake_direction != "LEFT":
        snake_direction = "RIGHT"

    # Move the snake
    if snake_direction == "UP":
        snake_y -= 1
    elif snake_direction == "DOWN":
        snake_y += 1
    elif snake_direction == "LEFT":
        snake_x -= 1
    elif snake_direction == "RIGHT":
        snake_x += 1

    # Add the new head to the snake's body
    snake_body.insert(0, (snake_x, snake_y))

    # Check if the snake has eaten the food
    if snake_x == food_x and snake_y == food_y:
        # Generate new food
        food_x = random.randint(0, grid_size - 1)
        food_y = random.randint(0, grid_size - 1)
        food_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    else:
        # Remove the tail of the snake
        snake_body.pop()

    # Check if the snake has hit the wall or itself
    if snake_x < 0 or snake_x >= grid_size or snake_y < 0 or snake_y >= grid_size or (snake_x, snake_y) in snake_body[1:]:
        running = False

    # Render
    screen.fill(DARK_GREEN)  # Fill the screen with a dark green color

    # Draw the grid
    for i in range(grid_size):
        pygame.draw.line(screen, BLACK, (i * pixel_per_grid, 0), (i * pixel_per_grid, size[1]), 2)
        pygame.draw.line(screen, BLACK, (0, i * pixel_per_grid), (size[0], i * pixel_per_grid), 2)

    # Draw the food
    pygame.draw.circle(screen, food_color, (food_x * pixel_per_grid + pixel_per_grid // 2, food_y * pixel_per_grid + pixel_per_grid // 2), pixel_per_grid // 3)

    # Draw the snake
    for part in snake_body:
        pygame.draw.circle(screen, snake_color, (part[0] * pixel_per_grid + pixel_per_grid // 2, part[1] * pixel_per_grid + pixel_per_grid // 2), pixel_per_grid // 3)

    # Update the screen
    pygame.display.flip()

    # Limit the loop to a maximum of `speed` times per second.
    clock.tick(speed)

# Close the window and quit
pygame.quit()
