import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 640, 480
GRAVITY = 0.2

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

class Player:
    def __init__(self):
        self.x = WIDTH / 4
        self.y = HEIGHT / 2
        self.velocity = 0
        self.alive = True

    def update(self, obstacles):
        if self.alive:
            self.velocity += GRAVITY
            self.y += self.velocity
            if self.y > HEIGHT or self.y < 0:
                self.die()

            for obstacle in obstacles:
                if (obstacle.x <= self.x + 10 <= obstacle.x + 25) or (obstacle.x <= self.x - 10 <= obstacle.x + 25):  
                    if not (obstacle.top_height < self.y < HEIGHT - obstacle.bottom_height):
                        self.die()
                        break
                elif (self.x - 10 <= obstacle.x <= self.x + 10) and (self.y - 10 <= obstacle.top_height or self.y + 10 >= HEIGHT - obstacle.bottom_height):
                    self.die()
                    break

    def draw(self, obstacles):
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), 10)

        for obstacle in obstacles:
            if obstacle.x + 25 > self.x:
                gap_y = (obstacle.top_height + HEIGHT - obstacle.bottom_height) / 2
                color = (0, 255, 0) if obstacle.top_height < self.y < HEIGHT - obstacle.bottom_height else (255, 0, 0)
                pygame.draw.line(screen, color, (self.x, self.y), (obstacle.x + 12.5, gap_y), 2)
                break

    def jump(self):
        if self.alive:
            self.velocity = -5

    def die(self):
        print(f"Player at x: {self.x}, y: {self.y} died")
        self.alive = False

class Obstacle:
    def __init__(self):
        self.x = WIDTH
        self.top_height = random.randint(100, 250)
        self.bottom_height = HEIGHT - self.top_height - random.randint(100, 250)
        self.velocity = -2

    def update(self):
        self.x += self.velocity

    def draw(self):
        pygame.draw.rect(screen, (0, 0, 0), (self.x, 0, 25, self.top_height))
        pygame.draw.rect(screen, (0, 0, 0), (self.x, HEIGHT - self.bottom_height, 25, self.bottom_height))

def main():
    player = Player()
    obstacles = [Obstacle()]
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()

        screen.fill((255, 255, 255))
        for obstacle in obstacles:
            obstacle.update()
            obstacle.draw()
            if obstacle.x + 25 < 0:  
                obstacles.remove(obstacle)

        if not obstacles or obstacles[-1].x < WIDTH - random.randint(250, 400):
            obstacles.append(Obstacle())

        player.update(obstacles)
        if player.alive:
            player.draw(obstacles)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()