import pygame
import random
import os

# Get the directory of this script
script_dir = os.path.dirname(__file__)

# Change the working directory to the script's directory
os.chdir(script_dir)

pygame.init()

# Colors
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Initial game state
first_mine_revealed = False
first_mine_position = None

# Difficulty settings
difficulty = "Medium"  # Change to "Easy", "Medium", or "Hard"
if difficulty == "Easy":
    rows, cols, mines = 9, 9, 10
elif difficulty == "Hard":
    rows, cols, mines = 16, 30, 99
else:  # Default to Medium
    rows, cols, mines = 16, 16, 40

# Window size
tile_size = 20
size = (cols * tile_size, rows * tile_size)
screen = pygame.display.set_mode(size)

# Game matrices
matrix = [[' ' for _ in range(cols)] for _ in range(rows)]
visible = [[False for _ in range(cols)] for _ in range(rows)]
flag = [[False for _ in range(cols)] for _ in range(rows)]

# Place mines
for _ in range(mines):
    x, y = random.randint(0, cols-1), random.randint(0, rows-1)
    while matrix[y][x] == 'm':
        x, y = random.randint(0, cols-1), random.randint(0, rows-1)
    matrix[y][x] = 'm'

# Calculate adjacent mines
for y in range(rows):
    for x in range(cols):
        if matrix[y][x] == 'm':
            continue
        count = sum(1 for i in range(-1, 2) for j in range(-1, 2) if 0 <= x+j < cols and 0 <= y+i < rows and matrix[y+i][x+j] == 'm')
        matrix[y][x] = str(count)

# Load icons
mine_icon = pygame.image.load("naval-mine-icon.png").convert_alpha()
mine_icon = pygame.transform.scale(mine_icon, (tile_size, tile_size))
flag_icon = pygame.image.load("minesweeper_flag.png").convert_alpha()
flag_icon = pygame.transform.scale(flag_icon, (tile_size-5, tile_size-5))

def draw_grid():
    for x in range(cols):
        pygame.draw.line(screen, BLACK, (x*tile_size, 0), (x*tile_size, size[1]), 1)
    for y in range(rows):
        pygame.draw.line(screen, BLACK, (0, y*tile_size), (size[0], y*tile_size), 1)

def draw_tiles():
    font = pygame.font.Font(None, 20)
    for y in range(rows):
        for x in range(cols):
            rect = pygame.Rect(x*tile_size, y*tile_size, tile_size, tile_size)
            pygame.draw.rect(screen, GREY, rect)
            if visible[y][x] and matrix[y][x] != 'm':
                text = font.render(matrix[y][x], True, BLACK)
                screen.blit(text, text.get_rect(center=rect.center))
            elif visible[y][x] and matrix[y][x] == 'm':
                if first_mine_position == (x, y):
                    pygame.draw.rect(screen, RED, rect)
                screen.blit(mine_icon, rect)
            elif flag[y][x]:
                screen.blit(flag_icon, flag_icon.get_rect(center=rect.center))

def on_reveal(x, y):
    global first_mine_revealed, first_mine_position
    if 0 <= x < cols and 0 <= y < rows and not visible[y][x] and not flag[y][x]:
        visible[y][x] = True
        if matrix[y][x] == 'm':
            if not first_mine_revealed:
                first_mine_revealed = True
                first_mine_position = (x, y)
            for row in visible:
                for i in range(len(row)):
                    row[i] = True
        elif matrix[y][x] == '0':
            for i in range(-1, 2):
                for j in range(-1, 2):
                    on_reveal(x+j, y+i)

def on_flag(x, y):
    if not visible[y][x]:
        flag[y][x] = not flag[y][x]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            x //= tile_size
            y //= tile_size
            if event.button == 1:
                on_reveal(x, y)
            elif event.button == 3:
                on_flag(x, y)
    screen.fill(WHITE)
    draw_tiles()
    draw_grid()
    pygame.display.flip()

pygame.quit()
