import sys
import random
import pygame
import pymunk
import pymunk.pygame_util
from pygame.locals import *

pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
space = pymunk.Space()
space.gravity = (0, 980)  # Apply a downward gravity
draw_options = pymunk.pygame_util.DrawOptions(screen)
BACKGROUND_COLOR = (0, 20, 40)
FPS = 60
score = 0
font = pygame.font.Font(None, 36)

Red = (255, 0, 0)  # Red
Green = (0, 255, 0)  # Green
Gold = (255, 215, 0)  # Gold, using a common RGB representation
colors = [Red, Green, Gold, Green, Red]
rows = 9  # Total number of rows
matrix_width = 21  # Total width of the pattern in 'pegs'
peg_spacing = WIDTH / matrix_width  # Space between pegs
peg_radius = peg_spacing / 4  # Radius of pegs
vertical_spacing = HEIGHT / (2 * rows)  # Vertical spacing to fit pattern on screen

def place_pegs():
    # Calculate the horizontal offset to center the pegs
    horizontal_offset = -140
    # Calculate the vertical offset to center the pegs
    vertical_offset = (HEIGHT - (rows * vertical_spacing * 1.5)) / 4
    for row in range(rows):
        ones_count = 1 + row * 2  # Calculate the number of '1's (pegs) in the current row
        start_pos = (matrix_width - ones_count) // 2  # Starting position for '1's
        end_pos = start_pos + ones_count
        for col in range(start_pos, end_pos, 2):
            peg_x = col * peg_spacing * 1.5 + horizontal_offset
            peg_y = row * vertical_spacing * 1.5 + vertical_offset + HEIGHT / 8  # Adjust to center vertically
            peg_body = pymunk.Body(body_type=pymunk.Body.STATIC)
            peg_body.position = peg_x, peg_y
            peg_shape = pymunk.Circle(peg_body, peg_radius)
            peg_shape.color = pygame.Color("grey")
            space.add(peg_body, peg_shape)

def draw_lines(screen, width, height):
    pygame.draw.line(screen, (0, 0, 0), (0, 0), (0, height), 5)
    pygame.draw.line(screen, (0, 0, 0), (width, 0), (width, height), 5)

def draw_rectangles(screen, colors, width, height):
    rect_width = width / len(colors)
    for i, color in enumerate(colors):
        surface = pygame.Surface((rect_width, 20))
        surface.fill(color)
        surface.set_alpha(128)
        screen.blit(surface, (i * rect_width, height - 20))

place_pegs()
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN and event.key == K_SPACE:
            ball_body = pymunk.Body(1, 100, body_type=pymunk.Body.DYNAMIC)
            ball_body.position = random.randint(WIDTH / 5 * 2, WIDTH / 5 * 3), 50
            ball_shape = pymunk.Circle(ball_body, peg_radius*2)
            ball_shape.elasticity = 0.5
            ball_shape.color = pygame.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            space.add(ball_body, ball_shape) 

    screen.fill(BACKGROUND_COLOR)
    draw_rectangles(screen, colors, WIDTH, HEIGHT)
    draw_lines(screen, WIDTH, HEIGHT)
    space.step(1/FPS)
    space.debug_draw(draw_options)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))
    pygame.display.flip()
    clock.tick(FPS)
    for shape in space.shapes:
        if shape.body.position.y > HEIGHT and shape.body.body_type == pymunk.Body.DYNAMIC:
            if shape.body.position.x < WIDTH / 6 or shape.body.position.x > 5 * WIDTH / 6:
                score -= 10  # Penalty for falling through the red rectangles or off screen
            elif 2*WIDTH / 5 <= shape.body.position.x < 3* WIDTH / 5:
                if shape.body.position.y > HEIGHT / 2:
                    score += 100  # Bonus for falling in the gold zone
            else:
                score += 10  # Bonus for falling in the green zone
            space.remove(shape.body, shape)

pygame.quit()
sys.exit()