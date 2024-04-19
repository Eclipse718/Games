import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 800, 700
GRID_SIZE = 250
TILE_SIZE = 20
ZOOM_SENSITIVITY = 0.1
TRANSLATE_SENSITIVITY = 15

# Create the game screen
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE)

# Create a grid with all zeros
grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Set up variables to track translation and zoom
translation_x = 0
translation_y = 0
zoom = 1

# Load the insect image
insect_image = pygame.image.load(os.path.join(os.path.dirname(__file__), 'insect.png'))

# Set up a list to hold all ants
ants = []

# Set up a clock to control the framerate
clock = pygame.time.Clock()

class Ant:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 0  # 0: up, 1: right, 2: down, 3: left

    def move(self):
        if grid[self.x][self.y] == 0:
            self.direction = (self.direction + 1) % 4
        else:
            self.direction = (self.direction - 1) % 4
        grid[self.x][self.y] = 1 - grid[self.x][self.y]
        if self.direction == 0:
            self.y = (self.y - 1) % GRID_SIZE
        elif self.direction == 1:
            self.x = (self.x + 1) % GRID_SIZE
        elif self.direction == 2:
            self.y = (self.y + 1) % GRID_SIZE
        elif self.direction == 3:
            self.x = (self.x - 1) % GRID_SIZE

    def draw(self):
        scaled_insect_image = pygame.transform.scale(insect_image, (TILE_SIZE * zoom, TILE_SIZE * zoom))
        screen.blit(scaled_insect_image, (self.x * TILE_SIZE * zoom + translation_x, self.y * TILE_SIZE * zoom + translation_y))

click_time = 0

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                zoom += ZOOM_SENSITIVITY
            else:
                zoom -= ZOOM_SENSITIVITY
                if zoom < 0.1:
                    zoom = 0.1
        elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
            translation_x += event.rel[0] / zoom
            translation_y += event.rel[1] / zoom
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click_time = pygame.time.get_ticks()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if pygame.time.get_ticks() - click_time <= 100:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                tile_x = int((mouse_x - translation_x) / (TILE_SIZE * zoom))
                tile_y = int((mouse_y - translation_y) / (TILE_SIZE * zoom))
                if 0 <= tile_x < GRID_SIZE and 0 <= tile_y < GRID_SIZE:
                    ants.append(Ant(tile_x, tile_y))

    # Fill the screen with white
    screen.fill((255, 255, 255))

    # Calculate the size of the tiles
    tile_size = TILE_SIZE * zoom

    # Draw the grid
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            color = (255, 255, 255) if grid[i][j] == 0 else (0, 0, 0)
            rect = pygame.Rect((i * tile_size + translation_x, j * tile_size + translation_y), (tile_size, tile_size))
            pygame.draw.rect(screen, color, rect)

    # Move and draw each ant
    for ant in ants:
        ant.move()
        ant.draw()

    # Draw the gridlines
    for i in range(GRID_SIZE + 1):
        pygame.draw.line(screen, (0, 0, 0), (i * tile_size + translation_x, translation_y), (i * tile_size + translation_x, GRID_SIZE * tile_size + translation_y))
        pygame.draw.line(screen, (0, 0, 0), (translation_x, i * tile_size + translation_y), (GRID_SIZE * tile_size + translation_x, i * tile_size + translation_y))

    # Update the display
    pygame.display.flip()

    # Limit the framerate to 60 FPS
    clock.tick(60)