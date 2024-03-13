import pygame
import random
import string
import math  # Import math module for calculations

pygame.init()

SCREEN_WIDTH = 370
SCREEN_HEIGHT = 380
CELL_SIZE = 70
MARGIN = 10
CELL_CENTER = CELL_SIZE // 2
RADIUS = CELL_CENTER // 2 + 5  # Circle radius
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Word Finder Game")

font = pygame.font.SysFont('Arial', 32)  # Initialize font

boards = [
    [['S', 'P', 'E', 'L', 'L'],
    ['D', 'A', 'Z', 'E', 'D'],
    ['R', 'A', 'I', 'N', 'S'],
    ['P', 'A', 'S', 'S', 'I'],
    ['C', 'A', 'T', 'N', 'O']],
    
    [['M', 'B', 'I', 'R', 'D'],
    ['E', 'A', 'D', 'F', 'D'],
    ['W', 'N', 'E', 'L', 'I'],
    ['R', 'I', 'A', 'O', 'R'],
    ['E', 'T', 'D', 'P', 'E']],
    
    [['B', 'E', 'D', 'O', 'G'],
    ['I', 'G', 'L', 'B', 'I'],
    ['U', 'M', 'T', 'E', 'K'],
    ['A', 'D', 'E', 'L', 'A'],
    ['E', 'R', 'D', 'S', 'S']]
]

def generate_grid():
    return random.choice(boards)

def get_cell_rect(i, j):
    return pygame.Rect(j * CELL_SIZE + MARGIN, i * CELL_SIZE + MARGIN, CELL_SIZE, CELL_SIZE)

def draw_grid():
    for i in range(5):
        for j in range(5):
            cell_rect = get_cell_rect(i, j)
            pygame.draw.rect(screen, (255, 255, 255), cell_rect)
            text = font.render(grid[i][j], True, (0, 0, 0))
            text_rect = text.get_rect(center=cell_rect.center)
            screen.blit(text, text_rect)

def draw_highlight(x, y):
    pygame.draw.circle(screen, (0, 0, 255), (x, y), RADIUS, 5)

def adjust_line(x1, y1, x2, y2, radius):
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx**2 + dy**2)
    if distance == 0:  # Prevent division by zero
        return x1, y1, x2, y2
    dx /= distance
    dy /= distance
    return x1 + dx * radius, y1 + dy * radius, x2 - dx * radius, y2 - dy * radius

def draw_line(x1, y1, x2, y2):
    adjusted_x1, adjusted_y1, adjusted_x2, adjusted_y2 = adjust_line(x1, y1, x2, y2, RADIUS)
    pygame.draw.line(screen, (0, 0, 255), (adjusted_x1, adjusted_y1), (adjusted_x2, adjusted_y2), 5)

def is_adjacent(pos1, pos2):
    return pos1[0] == pos2[0] and abs(pos1[1] - pos2[1]) == 1 or pos1[1] == pos2[1] and abs(pos1[0] - pos2[0]) == 1

grid = generate_grid()
is_drawing = False
previous_positions = []
word = ''
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if mx < 0 or my < 0 or mx > SCREEN_WIDTH or my > SCREEN_HEIGHT:
                continue  # Ignore clicks outside the window
            col = mx // CELL_SIZE
            row = my // CELL_SIZE
            if 0 <= row < 5 and 0 <= col < 5:
                is_drawing = True
                previous_positions = [(col, row)]
                word = grid[row][col]  # Start the word with the first letter
        elif event.type == pygame.MOUSEBUTTONUP or (event.type == pygame.MOUSEMOTION and (event.pos[0] < 0 or event.pos[1] < 0 or event.pos[0] > SCREEN_WIDTH or event.pos[1] > SCREEN_HEIGHT)):
            is_drawing = False
            print(word)  # Output the collected word
            word = ''  # Reset for the next word collection
            previous_positions = []

    if is_drawing:
        mx, my = pygame.mouse.get_pos()
        if mx < 0 or my < 0 or mx > SCREEN_WIDTH or my > SCREEN_HEIGHT:
            is_drawing = False
            print(word)  # Output the collected word as if the mouse was released
            word = ''  # Reset for the next word collection
            previous_positions = []
        else:
            col = mx // CELL_SIZE
            row = my // CELL_SIZE
            if 0 <= row < 5 and 0 <= col < 5:
                current_position = (col, row)
                if current_position not in previous_positions and is_adjacent(current_position, previous_positions[-1]):
                    previous_positions.append(current_position)
                    if len(word) < len(previous_positions):  # Append new letter if not already added
                        word += grid[row][col]

    screen.fill((255, 255, 255))
    draw_grid()

    for i, (col, row) in enumerate(previous_positions):
        x, y = col * CELL_SIZE + MARGIN + CELL_CENTER, row * CELL_SIZE + MARGIN + CELL_CENTER
        draw_highlight(x, y)
        if i > 0:
            prev_col, prev_row = previous_positions[i-1]
            prev_x = prev_col * CELL_SIZE + MARGIN + CELL_CENTER
            prev_y = prev_row * CELL_SIZE + MARGIN + CELL_CENTER
            draw_line(prev_x, prev_y, x, y)

    pygame.display.flip()

pygame.quit()