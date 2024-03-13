import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Define some colors
BLACK = (0, 0, 0)
DARK_GREY = (100, 100, 100)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
DARK_FOREST_GREEN = (22, 86, 41)
DARK_DESATURATED_RED = (100, 20, 20)

# Set the width and height of the screen (width, height).
size = (420, 420)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Connect Four")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates.
clock = pygame.time.Clock()

# Set the width and height of the grid
grid_width = 7
grid_height = 6

# Create the grid
grid = [[' ' for _ in range(grid_width)] for _ in range(grid_height)]


def cpu_turn(grid):
    for i in range(grid_height - 1, -1, -1):
        for j in range(grid_width):
            if grid[i][j] == ' ':
                grid[i][j] = 'O'
                if check_win('O', grid):
                    return
                grid[i][j] = ' '
    return

# Checks if there is a win
def check_win(player, grid):
    # Check for win conditions
    for i in range(grid_height):
        for j in range(grid_width - 3):
            if grid[i][j] == grid[i][j+1] == grid[i][j+2] == grid[i][j+3] == player:
                return True



def check_winner(grid):
    # Check for horizontal wins
    for i in range(grid_height):
        for j in range(grid_width - 3):
            if grid[i][j] == grid[i][j+1] == grid[i][j+2] == grid[i][j+3] != ' ':
                return grid[i][j]

    # Check for vertical wins
    for i in range(grid_height - 3):
        for j in range(grid_width):
            if grid[i][j] == grid[i+1][j] == grid[i+2][j] == grid[i+3][j] != ' ':
                return grid[i][j]

    # Check for diagonal wins (top-left to bottom-right)
    for i in range(grid_height - 3):
        for j in range(grid_width - 3):
            if grid[i][j] == grid[i+1][j+1] == grid[i+2][j+2] == grid[i+3][j+3] != ' ':
                return grid[i][j]

    # Check for diagonal wins (bottom-left to top-right)
    for i in range(3, grid_height):
        for j in range(grid_width - 3):
            if grid[i][j] == grid[i-1][j+1] == grid[i-2][j+2] == grid[i-3][j+3] != ' ':
                return grid[i][j]

    return None

# -------- Main Program Loop -----------
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Get the mouse position
            pos = pygame.mouse.get_pos()

            column = pos[0] // 60
            for i in range(grid_height - 1, -1, -1):
                if grid[i][column] == ' ':
                    grid[i][column] = 'X'
                    break

            cpu_column = random.randint(0, grid_width - 1)
            for i in range(grid_height - 1, -1, -1):
                if grid[i][cpu_column] == ' ':
                    grid[i][cpu_column] = 'O'
                    break

            # Check for win conditions
            for i in range(grid_height - 3):
                for j in range(grid_width - 3):
                    if grid[i][j] == grid[i+1][j+1] == grid[i+2][j+2] == grid[i+3][j+3] != ' ':
                        if grid[i][j] == 'X':
                            text = "You Win"
                            color = DARK_FOREST_GREEN
                        else:
                            text = "You Lose"
                            color = DARK_DESATURATED_RED
                        font = pygame.font.Font(None, 40)
                        text_surface = font.render(text, True, color)
                        text_rect = text_surface.get_rect(center=(210, 400))
                        screen.blit(text_surface, text_rect)
                        pygame.display.flip()
                        pygame.time.wait(3000)
                        done = True
                        break

    screen.fill(BLACK)
    for i in range(grid_height):
        for j in range(grid_width):
            pygame.draw.rect(screen, DARK_GREY, [j * 60, i * 60, 60, 60], 1)
    for i in range(grid_height):
        for j in range(grid_width):
            if grid[i][j] == 'X':
                pygame.draw.circle(screen, RED, [j * 60 + 30, i * 60 + 30], 20)
            elif grid[i][j] == 'O':
                pygame.draw.circle(screen, YELLOW, [j * 60 + 30, i * 60 + 30], 20)
            elif grid[i][j] == ' ':
                pygame.draw.circle(screen, DARK_GREY, [j * 60 + 30, i * 60 + 30], 20)
    pygame.draw.rect(screen, DARK_GREY, [0, 400, 420, 20])

    # Check if the game is still ongoing
    if not done:
        text = "Connect Four"
        color = DARK_GREY
    else:
        text = "Game Over"
        color = BLACK

    font = pygame.font.Font(None, 40)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(210, 410))
    screen.blit(text_surface, text_rect)
    clock.tick(60)
    pygame.display.flip()
pygame.quit()
