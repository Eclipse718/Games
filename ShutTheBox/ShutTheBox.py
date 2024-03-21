import pygame
import pygame_gui
import os
import random
from itertools import combinations
import time
import numpy as np
from collections import Counter

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()

WIDTH = 600
HEIGHT = 400
FONT = 'PathwayGothicOne.ttf'
TITLE_FONT_SIZE = 65
BUTTON_FONT_SIZE = 45
SIMULATE_FONT_SIZE = 34
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50
ENTER_FONT_SIZE = 27
PLAYAGAIN_FONT_SIZE = 13


global frames
frames = 0

title_font = pygame.font.Font(FONT, TITLE_FONT_SIZE)
button_font = pygame.font.Font(FONT, BUTTON_FONT_SIZE)
iterations_font = pygame.font.Font(FONT, 23)
simulator_scores_font = pygame.font.Font(FONT, 18)
simulate_font = pygame.font.Font(FONT, SIMULATE_FONT_SIZE)
stats_or_board_font = pygame.font.Font(FONT, 24)
window_surface = pygame.display.set_mode((WIDTH, HEIGHT))

background = pygame.image.load('wood_grain.jpg')
background = pygame.transform.scale(background, (WIDTH, HEIGHT))  

back_arrow = pygame.image.load('BackArrow.png')
back_arrow = pygame.transform.scale(back_arrow, (50, 50))

dice_images = [pygame.image.load(f'dice{i}.png') for i in range(1, 7)]
for i in range(len(dice_images)):
    dice_images[i] = pygame.transform.scale(dice_images[i], (40, 40))

back_arrow_rect = back_arrow.get_rect(bottomright=(WIDTH - 10, HEIGHT - 10))

screen = pygame.display.set_mode((WIDTH, HEIGHT))

scores = []

play_button = pygame.Rect(WIDTH / 4 - BUTTON_WIDTH / 2, HEIGHT / 2 - BUTTON_HEIGHT / 2, BUTTON_WIDTH, BUTTON_HEIGHT)
simulate_button = pygame.Rect(WIDTH * 3 / 4 - BUTTON_WIDTH / 2, HEIGHT / 2 - BUTTON_HEIGHT / 2, BUTTON_WIDTH, BUTTON_HEIGHT)
roll_button = pygame.Rect(WIDTH / 2 - BUTTON_WIDTH / 2, HEIGHT / 2 + 50, BUTTON_WIDTH, BUTTON_HEIGHT)
start_button = pygame.Rect(WIDTH / 2 - BUTTON_WIDTH / 2, HEIGHT / 2 + 50, BUTTON_WIDTH, BUTTON_HEIGHT)


box_width = 300
box_height = 100

global iterations
iterations = 1

global play_screen
play_screen = False

box_rect = pygame.Rect((WIDTH - box_width) / 2, 100, box_width, box_height)

roll1 = None
roll2 = None

tiles_up = [i for i in range(1, 10)]
tiles_down = []
selected_numbers = []

stats_or_board = False

global rolled
rolled = False

global viable_moves
viable_moves = []

global lost
lost = False

global runs
runs = 0

global total_score 
total_score = 0

global simulating
simulating = False

global high_clicked, low_clicked, most_clicked, least_clicked, last_clicked_button 
high_clicked = True
low_clicked = False
most_clicked = False
least_clicked = False

last_clicked_button = None

# This will keep track of the last clicked button
current_active_button = None

manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Create a slider
slider_range = 100
global slider
slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((425, 20), (150, 20)),
                                                start_value=1,
                                                value_range=(1, slider_range),
                                                manager=manager)

class Button:
    def __init__(self, x, y, width, height, text=None, font=None, bold=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.font = font if font else pygame.font.Font(None, 14)
        self.bold = bold
        self.color = (0, 0, 0) 
        self.box_color = (0, 0, 0)  

    def draw(self, color=None, box_color=None):
        if color:
            self.color = color
        if box_color is not None:
            self.box_color = box_color

        if self.bold:
            font = self.font.copy()
            font.set_bold(True)
        else:
            font = self.font

        if self.text:
            text_surface = font.render(self.text, True, self.color)
            text_rect = text_surface.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
    
        pygame.draw.rect(screen, self.box_color, (self.x, self.y, self.width, self.height), 2)
        
        if self.text:
            screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False

    def on_click(self):
        pass

class TileButton(Button):
    def __init__(self, x, y, width, height, text, font):
        super().__init__(x, y, width, height, text, font)

    def on_click(self):
        global tiles_up, tiles_down, selected_numbers, rolled
        if rolled:
            tile_number = int(self.text)
            if tile_number in tiles_up:
                if tile_number not in selected_numbers:
                    selected_numbers.append(tile_number)
                else:
                    selected_numbers.remove(tile_number)
            else:
                return
        else:
            return

class BackArrowButton(Button):
    def __init__(self, x, y, width, height, image):
        super().__init__(x, y, width, height)
        self.image = image

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def on_click(self):
        global rolled, is_homescreen, play_screen, lost, total_score, simulate_select, runs, roll1, roll2, tiles_up, tiles_down, selected_numbers
        rolled = False
        is_homescreen = True
        play_screen = False
        lost = False
        total_score = 0
        runs = 0
        roll1 = None
        roll2 = None
        tiles_up = [i for i in range(1, 10)]
        tiles_down = []
        selected_numbers = []
        simulate_select = False

class PlayButton(Button):
    def __init__(self, x, y, width, height, text, font=button_font):
        super().__init__(x, y, width, height, text, font)

    def on_click(self):
        global is_homescreen, play_screen
        is_homescreen = False
        play_screen = True

class HomeScreenButton(Button):
    def __init__(self, x, y, width, height, text, font=button_font):
        super().__init__(x, y, width, height, text, font)
        

class ButtonState:
    def __init__(self):
        self.active_button = None


class SimulateButton(Button):
    def __init__(self, x, y, width, height, text):
        super().__init__(x, y, width, height, text, pygame.font.Font(FONT, SIMULATE_FONT_SIZE))

    def on_click(self):
        global simulating, is_homescreen
        is_homescreen = False
        simulating = True



class SimulateSelect(Button):
    def __init__(self, x, y, width, height, text, font):
        super().__init__(x, y, width, height, text, font)
    
    def on_click(self):
        global current_active_button
        current_active_button = self


class RollButton(Button):
    def __init__(self, x, y, width, height, text, font=button_font):
        super().__init__(x, y, width, height, text, font)

    def on_click(self):
        roll_dice()


class StartButton(Button):
    def __init__(self, x, y, width, height, text, font=button_font):
        super().__init__(x, y, width, height, text, font)

    def on_click(self):
        start_simulation()

class StatsButton(Button):
    def __init__(self, x, y, width, height, text, font=stats_or_board_font):
        super().__init__(x, y, width, height, text, font)

    def on_click(self):
        global stats_or_board, slider_range, slider, manager, iterations
        stats_or_board = not stats_or_board

        if slider is not None:
            slider.kill()

        if stats_or_board:
            self.text = "Board"
            slider_range = 1000
            iterations = 1
        else:
            self.text = "Stats"
            slider_range = 100 
            iterations = 1


        slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((425, 20), (150, 20)),
                                                        start_value=1,
                                                        value_range=(1, slider_range),
                                                        manager=manager)



class EnterButton(Button):
    def __init__(self, x, y, width, height, text, font_size=ENTER_FONT_SIZE):
        super().__init__(x, y, width, height, text, button_font)

    def on_click(self):
        global selected_numbers, tiles_down, tiles_up, rolled, lost, runs, total_score
        if self.text == "Enter":
            if rolled:
                total = sum(selected_numbers)
                if total == roll1 + roll2:
                    tiles_down.extend(selected_numbers)
                    for i in selected_numbers:
                        tiles_up.remove(i)
                    selected_numbers = []
                    rolled = False
            else:
                return
        elif self.text == "Play Again?":
            runs += 1
            total_score += sum(tiles_up)
            tiles_up = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            tiles_down = []
            selected_numbers = []
            rolled = False
            lost = False
            self.text = "Enter"
            self.font = pygame.font.Font(FONT, ENTER_FONT_SIZE)

play_buttons = [
    TileButton(box_rect.x + (i % 9) * (box_width / 9), box_rect.y, box_width / 9, box_height, str(i + 1), button_font) for i in range(9)
]
play_buttons.append(RollButton(roll_button.x, roll_button.y, roll_button.width, roll_button.height, "Roll"))
play_buttons.append(Button(WIDTH / 2 - 50, HEIGHT / 2 + 200, 100, 50, "Back", pygame.font.Font(FONT, 20)))
play_buttons.append(EnterButton(box_rect.x + box_width - 50, box_rect.y + box_height + 50, 50, 50, "Enter"))
play_buttons.append(BackArrowButton(WIDTH - 60, HEIGHT - 60, 50, 50, back_arrow))

home_screen_buttons = [
    PlayButton(WIDTH / 4 - BUTTON_WIDTH / 2, HEIGHT / 2 - BUTTON_HEIGHT / 2, BUTTON_WIDTH, BUTTON_HEIGHT, "Play"),
    SimulateButton(WIDTH * 3 / 4 - BUTTON_WIDTH / 2, HEIGHT / 2 - BUTTON_HEIGHT / 2, BUTTON_WIDTH, BUTTON_HEIGHT, "Simulate"),
]

high_button = SimulateSelect(10, 10, 70, 30, "High #'s First", font= pygame.font.Font(FONT, 16))
low_button = SimulateSelect(10, 60, 70, 30, "Low #'s First", font= pygame.font.Font(FONT, 16))
most_button = SimulateSelect(10, 110, 90, 30, "Select Most Tiles", font= pygame.font.Font(FONT, 16))
least_button = SimulateSelect(10, 160, 90, 30, "Select Least Tiles", font= pygame.font.Font(FONT, 16))
random_button = SimulateSelect(10, 210, 60, 30, "Random", font= pygame.font.Font(FONT, 16))
semiRandom_button = SimulateSelect(10, 260, 75, 30, "Semi-Random", font= pygame.font.Font(FONT, 16))

colored_simulate_selection_buttons = [
    high_button,
    low_button,
    most_button,
    least_button,
    random_button,
    semiRandom_button
]
simulate_selection_buttons = [
    BackArrowButton(WIDTH - 60, HEIGHT - 60, 50, 50, back_arrow),
    StatsButton(WIDTH - 180, HEIGHT - 90, 60, 30, "Stats")
]


simulate_selection_buttons.append(StartButton(roll_button.x, roll_button.y, roll_button.width, roll_button.height, "Start"))

def calculate_viable_moves(tiles_up, roll):
    viable_moves = []
    for r in range(1, len(tiles_up) + 1):
        for combo in combinations(tiles_up, r):
            if sum(combo) == roll:
                viable_moves.append(list(combo))
    return viable_moves

def start_simulation():
    global iterations, roll1, roll2, current_active_button, frames, tiles_down, scores
    frames = 0
    scores = []
    new_game = True
    for _ in range(iterations):
        tiles_up = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        tiles_down = []
        viable_moves = []
        if(stats_or_board):
            frames_delay = 500
        else:
            frames_delay = 800000
        while True:
            frames += 1
            if frames % frames_delay == 0:
                roll1, roll2 = random.randint(1, 6), random.randint(1, 6)
                viable_moves = calculate_viable_moves(tiles_up, roll1 + roll2)
                if not viable_moves:
                    scores.append(sum(tiles_up))
                    break
                winning_moves = [move for move in viable_moves if sum(move) == len(tiles_up)]
                if current_active_button == random_button:
                    chosen_move = random.choice(viable_moves)
                elif current_active_button == semiRandom_button:
                    if winning_moves:
                        chosen_move = winning_moves[0]
                    else:
                        chosen_move = random.choice(viable_moves)
                elif current_active_button == high_button:
                    high_moves = [move for move in viable_moves if max(move) == max(tiles_up)]
                    if high_moves:
                        chosen_move = random.choice(high_moves)
                    else:
                        chosen_move = random.choice(viable_moves)
                elif current_active_button == low_button:
                    low_moves = [move for move in viable_moves if min(move) == min(tiles_up)]
                    if low_moves:
                        chosen_move = random.choice(low_moves)
                    else:
                        chosen_move = random.choice(viable_moves)
                elif current_active_button == most_button:
                    most_moves = [move for move in viable_moves if len(move) == max([len(move) for move in viable_moves])]
                    if most_moves:
                        chosen_move = random.choice(most_moves)
                    else:
                        chosen_move = random.choice(viable_moves)
                elif current_active_button == least_button:
                    least_moves = [move for move in viable_moves if len(move) == min([len(move) for move in viable_moves])]
                    if least_moves:
                        chosen_move = random.choice(least_moves)
                    else:
                        chosen_move = random.choice(viable_moves)
                tiles_up = [tile for tile in tiles_up if tile not in chosen_move]
                tiles_down.extend(chosen_move)

                draw_simulator()
                pygame.display.update()  
            
                if tiles_up == []:
                    scores.append(sum(tiles_up))
                    break


current_active_button = random_button
def draw_simulator():
    global iterations, scores
    screen.blit(background, (0, 0))
    
    for button in colored_simulate_selection_buttons:
        if button == current_active_button:
            button.font.set_underline(True)
            button.draw(color=(0, 0, 0))  
            pygame.draw.rect(screen, (0, 0, 0), (button.x - 2, button.y - 2, button.width + 4, button.height + 4), 2)
        else:
            button.font.set_underline(False)
            button.draw(color=(0, 0, 0))  
    
    manager.process_events(event)

    if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED and event.ui_element == slider:
        iterations = slider.get_current_value()

    manager.update(time_delta)
    text_surface = iterations_font.render("Games: " + str(iterations), True, (0, 0, 0))

    text_rect = text_surface.get_rect(center=(500, 50))
    window_surface.blit(text_surface, text_rect)
    manager.draw_ui(window_surface)

    for button in simulate_selection_buttons:
        button.draw()
    
    if roll1 is not None and roll2 is not None:
        dice_rect1 = dice_images[roll1 - 1].get_rect(center=(WIDTH / 2 - 50, HEIGHT / 2 + 150))
        dice_rect2 = dice_images[roll2 - 1].get_rect(center=(WIDTH / 2 + 50, HEIGHT / 2 + 150))
        screen.blit(dice_images[roll1 - 1], dice_rect1)
        screen.blit(dice_images[roll2 - 1], dice_rect2)
    
    if scores:
        last_score = scores[-1]
        total_score = sum(scores)
        mean_score = round(total_score / len(scores), 1)

        last_score_text = simulator_scores_font.render("Last Score: " + str(last_score), True, (0,0,0))
        total_score_text = simulator_scores_font.render("Total Score: " + str(total_score), True, (0,0,0))
        mean_score_text = simulator_scores_font.render("Mean Score Over " + str(len(scores)) + " games: " + str(mean_score), True, (0,0,0))

        screen.blit(last_score_text, (370, 250))
        screen.blit(total_score_text, (370, 265))
        screen.blit(mean_score_text, (370, 280))

        games_won = len([score for score in scores if score == 0])
        win_percentage = round(games_won / len(scores) * 100, 1)
        std_dev = round(np.std(scores), 1)

        games_won_text = simulator_scores_font.render("Games Won: " + str(games_won), True, (0,0,0))
        win_percentage_text = simulator_scores_font.render("Win Percent: " + str(win_percentage) + "%", True, (0,0,0))
        std_dev_text = simulator_scores_font.render("Std. Deviation: " + str(std_dev), True, (0,0,0))

        screen.blit(games_won_text, (120, 250))
        screen.blit(win_percentage_text, (120, 265))
        screen.blit(std_dev_text, (120, 280))

    if(stats_or_board):
        draw_bar_graph(screen, scores)
        small_box_height = box_height
        y = box_rect.y + 2 * small_box_height
        pygame.draw.line(screen, (0, 0, 0), (box_rect.x, y), (box_rect.x + box_width, y), 2)
    else:
        draw_box()

def draw_game_status():
    global lost, tiles_up, screen
    if lost:
        font = pygame.font.Font('PathwayGothicOne.ttf', 30)
        text = font.render('Game Lost', True, (255, 0, 0))
        text_rect = text.get_rect(center=(WIDTH - 60, HEIGHT - 100))
        screen.blit(text, text_rect)

        score = sum(tiles_up)
        font = pygame.font.Font('PathwayGothicOne.ttf', 20)
        text = font.render('Score: ' + str(score), True, (0, 0, 0))
        text_rect = text.get_rect(center=(WIDTH - 60, HEIGHT - 75))
        screen.blit(text, text_rect)
    elif lost == False and not tiles_up:
        font = pygame.font.Font('PathwayGothicOne.ttf', 30)
        text = font.render('Game Won', True, (0, 255, 0))
        text_rect = text.get_rect(center=(WIDTH - 60, HEIGHT - 100))
        screen.blit(text, text_rect)

        font = pygame.font.Font('PathwayGothicOne.ttf', 20)
        text = font.render('Score: 0', True, (0, 0, 0))
        text_rect = text.get_rect(center=(WIDTH - 60, HEIGHT - 75))
        screen.blit(text, text_rect)
    if runs > 0:
        font = pygame.font.Font('PathwayGothicOne.ttf', 20)
        text = font.render('Run Number: ' + str(runs), True, (0, 0, 0))
        text_rect = text.get_rect(center=(50, HEIGHT - 50))
        screen.blit(text, text_rect)

        font = pygame.font.Font('PathwayGothicOne.ttf', 20)
        text = font.render('Total Score: ' + str(total_score), True, (0, 0, 0))
        text_rect = text.get_rect(center=(50, HEIGHT - 25))
        screen.blit(text, text_rect)

def draw_box():
    small_box_width = box_width // 9
    small_box_height = box_height

    box_rect = pygame.Rect((WIDTH - box_width) / 2, 100, box_width, box_height)
    pygame.draw.rect(screen, (0, 0, 0), box_rect, 2)

    for i in range(1, 9):
        x = box_rect.x + i * small_box_width
        y = box_rect.y
        pygame.draw.line(screen, (0, 0, 0), (x, y), (x, y + box_height), 2)

    for i in range(1, 3):
        y = box_rect.y + i * small_box_height
        pygame.draw.line(screen, (0, 0, 0), (box_rect.x, y), (box_rect.x + box_width, y), 2)

    for i in range(9):
        button = play_buttons[i]
        if i + 1 in tiles_down:
            button.font.set_underline(False)
            button_text = button.font.render(button.text, True, (255, 0, 0))
        elif i + 1 in selected_numbers:
            button.font.set_underline(True)
            button_text = button.font.render(button.text, True, (0, 0, 0))
            button.font.set_underline(False)  
        else:
            button_text = button.font.render(button.text, True, (0, 0, 0))
        
        button_text_rect = button_text.get_rect(center=(button.x + button.width / 2, button.y + button.height / 2))
        screen.blit(button_text, button_text_rect)


def draw_bar_graph(screen, scores):
    pygame.init()

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    counter = Counter(scores)

    if not scores:
        font = pygame.font.SysFont('Arial', 22)
        label = font.render("No scores to display", True, BLACK)
        screen.blit(label, (screen.get_width() // 2 - label.get_width() // 2, screen.get_height() // 2 - label.get_height() // 2 -50))
    else:
        values, counts = zip(*counter.items())
        values, counts = np.array(values), np.array(counts)

        # Sort values and counts in descending order
        sort_indices = np.argsort(values)[::-1]
        values, counts = values[sort_indices], counts[sort_indices]

        graph_width = 390
        graph_height = 170
        graph_surface = pygame.Surface((graph_width, graph_height))
        graph_surface.fill(WHITE)

        max_count = max(counts)

        num_bars = len(values)
        if num_bars > 0:
            max_bar_width = 30  
            bar_width = min(max_bar_width, graph_width / (num_bars * 1.5)) 
            bar_spacing = bar_width * 0.5 
        else:
            bar_width = 0
            bar_spacing = 0

        x_start = (graph_width - (num_bars * (bar_width + bar_spacing) - bar_spacing)) / 2
        y_start = graph_height - 50  

        font_size = 20 - (num_bars // 4) * 1  
        font = pygame.font.SysFont('Arial', font_size)

        score_font = pygame.font.SysFont('Arial', 18)

        for i, (value, count) in enumerate(zip(values, counts)):
            bar_height = (count / max_count) * (y_start - 20)
            x = x_start + i * (bar_width + bar_spacing)
            y = y_start - bar_height

            pygame.draw.rect(graph_surface, BLACK, (x, y, bar_width, bar_height))

            if num_bars >= 25:
                label = font.render(str(value), True, BLACK)
                label_rect = label.get_rect(center=(x + (bar_width - label.get_width()) / 2, y_start + 5))
                label_rotated = pygame.transform.rotate(label, -90)
                graph_surface.blit(label_rotated, (x + (bar_width - label_rotated.get_width()) / 2, y_start + 5))
            else:
                label = font.render(str(value), True, BLACK)
                graph_surface.blit(label, (x + (bar_width - label.get_width()) / 2, y_start + 5))

        score_label = score_font.render('Score', True, BLACK)
        graph_surface.blit(score_label, (graph_width // 2 - score_label.get_width() // 2, graph_height - 25))

        pygame.draw.rect(graph_surface, BLACK, (0, 0, graph_width, graph_height), 2)

        screen.blit(graph_surface, (screen.get_width() // 2 - graph_width // 2, screen.get_height() // 2 - graph_height // 2 - 50))



def roll_dice():
    global roll1, roll2, rolled, tiles_up, viable_moves, lost
    if not rolled:  
        roll1 = random.randint(1, 6)
        roll2 = random.randint(1, 6)
        rolled = True 
        viable_moves = [combo for i in range(1, len(tiles_up) + 1) for combo in combinations(tiles_up, i) if sum(combo) == roll1 + roll2]
        if not viable_moves:
            lost = True

def draw_homescreen():
    screen.blit(background, (0, 0))

    for button in home_screen_buttons:
        button.draw()
    
    title_text = title_font.render("Shut The Box", True, (0, 0, 0))
    title_rect = title_text.get_rect(center=(WIDTH / 2, HEIGHT / 4))  
    screen.blit(title_text, title_rect)

def draw_play_screen():
    screen.blit(background, (0, 0))

    if roll1 is not None and roll2 is not None:
        dice_rect1 = dice_images[roll1 - 1].get_rect(center=(WIDTH / 2 - 50, HEIGHT / 2 + 150))
        dice_rect2 = dice_images[roll2 - 1].get_rect(center=(WIDTH / 2 + 50, HEIGHT / 2 + 150))
        screen.blit(dice_images[roll1 - 1], dice_rect1)
        screen.blit(dice_images[roll2 - 1], dice_rect2)

    for button in play_buttons:
        if button.text == "Enter":
            if lost or len(tiles_up) == 0:
                button.text = "Play Again?"
                button.font = pygame.font.Font(FONT, PLAYAGAIN_FONT_SIZE)
            else:
                button.text = "Enter"
                button.font = pygame.font.Font(FONT, ENTER_FONT_SIZE)
        button.draw()

    draw_box()
    
    draw_game_status()

is_homescreen = True
running = True
clock = pygame.time.Clock()

while running:
    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if is_homescreen:
                current_buttons = home_screen_buttons
            elif play_screen:
                current_buttons = play_buttons
            elif simulating:
                current_buttons = simulate_selection_buttons + colored_simulate_selection_buttons
            for button in current_buttons:
                if button.is_clicked(event.pos):
                    button.on_click()
                    break  


    if is_homescreen:
        draw_homescreen()
    elif play_screen:
        draw_play_screen()
    elif simulating:
        draw_simulator()

    pygame.display.flip()
