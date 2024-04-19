import pygame
import sys
import random
import os
import neat


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
        self.passed_obstacles = []
        self.color = (0, 0, 0)  # Default color is black 

    def update(self):
        if self.alive:
            self.velocity += GRAVITY
            self.y += self.velocity


    def draw(self, obstacles):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 10)

        for obstacle in obstacles:
            if obstacle.x + 25 > self.x:
                gap_y = (obstacle.top_height + HEIGHT - obstacle.bottom_height) / 2
                color = (0, 255, 0) if obstacle.top_height < self.y < HEIGHT - obstacle.bottom_height else (255, 0, 0)
                pygame.draw.line(screen, color, (self.x, self.y), (obstacle.x + 12.5, gap_y), 2)
                break

    def jump(self):
        if self.alive:
            self.velocity = -5


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

def main(genomes, config):
    nets = []
    ge = []
    players = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        players.append(Player())
        g.fitness = 0
        ge.append(g)

    obstacles = [Obstacle()]
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((255, 255, 255))
        for obstacle in obstacles:
            obstacle.update()
            obstacle.draw()
            if obstacle.x + 25 < 0:  
                obstacles.remove(obstacle)

        if not obstacles or obstacles[-1].x < WIDTH - random.randint(250, 400):
            obstacles.append(Obstacle())

        for x, player in enumerate(players):
            player.update()
            
            if player.y > HEIGHT or player.y < 0:
                ge[x].fitness -= 1
                players.pop(x)
                nets.pop(x)
                ge.pop(x)
            else:
                for obstacle in obstacles:
                    if (obstacle.x <= player.x + 10 <= obstacle.x + 25) or (obstacle.x <= player.x - 10 <= obstacle.x + 25):  
                        if not (obstacle.top_height < player.y < HEIGHT - obstacle.bottom_height):
                            ge[x].fitness -= 1
                            players.pop(x)
                            nets.pop(x)
                            ge.pop(x)
                            break
                    elif (player.x - 10 <= obstacle.x <= player.x + 10) and (player.y - 10 <= obstacle.top_height or player.y + 10 >= HEIGHT - obstacle.bottom_height):
                        ge[x].fitness -= 1
                        players.pop(x)
                        nets.pop(x)
                        ge.pop(x)
                        break
                    elif player.x > obstacle.x + 25 and obstacle not in player.passed_obstacles:
                        ge[x].fitness += 5
                        player.passed_obstacles.append(obstacle)

                if player in players:
                    player.draw(obstacles)
                    ge[x].fitness += 0.1

                    next_obstacle = None
                    for obstacle in obstacles:
                        if obstacle not in player.passed_obstacles:
                            next_obstacle = obstacle
                            break

                    if next_obstacle is not None:
                        output = nets[x].activate((player.y, next_obstacle.top_height, next_obstacle.bottom_height))
                    else:
                        output = nets[x].activate((player.y, 0, 0))  # Default values if there are no more obstacles
                    if output[0] > 0.5:
                        player.jump()
                        player.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            # Check if all players are dead
        if len(players) == 0:
            break

        pygame.display.flip()
        clock.tick(60)

def run(config_path):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Create a population from the configuration.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))

    # Add a statistics reporter to gather and report statistics of the evolution.
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run for up to 50 generations.
    winner = p.run(main, 50)
    
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "NEATConfig.txt")
    run(config_path)
    main()
