import pygame
import random
import sys

GRID_SIZE = 4
TILE_DIMENSION = 100
GAP_SIZE = 10
WINDOW_DIMENSION = GRID_SIZE * (TILE_DIMENSION + GAP_SIZE) + GAP_SIZE

COLOR_MAP = {
    0: (240, 240, 240),
    2: (255, 255, 200),
    4: (255, 225, 150),
    8: (255, 180, 100),
    16: (255, 140, 70),
    32: (255, 100, 50),
    64: (255, 60, 30),
    128: (240, 220, 110),
    256: (240, 210, 90),
    512: (240, 200, 70),
    1024: (240, 190, 50),
    2048: (240, 180, 30)
}

pygame.init()
screen = pygame.display.set_mode((WINDOW_DIMENSION, WINDOW_DIMENSION))
pygame.display.set_caption("2048 arutkuz")
font = pygame.font.Font(None, 48)
button_font = pygame.font.Font(None, 36)


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
    screen.fill((187, 173, 160))
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            value = board[row][col]
            color = COLOR_MAP.get(value, (60, 58, 50))
            rect = pygame.Rect(
                col * (TILE_DIMENSION + GAP_SIZE) + GAP_SIZE,
                row * (TILE_DIMENSION + GAP_SIZE) + GAP_SIZE,
                TILE_DIMENSION,
                TILE_DIMENSION
            )
            pygame.draw.rect(screen, color, rect, border_radius=10)
            if value:
                text_surface = font.render(str(value), True, (0, 0, 0))
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


def draw_button(text, x, y, width, height, color, hover_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, hover_color, (x, y, width, height), border_radius=10)
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(screen, color, (x, y, width, height), border_radius=10)
    text_surface = button_font.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(x + width / 2, y + height / 2))
    screen.blit(text_surface, text_rect)
    return False


def main_menu():
    while True:
        screen.fill((187, 173, 160))
        title_surface = font.render("2048 ArutKuz", True, (0, 0, 0))
        title_rect = title_surface.get_rect(center=(WINDOW_DIMENSION / 2, WINDOW_DIMENSION / 4))
        screen.blit(title_surface, title_rect)

        if draw_button("Начать", WINDOW_DIMENSION / 2 - 75, WINDOW_DIMENSION / 2 - 50, 150, 50, (240, 240, 240),
                       (200, 200, 200)):
            return "start"
        if draw_button("Настройки", WINDOW_DIMENSION / 2 - 75, WINDOW_DIMENSION / 2 + 20, 150, 50, (240, 240, 240),
                       (200, 200, 200)):
            return "settings"
        if draw_button("Выйти", WINDOW_DIMENSION / 2 - 75, WINDOW_DIMENSION / 2 + 90, 150, 50, (240, 240, 240),
                       (200, 200, 200)):
            return "exit"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()


def game_over_screen():
    while True:
        screen.fill((187, 173, 160))
        title_surface = font.render("Игра окончена!", True, (0, 0, 0))
        title_rect = title_surface.get_rect(center=(WINDOW_DIMENSION / 2, WINDOW_DIMENSION / 4))
        screen.blit(title_surface, title_rect)

        if draw_button("Начать заново", WINDOW_DIMENSION / 2 - 100, WINDOW_DIMENSION / 2 - 80, 200, 50, (240, 240, 240),
                       (200, 200, 200)):
            return "restart"
        if draw_button("Меню", WINDOW_DIMENSION / 2 - 100, WINDOW_DIMENSION / 2 - 20, 200, 50, (240, 240, 240),
                       (200, 200, 200)):
            return "menu"
        if draw_button("Выйти", WINDOW_DIMENSION / 2 - 100, WINDOW_DIMENSION / 2 + 40, 200, 50, (240, 240, 240),
                       (200, 200, 200)):
            return "exit"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()


def main():
    while True:
        menu_action = main_menu()
        if menu_action == "start":
            board = initialize_game()
            game_active = True
            while game_active:
                display_board(board)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_active = False
                    elif event.type == pygame.KEYDOWN:
                        previous_board = [row[:] for row in board]
                        if event.key in (pygame.K_LEFT, pygame.K_a):
                            board = move_left(board)
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            board = move_right(board)
                        elif event.key in (pygame.K_UP, pygame.K_w):
                            board = move_up(board)
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            board = move_down(board)
                        if board != previous_board:
                            spawn_tile(board)
                        if is_game_over(board):
                            display_board(board)
                            pygame.time.delay(500)  # Задержка перед показом экрана окончания
                            game_over_action = game_over_screen()
                            if game_over_action == "restart":
                                board = initialize_game()
                            elif game_over_action == "menu":
                                game_active = False  # Выход из игрового цикла
                            else:
                                pygame.quit()
                                sys.exit()
            if game_over_action == "exit":
                pygame.quit()
                sys.exit()
        elif menu_action == "settings":
            print("Настройки будут позже")
        elif menu_action == "exit":
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    main()
