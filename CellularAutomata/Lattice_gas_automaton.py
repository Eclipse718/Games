import numpy as np
import random
import pygame
import sys

class ParticleLattice:
    """Hybrid Particle and Lattice Gas Simulation for 2D fluid dynamics with diagonal movements."""
    # Simulation parameters
    SIZE_X = 128
    SIZE_Y = 128
    DENSITY = 0.4  # Initial probability of particle presence
    SCALE = 7     # Scaling factor for visualization

    # Pygame parameters
    SIZE_PX = SIZE_X * SCALE, SIZE_Y * SCALE
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    def __init__(self):
        self.lattice = np.zeros((self.SIZE_Y, self.SIZE_X), dtype=np.uint8)
        self.screen = pygame.display.set_mode(self.SIZE_PX)
        pygame.display.set_caption("Particle Lattice Gas Simulation")
        self.init_lattice()

    def init_lattice(self):
        """Initializes the lattice with particles randomly placed according to DENSITY."""
        for y in range(self.SIZE_Y):
            for x in range(self.SIZE_X):
                for direction in range(8):  # 8 directions: including diagonals
                    if random.random() < self.DENSITY:
                        self.lattice[y, x] |= 1 << direction

    def run(self):
        """Main loop handling events and updating the simulation."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Get the current mouse position and translate it to lattice coordinates
                        mx, my = pygame.mouse.get_pos()
                        lattice_x = min(max(mx // self.SCALE, 0), self.SIZE_X - 1)
                        lattice_y = min(max(my // self.SCALE, 0), self.SIZE_Y - 1)
                        self.add_dense_region(lattice_x, lattice_y)
                        print(f"Added dense region at {lattice_x}, {lattice_y}")

            self.update()
            self.draw()
            pygame.display.flip()


    def add_dense_region(self, cx, cy):
        """Adds a dense region with all particles moving in all directions at the specified location."""
        size = 10  # Size of the dense region
        for x in range(cx - size // 2, cx + size // 2 + 1):
            for y in range(cy - size // 2, cy + size // 2 + 1):
                # Ensure coordinates wrap around using modulo to prevent index out of range errors
                self.lattice[y % self.SIZE_Y, x % self.SIZE_X] = 0xFF  # All directions set


    def update(self):
        """Updates the lattice state by propagating and handling collisions."""
        new_lattice = np.zeros_like(self.lattice)
        for y in range(self.SIZE_Y):
            for x in range(self.SIZE_X):
                cell = self.lattice[y, x]
                # Handling propagation for all directions
                if cell & 0b00000001:  # Up
                    new_lattice[(y - 1) % self.SIZE_Y, x] |= 0b00000001
                if cell & 0b00000010:  # Right
                    new_lattice[y, (x + 1) % self.SIZE_X] |= 0b00000010
                if cell & 0b00000100:  # Down
                    new_lattice[(y + 1) % self.SIZE_Y, x] |= 0b00000100
                if cell & 0b00001000:  # Left
                    new_lattice[y, (x - 1) % self.SIZE_X] |= 0b00001000
                if cell & 0b00010000:  # Northeast
                    new_lattice[(y - 1) % self.SIZE_Y, (x + 1) % self.SIZE_X] |= 0b00010000
                if cell & 0b00100000:  # Southeast
                    new_lattice[(y + 1) % self.SIZE_Y, (x + 1) % self.SIZE_X] |= 0b00100000
                if cell & 0b01000000:  # Southwest
                    new_lattice[(y + 1) % self.SIZE_Y, (x - 1) % self.SIZE_X] |= 0b01000000
                if cell & 0b10000000:  # Northwest
                    new_lattice[(y - 1) % self.SIZE_Y, (x - 1) % self.SIZE_X] |= 0b10000000

        self.lattice = new_lattice

    def draw(self):
        """Draws the current state of the lattice on the screen."""
        self.screen.fill(self.WHITE)
        for y in range(self.SIZE_Y):
            for x in range(self.SIZE_X):
                color_value = 255 * (1 - bin(self.lattice[y, x]).count('1') / 8.0)
                color = (color_value, color_value, color_value)
                pygame.draw.rect(self.screen, color, (x * self.SCALE, y * self.SCALE, self.SCALE, self.SCALE))

# Initialize the simulation
pygame.init()
simulation = ParticleLattice()
simulation.run()
