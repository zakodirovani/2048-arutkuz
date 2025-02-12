import pygame
import random
import sys

SIZE = 4
CELL_SIZE = 100
MARGIN = 10
WIDTH = HEIGHT = SIZE * (CELL_SIZE + MARGIN) + MARGIN
COLORS = {
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

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048 Arutkuz")
font = pygame.font.Font(None, 50)


def init_board():
    board = [[0] * SIZE for _ in range(SIZE)]
    add_new_tile(board)
    add_new_tile(board)
    return board


def add_new_tile(board):
    empty_cells = [(r, c) for r in range(SIZE) for c in range(SIZE) if board[r][c] == 0]
    if empty_cells:
        r, c = random.choice(empty_cells)
        board[r][c] = 2 if random.random() < 0.9 else 4


def draw_board(board):
    screen.fill((187, 173, 160))
    for r in range(SIZE):
        for c in range(SIZE):
            value = board[r][c]
            color = COLORS.get(value, (60, 58, 50))
            rect = pygame.Rect(
                c * (CELL_SIZE + MARGIN) + MARGIN,
                r * (CELL_SIZE + MARGIN) + MARGIN,
                CELL_SIZE,
                CELL_SIZE
            )
            pygame.draw.rect(screen, color, rect, border_radius=8)
            if value:
                text = font.render(str(value), True, (0, 0, 0))
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
    pygame.display.flip()


def compress(row):
    new_row = [num for num in row if num != 0]
    new_row += [0] * (SIZE - len(new_row))
    return new_row


def merge(row):
    for i in range(SIZE - 1):
        if row[i] == row[i + 1] and row[i] != 0:
            row[i] *= 2
            row[i + 1] = 0
    return row


def move_left(board):
    new_board = []
    for row in board:
        compressed = compress(row)
        merged = merge(compressed)
        new_row = compress(merged)
        new_board.append(new_row)
    return new_board


def move_right(board):
    return [list(reversed(row)) for row in move_left([list(reversed(row)) for row in board])]


def move_up(board):
    transposed = list(map(list, zip(*board)))
    new_board = move_left(transposed)
    return list(map(list, zip(*new_board)))


def move_down(board):
    transposed = list(map(list, zip(*board)))
    new_board = move_right(transposed)
    return list(map(list, zip(*new_board)))


def is_game_over(board):
    if any(0 in row for row in board):
        return False
    for r in range(SIZE):
        for c in range(SIZE - 1):
            if board[r][c] == board[r][c + 1]:
                return False
    for c in range(SIZE):
        for r in range(SIZE - 1):
            if board[r][c] == board[r + 1][c]:
                return False
    return True


def main():
    board = init_board()
    running = True
    while running:
        draw_board(board)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
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
                    add_new_tile(board)
                if is_game_over(board):
                    print("Game Over!")
                    running = False
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
