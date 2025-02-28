import pygame
import random
import sys
import sqlite3

GRID_SIZE = 4
TILE_DIMENSION = 100
GAP_SIZE = 10
HEADER_HEIGHT = 120
BOARD_SIZE = GRID_SIZE * (TILE_DIMENSION + GAP_SIZE) + GAP_SIZE
WINDOW_WIDTH = BOARD_SIZE
WINDOW_HEIGHT = HEADER_HEIGHT + BOARD_SIZE

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


class DatabaseManager:
    def __init__(self, db_path="highscore.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS highscore (score INTEGER)")
        cursor.execute("SELECT score FROM highscore")
        row = cursor.fetchone()
        if row is None:
            cursor.execute("INSERT INTO highscore (score) VALUES (0)")
            self.conn.commit()
            self.high_score = 0
        else:
            self.high_score = row[0]

    def update_high_score(self, new_score):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE highscore SET score = ?", (new_score,))
        self.conn.commit()
        self.high_score = new_score

    def close(self):
        self.conn.close()


class Board:
    def __init__(self):
        self.grid_size = GRID_SIZE
        self.score = 0
        self.board = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.spawn_tile()
        self.spawn_tile()

    def spawn_tile(self):
        empty_positions = [(r, c) for r in range(self.grid_size)
                           for c in range(self.grid_size) if self.board[r][c] == 0]
        if empty_positions:
            row, col = random.choice(empty_positions)
            self.board[row][col] = 2 if random.random() < 0.9 else 4

    def compress_and_merge(self, line):
        new_line = [num for num in line if num != 0]
        merged_line = []
        skip = False
        for i in range(len(new_line)):
            if skip:
                skip = False
                continue
            if i < len(new_line) - 1 and new_line[i] == new_line[i + 1]:
                merged_value = new_line[i] * 2
                merged_line.append(merged_value)
                self.score += merged_value
                skip = True
            else:
                merged_line.append(new_line[i])
        merged_line += [0] * (self.grid_size - len(merged_line))
        return merged_line

    def move_left(self):
        new_board = []
        for row in self.board:
            new_board.append(self.compress_and_merge(row))
        self.board = new_board

    def move_right(self):
        new_board = []
        for row in self.board:
            reversed_row = list(reversed(row))
            merged = self.compress_and_merge(reversed_row)
            new_board.append(list(reversed(merged)))
        self.board = new_board

    def move_up(self):
        self.board = self._transpose(self.board)
        self.move_left()
        self.board = self._transpose(self.board)

    def move_down(self):
        self.board = self._transpose(self.board)
        self.move_right()
        self.board = self._transpose(self.board)

    def is_game_over(self):

        if any(0 in row for row in self.board):
            return False


        for r in range(self.grid_size):
            for c in range(self.grid_size - 1):
                if self.board[r][c] == self.board[r][c + 1]:
                    return False


        for c in range(self.grid_size):
            for r in range(self.grid_size - 1):
                if self.board[r][c] == self.board[r + 1][c]:
                    return False


        return True

    def _transpose(self, board):
        return [list(row) for row in zip(*board)]


class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, font):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.font = font

    def draw(self, screen, events):
        mouse_pos = pygame.mouse.get_pos()
        mouse_over = self.rect.collidepoint(mouse_pos)
        clicked = False
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and mouse_over:
                clicked = True
        current_color = self.hover_color if mouse_over else self.color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=10)
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        return clicked


class ThemeManager:
    def __init__(self):
        self.theme_name = "Классическая"

    def current_theme_settings(self):
        return THEMES[self.theme_name]

    def get_text_color(self):
        if self.theme_name == "Классическая":
            return (0, 0, 0)
        else:
            return (255, 255, 255)


class UI:
    def __init__(self, screen, theme_manager, font, button_font):
        self.screen = screen
        self.theme_manager = theme_manager
        self.font = font
        self.button_font = button_font

    def draw_header(self, score, high_score, events):
        text_color = self.theme_manager.get_text_color()
        score_text = self.button_font.render(f"Счет: {score}", True, text_color)
        record_text = self.button_font.render(f"Рекорд: {high_score}", True, text_color)
        self.screen.blit(score_text, (20, 20))
        self.screen.blit(record_text, (20, 60))
        restart_button = Button("Заново", WINDOW_WIDTH - 230, 30, 100, 40, (220, 220, 220), (200, 200, 200),
                                self.button_font)
        exit_button = Button("Выйти", WINDOW_WIDTH - 110, 30, 100, 40, (220, 220, 220), (200, 200, 200),
                             self.button_font)
        restart_clicked = restart_button.draw(self.screen, events)
        exit_clicked = exit_button.draw(self.screen, events)
        return restart_clicked, exit_clicked

    def draw_board(self, board):
        theme = self.theme_manager.current_theme_settings()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                value = board[r][c]
                color = theme["colors"].get(value, (60, 58, 50))
                rect = pygame.Rect(
                    c * (TILE_DIMENSION + GAP_SIZE) + GAP_SIZE,
                    HEADER_HEIGHT + r * (TILE_DIMENSION + GAP_SIZE) + GAP_SIZE,
                    TILE_DIMENSION,
                    TILE_DIMENSION
                )
                pygame.draw.rect(self.screen, color, rect, border_radius=10)
                if value:
                    text_color = (30, 30, 30) if value < 8 and self.theme_manager.theme_name == "Классическая" else (
                        255, 255, 255)
                    text_surface = self.font.render(str(value), True, text_color)
                    text_rect = text_surface.get_rect(center=rect.center)
                    self.screen.blit(text_surface, text_rect)\



class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("2048 ArutKuz")
        self.font = pygame.font.Font(None, 48)
        self.button_font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        self.db_manager = DatabaseManager()
        self.theme_manager = ThemeManager()
        self.ui = UI(self.screen, self.theme_manager, self.font, self.button_font)
        self.running = True

    def game_over_screen(self, score):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill(self.theme_manager.current_theme_settings()["background"])
            title_surface = self.font.render("Игра окончена", True, self.theme_manager.get_text_color())
            title_rect = title_surface.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4))
            self.screen.blit(title_surface, title_rect)

            score_text = self.font.render(f"Ваш счёт: {score}", True, self.theme_manager.get_text_color())
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
            self.screen.blit(score_text, score_rect)

            restart_button = Button("Заново", WINDOW_WIDTH / 2 - 75, WINDOW_HEIGHT / 2 + 40, 150, 50, (240, 240, 240),
                                    (200, 200, 200), self.button_font)
            exit_button = Button("Выйти", WINDOW_WIDTH / 2 - 75, WINDOW_HEIGHT / 2 + 100, 150, 50, (240, 240, 240),
                                 (200, 200, 200), self.button_font)
            menu_button = Button("Меню", WINDOW_WIDTH / 2 - 75, WINDOW_HEIGHT / 2 + 160, 150, 50, (240, 240, 240),
                                 (200, 200, 200), self.button_font)

            if restart_button.draw(self.screen, events):
                return "restart"
            if exit_button.draw(self.screen, events):
                return "exit"
            if menu_button.draw(self.screen, events):
                return "menu"

            pygame.display.flip()
            self.clock.tick(60)

    def settings_screen_v2(self):
        global current_theme
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill(THEMES[self.theme_manager.theme_name]["background"])
            title_surface = self.font.render("Настройки", True, self.theme_manager.get_text_color())
            title_rect = title_surface.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 6))
            self.screen.blit(title_surface, title_rect)

            y_position = WINDOW_HEIGHT // 4
            if Button("Тема", WINDOW_WIDTH // 2 - 100, y_position, 200, 40, (220, 220, 220), (200, 200, 200),
                      self.button_font).draw(self.screen, events):
                self.theme_settings_screen()
            y_position += 60
            if Button("Рекорд", WINDOW_WIDTH // 2 - 100, y_position, 200, 40, (220, 220, 220), (200, 200, 200),
                      self.button_font).draw(self.screen, events):
                self.record_settings_screen()
            y_position += 60
            if Button("Назад", WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT - 100, 100, 40, (220, 220, 220), (200, 200, 200),
                      self.button_font).draw(self.screen, events):
                return
            pygame.display.flip()
            self.clock.tick(60)

    def theme_settings_screen(self):
        global current_theme
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.screen.fill(THEMES[self.theme_manager.theme_name]["background"])
            title_surface = self.font.render("Выбор темы", True, self.theme_manager.get_text_color())
            title_rect = title_surface.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 6))
            self.screen.blit(title_surface, title_rect)

            y_position = WINDOW_HEIGHT // 4
            for theme_name in THEMES:
                if Button(theme_name, WINDOW_WIDTH // 2 - 100, y_position, 200, 40, (220, 220, 220), (200, 200, 200),
                          self.button_font).draw(self.screen, events):
                    self.theme_manager.theme_name = theme_name
                y_position += 60

            if Button("Назад", WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT - 100, 100, 40, (220, 220, 220), (200, 200, 200),
                      self.button_font).draw(self.screen, events):
                return
            pygame.display.flip()
            self.clock.tick(60)

    def record_settings_screen(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill(THEMES[self.theme_manager.theme_name]["background"])
            title_surface = self.font.render("Рекорд", True, self.theme_manager.get_text_color())
            title_rect = title_surface.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 6))
            self.screen.blit(title_surface, title_rect)

            record_text = self.font.render(f"Рекорд: {self.db_manager.high_score}", True,
                                           self.theme_manager.get_text_color())
            record_rect = record_text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT // 2))
            self.screen.blit(record_text, record_rect)

            if Button("Сбросить", WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 40, 200, 40, (220, 220, 220),
                      (200, 200, 200), self.button_font).draw(self.screen, events):
                self.db_manager.update_high_score(0)
                self.db_manager.high_score = 0  

            if Button("Назад", WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT - 100, 100, 40, (220, 220, 220), (200, 200, 200),
                      self.button_font).draw(self.screen, events):
                return

            pygame.display.flip()
            self.clock.tick(60)

    def main_menu(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill(self.theme_manager.current_theme_settings()["background"])
            title_surface = self.font.render("2048 ArutKuz", True, self.theme_manager.get_text_color())
            title_rect = title_surface.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4))
            self.screen.blit(title_surface, title_rect)

            start_button = Button("Начать", WINDOW_WIDTH / 2 - 75, WINDOW_HEIGHT / 2 - 50, 150, 50, (240, 240, 240),
                                  (200, 200, 200), self.button_font)
            settings_button = Button("Настройки", WINDOW_WIDTH / 2 - 75, WINDOW_HEIGHT / 2 + 20, 150, 50,
                                     (240, 240, 240),
                                     (200, 200, 200), self.button_font)
            exit_button = Button("Выйти", WINDOW_WIDTH / 2 - 75, WINDOW_HEIGHT / 2 + 90, 150, 50, (240, 240, 240),
                                 (200, 200, 200), self.button_font)

            if start_button.draw(self.screen, events):
                return "start"
            if settings_button.draw(self.screen, events):
                return "settings"
            if exit_button.draw(self.screen, events):
                return "exit"

            pygame.display.flip()
            self.clock.tick(60)

    def run(self):
        while self.running:
            action = self.main_menu()
            if action == "start":
                self.run_game()
            elif action == "settings":
                self.settings_screen_v2()
            elif action == "exit":
                self.running = False
        self.db_manager.close()
        pygame.quit()
        sys.exit()

    def run_game(self):
        board_obj = Board()
        game_active = True
        while game_active:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    game_active = False
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    old_board = [row[:] for row in board_obj.board]
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        board_obj.move_left()
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        board_obj.move_right()
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        board_obj.move_up()
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        board_obj.move_down()
                    if board_obj.board != old_board:
                        board_obj.spawn_tile()
                    if board_obj.is_game_over():
                        if board_obj.score > self.db_manager.high_score:
                            self.db_manager.update_high_score(board_obj.score)
                        game_active = False

            self.screen.fill(self.theme_manager.current_theme_settings()["background"])
            header_buttons = self.ui.draw_header(board_obj.score, self.db_manager.high_score, events)
            self.ui.draw_board(board_obj.board)
            pygame.display.flip()
            if header_buttons[0]:
                board_obj = Board()
            if header_buttons[1]:
                game_active = False
            self.clock.tick(60)

        result = self.game_over_screen(board_obj.score)

        if result == "restart":
            self.run_game()
        elif result == "exit":
            self.running = False
            pygame.quit()
            sys.exit()
        elif result == "menu":
            self.main_menu()


if __name__ == "__main__":
    game = Game()
    game.run()
