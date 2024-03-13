import pygame
import random

# Initialize Pygame
pygame.init()

# Setup display
display_size = 600
win = pygame.display.set_mode((display_size, display_size))

# Colors
FOREST_GREEN = (34, 139, 34)
BLACK = (0, 0, 0)

# Grid
grid = [[" " for _ in range(3)] for _ in range(3)]

def draw_grid():
    win.fill(FOREST_GREEN)
    for i in range(1, 3):
        pygame.draw.line(win, BLACK, (i * 200, 0), (i * 200, display_size), 5)
        pygame.draw.line(win, BLACK, (0, i * 200), (display_size, i * 200), 5)
    
    for row in range(3):
        for col in range(3):
            center = (col * 200 + 100, row * 200 + 100)
            if grid[row][col] == "X":
                pygame.draw.line(win, BLACK, (center[0] - 50, center[1] - 50), (center[0] + 50, center[1] + 50), 10)
                pygame.draw.line(win, BLACK, (center[0] + 50, center[1] - 50), (center[0] - 50, center[1] + 50), 10)
            elif grid[row][col] == "O":
                pygame.draw.circle(win, BLACK, center, 75, 10)

def check_for_win_or_tie():
    lines = [
        [grid[row][col] for col in range(3)] for row in range(3)
    ] + [
        [grid[col][row] for col in range(3)] for row in range(3)
    ] + [
        [grid[i][i] for i in range(3)],
        [grid[i][2-i] for i in range(3)]
    ]

    for line in lines:
        if line[0] == line[1] == line[2] and line[0] != " ":
            return line[0]
    if all(grid[row][col] != " " for row in range(3) for col in range(3)):
        return "Tie"
    return None

def find_best_move():
    # Winning Moves
    for move in get_available_moves():
        if check_move_outcome(move, "O") == "O":
            return move
    
    # Blocking Player's Winning Moves
    for move in get_available_moves():
        if check_move_outcome(move, "X") == "X":
            return move
    
    # Taking the Middle Slot
    if grid[1][1] == " ":
        return (1, 1)
    
    # Random Move
    return random.choice(get_available_moves()) if get_available_moves() else None

def get_available_moves():
    return [(row, col) for row in range(3) for col in range(3) if grid[row][col] == " "]

def check_move_outcome(move, player):
    row, col = move
    grid[row][col] = player
    outcome = None
    if check_for_win_or_tie() == player:
        outcome = player
    grid[row][col] = " "  # Reset move
    return outcome

# Game loop
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            row, col = y // 200, x // 200
            if grid[row][col] == " ":
                grid[row][col] = "X"
                result = check_for_win_or_tie()
                if result:
                    print(f"{result} wins!" if result != "Tie" else "It's a tie!")
                    run = False
                else:
                    cpu_move = find_best_move()
                    if cpu_move:
                        grid[cpu_move[0]][cpu_move[1]] = "O"
                        if check_for_win_or_tie():
                            print("O wins!")
                            run = False

    draw_grid()
    pygame.display.update()

pygame.quit()
