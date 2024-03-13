import random

def print_board(board):
    for row in board:
        print(" ".join(row))

def check_win(board, player):
    # Check rows, columns, and diagonals for a win
    for row in board:
        if row.count(player) == 3:
            return True
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True
    if all(board[i][i] == player for i in range(3)):
        return True
    if all(board[i][2-i] == player for i in range(3)):
        return True
    return False

def check_draw(board):
    return all(board[row][col] != ' ' for row in range(3) for col in range(3))

def find_winning_move(board, player):
    # Check if the player can win on the next move and return the move if possible
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = player
                if check_win(board, player):
                    board[i][j] = ' '  # Reset to original state after checking
                    return (i, j)
                board[i][j] = ' '  # Reset to original state after checking
    return None

def take_center_if_available(board):
    if board[1][1] == ' ':
        return (1, 1)
    return None

def tic_tac_toe():
    placeholder_board = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]
    board = [[' ' for _ in range(3)] for _ in range(3)]
    while True:
        print_board(placeholder_board)
        # Check for win or draw before player's move
        if check_win(board, 'X'):
            print("You won!")
            break
        elif check_win(board, 'O'):
            print("You lost!")
            break
        elif check_draw(board):
            print("It's a draw!")
            break
        
        user_move = input("Enter a number from 1 to 9 to place an X: ")
        if user_move.isdigit() and 1 <= int(user_move) <= 9:
            row, col = (int(user_move) - 1) // 3, (int(user_move) - 1) % 3
            if board[row][col] == ' ':
                board[row][col], placeholder_board[row][col] = 'X', 'X'
            else:
                print("Invalid move! This spot is already taken.")
                continue
        else:
            print("Invalid input!")
            continue

        # AI's strategy
        win_move = find_winning_move(board, 'O')
        block_move = find_winning_move(board, 'X')
        center_move = take_center_if_available(board)

        if win_move:
            board[win_move[0]][win_move[1]], placeholder_board[win_move[0]][win_move[1]] = 'O', 'O'
        elif block_move:
            board[block_move[0]][block_move[1]], placeholder_board[block_move[0]][block_move[1]] = 'O', 'O'
        elif center_move:
            board[center_move[0]][center_move[1]], placeholder_board[center_move[0]][center_move[1]] = 'O', 'O'
        else:
            # Place randomly in available spaces
            while True:
                random_move = random.randint(0, 8)
                row, col = random_move // 3, random_move % 3
                if board[row][col] == ' ':
                    board[row][col], placeholder_board[row][col] = 'O', 'O'
                    break
        
        print_board(placeholder_board)  # Only print the placeholder board

tic_tac_toe()
