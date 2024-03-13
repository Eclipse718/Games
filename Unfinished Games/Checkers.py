import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 640, 640
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREY = (128, 128, 128)

def get_opponent(color):
    """Return the opponent's color."""
    return 'yellow' if color == 'red' else 'red'

def is_valid_move(source, dest):
    """Check if a move from source to destination is valid."""
    row_src, col_src = source
    row_dest, col_dest = dest
    piece_color = board[row_src][col_src]

    # Simple move
    if abs(row_dest - row_src) == 1 and abs(col_dest - col_src) == 1 and board[row_dest][col_dest] == 'empty':
        return True
    
    # Jump move
    if abs(row_dest - row_src) == 2 and abs(col_dest - col_src) == 2:
        mid_row, mid_col = (row_src + row_dest) // 2, (col_src + col_dest) // 2
        if board[mid_row][mid_col] != 'empty' and board[row_dest][col_dest] == 'empty':
            return True

    return False

def highlight_moves(source):
    """Highlight valid moves for the selected piece."""
    row, col = source
    piece_color = board[row][col]
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] # All directions for potential jumps

    for dir in directions:
        # Highlight simple moves
        next_row, next_col = row + dir[0], col + dir[1]
        if 0 <= next_row < 8 and 0 <= next_col < 8 and board[next_row][next_col] == 'empty':
            pygame.draw.circle(screen, GREY, (next_col * 80 + 40, next_row * 80 + 40), 15)

        # Highlight jumps
        jump_row, jump_col = row + 2*dir[0], col + 2*dir[1]
        if 0 <= jump_row < 8 and 0 <= jump_col < 8 and is_valid_move(source, (jump_row, jump_col)):
            pygame.draw.circle(screen, GREY, (jump_col * 80 + 40, jump_row * 80 + 40), 15)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Create a 2D list to represent the board
board = [['empty' for _ in range(8)] for _ in range(8)]

# Fill in the board with alternating black and white squares and add checkers pieces
for i in range(8):
    for j in range((i % 2), 8, 2):
        if i < 3:
            board[i][j] = 'yellow'
        elif i > 4:
            board[i][j] = 'red'

# Variables to store the source of the move
source = None  # Initially, no piece is selected

# Main game loop
running = True
# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            col = mouse_x // 80
            row = mouse_y // 80

            # Select piece or attempt move
            if source is not None and board[row][col] == 'empty' and is_valid_move(source, (row, col)):
                # Execute move
                if board[source[0]][source[1]] == 'red':
                    if board[(row + source[0]) // 2][(col + source[1]) // 2] == 'yellow':
                        board[(row + source[0]) // 2][(col + source[1]) // 2] = 'empty'
                elif board[source[0]][source[1]] == 'yellow':
                    if board[(row + source[0]) // 2][(col + source[1]) // 2] == 'red':
                        board[(row + source[0]) // 2][(col + source[1]) // 2] = 'empty'
                board[row][col] = board[source[0]][source[1]]
                board[source[0]][source[1]] = 'empty'
                source = None
            elif board[row][col] in ['red', 'yellow']:
                source = (row, col)
            else:
                source = None

    # Redraw board and pieces
    screen.fill(BLACK)
    for i in range(8):
        for j in range(8):
            square_color = WHITE if (i + j) % 2 == 0 else BLACK
            pygame.draw.rect(screen, square_color, (j * 80, i * 80, 80, 80))
            if board[i][j] in ['red', 'yellow']:
                piece_color = RED if board[i][j] == 'red' else YELLOW
                pygame.draw.circle(screen, piece_color, (j * 80 + 40, i * 80 + 40), 25)

    # Highlight moves for selected piece
    if source:
        highlight_moves(source)

    pygame.display.flip()

pygame.quit()
sys.exit()