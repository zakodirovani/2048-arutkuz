import pygame
import random
import sys

GRID_SIZE = 4
TILE_DIMENSION = 100
GAP_SIZE = 10
WINDOW_DIMENSION = GRID_SIZE * (TILE_DIMENSION + GAP_SIZE) + GAP_SIZE

THEMES = {
     "Классическая": {
        "background": (187, 173, 160),
        "colors": {
            0: (205, 193, 180),
            2: (238, 228, 218),
            4: (237, 224, 200),
            8: (242, 177, 121),
            16: (245, 149, 99),
            32: (246, 124, 95),
            64: (246, 94, 59),
            128: (237, 207, 114),
            256: (237, 204, 97),
            512: (237, 200, 80),
            1024: (237, 197, 63),
            2048: (237, 194, 46)
        }
    },
    "Тёмная": {
        "background": (30, 30, 40),
        "colors": {
            0: (40, 40, 50),
            2: (60, 60, 70),
            4: (80, 80, 90),
            8: (100, 100, 110),
            16: (120, 80, 100),
            32: (140, 70, 90),
            64: (160, 60, 80),
            128: (180, 150, 140),
            256: (190, 130, 120),
            512: (200, 110, 100),
            1024: (210, 90, 80),
            2048: (220, 70, 60)
        }
    },
    "Неоновая": {
        "background": (20, 20, 20),
        "colors": {
            0: (30, 30, 30),
            2: (0, 255, 128),
            4: (0, 204, 255),
            8: (255, 0, 255),
            16: (255, 128, 0),
            32: (255, 0, 0),
            64: (128, 0, 255),
            128: (0, 255, 255),
            256: (255, 255, 0),
            512: (128, 255, 0),
            1024: (255, 0, 128),
            2048: (0, 128, 255)
        }
    }
}

current_theme = "Классическая"

pygame.init()
screen = pygame.display.set_mode((WINDOW_DIMENSION, WINDOW_DIMENSION))
pygame.display.set_caption("2048 arutkuz")
font = pygame.font.Font(None, 48)
button_font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

def draw_button(text, x, y, width, height, color, hover_color, events):
    rect = pygame.Rect(x, y, width, height)
    mouse_pos = pygame.mouse.get_pos()
    mouse_over = rect.collidepoint(mouse_pos)
    clicked = False
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and mouse_over:
            clicked = True
    pygame.draw.rect(screen, hover_color if mouse_over else color, rect, border_radius=10)
    text_surface = button_font.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)
    return clicked

def get_text_color():
    return (0, 0, 0) if current_theme == "Классическая" else (255, 255, 255)

def settings_screen():
    global current_theme
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(THEMES[current_theme]["background"])
        title_surface = font.render("Настройки", True, get_text_color())
        title_rect = title_surface.get_rect(center=(WINDOW_DIMENSION / 2, WINDOW_DIMENSION / 6))
        screen.blit(title_surface, title_rect)
        y_position = WINDOW_DIMENSION // 4
        for theme_name in THEMES:
            if draw_button(theme_name, WINDOW_DIMENSION // 2 - 100, y_position, 200, 40, (220, 220, 220), (200, 200, 200), events):
                current_theme = theme_name
            y_position += 60
        if draw_button("Назад", WINDOW_DIMENSION // 2 - 50, WINDOW_DIMENSION - 100, 100, 40, (220, 220, 220), (200, 200, 200), events):
            return
        pygame.display.flip()
        clock.tick(60)

def initialize_game():
    board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    spawn_tile(board)
    spawn_tile(board)
    return board

def spawn_tile(board):
    empty_positions = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if board[r][c] == 0]
    if empty_positions:
        row, col = random.choice(empty_positions)
        board[row][col] = 2 if random.random() < 0.9 else 4

def display_board(board):
    theme = THEMES[current_theme]
    screen.fill(theme["background"])
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            value = board[row][col]
            color = theme["colors"].get(value, (60, 58, 50))
            rect = pygame.Rect(col * (TILE_DIMENSION + GAP_SIZE) + GAP_SIZE, row * (TILE_DIMENSION + GAP_SIZE) + GAP_SIZE, TILE_DIMENSION, TILE_DIMENSION)
            pygame.draw.rect(screen, color, rect, border_radius=10)
            if value:
                if current_theme == "Классическая":
                    text_color = (30, 30, 30) if value < 8 else (255, 255, 255)
                else:
                    text_color = (255, 255, 255)
                text_surface = font.render(str(value), True, text_color)
                text_rect = text_surface.get_rect(center=rect.center)
                screen.blit(text_surface, text_rect)
    pygame.display.flip()

def compress_and_merge(line):
    new_line = [num for num in line if num != 0]
    merged_line = []
    skip = False
    for i in range(len(new_line)):
        if skip:
            skip = False
            continue
        if i < len(new_line) - 1 and new_line[i] == new_line[i + 1]:
            merged_line.append(new_line[i] * 2)
            skip = True
        else:
            merged_line.append(new_line[i])
    return merged_line + [0] * (GRID_SIZE - len(merged_line))

def move_left(board):
    return [compress_and_merge(row) for row in board]

def move_right(board):
    return [list(reversed(compress_and_merge(list(reversed(row))))) for row in board]

def move_up(board):
    transposed = list(map(list, zip(*board)))
    return list(map(list, zip(*move_left(transposed))))

def move_down(board):
    transposed = list(map(list, zip(*board)))
    return list(map(list, zip(*move_right(transposed))))

def is_game_over(board):
    if any(0 in row for row in board):
        return False
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 1):
            if board[r][c] == board[r][c + 1]:
                return False
    for c in range(GRID_SIZE):
        for r in range(GRID_SIZE - 1):
            if board[r][c] == board[r + 1][c]:
                return False
    return True

def main_menu():
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(THEMES[current_theme]["background"])
        title_surface = font.render("2048 ArutKuz", True, get_text_color())
        title_rect = title_surface.get_rect(center=(WINDOW_DIMENSION / 2, WINDOW_DIMENSION / 4))
        screen.blit(title_surface, title_rect)
        if draw_button("Начать", WINDOW_DIMENSION / 2 - 75, WINDOW_DIMENSION / 2 - 50, 150, 50, (240, 240, 240), (200, 200, 200), events):
            return "start"
        if draw_button("Настройки", WINDOW_DIMENSION / 2 - 75, WINDOW_DIMENSION / 2 + 20, 150, 50, (240, 240, 240), (200, 200, 200), events):
            return "settings"
        if draw_button("Выйти", WINDOW_DIMENSION / 2 - 75, WINDOW_DIMENSION / 2 + 90, 150, 50, (240, 240, 240), (200, 200, 200), events):
            return "exit"
        pygame.display.flip()
        clock.tick(60)

def game_over_screen():
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(THEMES[current_theme]["background"])
        title_surface = font.render("Игра окончена!", True, get_text_color())
        title_rect = title_surface.get_rect(center=(WINDOW_DIMENSION / 2, WINDOW_DIMENSION / 4))
        screen.blit(title_surface, title_rect)
        if draw_button("Начать заново", WINDOW_DIMENSION // 2 - 100, WINDOW_DIMENSION // 2 - 80, 200, 50, (240, 240, 240), (200, 200, 200), events):
            return "restart"
        if draw_button("Меню", WINDOW_DIMENSION // 2 - 100, WINDOW_DIMENSION // 2 - 20, 200, 50, (240, 240, 240), (200, 200, 200), events):
            return "menu"
        if draw_button("Выйти", WINDOW_DIMENSION // 2 - 100, WINDOW_DIMENSION // 2 + 40, 200, 50, (240, 240, 240), (200, 200, 200), events):
            return "exit"
        pygame.display.flip()
        clock.tick(60)

def main():
    global current_theme
    running = True
    while running:
        menu_action = main_menu()
        if menu_action == "start":
            board = initialize_game()
            game_active = True
            while game_active:
                display_board(board)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        game_active = False
                    elif event.type == pygame.KEYDOWN:
                        old_board = [row[:] for row in board]
                        if event.key in (pygame.K_LEFT, pygame.K_a):
                            board = move_left(board)
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            board = move_right(board)
                        elif event.key in (pygame.K_UP, pygame.K_w):
                            board = move_up(board)
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            board = move_down(board)
                        if board != old_board:
                            spawn_tile(board)
                        if is_game_over(board):
                            game_over_action = game_over_screen()
                            if game_over_action == "restart":
                                board = initialize_game()
                            elif game_over_action == "menu":
                                game_active = False
                            elif game_over_action == "exit":
                                pygame.quit()
                                sys.exit()

        elif menu_action == "settings":
            settings_screen()
        elif menu_action == "exit":
            running = False
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
