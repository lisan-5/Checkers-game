import pygame
import sys
import random
import time
from enum import Enum

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
CELL_SIZE = 80
BOARD_WIDTH = (CELL_SIZE * 8) + 200
BOARD_HEIGHT = CELL_SIZE * 8
QORKI_SIZE = 30
MAX_MOVES = 12
MAX_CAPTURES = 12

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
LIGHTGRAY = (211, 211, 211)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
GOLD = (255, 215, 0)
DARKPURPLE = (48, 25, 52)

# Enums
class CellType(Enum):
    EMPTY = 0
    PLAYER1_QORKI = 1
    PLAYER2_QORKI = 2
    PLAYER1_KING_QORKI = 3
    PLAYER2_KING_QORKI = 4

class Difficulty(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2

# Load images
CROWN_IMG = pygame.image.load('crown.png')
CROWN_IMG = pygame.transform.scale(CROWN_IMG, (QORKI_SIZE, QORKI_SIZE))

# Load sounds
MOVE_SOUND = pygame.mixer.Sound('move.wav')
CAPTURE_SOUND = pygame.mixer.Sound('capture.wav')
KING_SOUND = pygame.mixer.Sound('king.wav')

# Load music
pygame.mixer.music.load('background_music.mp3')

class Cell:
    def __init__(self, row, col, cell_type):
        self.row = row
        self.col = col
        self.cell_type = cell_type

class Board:
    def __init__(self):
        self.cells = [[Cell(row, col, CellType.EMPTY) for col in range(8)] for row in range(8)]

class Player:
    def __init__(self, name):
        self.name = name
        self.captured_pieces = 0
        self.moves_made = 0
        self.time_played = 0

class Game:
    def __init__(self):
        self.board = Board()
        self.player1 = Player("Player 1")
        self.player2 = Player("Player 2")
        self.is_player1_turn = True
        self.piece_selected = False
        self.selected_row = -1
        self.selected_col = -1
        self.save_on_exit = False
        self.difficulty = Difficulty.MEDIUM
        self.move_history = []
        self.last_move = None
        self.start_time = time.time()
        self.paused = False
        self.pause_start_time = None

    def toggle_pause(self):
        if self.paused:
            self.start_time += time.time() - self.pause_start_time
            self.paused = False
        else:
            self.pause_start_time = time.time()
            self.paused = True

class Move:
    def __init__(self, start_row, start_col, end_row, end_col, is_capture, is_double_capture, is_triple_capture):
        self.start_row = start_row
        self.start_col = start_col
        self.end_row = end_row
        self.end_col = end_col
        self.is_capture = is_capture
        self.is_double_capture = is_double_capture
        self.is_triple_capture = is_triple_capture

class Settings:
    def __init__(self):
        self.music_on = True
        self.sound_on = True
        self.difficulty = Difficulty.MEDIUM

def init_game(game):
    game.player1.name = "Player 1"
    game.player2.name = "Player 2"
    game.player1.captured_pieces = 0
    game.player2.captured_pieces = 0
    game.is_player1_turn = True
    game.piece_selected = False
    game.move_history = []
    game.last_move = None
    game.start_time = time.time()
    init_board(game.board)

def init_board(board):
    for row in range(8):
        for col in range(8):
            if (row + col) % 2 != 0:
                if row < 3:
                    board.cells[row][col].cell_type = CellType.PLAYER2_QORKI
                elif row > 4:
                    board.cells[row][col].cell_type = CellType.PLAYER1_QORKI
                else:
                    board.cells[row][col].cell_type = CellType.EMPTY
            else:
                board.cells[row][col].cell_type = CellType.EMPTY

def draw_board(screen, game):
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else GRAY
            pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Highlight last move
    if game.last_move:
        pygame.draw.rect(screen, ORANGE, (game.last_move.start_col * CELL_SIZE, game.last_move.start_row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
        pygame.draw.rect(screen, ORANGE, (game.last_move.end_col * CELL_SIZE, game.last_move.end_row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

    # Draw scoreboard
    scoreboard_x = BOARD_WIDTH - 180
    font = pygame.font.Font(None, 36)
    screen.blit(font.render("Scoreboard", True, BLACK), (scoreboard_x, 20))
    screen.blit(font.render(game.player1.name, True, RED), (scoreboard_x, 60))
    if game.is_player1_turn:
        pygame.draw.polygon(screen, DARKPURPLE, [(760, 70), (780, 80), (780, 60)])
    screen.blit(font.render(f"Captured: {game.player1.captured_pieces}", True, BLACK), (scoreboard_x, 90))

    screen.blit(font.render(game.player2.name, True, BLUE), (scoreboard_x, 160))
    if not game.is_player1_turn:
        pygame.draw.polygon(screen, DARKPURPLE, [(760, 170), (780, 180), (780, 160)])
    screen.blit(font.render(f"Captured: {game.player2.captured_pieces}", True, BLACK), (scoreboard_x, 190))

    # Draw game timer
    elapsed_time = int(time.time() - game.start_time)
    if game.paused:
        elapsed_time = int(game.pause_start_time - game.start_time)
    minutes, seconds = divmod(elapsed_time, 60)
    timer_text = f"Time: {minutes:02d}:{seconds:02d}"
    screen.blit(font.render(timer_text, True, BLACK), (scoreboard_x, 250))

    # Draw checkbox for saving on exit
    checkbox_size = 15
    checkbox_rect = pygame.Rect(scoreboard_x, 300, checkbox_size, checkbox_size)
    pygame.draw.rect(screen, GREEN if game.save_on_exit else LIGHTGRAY, checkbox_rect)
    pygame.draw.rect(screen, BLACK, checkbox_rect, 2)
    screen.blit(font.render("Save on Exit", True, BLACK), (checkbox_rect.right + 5, checkbox_rect.top))

    # Draw difficulty level
    difficulty_text = f"Difficulty: {game.difficulty.name}"
    screen.blit(font.render(difficulty_text, True, BLACK), (scoreboard_x, 350))

def draw_cells(screen, game):
    for row in range(8):
        for col in range(8):
            draw_qorki(screen, game.board.cells[row][col])

    if game.piece_selected:
        valid_moves = get_valid_moves(game, game.selected_row, game.selected_col)
        for move in valid_moves:
            if move.is_capture:
                color = RED if move.is_triple_capture else (ORANGE if move.is_double_capture else GREEN)
            else:
                color = GREEN
            pygame.draw.rect(screen, color, (move.end_col * CELL_SIZE, move.end_row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 4)

def draw_qorki(screen, cell):
    if cell.cell_type == CellType.EMPTY:
        return

    if cell.cell_type in [CellType.PLAYER1_QORKI, CellType.PLAYER1_KING_QORKI]:
        color = RED
    else:
        color = BLUE

    center_x = cell.col * CELL_SIZE + CELL_SIZE // 2
    center_y = cell.row * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(screen, color, (center_x, center_y), QORKI_SIZE)

    if cell.cell_type in [CellType.PLAYER1_KING_QORKI, CellType.PLAYER2_KING_QORKI]:
        screen.blit(CROWN_IMG, (center_x - QORKI_SIZE // 2, center_y - QORKI_SIZE // 2))

def handle_input(game, pos):
    mouse_x, mouse_y = pos
    col = mouse_x // CELL_SIZE
    row = mouse_y // CELL_SIZE

    if col < 0 or col >= 8 or row < 0 or row >= 8:
        return

    clicked_cell = game.board.cells[row][col]

    if game.piece_selected:
        if move_piece(game, game.selected_row, game.selected_col, row, col):
            game.is_player1_turn = not game.is_player1_turn
            if game.is_player1_turn:
                game.player2.moves_made += 1
            else:
                game.player1.moves_made += 1
        game.piece_selected = False
    else:
        if (game.is_player1_turn and clicked_cell.cell_type in [CellType.PLAYER1_QORKI, CellType.PLAYER1_KING_QORKI]) or \
           (not game.is_player1_turn and clicked_cell.cell_type in [CellType.PLAYER2_QORKI, CellType.PLAYER2_KING_QORKI]):
            game.selected_row = row
            game.selected_col = col
            game.piece_selected = True

def move_piece(game, start_row, start_col, end_row, end_col):
    start_cell = game.board.cells[start_row][start_col]
    end_cell = game.board.cells[end_row][end_col]

    must_capture = [False]
    if not is_move_valid(game, start_row, start_col, end_row, end_col, must_capture):
        return False

    move = Move(start_row, start_col, end_row, end_col, must_capture[0], False, False)
    game.move_history.append(move)
    game.last_move = move

    end_cell.cell_type = start_cell.cell_type
    start_cell.cell_type = CellType.EMPTY

    if must_capture[0]:
        row_diff = end_row - start_row
        col_diff = end_col - start_col
        row_step = 1 if row_diff > 0 else -1
        col_step = 1 if col_diff > 0 else -1

        row, col = start_row, start_col
        while row != end_row and col != end_col:
            row += row_step
            col += col_step
            captured_piece = game.board.cells[row][col].cell_type

            if is_opponent_piece(end_cell.cell_type, captured_piece):
                game.board.cells[row][col].cell_type = CellType.EMPTY
                if captured_piece in [CellType.PLAYER2_QORKI, CellType.PLAYER2_KING_QORKI]:
                    game.player1.captured_pieces += 1
                elif captured_piece in [CellType.PLAYER1_QORKI, CellType.PLAYER1_KING_QORKI]:
                    game.player2.captured_pieces += 1
                row += row_step
                col += col_step
        
        if settings.sound_on:
            CAPTURE_SOUND.play()
    else:
        if settings.sound_on:
            MOVE_SOUND.play()

    if end_row == 0 and end_cell.cell_type == CellType.PLAYER1_QORKI:
        end_cell.cell_type = CellType.PLAYER1_KING_QORKI
        if settings.sound_on:
            KING_SOUND.play()
    if end_row == 7 and end_cell.cell_type == CellType.PLAYER2_QORKI:
        end_cell.cell_type = CellType.PLAYER2_KING_QORKI
        if settings.sound_on:
            KING_SOUND.play()

    return True

def is_move_valid(game, start_row, start_col, end_row, end_col, must_capture):
    moving_piece = game.board.cells[start_row][start_col].cell_type
    must_capture[0] = False

    if end_row < 0 or end_row >= 8 or end_col < 0 or end_col >= 8 or game.board.cells[end_row][end_col].cell_type != CellType.EMPTY:
        return False

    row_diff = end_row - start_row
    col_diff = end_col - start_col

    if abs(row_diff) != abs(col_diff):
        return False

    if (moving_piece == CellType.PLAYER1_QORKI and row_diff >= 0) or (moving_piece == CellType.PLAYER2_QORKI and row_diff <= 0):
        return False

    is_king = moving_piece in [CellType.PLAYER1_KING_QORKI, CellType.PLAYER2_KING_QORKI]

    if abs(row_diff) > 2:
        return validate_multiple_capture(game, start_row, start_col, end_row, end_col, moving_piece, must_capture)

    if abs(row_diff) == 2:
        middle_row = (start_row + end_row) // 2
        middle_col = (start_col + end_col) // 2
        captured_piece = game.board.cells[middle_row][middle_col].cell_type

        if not is_opponent_piece(moving_piece, captured_piece):
            return False

        must_capture[0] = True
        return True

    return abs(row_diff) == 1

def is_opponent_piece(moving_piece, other_piece):
    return ((moving_piece in [CellType.PLAYER1_QORKI, CellType.PLAYER1_KING_QORKI] and
             other_piece in [CellType.PLAYER2_QORKI, CellType.PLAYER2_KING_QORKI]) or
            (moving_piece in [CellType.PLAYER2_QORKI, CellType.PLAYER2_KING_QORKI] and
             other_piece in [CellType.PLAYER1_QORKI, CellType.PLAYER1_KING_QORKI]))

def validate_multiple_capture(game, start_row, start_col, end_row, end_col, moving_piece, must_capture):
    row_step = 1 if end_row > start_row else -1
    col_step = 1 if end_col > start_col else -1

    row, col = start_row, start_col
    found_capture = False

    while row != end_row and col != end_col:
        row += row_step
        col += col_step

        current_cell = game.board.cells[row][col].cell_type

        if current_cell == CellType.EMPTY:
            continue

        if is_opponent_piece(moving_piece, current_cell):
            next_row = row + row_step
            next_col = col + col_step

            if 0 <= next_row < 8 and 0 <= next_col < 8 and game.board.cells[next_row][next_col].cell_type == CellType.EMPTY:
                found_capture = True
                row = next_row
                col = next_col
                must_capture[0] = True
            else:
                return False
        else:
            return False

    return found_capture

def can_capture(game, row, col):
    piece_type = game.board.cells[row][col].cell_type
    for dr in [-2, 2]:
        for dc in [-2, 2]:
            new_row = row + dr
            new_col = col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                must_capture = [False]
                if is_move_valid(game, row, col, new_row, new_col, must_capture) and must_capture[0]:
                    return True
    return False

def check_game_over(game):
    player1_has_moves = has_any_moves(game, CellType.PLAYER1_QORKI) or has_any_moves(game, CellType.PLAYER1_KING_QORKI)
    player2_has_moves = has_any_moves(game, CellType.PLAYER2_QORKI) or has_any_moves(game, CellType.PLAYER2_KING_QORKI)

    if not player1_has_moves and not player2_has_moves:
        if game.player1.captured_pieces == game.player2.captured_pieces:
            return 3  # Game is a draw
        elif game.player1.captured_pieces > game.player2.captured_pieces:
            return 1  # Player 1 wins
        else:
            return 2  # Player 2 wins
    elif not player1_has_moves:
        return 2  # Player 2 wins
    elif not player2_has_moves:
        return 1  # Player 1 wins

    return 0  # Game is still ongoing

def has_any_moves(game, player_type):
    for row in range(8):
        for col in range(8):
            if game.board.cells[row][col].cell_type == player_type:
                if can_capture(game, row, col):
                    return True
                for dr in [-1, 1]:
                    for dc in [-1, 1]:
                        new_row = row + dr
                        new_col = col + dc
                        if 0 <= new_row < 8 and 0 <= new_col < 8:
                            must_capture = [False]
                            if is_move_valid(game, row, col, new_row, new_col, must_capture) and not must_capture[0]:
                                return True
    return False

def find_captures(game, start_row, start_col, valid_moves, depth=1):
    for row_offset in [-2, 2]:
        for col_offset in [-2, 2]:
            middle_row = start_row + row_offset // 2
            middle_col = start_col + col_offset // 2
            end_row = start_row + row_offset
            end_col = start_col + col_offset

            must_capture = [False]
            if is_move_valid(game, start_row, start_col, end_row, end_col, must_capture) and must_capture[0]:
                move = Move(start_row, start_col, end_row, end_col, True, depth > 1, depth > 2)
                valid_moves.append(move)

                temp_game = Game()
                temp_game.board = game.board
                move_piece(temp_game, start_row, start_col, end_row, end_col)
                find_captures(temp_game, end_row, end_col, valid_moves, depth + 1)

def get_valid_moves(game, start_row, start_col):
    valid_moves = []
    piece = game.board.cells[start_row][start_col].cell_type

    if piece == CellType.EMPTY:
        return valid_moves

    find_captures(game, start_row, start_col, valid_moves)

    if not valid_moves:
        for row_offset in [-1, 1]:
            for col_offset in [-1, 1]:
                end_row = start_row + row_offset
                end_col = start_col + col_offset

                must_capture = [False]
                if is_move_valid(game, start_row, start_col, end_row, end_col, must_capture) and not must_capture[0]:
                    valid_moves.append(Move(start_row, start_col, end_row, end_col, False, False, False))

    return valid_moves

def save_game(game, filename):
    with open(filename, 'w') as outfile:
        outfile.write(f"{game.player1.name}\n")
        outfile.write(f"{game.player2.name}\n")
        outfile.write(f"{int(game.is_player1_turn)}\n")
        outfile.write(f"{game.player1.captured_pieces}\n")
        outfile.write(f"{game.player2.captured_pieces}\n")
        outfile.write(f"{game.player1.moves_made}\n")
        outfile.write(f"{game.player2.moves_made}\n")
        outfile.write(f"{game.start_time}\n")

        for row in range(8):
            for col in range(8):
                outfile.write(f"{game.board.cells[row][col].cell_type.value} ")
            outfile.write("\n")

    print("Game saved successfully!")

def load_game(game, filename):
    try:
        with open(filename, 'r') as infile:
            game.player1.name = infile.readline().strip()
            game.player2.name = infile.readline().strip()
            game.is_player1_turn = bool(int(infile.readline().strip()))
            game.player1.captured_pieces = int(infile.readline().strip())
            game.player2.captured_pieces = int(infile.readline().strip())
            game.player1.moves_made = int(infile.readline().strip())
            game.player2.moves_made = int(infile.readline().strip())
            game.start_time = float(infile.readline().strip())

            for row in range(8):
                cell_types = infile.readline().strip().split()
                for col, cell_type in enumerate(cell_types):
                    game.board.cells[row][col].cell_type = CellType(int(cell_type))

        print("Game loaded successfully!")
        return True
    except Exception as e:
        print(f"Error: Could not load the game. {e}")
        return False

def draw_main_menu(screen):
    screen.fill(WHITE)
    font = pygame.font.Font(None, 36)

    title = font.render("Welcome to Checkers!", True, (50, 50, 50))
    screen.blit(title, (BOARD_WIDTH // 2 - title.get_width() // 2, BOARD_HEIGHT // 2 - 220))

    new_game_button = pygame.Rect(BOARD_WIDTH // 2 - 100, BOARD_HEIGHT // 2 - 135, 200, 50)
    load_game_button = pygame.Rect(BOARD_WIDTH // 2 - 100, BOARD_HEIGHT // 2 - 50, 200, 50)
    settings_button = pygame.Rect(BOARD_WIDTH // 2 - 100, BOARD_HEIGHT // 2 + 35, 200, 50)

    pygame.draw.rect(screen, LIGHTGRAY, new_game_button)
    pygame.draw.rect(screen, BLACK, new_game_button, 3)
    new_game_text = font.render("New Game", True, BLACK)
    screen.blit(new_game_text, (new_game_button.centerx - new_game_text.get_width() // 2, new_game_button.centery - new_game_text.get_height() // 2))

    pygame.draw.rect(screen, LIGHTGRAY, load_game_button)
    pygame.draw.rect(screen, BLACK, load_game_button, 3)
    load_game_text = font.render("Load Game", True, BLACK)
    screen.blit(load_game_text, (load_game_button.centerx - load_game_text.get_width() // 2, load_game_button.centery - load_game_text.get_height() // 2))

    pygame.draw.rect(screen, LIGHTGRAY, settings_button)
    pygame.draw.rect(screen, BLACK, settings_button, 3)
    settings_text = font.render("Settings", True, BLACK)
    screen.blit(settings_text, (settings_button.centerx - settings_text.get_width() // 2, settings_button.centery - settings_text.get_height() // 2))

    pygame.display.flip()

    return new_game_button, load_game_button, settings_button

def draw_settings_menu(screen, settings):
    screen.fill(WHITE)
    font = pygame.font.Font(None, 36)

    title = font.render("Settings", True, (50, 50, 50))
    screen.blit(title, (BOARD_WIDTH // 2 - title.get_width() // 2, BOARD_HEIGHT // 2 - 220))

    music_button = pygame.Rect(BOARD_WIDTH // 2 - 100, BOARD_HEIGHT // 2 - 135, 200, 50)
    sound_button = pygame.Rect(BOARD_WIDTH // 2 - 100, BOARD_HEIGHT // 2 - 50, 200, 50)
    difficulty_button = pygame.Rect(BOARD_WIDTH // 2 - 100, BOARD_HEIGHT // 2 + 35, 200, 50)
    back_button = pygame.Rect(BOARD_WIDTH // 2 - 100, BOARD_HEIGHT // 2 + 120, 200, 50)

    pygame.draw.rect(screen, LIGHTGRAY, music_button)
    pygame.draw.rect(screen, BLACK, music_button, 3)
    music_text = font.render(f"Music: {'On' if settings.music_on else 'Off'}", True, BLACK)
    screen.blit(music_text, (music_button.centerx - music_text.get_width() // 2, music_button.centery - music_text.get_height() // 2))

    pygame.draw.rect(screen, LIGHTGRAY, sound_button)
    pygame.draw.rect(screen, BLACK, sound_button, 3)
    sound_text = font.render(f"Sound: {'On' if settings.sound_on else 'Off'}", True, BLACK)
    screen.blit(sound_text, (sound_button.centerx - sound_text.get_width() // 2, sound_button.centery - sound_text.get_height() // 2))

    pygame.draw.rect(screen, LIGHTGRAY, difficulty_button)
    pygame.draw.rect(screen, BLACK, difficulty_button, 3)
    difficulty_text = font.render(f"Difficulty: {settings.difficulty.name}", True, BLACK)
    screen.blit(difficulty_text, (difficulty_button.centerx - difficulty_text.get_width() // 2, difficulty_button.centery - difficulty_text.get_height() // 2))

    pygame.draw.rect(screen, LIGHTGRAY, back_button)
    pygame.draw.rect(screen, BLACK, back_button, 3)
    back_text = font.render("Back", True, BLACK)
    screen.blit(back_text, (back_button.centerx - back_text.get_width() // 2, back_button.centery - back_text.get_height() // 2))

    pygame.display.flip()

    return music_button, sound_button, difficulty_button, back_button

def ai_move(game):
    valid_moves = []
    for row in range(8):
        for col in range(8):
            if game.is_player1_turn and game.board.cells[row][col].cell_type in [CellType.PLAYER1_QORKI, CellType.PLAYER1_KING_QORKI]:
                valid_moves.extend(get_valid_moves(game, row, col))
            elif not game.is_player1_turn and game.board.cells[row][col].cell_type in [CellType.PLAYER2_QORKI, CellType.PLAYER2_KING_QORKI]:
                valid_moves.extend(get_valid_moves(game, row, col))

    if valid_moves:
        if game.difficulty == Difficulty.EASY:
            chosen_move = random.choice(valid_moves)
        elif game.difficulty == Difficulty.MEDIUM:
            capture_moves = [move for move in valid_moves if move.is_capture]
            if capture_moves:
                chosen_move = random.choice(capture_moves)
            else:
                chosen_move = random.choice(valid_moves)
        else:  # HARD
            capture_moves = [move for move in valid_moves if move.is_capture]
            if capture_moves:
                chosen_move = max(capture_moves, key=lambda m: m.is_triple_capture * 3 + m.is_double_capture * 2 + m.is_capture)
            else:
                chosen_move = random.choice(valid_moves)

        move_piece(game, chosen_move.start_row, chosenchosen_move.start_col, chosen_move.end_row, chosen_move.end_col)
            game.is_player1_turn = not game.is_player1_turn
            if game.is_player1_turn:
                game.player2.moves_made += 1
            else:
                game.player1.moves_made += 1

def undo_move(game):
    if game.move_history:
        last_move = game.move_history.pop()
        game.board.cells[last_move.start_row][last_move.start_col].cell_type = game.board.cells[last_move.end_row][last_move.end_col].cell_type
        game.board.cells[last_move.end_row][last_move.end_col].cell_type = CellType.EMPTY
        game.is_player1_turn = not game.is_player1_turn
        if game.is_player1_turn:
            game.player2.moves_made -= 1
        else:
            game.player1.moves_made -= 1
        if last_move.is_capture:
            mid_row = (last_move.start_row + last_move.end_row) // 2
            mid_col = (last_move.start_col + last_move.end_col) // 2
            game.board.cells[mid_row][mid_col].cell_type = CellType.PLAYER2_QORKI if game.is_player1_turn else CellType.PLAYER1_QORKI
            if game.is_player1_turn:
                game.player1.captured_pieces -= 1
            else:
                game.player2.captured_pieces -= 1
        game.last_move = game.move_history[-1] if game.move_history else None

def main():
    pygame.init()
    screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))
    pygame.display.set_caption("Checkers Game")
    clock = pygame.time.Clock()

    game = Game()
    settings = Settings()
    init_game(game)

    is_main_menu = True
    is_settings_menu = False
    is_game_over = False
    game_over_status = 0

    if settings.music_on:
        pygame.mixer.music.play(-1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if game.save_on_exit:
                    save_game(game, "saved_game.txt")
                pygame.quit()
                sys.exit()

            if is_main_menu:
                new_game_button, load_game_button, settings_button = draw_main_menu(screen)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if new_game_button.collidepoint(event.pos):
                        init_game(game)
                        is_game_over = False
                        is_main_menu = False
                    elif load_game_button.collidepoint(event.pos):
                        if load_game(game, "saved_game.txt"):
                            is_game_over = False
                            is_main_menu = False
                    elif settings_button.collidepoint(event.pos):
                        is_settings_menu = True
                        is_main_menu = False
            elif is_settings_menu:
                music_button, sound_button, difficulty_button, back_button = draw_settings_menu(screen, settings)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if music_button.collidepoint(event.pos):
                        settings.music_on = not settings.music_on
                        if settings.music_on:
                            pygame.mixer.music.play(-1)
                        else:
                            pygame.mixer.music.stop()
                    elif sound_button.collidepoint(event.pos):
                        settings.sound_on = not settings.sound_on
                    elif difficulty_button.collidepoint(event.pos):
                        difficulties = list(Difficulty)
                        current_index = difficulties.index(settings.difficulty)
                        settings.difficulty = difficulties[(current_index + 1) % len(difficulties)]
                    elif back_button.collidepoint(event.pos):
                        is_settings_menu = False
                        is_main_menu = True
            else:
                if not is_game_over:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        handle_input(game, event.pos)
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_u:  # Undo move
                            undo_move(game)
                        elif event.key == pygame.K_p:  # Pause game
                            game.toggle_pause()

                    game_over_status = check_game_over(game)
                    if game_over_status != 0:
                        is_game_over = True

                    if not game.is_player1_turn:  # AI's turn
                        ai_move(game)

        if not is_main_menu and not is_settings_menu:
            screen.fill(WHITE)
            draw_board(screen, game)
            draw_cells(screen, game)

            if is_game_over:
                font = pygame.font.Font(None, 36)
                if game_over_status == 0:
                    text = font.render("Game Over", True, BLACK)
                elif game_over_status == 1:
                    text = font.render("Player 1 Wins!", True, BLACK)
                elif game_over_status == 2:
                    text = font.render("Player 2 Wins!", True, BLACK)
                else:
                    text = font.render("It's a Draw!", True, BLACK)
                screen.blit(text, (BOARD_WIDTH // 2 - text.get_width() // 2, BOARD_HEIGHT // 2))

                return_text = font.render("Press 'R' to return to Main Menu", True, BLACK)
                screen.blit(return_text, (BOARD_WIDTH // 2 - return_text.get_width() // 2, BOARD_HEIGHT // 2 + 40))

                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:
                    is_main_menu = True
                    is_game_over = False

            if game.paused:
                font = pygame.font.Font(None, 72)
                pause_text = font.render("PAUSED", True, RED)
                screen.blit(pause_text, (BOARD_WIDTH // 2 - pause_text.get_width() // 2, BOARD_HEIGHT // 2 - pause_text.get_height() // 2))

            pygame.display.flip()

        clock.tick(60)

if __name__ == "__main__":
    main()
