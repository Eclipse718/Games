import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH = 800
HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 128, 0)
RED = (255, 0, 0)
PURPLE = (128, 0, 128)  # Purple color for special bricks
GOLD = (218,165,32)  # Gold color for special bricks


# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the player
player = pygame.Rect(WIDTH / 2, HEIGHT - 100, 100, 12)
player_speed = 15

# Set up the bricks
brick_width = 50
brick_height = 20
brick_rows = 4
brick_cols = WIDTH // brick_width

class Brick:
    def __init__(self, x, y, width, height, color, special=False, gold=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.special = special
        self.gold = gold

# Function to create bricks, including special bricks
def create_bricks():
    bricks = []
    colors = [YELLOW, GREEN, ORANGE, RED]
    for i in range(brick_rows):
        color_index = i % len(colors)
        for j in range(brick_cols):
            if random.randint(0, 10) == 0:  # 10% chance of a gold brick
                bricks.append(Brick(j * brick_width, i * brick_height, brick_width, brick_height, GOLD, False, True))
                pygame.draw.rect(screen, BLACK, (j * brick_width, i * brick_height, brick_width, brick_height), 1)  # Add black outline
            else:
                bricks.append(Brick(j * brick_width, i * brick_height, brick_width, brick_height, colors[color_index], False, False))
            color_index = (color_index + 1) % len(colors)
    
    # Randomly select and replace two bricks with special bricks
    for _ in range(2):
        index = random.randint(0, len(bricks) - 1)
        brick = bricks[index]
        bricks[index] = Brick(brick.rect.x, brick.rect.y, brick_width, brick_height, PURPLE, True, False)
    return bricks

bricks = create_bricks()

# Set up the balls
balls = [pygame.Rect(WIDTH / 2, HEIGHT / 3, brick_height / 2 * 1.5, brick_height / 2 * 1.5)]
ball_speeds = [(random.uniform(-4, 4), random.uniform(5, 6))]  # Initial speed of the ball

# Set up the lives
lives = 5
lives_balls = [pygame.Rect(WIDTH - 25 - i * 50, HEIGHT - 25, brick_height / 2 * 1.5, brick_height / 2 * 1.5) for i in range(lives)]

# Set up the score
score = 0

# Clock for controlling frame rate and calculating delta time
clock = pygame.time.Clock()

# Main game loop
running = True
while running:
    dt = clock.tick(60)  # Delta time in milliseconds
    player_movement = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player.x -= player_speed
        player_movement = -player_speed
    if keys[pygame.K_d]:
        player.x += player_speed
        player_movement = player_speed

    if player.left < 0:
        player.left = 0
    elif player.right > WIDTH:
        player.right = WIDTH
    
    # Ball movement and collisions
    for i, ball in enumerate(list(balls)):  # Use list() to create a copy since we might modify balls during iteration
        ball_speed = ball_speeds[i]
        ball.x += ball_speed[0]
        ball.y += ball_speed[1]

        # Ball collision with walls
        if ball.left <= 0 or ball.right >= WIDTH:
            ball_speeds[i] = (-ball_speed[0], ball_speed[1])
        if ball.top <= 0:
            ball_speeds[i] = (ball_speed[0], -ball_speed[1])
        # Ball collision with player
        if ball.colliderect(player):
            ball_speeds[i] = (ball_speed[0] + player_movement * 0.1, -ball_speed[1])  # Adjust direction based on player movement
        # Ball collision with bricks
        for brick in list(bricks):  # Use list() to create a copy since we might modify bricks during iteration
            if ball.colliderect(brick.rect):
                score += 1000 if brick.gold else 100  # Increase score
                ball_speeds[i] = (ball_speed[0], -ball_speed[1])  # Bounce the ball
                if brick.special:  # Check if the brick is special
                    new_ball = pygame.Rect(ball.x, ball.y, ball.width, ball.height)  # Create a new ball
                    balls.append(new_ball)
                    ball_speeds.append((random.uniform(-4, 4), random.uniform(-5, 6)))  # Add initial speed for the new ball
                bricks.remove(brick)  # Remove the brick
                break  # Exit the loop to avoid errors due to modifying the list
        # Ball falls out of the screena
        if ball.bottom >= HEIGHT:
            if len(balls) > 1:
                balls.remove(ball)
                ball_speeds.pop(i)
            else:
                lives -= 1  # Lose a life if there's only one ball
                ball.center = (WIDTH / 2, HEIGHT / 3)  # Reset ball position
                ball_speeds[i] = (random.uniform(-4, 4), random.uniform(5, 6)) # Reset ball speed
                if lives <= 0:
                    running = False  # Game over if no lives left

    # Drawing the game
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, player)  # Draw player
    for brick in bricks:  # Draw bricks
        if brick.gold:
            pygame.draw.rect(screen, GOLD, brick.rect)
            pygame.draw.rect(screen, BLACK, brick.rect, 1)  # Add a black outline
        else:
            pygame.draw.rect(screen, brick.color, brick.rect)
    for ball in balls:  # Draw balls
        pygame.draw.ellipse(screen, WHITE, ball)
    for i in range(lives):  # Draw lives
        pygame.draw.ellipse(screen, WHITE, lives_balls[i])
    score_text = pygame.font.Font(None, 36).render(str(score), True, WHITE)  # Display score
    screen.blit(score_text, (10, 568))
    pygame.display.flip()  # Update the display

pygame.quit()