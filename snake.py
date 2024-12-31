import pygame
import time
import random
import os
import json

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)
YELLOW = (255, 255, 102)
GREY = (200, 200, 200)
DARK_GREY = (50, 50, 50)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 102, 204)
ORANGE = (243, 112, 33)
WIDTH, HEIGHT = 800, 600
GAME_HEIGHT = HEIGHT 
SCOREBOARD_HEIGHT = 50 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
BLOCK_SIZE = 20
SPEED = 10
RECORD = 0
font_style = pygame.font.SysFont("bahnschrift", 30)
font_style_small = pygame.font.SysFont('Arial', 15)
title_font = pygame.font.SysFont("bahnschrift", 55)
CURRENT_DIFFICULTY = "Balanced"

def draw_background():
    for y in range(HEIGHT):
        color = tuple(
            DARK_GREY[i] + (GREY[i] - DARK_GREY[i]) * y // HEIGHT for i in range(3)
        )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

def draw_title_with_border(title_text, font, x_pos, y_pos, text_color, border_color, bg_color):
    title_width = font.render(title_text, True, text_color).get_width()
    title_height = font.render(title_text, True, text_color).get_height()
    pygame.draw.rect(screen, border_color, 
                     [x_pos - 8, y_pos - 8, title_width + 16, title_height + 16], 
                     border_radius=20)
    pygame.draw.rect(screen, bg_color, 
                     [x_pos - 5, y_pos - 5, title_width + 10, title_height + 10], 
                     border_radius=15)
    screen.blit(font.render(title_text, True, text_color), (x_pos, y_pos))

def draw_text_with_outline(text, font, color, outline_color, x, y):
    text_surface = font.render(text, True, color)
    outline_surfaces = [font.render(text, True, outline_color) for _ in range(8)]
    offsets = [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (-2, 2), (2, -2), (2, 2)]
    for offset, outline_surface in zip(offsets, outline_surfaces):
        screen.blit(outline_surface, (x + offset[0], y + offset[1]))
    screen.blit(text_surface, (x, y))

def draw_score_bar(score, records, CURRENT_DIFFICULTY):
    bar_height = 60
    pygame.draw.rect(screen, (50, 50, 50), [0, 0, WIDTH, bar_height])
    
    # Mostra il punteggio corrente
    draw_text_with_outline(f"Score: {score}", font_style, (255, 255, 255), (0, 0, 0), 15, 15)
    
    # Ottieni il record per la modalità corrente
    top_record = max(records.get(CURRENT_DIFFICULTY, [0]), default=0)
    
    # Mostra il record per la modalità corrente
    record_x = WIDTH - font_style.size(f"Record: {top_record}")[0] - 15
    draw_text_with_outline(f"Record: {top_record}", font_style, (255, 255, 255), (0, 0, 0), record_x, 15)
    
    # Mostra la modalità corrente
    difficulty_label = "Mode:"
    label_x = (WIDTH - font_style.size(difficulty_label + " " + CURRENT_DIFFICULTY)[0]) // 2
    draw_text_with_outline(difficulty_label, font_style, (255, 255, 255), (0, 0, 0), label_x, 15)
    
    if CURRENT_DIFFICULTY == "Relaxed":
        difficulty_color = (0, 255, 0)
    elif CURRENT_DIFFICULTY == "Balanced":
        difficulty_color = (255, 255, 0) 
    elif CURRENT_DIFFICULTY == "Extreme":
        difficulty_color = (255, 0, 0)
    else:
        difficulty_color = (255, 255, 255) 
    
    difficulty_x = label_x + font_style.size(difficulty_label)[0] + 5
    draw_text_with_outline(CURRENT_DIFFICULTY, font_style, difficulty_color, (0, 0, 0), difficulty_x, 15)
    
    # Mostra la velocità
    speed_text = f"Speed: {SPEED:.2f}"
    speed_x = 20
    speed_y = 40
    draw_text_with_outline(speed_text, font_style_small, (255, 255, 255), (0, 0, 0), speed_x, speed_y)

def read_records():
    try:
        with open("record.txt", "r") as file:
            records = json.load(file)
            return records
    except FileNotFoundError:
        return {
            "Relaxed": [],
            "Balanced": [],
            "Extreme": []
        }

def write_records(records):
    with open("record.txt", "w") as file:
        json.dump(records, file)

def update_records(records, mode, score):
    if mode not in records:
        records[mode] = []
    records[mode].append(score)
    records[mode] = sorted(records[mode], reverse=True)
    records[mode] = records[mode][:3]
    
    return records

def our_snake(block_size, snake_list):
    for i, x in enumerate(snake_list):
        color = (0, max(0, 255 - i * 5), 0)
        pygame.draw.rect(screen, (0, 0, 0), [x[0] - 2, x[1] - 2, block_size + 4, block_size + 4], border_radius=5)
        pygame.draw.rect(screen, color, [x[0], x[1], block_size, block_size], border_radius=5)

def is_valid_food_position(x, y, snake_list):
    for segment in snake_list:
        if segment == [x, y]:
            return False
    return True

def generate_food(snake_List):
    while True:
        food_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
        food_y = round(random.randrange(SCOREBOARD_HEIGHT, HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
        if is_valid_food_position(food_x, food_y, snake_List): 
            return food_x, food_y

def message(msg, color, position, font=font_style, bg_color=None):
    mesg = font.render(msg, True, color)
    x_pos = position[0] - mesg.get_width() // 2
    y_pos = position[1] - mesg.get_height() // 2
    if bg_color:
        pygame.draw.rect(screen, bg_color, [position[0] - 5, position[1] - 5, mesg.get_width() + 10, mesg.get_height() + 10])
    screen.blit(mesg, [x_pos, y_pos])

def gameMenu():
    menu = True
    selected_option = 0
    options = ["Play", "High Score", "Mode", "Resolution", "Quit"]
    while menu:
        draw_background()
        title_text = "Snake Game"
        title_x = (WIDTH - title_font.render(title_text, True, GREEN).get_width()) // 2
        title_y = HEIGHT // 5
        draw_title_with_border(title_text, title_font, title_x, title_y, WHITE, BLACK, DARK_GREY)
        for i, option in enumerate(options):
            color = WHITE if i != selected_option else BLACK
            option_text = font_style.render(option, True, color)
            option_x = WIDTH // 2 - option_text.get_width() // 2
            option_y = HEIGHT // 3 + i * 50
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (-2, 2), (2, -2), (2, 2)]:
                outline_text = font_style.render(option, True, BLACK)
                screen.blit(outline_text, (option_x + dx, option_y + dy))
            screen.blit(option_text, (option_x, option_y))
            if i == selected_option:
                border_color = BLACK
                bg_color = WHITE
                pygame.draw.rect(screen, border_color, 
                                 [option_x - 8, option_y - 8, option_text.get_width() + 16, option_text.get_height() + 16],
                                 border_radius=20)
                pygame.draw.rect(screen, bg_color, 
                                 [option_x - 5, option_y - 5, option_text.get_width() + 10, option_text.get_height() + 10],
                                 border_radius=15)
            else:
                bg_color = None
            screen.blit(option_text, (option_x, option_y))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if selected_option == 0:
                        menu = False
                        gameLoop()
                    elif selected_option == 1: 
                         showHighScore()
                    elif selected_option == 2:
                        changeDifficulty()
                    elif selected_option == 3:
                        changeResolution()
                    elif selected_option == 4:
                        pygame.quit()
                        quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, option in enumerate(options):
                    if WIDTH / 2 - 50 <= mouse_pos[0] <= WIDTH / 2 + 100 and HEIGHT / 3 + i * 50 <= mouse_pos[1] <= HEIGHT / 3 + i * 50 + 30:
                        if option == "Play":
                            menu = False
                            gameLoop()
                        elif option == "High Score":
                            showHighScore()
                        elif option == "Mode":
                            changeDifficulty()
                        elif option == "Resolution":
                            changeResolution()
                        elif option == "Quit":
                            pygame.quit()
                            quit()

def showHighScore():
    high_score_menu = True
    selected_option = 0
    options = ["Back"]
    records = read_records()
    while high_score_menu:
        draw_background()
        title_text = "High Score"
        title_x = (WIDTH - title_font.render(title_text, True, GREEN).get_width()) // 2
        title_y = HEIGHT // 5
        draw_title_with_border(title_text, title_font, title_x, title_y, WHITE, BLACK, DARK_GREY)
        column_width = WIDTH // 4
        start_x = (WIDTH - (3 * column_width)) // 2
        y_start = HEIGHT // 3
        record_color = (255, 255, 255)
        large_font_style = pygame.font.SysFont('Arial', 40)
        large_font_style_small = pygame.font.SysFont('Arial', 30) 
        for idx, (mode, scores) in enumerate(records.items()):
            column_x = start_x + idx * column_width
            mode_title_text = f"{mode}"
            draw_title_with_border(
                mode_title_text, 
                large_font_style, 
                column_x + (column_width - large_font_style.size(mode_title_text)[0]) // 2, 
                y_start+10, 
                BLACK, 
                BLACK, 
                WHITE
            )
            y_offset = y_start + 75 
            top_scores = scores[:3] if scores else ["No Records"]
            for i, score in enumerate(top_scores):
                record_text = f"{i + 1}. {score}"
                draw_text_with_outline(record_text, large_font_style_small, record_color, BLACK, 
                                       column_x + (column_width - large_font_style_small.size(record_text)[0]) // 2, y_offset)
                y_offset += 40
            
        for i, option in enumerate(options):
            color = WHITE if i != selected_option else BLACK
            option_text = font_style.render(option, True, color)
            option_x = WIDTH // 2 - option_text.get_width() // 2
            option_y = HEIGHT - 80 + i * 50
            if i == selected_option:
                border_color = BLACK
                bg_color = WHITE
                pygame.draw.rect(screen, border_color, [option_x - 8, option_y - 8, option_text.get_width() + 16, option_text.get_height() + 16], border_radius=20)
                pygame.draw.rect(screen, bg_color, [option_x - 5, option_y - 5, option_text.get_width() + 10, option_text.get_height() + 10], border_radius=15)
            screen.blit(option_text, (option_x, option_y))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:  
                    selected_option = (selected_option - 1) % len(options)
                elif event.key in [pygame.K_DOWN, pygame.K_s]: 
                    selected_option = (selected_option + 1) % len(options)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]: 
                    if selected_option == 0: 
                        high_score_menu = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, option in enumerate(options):
                    option_x = WIDTH // 2 - font_style.size(option)[0] // 2
                    option_y = HEIGHT // 2 + i * 50
                    option_width = font_style.size(option)[0]
                    option_height = font_style.size(option)[1]
                    if option_x <= mouse_pos[0] <= option_x + option_width and option_y <= mouse_pos[1] <= option_y + option_height:
                        if option == "Back":
                            high_score_menu = False

def changeDifficulty():
    difficulty_menu = True
    selected_option = 0
    options = ["Relaxed", "Balanced", "Extreme", "Back"]
    global SPEED, CURRENT_DIFFICULTY
    while difficulty_menu:
        draw_background()
        title_text = "Change Mode"
        title_x = (WIDTH - title_font.render(title_text, True, GREEN).get_width()) // 2
        title_y = HEIGHT // 5
        draw_title_with_border(title_text, title_font, title_x, title_y, WHITE, BLACK, DARK_GREY)
        for i, option in enumerate(options):
            color = WHITE if i != selected_option else BLACK
            option_text = font_style.render(option, True, color)
            option_x = WIDTH // 2 - option_text.get_width() // 2
            option_y = HEIGHT // 3 + i * 50
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (-2, 2), (2, -2), (2, 2)]:
                outline_text = font_style.render(option, True, BLACK)
                screen.blit(outline_text, (option_x + dx, option_y + dy))
            screen.blit(option_text, (option_x, option_y))
            if i == selected_option:
                border_color = BLACK
                bg_color = WHITE
                pygame.draw.rect(screen, border_color, 
                                 [option_x - 8, option_y - 8, option_text.get_width() + 16, option_text.get_height() + 16],
                                 border_radius=20)
                pygame.draw.rect(screen, bg_color, 
                                 [option_x - 5, option_y - 5, option_text.get_width() + 10, option_text.get_height() + 10],
                                 border_radius=15)
            screen.blit(option_text, (option_x, option_y))
        if CURRENT_DIFFICULTY == "Relaxed":
            indicator_option = 0
        elif CURRENT_DIFFICULTY == "Balanced":
            indicator_option = 1
        elif CURRENT_DIFFICULTY == "Extreme":
            indicator_option = 2
        else:
            indicator_option = None
        if indicator_option is not None:
            option_text = font_style.render(options[indicator_option], True, WHITE)
            option_x = WIDTH // 2 - option_text.get_width() // 2
            option_y = HEIGHT // 3 + indicator_option * 50
            indicator_radius = 6
            indicator_x = option_x - 30
            indicator_y = option_y + option_text.get_height() // 2 
            pygame.draw.circle(screen, BLACK, (indicator_x, indicator_y), indicator_radius + 3)
            pygame.draw.circle(screen, GREEN, (indicator_x, indicator_y), indicator_radius)

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:

                    if selected_option == 0:
                        SPEED = 8
                        CURRENT_DIFFICULTY = "Relaxed"
                        difficulty_menu = False
                    elif selected_option == 1:
                        SPEED = 13
                        CURRENT_DIFFICULTY = "Balanced"
                        difficulty_menu = False
                    elif selected_option == 2:
                        SPEED = 20
                        CURRENT_DIFFICULTY = "Extreme"
                        difficulty_menu = False
                    elif selected_option == 3:
                        difficulty_menu = False
                        gameMenu()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, option in enumerate(options):
                    option_width = font_style.size(option)[0]
                    option_height = font_style.size(option)[1]
                    option_x = WIDTH // 2 - option_width // 2
                    option_y = HEIGHT // 3 + i * 50
                    if option_x <= mouse_pos[0] <= option_x + option_width and option_y <= mouse_pos[1] <= option_y + option_height:
                        if option == "Relaxed":
                            SPEED = 8
                            CURRENT_DIFFICULTY = "Relaxed"
                            difficulty_menu = False
                        elif option == "Balanced":
                            SPEED = 13
                            CURRENT_DIFFICULTY = "Balanced"
                            difficulty_menu = False
                        elif option == "Extreme":
                            SPEED = 20
                            CURRENT_DIFFICULTY = "Extreme"
                            difficulty_menu = False
                        elif option == "Back":
                            difficulty_menu = False
                            gameMenu()

def update_speed(score, CURRENT_DIFFICULTY, initial_speed, last_updated_score):
    if CURRENT_DIFFICULTY == "Relaxed":
        speed_increment = 0.5
        threshold = 10
    elif CURRENT_DIFFICULTY == "Balanced":
        speed_increment = 0.5
        threshold = 5
    elif CURRENT_DIFFICULTY == "Extreme":
        speed_increment = 1
        threshold = 5
    else:
        speed_increment = 0.05
        threshold = 10
    if score - last_updated_score >= threshold:
        last_updated_score = score
        return initial_speed + (score // threshold) * speed_increment, last_updated_score
    return initial_speed + (last_updated_score // threshold) * speed_increment, last_updated_score


def changeResolution():
    global WIDTH, HEIGHT, screen
    resolutions = [
        (800, 600),
        (1024, 768),
        (1280, 720),
        (1920, 1080),
        'fullscreen' 
    ]
    options = ["800 x 600", "1024 x 768", "1280 x 720", "1920 x 1080", "Fullscreen", "Back"]
    selected_option = 0 
    is_fullscreen = False
    while True:
        draw_background()
        title_text = "Change Resolution"
        title_x = (WIDTH - title_font.render(title_text, True, GREEN).get_width()) // 2
        title_y = HEIGHT // 5
        draw_title_with_border(title_text, title_font, title_x, title_y, WHITE, BLACK, DARK_GREY)
        current_resolution = (WIDTH, HEIGHT)
        if is_fullscreen:
            current_index = 4
        elif current_resolution == (1920, 1080):
            current_index = 3  
        else:
            current_index = resolutions.index(current_resolution) if current_resolution in resolutions else 4
        for i, option in enumerate(options):
            is_selected = i == selected_option
            text_color = BLACK if is_selected else WHITE
            rendered_option = font_style.render(option, True, text_color)
            option_x = WIDTH // 2 - rendered_option.get_width() // 2
            option_y = HEIGHT // 3 + i * 50
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (-2, 2), (2, -2), (2, 2)]:
                outline_text = font_style.render(option, True, BLACK)
                screen.blit(outline_text, (option_x + dx, option_y + dy))
            if is_selected:
                pygame.draw.rect(screen, BLACK,
                                 [option_x - 8, option_y - 8, rendered_option.get_width() + 16, rendered_option.get_height() + 16],
                                 border_radius=15)
                pygame.draw.rect(screen, WHITE,
                                 [option_x - 5, option_y - 5, rendered_option.get_width() + 10, rendered_option.get_height() + 10],
                                 border_radius=15)
            if i == current_index:
                indicator_radius = 6
                indicator_x = option_x - 30
                indicator_y = option_y + rendered_option.get_height() // 2
                pygame.draw.circle(screen, BLACK, (indicator_x, indicator_y), indicator_radius + 3)
                pygame.draw.circle(screen, GREEN, (indicator_x, indicator_y), indicator_radius)
            screen.blit(rendered_option, (option_x, option_y))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if selected_option == 5:
                        return
                    elif selected_option == 4:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        WIDTH, HEIGHT = screen.get_size()
                        is_fullscreen = True  
                    else:
                        is_fullscreen = False
                        WIDTH, HEIGHT = resolutions[selected_option]  
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))
                elif event.key == pygame.K_ESCAPE:
                    return 
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, option in enumerate(options):
                    option_x = WIDTH // 2 - rendered_option.get_width() // 2
                    option_y = HEIGHT // 3 + i * 50
                    if option_x <= mouse_pos[0] <= option_x + rendered_option.get_width() and option_y <= mouse_pos[1] <= option_y + rendered_option.get_height():
                        if i == 5: 
                            return
                        elif i == 4:                
                            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                            WIDTH, HEIGHT = screen.get_size()
                            is_fullscreen = True 
                        else:
                            WIDTH, HEIGHT = resolutions[i] 
                            screen = pygame.display.set_mode((WIDTH, HEIGHT))
                            is_fullscreen = False

def pauseMenu(score, record):
    paused = True
    selected_option = 0
    options = ["Resume", "Restart", "Main Menu"]
    while paused:
        draw_background()
        draw_score_bar(score, record, CURRENT_DIFFICULTY)
        title_text = "Pause Menu"
        title_x = (WIDTH - title_font.render(title_text, True, GREEN).get_width()) // 2
        title_y = HEIGHT // 5
        draw_title_with_border(title_text, title_font, title_x, title_y, WHITE, BLACK, DARK_GREY)
        for i, option in enumerate(options):
            color = WHITE if i != selected_option else BLACK
            option_text = font_style.render(option, True, color)
            option_x = WIDTH // 2 - option_text.get_width() // 2
            option_y = HEIGHT // 3 + i * 50
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (-2, 2), (2, -2), (2, 2)]:
                outline_text = font_style.render(option, True, BLACK)
                screen.blit(outline_text, (option_x + dx, option_y + dy))
            screen.blit(option_text, (option_x, option_y))
            if i == selected_option:
                border_color = BLACK
                bg_color = WHITE
                pygame.draw.rect(screen, border_color, 
                                 [option_x - 8, option_y - 8, option_text.get_width() + 16, option_text.get_height() + 16],
                                 border_radius=20)
                pygame.draw.rect(screen, bg_color, 
                                 [option_x - 5, option_y - 5, option_text.get_width() + 10, option_text.get_height() + 10],
                                 border_radius=15)
            screen.blit(option_text, (option_x, option_y))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if selected_option == 0: 
                        paused = False
                    elif selected_option == 1:  
                        gameLoop()
                    elif selected_option == 2: 
                        gameMenu()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, option in enumerate(options):
                    option_width = font_style.size(option)[0]
                    option_height = font_style.size(option)[1]
                    option_x = WIDTH // 2 - option_width // 2
                    option_y = HEIGHT // 3 + i * 60
                    if option_x <= mouse_pos[0] <= option_x + option_width and option_y <= mouse_pos[1] <= option_y + option_height:
                        if option == "Resume":
                            paused = False
                        elif option == "Restart":
                            gameLoop()
                        elif option == "Main Menu":
                            gameMenu()
    return True

def gameOverMenu(score, record):
    game_close = True
    selected_option = 0
    options = ["Play Again", "Main Menu"]
    score_font = pygame.font.SysFont("bahnschrift", 30)
    records = read_records()
    record = max(records[CURRENT_DIFFICULTY], default=0)
    while game_close:
        draw_background()
        title_text = "Game Over"
        title_x = (WIDTH - title_font.render(title_text, True, GREEN).get_width()) // 2
        title_y = HEIGHT // 5
        draw_title_with_border(title_text, title_font, title_x, title_y, WHITE, BLACK, DARK_GREY)
        score_text = f"Your Score: {score}"
        score_width = score_font.render(score_text, True, GREEN).get_width()
        draw_text_with_outline(score_text, score_font, DARK_GREY, WHITE, 
                            (WIDTH - score_width) // 2, HEIGHT // 3)
        record_text = f"High Score: {record}"
        record_width = score_font.render(record_text, True, GREEN).get_width()
        draw_text_with_outline(record_text, score_font, DARK_GREY, WHITE, 
                            (WIDTH - record_width) // 2, HEIGHT // 3 + 40)
        for i, option in enumerate(options):
            color = WHITE if i != selected_option else BLACK
            option_text = font_style.render(option, True, color)
            option_x = WIDTH // 2 - option_text.get_width() // 2
            option_y = HEIGHT // 2 + i * 60
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (-2, 2), (2, -2), (2, 2)]:
                outline_text = font_style.render(option, True, BLACK)
                screen.blit(outline_text, (option_x + dx, option_y + dy))
            screen.blit(option_text, (option_x, option_y))
            if i == selected_option:
                border_color = BLACK
                bg_color = WHITE
                pygame.draw.rect(screen, border_color, 
                                 [option_x - 8, option_y - 8, option_text.get_width() + 16, option_text.get_height() + 16],
                                 border_radius=20)
                pygame.draw.rect(screen, bg_color, 
                                 [option_x - 5, option_y - 5, option_text.get_width() + 10, option_text.get_height() + 10],
                                 border_radius=15)
            screen.blit(option_text, (option_x, option_y))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:  
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:  
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE: 
                    if selected_option == 0: 
                        gameLoop()
                    elif selected_option == 1: 
                        gameMenu()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, option in enumerate(options):
                    if WIDTH / 2 - 60 <= mouse_pos[0] <= WIDTH / 2 + 150 and HEIGHT / 2 + i * 60 <= mouse_pos[1] <= HEIGHT / 2 + i * 60 + 30:
                        if option == "Play Again":
                            gameLoop()
                        elif option == "Main Menu":
                            gameMenu()
    return True

def gameLoop():
    global RECORD, CURRENT_DIFFICULTY, SPEED, last_updated_score
    game_over = False
    game_close = False
    x1 = WIDTH / 2
    y1 = HEIGHT / 2  
    x1_change = 0
    y1_change = 0
    direction = None
    snake_List = []
    Length_of_snake = 1
    foodx, foody = generate_food(snake_List)
    special_food_timer = 0
    special_foodx, special_foody = None, None
    score = 0
    last_updated_score = 0
    records = read_records()
    
    if CURRENT_DIFFICULTY == "Relaxed":
        initial_speed = 8 
    elif CURRENT_DIFFICULTY == "Balanced":
        initial_speed = 13 
    elif CURRENT_DIFFICULTY == "Extreme":
        initial_speed = 20
    else:
        initial_speed = 5  
    SPEED = initial_speed
    while not game_over:
        while game_close:
            game_over = not gameOverMenu(score, RECORD)
            if not game_over:
                break  
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pauseMenu(score, RECORD)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if direction != "RIGHT":
                        x1_change = -BLOCK_SIZE
                        y1_change = 0
                        direction = "LEFT"
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if direction != "LEFT":
                        x1_change = BLOCK_SIZE
                        y1_change = 0
                        direction = "RIGHT"
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    if direction != "DOWN":
                        y1_change = -BLOCK_SIZE
                        x1_change = 0
                        direction = "UP"
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if direction != "UP":
                        y1_change = BLOCK_SIZE
                        x1_change = 0
                        direction = "DOWN"
        SPEED = update_speed(score, CURRENT_DIFFICULTY, SPEED, last_updated_score)
        x1 += x1_change
        y1 += y1_change
        if x1 < 0:
            x1 = WIDTH - BLOCK_SIZE  
        elif x1 >= WIDTH:
            x1 = 0  
        if y1 < SCOREBOARD_HEIGHT: 
            y1 = HEIGHT - BLOCK_SIZE 
        elif y1 >= HEIGHT:
            y1 = SCOREBOARD_HEIGHT  
        x1 = (x1 // BLOCK_SIZE) * BLOCK_SIZE
        y1 = (y1 // BLOCK_SIZE) * BLOCK_SIZE
        for x in range(0, WIDTH, BLOCK_SIZE):
            pygame.draw.line(screen, (200, 200, 200), (x, SCOREBOARD_HEIGHT), (x, HEIGHT))
        for y in range(SCOREBOARD_HEIGHT, HEIGHT, BLOCK_SIZE):
            pygame.draw.line(screen, (200, 200, 200), (0, y), (WIDTH, y))
        draw_background()
        pygame.draw.circle(screen, BLACK, (foodx + BLOCK_SIZE // 2, foody + BLOCK_SIZE // 2), BLOCK_SIZE // 2)
        pygame.draw.circle(screen, WHITE, (foodx + BLOCK_SIZE // 2, foody + BLOCK_SIZE // 2), BLOCK_SIZE // 2 - 2)
        if special_food_timer > 0:
            pygame.draw.circle(screen, BLACK, (special_foodx + BLOCK_SIZE // 2, special_foody + BLOCK_SIZE // 2), BLOCK_SIZE // 2)
            pygame.draw.circle(screen, DARK_GREY, (special_foodx + BLOCK_SIZE // 2, special_foody + BLOCK_SIZE // 2), BLOCK_SIZE // 2 -2)
            special_food_timer -= 1
        elif special_food_timer == 0 and random.randint(1, 100) == 1:
            special_foodx = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            special_foody = round(random.randrange(0, HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            special_food_timer = 100
        snake_Head = [x1, y1]
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]
        for block in snake_List[:-1]:
            if block == snake_Head:
                game_close = True
        our_snake(BLOCK_SIZE, snake_List)
        SPEED, last_updated_score = update_speed(score, CURRENT_DIFFICULTY, initial_speed, last_updated_score)
        draw_score_bar(score, RECORD, CURRENT_DIFFICULTY)
        if x1 == foodx and y1 == foody:
            foodx, foody = generate_food(snake_List)
            Length_of_snake += 1
            score += 1
        if special_food_timer > 0 and x1 == special_foodx and y1 == special_foody:
            special_foodx, special_foody = None, None
            special_food_timer = 0
            Length_of_snake += 5
            score += 5
        if score > max(records[CURRENT_DIFFICULTY], default=0):
            records = update_records(records, CURRENT_DIFFICULTY, score)
        write_records(records)
        pygame.display.update()
        clock.tick(SPEED)
    pygame.quit()
    quit()
RECORD = read_records()
gameMenu()
