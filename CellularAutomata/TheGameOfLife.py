import pygame
import numpy as np
import os
import pygame_gui

# Window size
WIDTH, HEIGHT = 800, 600
# Cell size
CELL_SIZE = 15
# Grid size
GRID_WIDTH, GRID_HEIGHT = 600 // CELL_SIZE, 600 // CELL_SIZE

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

# Load the BackArrow image
back_arrow = pygame.image.load('BackArrow.png')
back_arrow = pygame.transform.scale(back_arrow, (50, 50))

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Game state variables
homescreen = True
game_of_life = False

global game_of_life_grid
game_of_life_grid = np.zeros((GRID_HEIGHT, GRID_WIDTH))
global stat_stop
start_stop = False

global frames
frames = 0

preset_selector = pygame.Rect(700 - 100, 300 - 25, 200, 50)
global colors


def get_color(color):
    if color == 0:
        return (255, 255, 255)  # White
    elif color == 1:
        return (0, 0, 255)  # Blue
    elif color == 2:
        return (255, 0, 0)  # Red
    elif color == 3:
        return (0, 255, 0)  # Green
    elif color == 4:
        return (255, 255, 0)  # Yellow
    elif color == 5:
        return (255, 192, 203)  # Pink
    elif color == 6:
        return (238, 130, 238)  # Violet
    elif color == 7:
        return (0, 255, 255)  # Turquoise
    else:
        return (255, 255, 255)  # White


langton_rules = {
    '00000': 0,
    '00001': 2,
    '00002': 0,
    '00003': 0,
    '00005': 0,
    '00006': 3,
    '00007': 1,
    '00011': 2,
    '00012': 2,
    '00013': 2,
    '00021': 2,
    '00022': 0,
    '00023': 0,
    '00026': 2,
    '00027': 2,
    '00032': 0,
    '00052': 5,
    '00062': 2,
    '00072': 2,
    '00102': 2,
    '00112': 0,
    '00202': 0,
    '00203': 0,
    '00205': 0,
    '00212': 5,
    '00222': 0,
    '00232': 2,
    '00522': 2,
    '01232': 1,
    '01242': 1,
    '01252': 5,
    '01262': 1,
    '01272': 1,
    '01275': 1,
    '01422': 1,
    '01432': 1,
    '01442': 1,
    '01472': 1,
    '01625': 1,
    '01722': 1,
    '01725': 5,
    '01752': 1,
    '01762': 1,
    '01772': 1,
    '02527': 1,
    '10001': 1,
    '10006': 1,
    '10007': 7,
    '10011': 1,
    '10012': 1,
    '10021': 1,
    '10024': 4,
    '10027': 7,
    '10051': 1,
    '10101': 1,
    '10111': 1,
    '10124': 4,
    '10127': 7,
    '10202': 6,
    '10212': 1,
    '10221': 1,
    '10224': 4,
    '10226': 3,
    '10227': 7,
    '10232': 7,
    '10242': 4,
    '10262': 6,
    '10264': 4,
    '10267': 7,
    '10271': 0,
    '10272': 7,
    '10542': 7,
    '11112': 1,
    '11122': 1,
    '11124': 4,
    '11125': 1,
    '11126': 1,
    '11127': 7,
    '11152': 2,
    '11212': 1,
    '11222': 1,
    '11224': 4,
    '11225': 1,
    '11227': 7,
    '11232': 1,
    '11242': 4,
    '11262': 1,
    '11272': 7,
    '11322': 1,
    '12224': 4,
    '12227': 7,
    '12243': 4,
    '12254': 7,
    '12324': 4,
    '12327': 7,
    '12425': 5,
    '12426': 7,
    '12527': 5,
    '20001': 2,
    '20002': 2,
    '20004': 2,
    '20007': 1,
    '20012': 2,
    '20015': 2,
    '20021': 2,
    '20022': 2,
    '20023': 2,
    '20024': 2,
    '20025': 0,
    '20026': 2,
    '20027': 2,
    '20032': 6,
    '20042': 3,
    '20051': 7,
    '20052': 2,
    '20057': 5,
    '20072': 2,
    '20102': 2,
    '20112': 2,
    '20122': 2,
    '20142': 2,
    '20172': 2,
    '20202': 2,
    '20203': 2,
    '20205': 2,
    '20207': 3,
    '20212': 2,
    '20215': 2,
    '20221': 2,
    '20222': 2,
    '20227': 2,
    '20232': 1,
    '20242': 2,
    '20245': 2,
    '20252': 0,
    '20255': 2,
    '20262': 2,
    '20272': 2,
    '20312': 2,
    '20321': 6,
    '20322': 6,
    '20342': 2,
    '20422': 2,
    '20512': 2,
    '20521': 2,
    '20522': 2,
    '20552': 1,
    '20572': 5,
    '20622': 2,
    '20672': 2,
    '20712': 2,
    '20722': 2,
    '20742': 2,
    '20772': 2,
    '21122': 2,
    '21126': 1,
    '21222': 2,
    '21224': 2,
    '21226': 2,
    '21227': 2,
    '21422': 2,
    '21522': 2,
    '21622': 2,
    '21722': 2,
    '22227': 2,
    '22244': 2,
    '22246': 2,
    '22276': 2,
    '22277': 2,
    '30001': 3,
    '30002': 2,
    '30004': 1,
    '30007': 6,
    '30012': 3,
    '30042': 1,
    '30062': 2,
    '30102': 1,
    '30122': 0,
    '30251': 1,
    '40112': 0,
    '40122': 0,
    '40125': 0,
    '40212': 0,
    '40222': 1,
    '40232': 6,
    '40252': 0,
    '40322': 1,
    '50002': 2,
    '50021': 5,
    '50022': 5,
    '50023': 2,
    '50027': 2,
    '50052': 0,
    '50202': 2,
    '50212': 2,
    '50215': 2,
    '50222': 0,
    '50224': 4,
    '50272': 2,
    '51212': 2,
    '51222': 0,
    '51242': 2,
    '51272': 2,
    '60001': 1,
    '60002': 1,
    '60212': 0,
    '61212': 5,
    '61213': 1,
    '61222': 5,
    '70007': 7,
    '70112': 0,
    '70122': 0,
    '70125': 0,
    '70212': 0,
    '70222': 1,
    '70225': 1,
    '70232': 1,
    '70252': 5,
    '70272': 0
}



# Function to draw the homescreen
def draw_homescreen():
    screen.fill((255, 255, 255))

    # Draw start button
    pygame.draw.rect(screen, (0, 0, 0), (WIDTH / 2 - 75, HEIGHT / 2 - 40, 150, 50), 2)
    font = pygame.font.Font(pygame.font.match_font('times new roman'), 36)
    text = font.render("Conway's", True, (0, 0, 0))
    text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 15))
    screen.blit(text, text_rect)

    # Draw Langton's Loop button
    pygame.draw.rect(screen, (0, 0, 0), (WIDTH / 2 - 115, HEIGHT / 2 + 50, 230, 50), 2)
    text = font.render("Langton's Loop", True, (0, 0, 0))
    text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 80))
    screen.blit(text, text_rect)


def apply_langton_loop_laws():
    global langton_loop_grid
    # Create a copy of the grid to calculate the next state
    grid_copy = langton_loop_grid.copy()

    # Iterate over each cell in the grid
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile_identity = get_tile_identity(x, y, grid_copy)
            found_match = False
            
            # List all symmetrical variants including the original orientation
            symmetrical_variants = [
                tile_identity,  # Original orientation
                (tile_identity[0], tile_identity[2], tile_identity[3], tile_identity[4], tile_identity[1]),  # Rotate 90 degrees
                (tile_identity[0], tile_identity[3], tile_identity[4], tile_identity[1], tile_identity[2]),  # Rotate 180 degrees
                (tile_identity[0], tile_identity[4], tile_identity[1], tile_identity[2], tile_identity[3])   # Rotate 270 degrees
            ]
            
            # Check each variant against the rules
            for variant in symmetrical_variants:
                if found_match:
                    break
                for law, result in langton_rules.items():
                    if variant == tuple(int(i) for i in law[:5]):
                        langton_loop_grid[y, x] = int(result)
                        found_match = True
                        break

# Helper function to get the tile's identity based on the current grid
def get_tile_identity(x, y, grid):
    # Wrap around the grid edges
    north = grid[(y - 1) % GRID_HEIGHT, x]
    east = grid[y, (x + 1) % GRID_WIDTH]
    south = grid[(y + 1) % GRID_HEIGHT, x]
    west = grid[y, (x - 1) % GRID_WIDTH]
    return (grid[y, x], north, east, south, west)



def apply_game_of_life_rules(grid):
    new_grid = np.copy(grid)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            live_neighbors = 0
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dy == 0 and dx == 0:
                        continue
                    ny = (y + dy) % GRID_HEIGHT
                    nx = (x + dx) % GRID_WIDTH
                    if grid[ny, nx] == 1:
                        live_neighbors += 1
            if grid[y, x] == 1:
                if live_neighbors < 2 or live_neighbors > 3:
                    new_grid[y, x] = 0
            else:
                if live_neighbors == 3:
                    new_grid[y, x] = 1
    return new_grid

# Function to draw the game of life
def draw_game_of_life():
    global game_of_life_grid, frames
    screen.fill((255, 255, 255))
    # Draw grid
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            pygame.draw.rect(screen, (0, 0, 0), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

    # Draw cells
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if game_of_life_grid[y, x]:
                pygame.draw.rect(screen, (0, 0, 0), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Draw start/stop button
    pygame.draw.rect(screen, (0, 0, 0), (700 - 50, 250 - 25, 100, 50), 2)

    font = pygame.font.Font(None, 36)
    text = font.render("Start" if not start_stop else "Stop", True, (0, 0, 0))
    screen.blit(text, (700 - 25, 250 - 15))

    if current_preset_index == 1:
        preset_selector = pygame.Rect(700 - 75, 300, 150, 50)
    elif current_preset_index == 2:
        preset_selector = pygame.Rect(700 - 80, 300, 160, 50)
    elif current_preset_index == 3:
        preset_selector = pygame.Rect(700 - 95, 300, 190, 50)
    elif current_preset_index == 4:
        preset_selector = pygame.Rect(700 - 95, 300, 190, 50)
    else:
        preset_selector = pygame.Rect(700 - 50, 300, 100, 50)

    pygame.draw.rect(screen, (0, 0, 0), preset_selector, 2)
    if current_preset_index == 3 or current_preset_index == 4:
        font = pygame.font.Font(None, 25)
    else:
        font = pygame.font.Font(None, 36)
    text = font.render(preset_names[current_preset_index], True, (0, 0, 0))

    # Calculate text position to center it in the box
    text_rect = text.get_rect(center=preset_selector.center)
    screen.blit(text, text_rect)

    # Draw back arrow
    screen.blit(back_arrow, (WIDTH - 60, HEIGHT - 60))
    
    if start_stop:
        if frames % 35 == 0:
            game_of_life_grid = apply_game_of_life_rules(game_of_life_grid)

# Create a grid of random 1s and 0s
grid = np.random.randint(2, size=(GRID_HEIGHT, GRID_WIDTH))

# Cell size
CELL_SIZE = 15
# Grid size
GRID_WIDTH, GRID_HEIGHT = 600 // CELL_SIZE, 600 // CELL_SIZE
langton_loop_grid = np.full((GRID_HEIGHT, GRID_WIDTH), 0)





selected_color = 2

def draw_Langton_loop():
    global langton_loop_grid, selected_color, langton_loop_start
    screen.fill((255, 255, 255))
    # Draw grid
    if langton_loop_start:
        apply_langton_loop_laws()
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            pygame.draw.rect(screen, (0, 0, 0), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

    # Draw cells
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if langton_loop_grid[y, x] == 0:
                color = (255, 255, 255)  # White
            elif langton_loop_grid[y, x] == 1:
                color = (0, 0, 255)  # Blue
            elif langton_loop_grid[y, x] == 2:
                color = (255, 0, 0)  # Red
            elif langton_loop_grid[y, x] == 3:
                color = (0, 255, 0)  # Green
            elif langton_loop_grid[y, x] == 4:
                color = (255, 255, 0)  # Yellow
            elif langton_loop_grid[y, x] == 5:
                color = (255, 192, 203)  # Pink
            elif langton_loop_grid[y, x] == 6:
                color = (238, 130, 238)  # Violet
            elif langton_loop_grid[y, x] == 7:
                color = (0, 255, 255)  # Turquoise

            pygame.draw.rect(screen, color, (x * CELL_SIZE + 1, y * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2))

    # Draw back arrow
    screen.blit(back_arrow, (WIDTH - 60, HEIGHT - 60))

    # Draw start button
    pygame.draw.rect(screen, (0, 0, 0), (700 - 50, 250 - 25, 100, 50), 2)
    font = pygame.font.Font(None, 36)
    text = font.render("Start" if not langton_loop_start else "Stop", True, (0, 0, 0))
    screen.blit(text, (700 - 30, 250 - 10))
    
    # Draw button to save configuration
    pygame.draw.rect(screen, (0, 0, 0), (700 - 50, 350 - 25, 100, 50), 2)
    font = pygame.font.Font(None, 36)
    text = font.render("Loop", True, (0, 0, 0))
    screen.blit(text, (700 - 30, 350 - 10))

    # Draw color selector buttons
    colors = [0, 1, 2, 3, 4, 5, 6, 7]
    for i, color in enumerate(colors):
        pygame.draw.rect(screen, (0, 0, 0), (700 - 80 + i * 20, 300 - 5, 20, 20), 2 if color != selected_color else 4)
        pygame.draw.rect(screen, get_color(color), (700 - 80 + i * 20 + 2, 300 - 5 + 2, 16, 16))
        if color == selected_color:
            pygame.draw.line(screen, (0, 0, 0), (700 - 83 + i * 20 + 4, 300 - 5 + 5), (700 - 80 + i * 20 + 15, 300 - 5 + 15), 2)
            pygame.draw.line(screen, (0, 0, 0), (700 - 83 + i * 20 + 4, 300 - 5 + 15), (700 - 80 + i * 20 + 15, 300 - 5 + 5), 2)



def handle_homescreen_events(event):
    global homescreen, game_of_life, langton_loop, langton_loop_grid
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()
        if WIDTH / 2 - 80 < mouse_pos[0] < WIDTH / 2 + 80 and HEIGHT / 2 - 40 < mouse_pos[1] < HEIGHT / 2 - 10:
            homescreen = False
            game_of_life = True
        elif WIDTH / 2 - 115 < mouse_pos[0] < WIDTH / 2 + 115 and HEIGHT / 2 + 50 < mouse_pos[1] < HEIGHT / 2 + 100:
            homescreen = False
            langton_loop = True

def handle_game_of_life_events(event):
    global game_of_life, start_stop, current_preset_index, mouse_dragging, last_updated_cell, game_of_life_grid, homescreen
    if event.type == pygame.MOUSEBUTTONDOWN:
        if current_preset_index == 1:
            preset_selector = pygame.Rect(700 - 75, 300, 150, 50)
        else:
            preset_selector = pygame.Rect(700 - 50, 300, 100, 50)
        mouse_pos = pygame.mouse.get_pos()
        if 700 - 50 < mouse_pos[0] < 700 + 50 and 250 - 25 < mouse_pos[1] < 250 + 25:
            start_stop = not start_stop
        elif WIDTH - 60 < mouse_pos[0] < WIDTH and HEIGHT - 60 < mouse_pos[1] < HEIGHT:
            game_of_life_grid = np.zeros((GRID_HEIGHT, GRID_WIDTH))
            homescreen = True
            game_of_life = False
            start_stop = False
        elif preset_selector.collidepoint(mouse_pos):
            current_preset_index = (current_preset_index + 1) % len(preset_names)
            preset_name = preset_names[current_preset_index]
            preset_grid = presets[preset_name]
            game_of_life_grid = np.zeros((GRID_HEIGHT, GRID_WIDTH))
            x = (GRID_WIDTH - preset_grid.shape[1]) // 2
            y = (GRID_HEIGHT - preset_grid.shape[0]) // 2
            game_of_life_grid[y:y+preset_grid.shape[0], x:x+preset_grid.shape[1]] = preset_grid

        else:
            x = mouse_pos[0] // CELL_SIZE
            y = mouse_pos[1] // CELL_SIZE
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                game_of_life_grid[y, x] = 1 - game_of_life_grid[y, x]
                mouse_dragging = True
                last_updated_cell = (x, y)

    elif event.type == pygame.MOUSEMOTION:
        if mouse_dragging:
            mouse_pos = pygame.mouse.get_pos()
            x = mouse_pos[0] // CELL_SIZE
            y = mouse_pos[1] // CELL_SIZE
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT and (x, y) != last_updated_cell:
                game_of_life_grid[y, x] = 1 - game_of_life_grid[y, x]
                last_updated_cell = (x, y)

    elif event.type == pygame.MOUSEBUTTONUP:
        mouse_dragging = False
        last_updated_cell = None

def handle_langton_loop_events(event):
    global langton_loop, langton_loop_start, selected_color, mouse_dragging, last_updated_cell, langton_loop_grid, homescreen
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()
        if WIDTH - 60 < mouse_pos[0] < WIDTH and HEIGHT - 60 < mouse_pos[1] < HEIGHT:
            langton_loop_grid = np.full((GRID_HEIGHT, GRID_WIDTH), 0)
            homescreen = True
            langton_loop = False
        elif 700 - 50 < mouse_pos[0] < 700 + 50 and 250 - 25 < mouse_pos[1] < 250 + 25:
            langton_loop_start = not langton_loop_start
        elif 700 - 80 < mouse_pos[0] < 700 + 80 and 300 - 5 < mouse_pos[1] < 300 + 25:  # Check if the click is within the color selector area
            color_index = (mouse_pos[0] - (700 - 80)) // 20  # Calculate the index of the clicked color
            selected_color = colors[color_index]  # Update the selected color
        elif 700 - 50 < mouse_pos[0] < 700 + 50 and 350 - 25 < mouse_pos[1] < 350 + 25:
            langton_loop_grid = np.full((GRID_HEIGHT, GRID_WIDTH), 0)
            langton_loop_grid[13] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            langton_loop_grid[14] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 7, 0, 1, 4, 0, 1, 4, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            langton_loop_grid[15] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 2, 2, 2, 2, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            langton_loop_grid[16] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 7, 2, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            langton_loop_grid[17] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            langton_loop_grid[18] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            langton_loop_grid[19] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 7, 2, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            langton_loop_grid[20] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            langton_loop_grid[21] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 7, 1, 0, 7, 1, 0, 7, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            langton_loop_grid[22] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


        
        if WIDTH - 60 < mouse_pos[0] < WIDTH and HEIGHT - 60 < mouse_pos[1] < HEIGHT:
            langton_loop_grid = np.full((GRID_HEIGHT, GRID_WIDTH), 0)
            homescreen = True
            langton_loop = False
        else:
            x = mouse_pos[0] // CELL_SIZE
            y = mouse_pos[1] // CELL_SIZE
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                langton_loop_grid[y, x] = selected_color  # Use the selected color when drawing on the grid
                mouse_dragging = True
                last_updated_cell = (x, y)

    elif event.type == pygame.MOUSEMOTION:
        if mouse_dragging:
            mouse_pos = pygame.mouse.get_pos()
            x = mouse_pos[0] // CELL_SIZE
            y = mouse_pos[1] // CELL_SIZE
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT and (x, y) != last_updated_cell:
                langton_loop_grid[y, x] = selected_color
                last_updated_cell = (x, y)

    elif event.type == pygame.MOUSEBUTTONUP:
        mouse_dragging = False
        last_updated_cell = None
    
gospersglidergungrid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)
glider_gun_points = [
    (5, 1), (5, 2), (6, 1), (6, 2),
    (5, 11), (6, 11), (7, 11), (4, 12), (8, 12), (3, 13), (9, 13), (3, 14), (9, 14),
    (6, 15), (4, 16), (8, 16), (5, 17), (6, 17), (7, 17), (6, 18),
    (3, 21), (4, 21), (5, 21), (3, 22), (4, 22), (5, 22),
    (2, 23), (6, 23), (1, 25), (2, 25), (6, 25), (7, 25),
    (3, 35), (4, 35), (3, 36), (4, 36)
]

# Fill the grid with the Gosper Glider Gun pattern
for y, x in glider_gun_points:
    gospersglidergungrid[y, x] = 1

presets = {
    "Glider": np.array([
        [1, 0, 1],
        [0, 1, 1],
        [0, 1, 0]
    ]),
    "Spaceship": np.array([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0],
        [0, 0, 1, 1, 1, 1, 0],
        [0, 0, 1, 1, 0, 1, 1],
        [0, 0, 0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0]
    ]),
    "Pulsar": np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0],
 [0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0],
 [0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0],
 [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
 [0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0],
 [0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0],
 [0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
,
    "Gosper's Glider Gun": gospersglidergungrid,
    "Penta-decathlon": np.array([
        [0, 0, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 0, 0],
        [0, 0, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 1, 1, 1, 0, 0]
        ]),
        "None": np.array([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0]
        ])
}
colors = [0, 1, 2, 3, 4, 5, 6, 7]
running = True
mouse_dragging = False
last_updated_cell = None
preset_names = list(presets.keys())

langton_loop = False
current_preset_index = 0
langton_loop_start = False
selected_color = 2

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if homescreen:
            handle_homescreen_events(event)
        elif game_of_life:
            handle_game_of_life_events(event)
        elif langton_loop:
            handle_langton_loop_events(event)

    frames+= 1
    # Draw homescreen or game of life
    if homescreen:
        draw_homescreen()
    elif game_of_life:
        draw_game_of_life()
    elif langton_loop:
        draw_Langton_loop()


    pygame.display.flip()

pygame.quit()