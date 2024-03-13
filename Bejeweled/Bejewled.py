import pygame
import sys
import random
import os

game_directory = os.path.dirname(__file__)
os.chdir(game_directory)

pygame.init()

# Set up some constants
BLOCK_SIZE = 50
GRID_SIZE = 8
EXPLOSION_TIME = 70  # Time in milliseconds for the explosion animation
HEIGHT_INCREASE = 30  # Additional height for the score display

# Set up the display
WIDTH, HEIGHT = BLOCK_SIZE * GRID_SIZE+2, BLOCK_SIZE * GRID_SIZE + HEIGHT_INCREASE
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BLUE = (135, 206, 250)

# Set up the font
font = pygame.font.Font(None, 36)

# Set up the grid
grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

explosion_times = {}  # key: (i, j) tuple for grid position, value: start_time

# Filenames of the images
image_filenames = [
    "blue_gem.png",
    "green_gem.png",
    "heart_gem.png",
    "orange_gem.png",
    "purple_gem.png",
    "red_gem.png",
    "yellow_gem.png",
]

# Load each image and append it to the list
images = []
for filename in image_filenames:
    image = pygame.image.load(filename)
    images.append(image)

# Scale the images to the size of a grid box
scaled_images = []
for image in images:
    scaled_image = pygame.transform.scale(image, (BLOCK_SIZE, BLOCK_SIZE))
    scaled_images.append(scaled_image)

# Load the explosion image
explosion_image = pygame.image.load("explosion.png")
explosion_image = pygame.transform.scale(explosion_image, (BLOCK_SIZE, BLOCK_SIZE))

# Randomly place the scaled images into the grid
for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        # Make sure not to place three of the same gem in a row
        while True:
            gem = random.choice(scaled_images)
            if (i > 0 and grid[i-1][j] == gem and (i > 1 and grid[i-2][j] == gem)) or (j > 0 and grid[i][j-1] == gem and (j > 1 and grid[i][j-2] == gem)):
                continue
            else:
                grid[i][j] = gem
                break

def can_switch(i, j, i2, j2):
    # Copy the grid to test if the switch would result in a match
    temp_grid = [row.copy() for row in grid]
    temp_grid[i][j], temp_grid[i2][j2] = temp_grid[i2][j2], temp_grid[i][j]
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if temp_grid[i][j] != 0:
                # Check for horizontal matches
                if j < GRID_SIZE - 2 and all(temp_grid[i][j+k] == temp_grid[i][j] for k in range(3)):
                    return True
                # Check for vertical matches
                if i < GRID_SIZE - 2 and all(temp_grid[i+k][j] == temp_grid[i][j] for k in range(3)):
                    return True
    return False

# Function to check and remove sequences
def check_and_remove_sequences():
    global score
    removed_gems = True
    while removed_gems:
        removed_gems = False
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if grid[i][j] != 0:
                    # Check horizontally
                    sequence_length = 1
                    while j + sequence_length < GRID_SIZE and grid[i][j+sequence_length] == grid[i][j]:
                        sequence_length += 1
                    if sequence_length >= 3:
                        multiplier = 1
                        if sequence_length == 4:
                            multiplier = 1.2
                        elif sequence_length == 5:
                            multiplier = 1.5
                        elif sequence_length > 5:
                            multiplier = 2
                        score += sequence_length * 100 * multiplier
                        for k in range(sequence_length):
                            grid[i][j+k] = 0
                            explosion_times[(i, j+k)] = pygame.time.get_ticks()
                        removed_gems = True
                    # Check vertically
                    sequence_length = 1
                    while i + sequence_length < GRID_SIZE and grid[i+sequence_length][j] == grid[i][j]:
                        sequence_length += 1
                    if sequence_length >= 3:
                        multiplier = 1
                        if sequence_length == 4:
                            multiplier = 1.2
                        elif sequence_length == 5:
                            multiplier = 1.5
                        elif sequence_length > 5:
                            multiplier = 2
                        score += sequence_length * 100 * multiplier
                        score = int(score)
                        for k in range(sequence_length):
                            grid[i+k][j] = 0
                            explosion_times[(i+k, j)] = pygame.time.get_ticks()
                        removed_gems = True
                        
    # After removing the sequences, slide down the gems
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE-1, -1, -1):
            if grid[i][j] == 0:
                for k in range(j-1, -1, -1):
                    if grid[i][k] != 0:
                        grid[i][j] = grid[i][k]
                        grid[i][k] = 0
                        break

    # Fill the top of the columns with new gems
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if grid[i][j] == 0:
                grid[i][j] = random.choice(scaled_images)
                
                
    # Create a new list to store the gems in their temporary positions
temp_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Fill the top of the columns with new gems
for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        if grid[i][j] == 0:
            temp_grid[i][j] = random.choice(scaled_images)

# Game loop
running = True
selected = None
selected_image = None
dragging = False
score = 0

# Set up the explosion animation
pygame.time.set_timer(pygame.USEREVENT + 1, EXPLOSION_TIME)
explosion_pos = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            i, j = x // BLOCK_SIZE, y // BLOCK_SIZE
            if grid[i][j] != 0:
                selected = (i, j)
                dragging = True
                drag_offset_x = x - i * BLOCK_SIZE
                drag_offset_y = y - j * BLOCK_SIZE
        elif event.type == pygame.MOUSEBUTTONUP:
            x, y = event.pos
            i2, j2 = x // BLOCK_SIZE, y // BLOCK_SIZE
            if selected and (i2, j2) != selected and dragging:
                if abs(i2 - selected[0]) + abs(j2 - selected[1]) == 1:
                    if can_switch(selected[0], selected[1], i2, j2):
                        grid[i2][j2], grid[selected[0]][selected[1]] = grid[selected[0]][selected[1]], grid[i2][j2]
                        check_and_remove_sequences()
                        # Reset the dragging state
                        selected = None
                        dragging = False
                    else:
                        # Snap the gem back into its original space
                        selected = None
                        dragging = False
                else:
                    # Snap the gem back into its original space
                    selected = None
                    dragging = False
            elif selected and (i2, j2) == selected:
                selected = None
                dragging = False
            elif selected and (i2, j2) == selected:
                selected = None
                dragging = False
        elif event.type == pygame.USEREVENT + 1:
            # Explosion animation event
            to_be_removed = []
            for pos in explosion_times:
                if pygame.time.get_ticks() - explosion_times[pos] >= EXPLOSION_TIME:
                    grid[pos[0]][pos[1]] = 0
                    to_be_removed.append(pos)

            for pos in to_be_removed:
                explosion_times.pop(pos)

            check_and_remove_sequences()

     # Move the gems down
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if temp_grid[i][j] != 0:
                # Move the gem down
                temp_grid[i][j] = grid[i][j]
                grid[i][j] = 0

    # Draw the gems in their temporary positions
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if temp_grid[i][j] != 0:
                screen.blit(temp_grid[i][j], (j * BLOCK_SIZE, i * BLOCK_SIZE))

    # Draw the gems in their final positions
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if grid[i][j] != 0:
                screen.blit(grid[i][j], (j * BLOCK_SIZE, i * BLOCK_SIZE))

    screen.fill(LIGHT_BLUE)

    # Draw the gridlines
    for i in range(GRID_SIZE + 1):
        pygame.draw.line(screen, BLACK, (i * BLOCK_SIZE, 0), (i * BLOCK_SIZE, HEIGHT - HEIGHT_INCREASE), 2)
        pygame.draw.line(screen, BLACK, (0, i * BLOCK_SIZE), (WIDTH, i * BLOCK_SIZE), 2)

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if grid[i][j] != 0:
                if (i, j) != selected or not dragging:  # Add this condition
                    screen.blit(grid[i][j], (i * BLOCK_SIZE, j * BLOCK_SIZE))
                if (i, j) in explosion_times:
                    screen.blit(explosion_image, (i * BLOCK_SIZE, j * BLOCK_SIZE))

    if dragging and selected:
        x, y = pygame.mouse.get_pos()
        gem_image = pygame.transform.scale(grid[selected[0]][selected[1]], (BLOCK_SIZE - 10, BLOCK_SIZE - 10))
        screen.blit(gem_image, (x - gem_image.get_width() // 2, y - gem_image.get_height() // 2))

    # Draw the score in the center at the bottom of the screen
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, BLACK)
    score_rect = score_text.get_rect(center=(110+WIDTH//2, HEIGHT-HEIGHT_INCREASE//2))
    screen.blit(score_text, score_rect)

    # Update the display
    pygame.display.flip()

pygame.quit()
sys.exit()
