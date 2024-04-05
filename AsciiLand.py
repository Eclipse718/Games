import pygame
import sys
import random
import heapq
import math

pygame.init()

width = 800
height = 630

light_green = (153, 255, 153)  # A lighter shade of green


global frames
frames = 0

screen = pygame.display.set_mode((width, height))

pygame.display.set_caption("Ascii Land")

bg_color = (0, 0, 0)

grid_color = (100, 100, 100)

RED = (255, 14, 30)

grid_width = 40
grid_height = 30
grid = [[' ' for _ in range(grid_width)] for _ in range(grid_height)]

picked_up_object = None
picked_up_animal = None

def draw_grid():
    for i in range(grid_height):
        for j in range(grid_width):
            pygame.draw.rect(screen, grid_color, pygame.Rect(j*20, i*20, 20, 20), 1)

class Terrain:
    def __init__(self, x, y, character, color, impassable=False):
        self.x = x
        self.y = y
        self.character = character
        self.color = color
        self.impassable = impassable

    def draw(self):
        text = font.render(self.character, True, self.color)
        screen.blit(text, (self.x*20 + 5, self.y*20 + 5))
    
    def look(self, radius):
        entities_in_range = []
        for entity in object_list + animal_list + [item for sublist in terrain_list for item in sublist]:
            if entity == self:
                continue
            dx = abs(self.x - entity.x)
            dy = abs(self.y - entity.y)
            dist = max(min(dx, grid_width - dx), min(dy, grid_height - dy))
            if dist <= radius:
                entities_in_range.append(entity)
        entities_in_range.sort(key=lambda x: max(min(abs(self.x - x.x), grid_width - abs(self.x - x.x)), min(abs(self.y - x.y), grid_height - abs(self.y - x.y))))
        return entities_in_range


class Water(Terrain):
    character = 'W'
    color = (0, 0, 255)

    def __init__(self, x, y):
        super().__init__(x, y, Water.character, Water.color, True)
        self.text = font.render(self.character, True, self.color)
        
class Fire(Terrain):
    character = 'F'
    color = (255, 165, 0)  # Fiery orange color

    def __init__(self, x, y):
        super().__init__(x, y, Fire.character, Fire.color, False)
        self.text = font.render(self.character, True, self.color)

    def terrain_effect(self):
        if frames % 70 == 0:
            for obj in object_list[:]:
                if obj.x == self.x and obj.y == self.y:
                    self.burn(obj)
                    break
            for animal in animal_list[:]:
                if animal.x == self.x and animal.y == self.y:
                    self.burn(animal)
                    break
        self.spread(terrain)
                
    
    def burn(self, target):
        if isinstance(target, Animal):
            if hasattr(target, 'weaknesses'):  
                if 'Fire' in target.weaknesses:
                    target.health -= 20
                    target.on_fire = 5  
                else:
                    target.health -= 10
                    target.on_fire = 5 
            else:
                target.health -= 10 
                target.on_fire = 5 

            if hasattr(target, 'jiggle_times'):  
                target.jiggle_times += 1
        elif isinstance(target, Meat):
            target.cookedness += 1
            if target.cookedness == 2:
                object_list.remove(target)
                object_list.append(CookedMeat(target.x, target.y))
        elif isinstance(target, Object) and not isinstance(target, CookedMeat):
            object_list.remove(target)
        if isinstance(target, (Wood, Tree)):
            self.spread_to_surrounding()

    def spread(self, terrain):
        if frames % 60 == 0:
            surrounding_terrain = [entity for entity in self.look(1) if isinstance(entity, Terrain) and (entity.x == self.x or entity.y == self.y)]
            surrounding_fire = [entity for entity in surrounding_terrain if isinstance(entity, Fire)]
            surrounding_objects = [entity for entity in self.look(1) if isinstance(entity, (Object, Animal))]

            # Check if all surrounding tiles are fire
            if len(surrounding_fire) == len(surrounding_terrain):
                if random.random() < 0.8:
                    terrain_list[self.y][self.x] = Terrain(self.x, self.y, ' ', (255, 255, 255))
                    return

            for terrain in surrounding_terrain:
                # Check if the tile is not a Water tile
                if not isinstance(terrain, Water):
                    # Check if there's a wood object or a tree animal on the tile
                    for obj in surrounding_objects:
                        if (isinstance(obj, Wood) or isinstance(obj, Tree)) and obj.x == terrain.x and obj.y == terrain.y:
                            # Spread at 80% chance
                            if random.random() < 0.82:
                                terrain_list[terrain.y][terrain.x] = Fire(terrain.x, terrain.y)
                            break
                    else:
                        # Spread at 5% chance
                        if random.random() < 0.05:
                            terrain_list[terrain.y][terrain.x] = Fire(terrain.x, terrain.y)
            # Extinguish itself
            if random.random() < 0.17:
                terrain_list[self.y][self.x] = Terrain(self.x, self.y, ' ', (255, 255, 255))

    def spread_to_surrounding(self):
        surrounding_terrain = [entity for entity in self.look(1) if isinstance(entity, Terrain) and (entity.x == self.x or entity.y == self.y)]
        for terrain in surrounding_terrain:
            if random.random() < 0.2 and not isinstance(terrain, Water):
                terrain_list[terrain.y][terrain.x] = Fire(terrain.x, terrain.y)

class IcePlain(Terrain):
    character = 'I'
    color = (100, 180, 255)
    
    def __init__(self, x, y, melt=150):
        super().__init__(x, y, 'I', (100, 180, 255), impassable=True)
        self.melt = melt
        self.text = font.render(self.character, True, self.color) 

    def terrain_effect(self):
        self.melt -= 1
        if self.melt <= 0:
            terrain_list[self.y][self.x] = Terrain(self.x, self.y, ' ', (255, 255, 255))
        if frames % 50 == 0:
            for animal in animal_list[:]:
                if animal.x == self.x and animal.y == self.y:
                    self.freeze(animal)
                    break

    def freeze(self, target):
        if isinstance(target, Animal):
            if hasattr(target, 'weaknesses'):  
                if 'Ice' in target.weaknesses:
                    target.health -= 10
                    target.frozen = 2  
                else:
                    target.health -= 5
                    target.frozen = 2 
            else:
                target.health -= 5
                target.frozen = 2 

            if hasattr(target, 'jiggle_times'):  
                target.jiggle_times += 1



class Object:
    def __init__(self, x, y, character, color):
        self.x = x
        self.y = y
        self.character = character
        self.color = color
        self.text = font.render(self.character, True, self.color)

    def draw(self):
        screen.blit(self.text, (self.x*20 + 5, self.y*20 + 5))

class Sword(Object):
    character = 'S'
    color = (100, 100, 100)
    def __init__(self, x, y):
        super().__init__(x, y, 'S', (100, 100, 100))
        self.equipment = True
        self.one_handed = True
        self.weapon = True
        self.damage_modifier = 5

class FireScepter(Object):
    character = 'f'
    color = (138, 10, 10)  # desaturated dark red

    def __init__(self, x, y):
        super().__init__(x, y, 'f', (100, 0, 0))
        self.equipment = True
        self.two_handed = True
        self.weapon = True
        self.damage_modifier = 0

class IceScepter(Object):
    character = 'i'
    color = (20, 50, 130)  # Desaturated dark blue

    def __init__(self, x, y):
        super().__init__(x, y, 'i', (20, 50, 130))
        self.equipment = True
        self.two_handed = True
        self.weapon = True
        self.damage_modifier = 0

class Axe(Object):
    character = 'a'
    color = (200, 200, 200)
    def __init__(self, x, y):
        super().__init__(x, y, 'a', (200, 200, 200))
        self.equipment = True
        self.weapon = True
        self.one_handed = True
        self.damage_modifier = 3

class Meat(Object):
    character = 'm'
    color = (235, 172, 183)  # Pinkish meat color
    def __init__(self, x, y, sustenance=10):
        super().__init__(x, y, 'm', (255, 182, 193))  # Pinkish meat color
        self.sustenance = sustenance
        self.cookedness = 0

class CookedMeat(Object):
    character = 'm'
    color = (139, 69, 19)  # Rusty brown color
    def __init__(self, x, y, sustenance=20):
        super().__init__(x, y, 'm', (139, 69, 19))  # Rusty brown color
        self.sustenance = sustenance

class Pelt(Object):
    character = 'p'
    color = (255, 165, 0)
    def __init__(self, x, y):
        super().__init__(x, y, 'p', (255, 165, 0))  # Orange color
        
class Wood(Object):
    character = 'w'
    color = (139, 69, 19)
    def __init__(self, x, y):
        super().__init__(x, y, 'w', (139, 69, 19))  # (139, 69, 19) is a woody birch color

class Animal:
    def __init__(self, x, y, character, color, move_function, aggression=0, max_health = 10, health = 10, damage = 1):
        self.x = x
        self.y = y
        self.character = character
        self.color = color
        self.move = move_function
        self.health = health
        self.max_health = max_health
        self.damage = damage
        self.is_fighting = False
        self.jiggle_times = 0
        self.text = font.render(self.character, True, self.color)
        self.aggression = aggression
        self.target = None
        self.on_fire = 0  
        self.frozen = 0  
    
    def move(self):
        self.move_function(self)

    def rest(self):
        if self.health < self.max_health:
            self.health += 5

    def draw(self):
        if not self.jiggle_times > 0:
            screen.blit(self.text, (self.x*20 + 5, self.y*20 + 5))

    def jiggle(self):
        if self.jiggle_times > 0:
            if self.jiggle_frame < 60:
                offset_x = -2
            elif self.jiggle_frame >= 60 and self.jiggle_frame < 120:
                offset_x = 2
            else:
                offset_x = -2
                self.jiggle_times -= 1
            self.jiggle_frame += 1

            # Draw the red outline
            pygame.draw.rect(screen, (128, 0, 0), pygame.Rect(self.x*20 + 1, self.y*20 + 1, 18, 18))

            # Draw the character
            screen.blit(self.text, (self.x*20 + 5 + offset_x, self.y*20 + 5))
        else:
            self.jiggle_frame = 0

    def can_move_to(self, x, y):
        if terrain_list[y][x].impassable:
            return False
        for animal in animal_list:
            if animal.x == x and animal.y == y:
                return False
        for obj in object_list:
            if obj.x == x and obj.y == y:
                return False
        return True

    def on_fire_effect(self):
        global frames
        if self.on_fire > 0:
            if frames % 120 == 0: 
                self.health -= 5
                self.jiggle_times += 1
                self.on_fire -= 1

    def move_random(self):
        directions = ['north', 'south', 'east', 'west']
        weights = [1, 1, 1, 1]
        
        if not self.can_move_to(self.x, (self.y - 1) % grid_height):  # North
            weights[0] = 0
        if not self.can_move_to(self.x, (self.y + 1) % grid_height):  # South
            weights[1] = 0
        if not self.can_move_to((self.x - 1) % grid_width, self.y):  # West
            weights[3] = 0  # Assuming west is the last direction in your array
        if not self.can_move_to((self.x + 1) % grid_width, self.y):  # East
            weights[2] = 0

        
        # Check if all directions are impassable
        if sum(weights) == 0:
            return
        
        # Normalize the weights
        total_weight = sum(weights)
        weights = [weight / total_weight for weight in weights]
        
        # Choose a direction based on the weights
        self.direction = random.choices(directions, weights=weights)[0]
        
        # Move in the chosen direction
        if self.direction == 'north':
            self.y = (self.y - 1) % grid_height
        elif self.direction == 'south':
            self.y = (self.y + 1) % grid_height
        elif self.direction == 'east':
            self.x = (self.x + 1) % grid_width
        elif self.direction == 'west':
            self.x = (self.x - 1) % grid_width

    def attack(self, target):
        if hasattr(target, 'weaknesses') and self.inventory and 'axe' in self.inventory:
            additional_damage = min(2, self.inventory.count('axe')) * 10
            target.health -= self.damage + additional_damage
        else:
            target.health -= self.damage
        target.jiggle_times += 1
        target.is_fighting = True
        target.target = self

    def move_towards_target(self, target, weights):
        directions = ['north', 'south', 'east', 'west']
        
        dx = min(abs(self.x - target.x), grid_width - abs(self.x - target.x))
        dy = min(abs(self.y - target.y), grid_height - abs(self.y - target.y))

        # Check if all directions are impassable
        if not self.can_move_to(self.x, (self.y - 1) % grid_height) and \
        not self.can_move_to(self.x, (self.y + 1) % grid_height) and \
        not self.can_move_to((self.x - 1) % grid_width, self.y) and \
        not self.can_move_to((self.x + 1) % grid_width, self.y):
            return

        # Use A* search to find the optimal path
        path = a_star_search(self, target, terrain_list, animal_list)

        # If there is no optimal path, move in a random direction
        if not path:
            self.move_random()
            return

        # Update the weights based on the optimal path
        for i, direction in enumerate(directions):
            x = self.x
            y = self.y
            if direction == 'north':
                y -= 1
            elif direction == 'south':
                y += 1
            elif direction == 'east':
                x += 1
            elif direction == 'west':
                x -= 1
            if (x, y) in path:
                weights[i] += 30  # Prefer the optimal path

        # Check if the preferred direction is impassable
        if not self.can_move_to(self.x, (self.y - 1) % grid_height):
            weights[0] = 0
        if not self.can_move_to(self.x, (self.y + 1) % grid_height):
            weights[1] = 0
        if not self.can_move_to((self.x + 1) % grid_width, self.y):
            weights[2] = 0
        if not self.can_move_to((self.x - 1) % grid_width, self.y):
            weights[3] = 0

        # Normalize the weights
        total_weight = sum(weights)
        weights = [weight / total_weight for weight in weights]

        # Choose a direction based on the weights
        self.direction = random.choices(directions, weights=weights)[0]

        # Move in the chosen direction
        if self.direction == 'north':
            self.y = (self.y - 1) % grid_height
        elif self.direction == 'south':
            self.y = (self.y + 1) % grid_height
        elif self.direction == 'east':
            self.x = (self.x + 1) % grid_width
        elif self.direction == 'west':
            self.x = (self.x - 1) % grid_width


    def hunt(self):
        directions = ['north', 'south', 'east', 'west']
        weights = [1, 1, 1, 1]

        dx = min(abs(self.x - self.target.x), grid_width - abs(self.x - self.target.x))
        dy = min(abs(self.y - self.target.y), grid_height - abs(self.y - self.target.y))

        # Check if the target is adjacent (horizontally or vertically) including wrap-around
        if (dx == 1 and dy == 0) or (dx == 0 and dy == 1):
            self.attack(self.target)
            return

        self.move_towards_target(self.target, weights)
    

    def flee(self):
        directions = ['north', 'south', 'east', 'west']
        weights = [1, 1, 1, 1]

        # Check if all directions are impassable
        if not self.can_move_to(self.x, (self.y - 1) % grid_height) and \
        not self.can_move_to(self.x, (self.y + 1) % grid_height) and \
        not self.can_move_to((self.x - 1) % grid_width, self.y) and \
        not self.can_move_to((self.x + 1) % grid_width, self.y):
            return

        # Prioritize the direction that moves the animal further away from its target
        if abs(self.x - self.target.x) > abs(self.y - self.target.y):
            if self.x < self.target.x:
                weights[3] += 16  # West
            else:
                weights[2] += 16  # East
        else:
            if self.y < self.target.y:
                weights[0] += 16  # North
            else:
                weights[1] += 16  # South

        # Check if the preferred direction is impassable
        if not self.can_move_to(self.x, (self.y - 1) % grid_height):
            weights[0] = 0
        if not self.can_move_to(self.x, (self.y + 1) % grid_height):
            weights[1] = 0
        if not self.can_move_to((self.x + 1) % grid_width, self.y):
            weights[2] = 0
        if not self.can_move_to((self.x - 1) % grid_width, self.y):
            weights[3] = 0

        # Normalize the weights
        total_weight = sum(weights)
        weights = [weight / total_weight for weight in weights]

        # Choose a direction based on the weights
        self.direction = random.choices(directions, weights=weights)[0]

        # If both preferred directions are impassable, move in a random direction
        if weights[0] == 0 and weights[1] == 0 and weights[2] == 0 and weights[3] == 0:
            self.move_random()

        # Move in the chosen direction
        if self.direction == 'north':
            self.y = (self.y - 1) % grid_height
        elif self.direction == 'south':
            self.y = (self.y + 1) % grid_height
        elif self.direction == 'east':
            self.x = (self.x + 1) % grid_width
        elif self.direction == 'west':
            self.x = (self.x - 1) % grid_width
    
    def eat(self, range=float('inf')):
        nearest_food = None
        nearest_distance = float('inf')

        for obj in object_list:
            if hasattr(obj, 'sustenance'):
                dx = abs(self.x - obj.x)
                dy = abs(self.y - obj.y)
                distance = (dx ** 2 + dy ** 2) ** 0.5  # Pythagorean theorem to calculate distance
                if distance <= range and distance < nearest_distance:
                    nearest_distance = distance
                    nearest_food = obj

        if nearest_food:
            self.target = nearest_food
            weights = [1, 1, 1, 1]
            self.move_towards_target(self.target, weights)
            if abs(self.x - self.target.x) + abs(self.y - self.target.y) == 1:
                self.health = min(self.health + self.target.sustenance, self.max_health)
                object_list.remove(self.target)
                self.target = None
            return True
        else:
            return False

    
    def runaway_decision(self):  
        if self.target:
            dist = max(abs(self.x - self.target.x), abs(self.y - self.target.y))
            # Check health for hunt vs flee behavior
            if self.health > (self.max_health * 0.25) and dist <= 7:
                self.hunt()
            else:
                if dist >= 7 and self.health < self.max_health * 0.5:
                    self.rest()
                    self.target = None
                else:
                    self.flee()

    def update_target(self):
        target = None
        closest_distance = float("inf")

        for animal in animal_list:
            if animal != self:
                dx = abs(self.x - animal.x)
                dy = abs(self.y - animal.y)
                dist = max(min(dx, grid_width - dx), min(dy, grid_height - dy))
                if dist <= self.aggression and dist < closest_distance:
                    closest_distance = dist
                    target = animal

        self.target = target

    def look(self, radius):
        entities_in_range = []
        for entity in object_list + animal_list + [item for sublist in terrain_list for item in sublist]:
            if entity == self:
                continue
            dx = abs(self.x - entity.x)
            dy = abs(self.y - entity.y)
            dist = max(min(dx, grid_width - dx), min(dy, grid_height - dy))
            if dist <= radius:
                entities_in_range.append(entity)
        entities_in_range.sort(key=lambda x: max(min(abs(self.x - x.x), grid_width - abs(self.x - x.x)), min(abs(self.y - x.y), grid_height - abs(self.y - x.y))))
        return entities_in_range


    def draw_tile_radius(obj, radius, color = (78, 0, 0)):
        for y in range(obj.y - radius, obj.y + radius + 1):
            for x in range(obj.x - radius, obj.x + radius + 1):
                if x >= 0 and x < grid_width and y >= 0 and y < grid_height:
                    if obj.distance_to(terrain_list[y][x]) <= radius:
                        pygame.draw.rect(screen, color, pygame.Rect(x*20 + 1, y*20 + 1, 18, 18))
    
    def distance_to(self, obj):
        dx = abs(self.x - obj.x)
        dy = abs(self.y - obj.y)
        dist = max(min(dx, grid_width - dx), min(dy, grid_height - dy))
        return dist

class Human(Animal):
    character = 'H'
    color = (245, 245, 220)
    def __init__(self, x, y):
        super().__init__(x, y, 'H', (245, 245, 220), self.move, aggression=0, max_health=50, health=50, damage=2)
        self.inventory = []
        self.called_for_aid = False
        self.base_damage = 2
        self.attack_modifier = 0
        self.item_drop = True
        self.black_list = []
        
    def call_for_aid(self, range=10):
        for animal in animal_list:
            if isinstance(animal, Human) and animal != self:
                dx = abs(animal.x - self.x)
                dy = abs(animal.y - self.y)
                if dx <= range and dy <= range:
                    if animal.target != self.target:
                        animal.target = self.target
                        return True
        return False

    def use_fire_scepter(self):
        path = a_star_search(self, self.target, terrain_list, animal_list)
        for i, node in enumerate(path):
            if i > 0 and i < len(path) - 1:
                x, y = node
                if isinstance(terrain_list[y][x], Terrain):
                    terrain_list[y][x] = Fire(x, y)
                    
    
    def use_ice_scepter(self):
        target_x, target_y = self.target.x, self.target.y
        self_x, self_y = self.x, self.y 

        dx, dy = target_x - self_x, target_y - self_y
        distance = max(abs(dx), abs(dy)) 

        for i in range(1, distance + 1):
            radius = min(i // 2 + 1, 2) 
            for j in range(-radius, radius + 1):
                x = self_x + (dx * i) // distance + j * (dy // distance)
                y = self_y + (dy * i) // distance - j * (dx // distance)
                if 0 <= x < grid_width and 0 <= y < grid_height:
                    if isinstance(terrain_list[y][x], Terrain):
                        melt_value = 50 + (i / distance) * 100  # Gradual melt increase
                        terrain_list[y][x] = IcePlain(x, y, int(melt_value))

    def hunt(self):
        directions = ['north', 'south', 'east', 'west']
        weights = [1, 1, 1, 1]

        dx = min(abs(self.x - self.target.x), grid_width - abs(self.x - self.target.x))
        dy = min(abs(self.y - self.target.y), grid_height - abs(self.y - self.target.y))
        
        if hasattr(self, 'inventory') and any(isinstance(item, FireScepter) for item in self.inventory) and not isinstance(self.target, Tree):
            entities_in_range = self.look(5)
            if self.target in entities_in_range:
                self.use_fire_scepter()
                return
        elif hasattr(self, 'inventory') and any(isinstance(item, IceScepter) for item in self.inventory) :
            entities_in_range = self.look(6) 
            if self.target in entities_in_range:
                self.use_ice_scepter()
                return
        elif (dx == 1 and dy == 0) or (dx == 0 and dy == 1):
            self.attack(self.target)
            return

        self.move_towards_target(self.target, weights)

    def inventory_check(self):
        self.attack_modifier = 0
        one_handed_equipment = 0
        two_handed_equipment = 0
        for item in self.inventory:
            if hasattr(item, 'equipment') and item.equipment:
                if hasattr(item, 'one_handed') and item.one_handed:
                    one_handed_equipment += 1
                    if hasattr(item, 'weapon') and item.weapon:
                        self.attack_modifier += item.damage_modifier
                elif hasattr(item, 'two_handed') and item.two_handed:
                    two_handed_equipment += 1
                    if hasattr(item, 'weapon') and item.weapon:
                        self.attack_modifier += item.damage_modifier
                        if two_handed_equipment == 2:
                            self.attack_modifier += item.damage_modifier
                if one_handed_equipment > 1 or two_handed_equipment > 0:
                    for obj in object_list:
                        if hasattr(obj, 'weapon') and obj.weapon:
                            self.black_list.append(obj)
        self.damage = self.base_damage + self.attack_modifier


    def gather(self):
        if (abs(self.x - self.target.x) == 1 and self.y == self.target.y) or (abs(self.y - self.target.y) == 1 and self.x == self.target.x):
            self.inventory.append(self.target)
            object_list.remove(self.target)
            self.target = None
            return
        else:
            weights = [1, 1, 1, 1]
            self.move_towards_target(self.target, weights)
            return

    def firefight(self):
        if (abs(self.x - self.target.x) == 1 and self.y == self.target.y) or (abs(self.y - self.target.y) == 1 and self.x == self.target.x):
            if isinstance(self.target, Fire):
                terrain_list[self.target.y][self.target.x] = Terrain(self.target.x, self.target.y, ' ', (255, 255, 255))
                self.target = None
                return
        else:
            weights = [1, 1, 1, 1]
            self.move_towards_target(self.target, weights)
            return

    def move(self):
        self.jiggle()
        self.inventory_check()
        self.on_fire_effect()

        entities_in_range = self.look(10)
        if (frames % 100) == 0 and not self.frozen:
            if self.target and isinstance(self.target, Animal) and not isinstance(self.target, Tree):
                if not self.called_for_aid:
                    self.called_for_aid = True
                    self.call_for_aid()
                else:
                    if self.target not in entities_in_range:
                        self.target = None
                        self.called_for_aid = False
                    elif self.distance_to(self.target) > 10:
                        self.target = None
                        self.called_for_aid = False
                    else:
                        self.hunt()
            else:
                fires_in_range = [entity for entity in entities_in_range if isinstance(entity, Fire)]
                if len(fires_in_range) >= 4:
                    self.target = fires_in_range[0]
                    self.firefight()
                else:
                    objects_in_range = [entity for entity in entities_in_range if not isinstance(entity, Terrain) and not isinstance(entity, Animal) and entity not in self.black_list]
                    trees_in_range = [entity for entity in entities_in_range if isinstance(entity, Tree) and entity not in self.black_list]
                    objects_and_trees_in_range = objects_in_range + trees_in_range

                    if self.target and self.target not in objects_and_trees_in_range:
                        self.target = None

                    if objects_and_trees_in_range:
                        self.target = objects_and_trees_in_range[0]
                        if isinstance(self.target, Tree):
                            self.hunt()
                        else:
                            self.gather()
                    else:
                        self.target = None
                    if not self.target:
                        self.move_random()
        elif(frames % 100 == 0 and self.frozen):
            self.frozen -= 1 

class Ant(Animal):
    character = 'A'
    color = (255, 255, 255)
    def __init__(self, x, y):
        super().__init__(x, y, 'A', (255, 255, 255), self.move)

    def move(self):
        self.jiggle()
        self.on_fire_effect()
        
        if (frames % 150)== 0 and not self.frozen:
            if self.target:
                self.runaway_decision()
            else:
                self.move_random()
        elif(frames % 150 == 0 and self.frozen):
            self.frozen -= 1

class Tree(Animal):
    character = 'T'
    color = (0, 128, 0)
    def __init__(self, x, y):
        super().__init__(x, y, 'T', (0, 128, 0), self.move, max_health=35, health=35, damage=0)
        self.item_drop = True
        self.weaknesses = [Axe]

    def move(self):
        self.jiggle()
        self.on_fire_effect()
        self.Target = None

class Tiger(Animal):
    character = 'T'
    color = (255, 165, 0)
    def __init__(self, x, y):
        super().__init__(x, y, 'T', (255, 165, 0), self.move, aggression=5, max_health = 50, health = 50, damage = 10)
        self.protocol_count = 0
        self.direction = random.choice(['north', 'south', 'east', 'west'])
        self.protocol = random.choice(['rest', 'random', 'line'])
        self.item_drop = True

    def move_line(self):
        if self.protocol_count == 5:
            self.direction = random.choice(['north', 'south', 'east', 'west'])
        new_x = self.x
        new_y = self.y
        if self.direction == 'north':
            new_y = (self.y - 1) % grid_height
        elif self.direction == 'south':
            new_y = (self.y + 1) % grid_height
        elif self.direction == 'east':
            new_x = (self.x + 1) % grid_width
        elif self.direction == 'west':
            new_x = (self.x - 1) % grid_width
        
        if not self.can_move_to(new_x, new_y):
            self.protocol_count = 0
        else:
            self.x = new_x
            self.y = new_y
            self.protocol_count -= 1


    def move(self):
        self.jiggle()
        self.on_fire_effect()
        if self.target and (not self.target in animal_list or (self.distance_to(self.target) > 9)):
            self.is_fighting = False
            self.target = None
        if not self.is_fighting:
            entities_in_range = self.look(7)
            animals_in_range = [entity for entity in entities_in_range if isinstance(entity, Animal) and not isinstance(entity, Tree)]
            if animals_in_range:
                self.target = animals_in_range[0]
            else:
                self.target = None
        if (frames % 90) == 0 and not self.frozen:
            if self.target and isinstance(self.target, Animal):
                self.is_fighting = True
                self.hunt()
            elif self.health < self.max_health:
                path = self.eat(10)  # Try to find food within a range of 5 tiles
                if not path:
                    self.target = None  # Reset target if no path is found
            else:
                if self.protocol_count <= 0:
                    self.protocol = random.choice(['rest', 'random', 'line'])
                    self.protocol_count = 5
                if self.protocol == 'rest':
                    self.rest()
                    self.protocol_count -= 1
                elif self.protocol == 'random':
                    self.move_random()
                elif self.protocol == 'line':
                    self.move_line()
        elif(frames % 90 == 0 and self.frozen):
            self.frozen -= 1

class Rhino(Animal):
    character = 'R'
    color = (150, 150, 150)
    def __init__(self, x, y):
        super().__init__(x, y, 'R', (150, 150, 150), self.move, max_health= 80, health=60, damage=4)
        self.protocol_count = 7
        self.direction = random.choice(['north', 'south', 'east', 'west'])
        self.protocol = random.choice(['rest', 'random', 'line'])
        self.item_drop = True

    def move_line(self):
        if self.protocol_count == 7:
            self.direction = random.choice(['north', 'south', 'east', 'west'])
        if self.direction == 'north':
            self.y = (self.y - 1) % grid_height
        elif self.direction == 'south':
            self.y = (self.y + 1) % grid_height
        elif self.direction == 'east':
            self.x = (self.x + 1) % grid_width
        elif self.direction == 'west':
            self.x = (self.x - 1) % grid_width
        self.protocol_count -= 2

    def move(self):
        self.jiggle()
        self.on_fire_effect()
        if (frames % 150) == 0 and not self.frozen:
            if self.target:
                self.runaway_decision()
            else:
                if self.protocol_count <= 0:
                    self.protocol = random.choice(['rest', 'random', 'line'])
                    self.protocol_count = 7
                if self.protocol == 'rest':
                    self.rest()
                    self.protocol_count -= 1
                if self.protocol == 'random':
                    self.move_random()
                    self.protocol_count -= 1
                if self.protocol == 'line':
                    self.move_line()
                    self.protocol_count -= 2
        elif(frames % 150 == 0 and self.frozen):
            self.frozen -= 1




def draw_tile_radius(obj, radius, color):
    for y in range(obj.y - radius, obj.y + radius + 1):
        for x in range(obj.x - radius, obj.x + radius + 1):
            if x >= 0 and x < grid_width and y >= 0 and y < grid_height:
                pygame.draw.rect(screen, color, pygame.Rect(x*20 + 1, y*20 + 1, 18, 18))

def heuristic(node, end_node, grid_width, grid_height):
    x, y = node
    end_x, end_y = end_node
    return min(abs(x - end_x), grid_width - abs(x - end_x)) + min(abs(y - end_y), grid_height - abs(y - end_y))

def a_star_search(animal, target, terrain_list, animal_list):
    grid_width = len(terrain_list[0])
    grid_height = len(terrain_list)

    open_set = []
    closed_set = set()

    start_node = (animal.x, animal.y)
    end_node = (target.x, target.y)

    def heuristic(node, end_node):
        x, y = node
        end_x, end_y = end_node
        return min(abs(x - end_x), grid_width - abs(x - end_x)) + min(abs(y - end_y), grid_height - abs(y - end_y))

    distance = {start_node: 0}
    parent = {start_node: None}

    heapq.heappush(open_set, (0, start_node))

    while open_set:
        _, current_node = heapq.heappop(open_set)

        if current_node == end_node:
            path = []
            while current_node:
                path.append(current_node)
                current_node = parent[current_node]
            return path[::-1]

        closed_set.add(current_node)

        x, y = current_node

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = (x + dx) % grid_width, (y + dy) % grid_height

            try:
                if terrain_list[new_y][new_x].impassable and (new_x, new_y) != end_node:
                    continue
            except IndexError:
                continue

            new_distance = distance[current_node] + 1

            if (new_x, new_y) not in distance or new_distance < distance[(new_x, new_y)]:
                distance[(new_x, new_y)] = new_distance
                parent[(new_x, new_y)] = current_node
                heapq.heappush(open_set, (new_distance + heuristic((new_x, new_y), end_node), (new_x, new_y)))

    return []

tile_size = 20

def draw_entities(animal_list, object_list, terrain_list):
    priority_dict = {}

    for animal in animal_list:
        animal.move()
        priority_dict[(animal.x, animal.y)] = 'animal'
        if animal.on_fire > 0: 
            fire_circle_center = (animal.x * tile_size + 4, animal.y * tile_size + 4)  # Adjust offset as needed
            pygame.draw.circle(screen, (255, 0, 0), fire_circle_center, 1) 
        if animal.frozen > 0:
            frozen_circle_center = (animal.x * tile_size + 4, animal.y * tile_size + 4) 
            pygame.draw.circle(screen, (0, 200, 255), frozen_circle_center, 1)  # Draw light blue circle

    for obj in object_list:
        if (obj.x, obj.y) not in priority_dict:
            priority_dict[(obj.x, obj.y)] = 'object'

    for y in range(len(terrain_list)):
        for x in range(len(terrain_list[y])):
            terrain = terrain_list[y][x]
            if terrain is not None:
                if (terrain.x, terrain.y) not in priority_dict:
                    priority_dict[(terrain.x, terrain.y)] = 'terrain'

    for animal in animal_list:
        if priority_dict.get((animal.x, animal.y)) == 'animal':
            animal.draw()
    for obj in object_list:
        if priority_dict.get((obj.x, obj.y)) == 'object':
            obj.draw()


    for y in range(len(terrain_list)):
        for x in range(len(terrain_list[y])):
            terrain = terrain_list[y][x]
            if terrain is not None: 
                if priority_dict.get((terrain.x, terrain.y)) == 'terrain':
                    terrain.draw()

def update_animal_list():
    global animal_list, object_list
    new_animal_list = []
    for animal in animal_list:
        if animal.health <= 0:
            # Drop the first item in the animal's location
            if hasattr(animal, 'item_drop'):
                if type(animal) == Tiger:
                    object_list.append(Pelt(animal.x, animal.y))
                    # Drop additional items in surrounding tiles for multi-drop animals
                    for i in range(1, random.randint(2,3)): # 1-2 for Tiger
                        new_x = (animal.x + random.randint(-1, 1)) % grid_width
                        new_y = (animal.y + random.randint(-1, 1)) % grid_height
                        # Check if the new location is not the same as the original location
                        if (new_x, new_y) != (animal.x, animal.y):
                            # Check if there is no item at the new location
                            if not any(obj.x == new_x and obj.y == new_y for obj in object_list):
                                object_list.append(Meat(new_x, new_y))
                elif type(animal) == Rhino:
                    object_list.append(Meat(animal.x, animal.y))
                    
                    # Drop additional items in surrounding tiles for multi-drop animals
                    for i in range(1, random.randint(2,3)): # 2-3 for Rhino
                        new_x = (animal.x + random.randint(-1, 1)) % grid_width
                        new_y = (animal.y + random.randint(-1, 1)) % grid_height
                        # Check if the new location is not the same as the original location
                        if (new_x, new_y) != (animal.x, animal.y):
                            # Check if there is no item at the new location
                            if not any(obj.x == new_x and obj.y == new_y for obj in object_list):
                                object_list.append(Meat(new_x, new_y))
                elif type(animal) == Tree:
                    for i in range(random.randint(2, 3)):  # 2-3 for Tree
                        new_x = (animal.x + random.randint(-1, 1)) % grid_width
                        new_y = (animal.y + random.randint(-1, 1)) % grid_height
                        # Check if the new location is not the same as the original location
                        if (new_x, new_y) != (animal.x, animal.y):
                            # Check if there is no item at the new location
                            if not any(obj.x == new_x and obj.y == new_y for obj in object_list):
                                object_list.append(Wood(new_x, new_y))
                elif type(animal) == Human:
                    for item in animal.inventory:
                        # Check if the tile where the Human died is already occupied
                        if not any(obj.x == animal.x and obj.y == animal.y for obj in object_list):
                            item.x = animal.x
                            item.y = animal.y
                            object_list.append(item)
                        else:
                            # If the tile is occupied, find an unoccupied tile in expanding rings around the death location
                            placed = False
                            for radius in range(1, max(grid_width, grid_height)):  # Use larger of grid dimensions as limit
                                if placed:
                                    break
                                for dx in range(-radius, radius + 1):
                                    for dy in range(-radius, radius + 1):
                                        new_x = (animal.x + dx) % grid_width
                                        new_y = (animal.y + dy) % grid_height
                                        # Check if the new tile is unoccupied
                                        if not any(obj.x == new_x and obj.y == new_y for obj in object_list):
                                            item.x = new_x
                                            item.y = new_y
                                            object_list.append(item)
                                            placed = True
                                            break  # Break from the innermost loop once an item is placed
                                    if placed:
                                        break  # Break from the second loop
  # Break from the outer loop
        else:
            new_animal_list.append(animal)
    animal_list = new_animal_list


red_x_position = (width - 15, height - 15)
def pick_up_and_drop(event):
    global picked_up_object, picked_up_animal, picked_up_terrain, object_list, animal_list, terrain_list, grid_width, grid_height
    mouse_x, mouse_y = pygame.mouse.get_pos()

    screen_width, screen_height = 800, 630
    
    grid_x, grid_y = mouse_x // 20, mouse_y // 20

    delete_area_x1 = screen_width - 20  
    delete_area_y1 = screen_height - 20
    
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for animal in animal_list:
            if animal.x == grid_x and animal.y == grid_y:
                if picked_up_animal is None:
                    picked_up_animal = animal
                    animal_list.remove(animal)
                    break

        if not picked_up_animal:  
            for obj in object_list:
                if obj.x == grid_x and obj.y == grid_y:
                    picked_up_object = obj
                    object_list.remove(obj)
                    break


        for char, (x, y, subclass) in character_positions.items():
            if x - 12 < mouse_x < x + 12 and y - 12 < mouse_y < y + 12:
                if issubclass(subclass, Animal):
                    picked_up_animal = subclass(-1, -1)  # Use placeholder positions
                elif issubclass(subclass, Object):
                    picked_up_object = subclass(-1, -1)  
                elif issubclass(subclass, Terrain) and subclass is not Terrain:
                    picked_up_terrain = subclass(-1, -1)  
                break
            
        if not picked_up_animal and not picked_up_object and not picked_up_terrain:
            for row in terrain_list:
                for terrain in row:
                    if terrain.x == grid_x and terrain.y == grid_y:
                        if isinstance(terrain_list[grid_y][grid_x], Terrain) and not type(terrain_list[grid_y][grid_x]) is Terrain:
                            picked_up_terrain = terrain
                            terrain_list[grid_y][grid_x] = Terrain(x, y, ' ', (0, 0, 0), False)
                            break

    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        if delete_area_x1 <= mouse_x <= screen_width and delete_area_y1 <= mouse_y <= screen_height:
            picked_up_object = None
            picked_up_animal = None
            if picked_up_terrain:
                x, y = picked_up_terrain.x, picked_up_terrain.y
                terrain_list[y][x] = Terrain(x, y, ' ', (0, 0, 0), False)
            picked_up_terrain = None
        else:
            pos_x, pos_y = max(0, min(mouse_x // 20, grid_width - 1)), max(0, min(mouse_y // 20, grid_height - 1))
            if picked_up_object:
                picked_up_object.x = pos_x
                picked_up_object.y = pos_y
                object_list.append(picked_up_object)
                picked_up_object = None
            if picked_up_animal:
                picked_up_animal.x = pos_x
                picked_up_animal.y = pos_y
                animal_list.append(picked_up_animal)
                picked_up_animal = None
            if picked_up_terrain:
                pos_x, pos_y = max(0, min(mouse_x // 20, grid_width - 1)), max(0, min(mouse_y // 20, grid_height - 1))
                picked_up_terrain.x = pos_x
                picked_up_terrain.y = pos_y
                terrain_list[pos_y][pos_x] = picked_up_terrain
                picked_up_terrain = None

def display_text(text, pos):
    screen.blit(text, (pos[0] - text.get_width() // 2, pos[1] - text.get_height() // 2))
    
    red_x_position = (width - 15, height - 15)
    pygame.draw.line(screen, (255, 0, 0), (red_x_position[0] - 6, red_x_position[1] - 6), (red_x_position[0] + 6, red_x_position[1] + 6), 3)
    pygame.draw.line(screen, (255, 0, 0), (red_x_position[0] - 6, red_x_position[1] + 6), (red_x_position[0] + 6, red_x_position[1] - 6), 3)

def display_info_box(entity, pos):
    font = pygame.font.Font(None, 16)
    text_color = (240, 240, 240)
    background_color = (0, 0, 0)

    if isinstance(entity, str):
        text = [entity]
    elif isinstance(entity, Human):
        text = [entity.__class__.__name__, f"Health: {entity.health}", f"Damage: {entity.damage}"]
        if entity.target:
            text.append(f"Hunting: {entity.target.__class__.__name__}") 
        text.append("Inventory:")
        text.append("-" * 10)
        for item in entity.inventory:
            text.append(item.__class__.__name__)
    elif isinstance(entity, Animal):
        text = [entity.__class__.__name__, f"Health: {entity.health}", f"Damage: {entity.damage}"]
        if entity.target:
            text.append(f"Hunting: {entity.target.__class__.__name__}") 
    elif isinstance(entity, Terrain):
        text = [entity.__class__.__name__]
        if entity.impassable:
            text.append("Impassable")
    else:
        text = [entity.__class__.__name__]
    
    text_surfaces = [font.render(t, True, text_color) for t in text]
    max_width = max(s.get_width() for s in text_surfaces)
    total_height = sum(s.get_height() for s in text_surfaces)

    box_width = max(100, max_width + 20)
    box_height = total_height + 20

    box_x = pos[0] + 20
    box_y = pos[1] - box_height

    # Dynamically adjust horizontal position
    overlap_right = (box_x + box_width) - screen.get_width()
    if overlap_right > 0:
        box_x -= overlap_right

    overlap_top = -box_y
    if overlap_top > 0:
        box_y += overlap_top

    pygame.draw.rect(screen, background_color, (box_x, box_y, box_width, box_height))

    y = box_y + 10
    for s in text_surfaces:
        screen.blit(s, (box_x + 10, y))
        y += s.get_height()


def generate_terrain(grid_width, grid_height):
    terrain_list = [[None for _ in range(grid_width)] for _ in range(grid_height)]
    
    for y in range(grid_height):
        for x in range(grid_width):
            if x < 5 and y < 5 and random.random() < 0.5:
                terrain_list[y][x] = Water(x, y)
            else:
                terrain_list[y][x] = Terrain(x, y, ' ', (0, 0, 0), False)
    return terrain_list

character_positions = {}

def display_legend(width, height):
    legend_x = 5 
    legend_y = height - 23  
    spacing = 15  

    terrains = [cls for cls in Terrain.__subclasses__()]
    animals = [cls for cls in Animal.__subclasses__()]
    objects = [cls for cls in Object.__subclasses__()]

    terrain_chars = [cls.character for cls in terrains]
    animal_chars = [cls.character for cls in animals]
    object_chars = [cls.character for cls in objects]

    terrain_colors = [cls.color for cls in terrains]
    animal_colors = [cls.color for cls in animals]
    object_colors = [cls.color for cls in objects]

    label_text = font.render("Terrains: ", True, (255, 255, 255))
    screen.blit(label_text, (legend_x, legend_y))
    legend_x += label_text.get_width()

    for char, color, terrain in zip(terrain_chars, terrain_colors, terrains):
        text = font.render(char, True, color)
        screen.blit(text, (legend_x, legend_y))
        character_positions[(char, color)] = (legend_x, legend_y, terrain)
        legend_x += spacing

    legend_x += 2 * spacing 
    label_text = font.render("Animals: ", True, (255, 255, 255))
    screen.blit(label_text, (legend_x, legend_y))
    legend_x += label_text.get_width()

    for char, color, animal in zip(animal_chars, animal_colors, animals):
        text = font.render(char, True, color)
        screen.blit(text, (legend_x, legend_y))
        character_positions[(char, color)] = (legend_x, legend_y, animal)
        legend_x += spacing

    legend_x += 2 * spacing  
    label_text = font.render("Objects: ", True, (255, 255, 255))
    screen.blit(label_text, (legend_x, legend_y))
    legend_x += label_text.get_width()

    for char, color, obj in zip(object_chars, object_colors, objects):
        text = font.render(char, True, color)
        screen.blit(text, (legend_x, legend_y))
        character_positions[(char, color)] = (legend_x, legend_y, obj)
        legend_x += spacing




font = pygame.font.Font(None, 20)

object_list = [Sword(grid_width//2, grid_height//2),
               Sword(grid_width//2+1, grid_height//2),
               Sword(grid_width//2-1, grid_height//2),
               Axe(grid_width//4, grid_height//2),
               Axe(grid_width//4+1, grid_height//2)]
animal_list = [Ant(random.randint(0, grid_width-1), random.randint(0, grid_height-1)),
               Ant(random.randint(0, grid_width-1), random.randint(0, grid_height-1)),
               Tiger(grid_width//2, 0),
               Rhino(0, 10),
               Human(random.randint(grid_width//2, grid_width-1), random.randint(grid_height//2, grid_height-1)),
               Human(random.randint(grid_width//2, grid_width-1), random.randint(grid_height//2, grid_height-1)),
               Human(random.randint(grid_width//2, grid_width-1), random.randint(grid_height//2, grid_height-1))]
for _ in range(15):
    tree = Tree(random.randint(0, grid_width-1), random.randint(0, grid_height-1))
    animal_list.append(tree)

terrain_list = generate_terrain(grid_width, grid_height)


legend_dict = {}
info_box_animal = None
info_box_object = None
info_box_frames = 0
picked_up_object = None
picked_up_animal = None
picked_up_terrain = None
legend_position = None
legend_name = None
running = True
while running:
    frames += 1 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                pick_up_and_drop(event)
            elif event.button == 3:  # Right click
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x, grid_y = mouse_x // 20, mouse_y // 20
                for animal in animal_list:
                    if animal.x == grid_x and animal.y == grid_y:
                        info_box_animal = animal
                        info_box_object = None
                        info_box_frames = 100  
                        legend_name = None
                        break
                else:  
                    for obj in object_list:
                        if obj.x == grid_x and obj.y == grid_y:
                            info_box_object = obj
                            info_box_animal = None
                            info_box_frames = 100  
                            legend_name = None
                            break
                    else: 
                        if grid_y < len(terrain_list) and grid_x < len(terrain_list[grid_y]):
                            terrain = terrain_list[grid_y][grid_x] 
                            info_box_object = terrain # Treating terrain like object
                            info_box_animal = None
                            info_box_frames = 100
                            legend_name = None
                            break
                        else:
                            for char, (x, y, subclass) in character_positions.items():
                                if x - 12 < mouse_x < x + 12 and y - 12 < mouse_y < y + 12:
                                    legend_name = subclass.__name__
                                    legend_position = (x, y)
                                    info_box_animal = None
                                    info_box_object = None
                                    info_box_frames = 100
                                    break
                            else:
                                legend_name = None
                                legend_position = None
        elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEMOTION:
            pick_up_and_drop(event)  


    screen.fill(bg_color)
    
    for animal in animal_list:
        if animal.target:
            path = a_star_search(animal, animal.target, terrain_list, animal_list)
            for i, node in enumerate(path):
                if i > 0 and i < len(path) - 1:
                    x, y = node
                    pygame.draw.rect(screen, (0, 78, 0), pygame.Rect(x*20 + 1, y*20 + 1, 18, 18))
    draw_grid()
    draw_entities(animal_list, object_list, terrain_list)
    display_legend(width, height)

    for row in terrain_list:
        for terrain in row:
            if terrain and hasattr(terrain, 'terrain_effect'):
                terrain.terrain_effect()

    if picked_up_object or picked_up_animal or picked_up_terrain:
        text_to_display = (picked_up_object.text if picked_up_object else
                        picked_up_animal.text if picked_up_animal else
                        picked_up_terrain.text if picked_up_terrain else None)
        display_text(text_to_display, pygame.mouse.get_pos())

    update_animal_list()
    

    if info_box_animal or info_box_object or legend_name:
        info_box_frames -= 1
        if info_box_frames > 0:
            if info_box_animal:
                entity = info_box_animal
            elif info_box_object:
                entity = info_box_object
            elif legend_name:  # Assuming legend_name has been defined somewhere as either a legend item name or None
                entity = legend_name
            if entity == info_box_animal or entity == info_box_object:
                display_info_box(entity, (entity.x * 20, entity.y * 20))
            else:
                display_info_box(entity, legend_position)
        else:
            info_box_animal = None
            info_box_object = None

    pygame.display.flip()

pygame.quit()
sys.exit()
