import random
from game_logic import Connect4

def random_move(game):
    valid_moves = [col for col in range(7) if game.can_make_move(col)]
    return random.choice(valid_moves) if valid_moves else None

def minimax_move(game, depth, is_maximizing, alpha=-float("inf"), beta=float("inf")):
    # Base case: Check for a win, loss, or draw, or if depth is 0
    if game.check_win('X'):  # Assuming 'X' is the AI
        return None, float("inf")
    elif game.check_win('O'):  # Assuming 'O' is the opponent
        return None, -float("inf")
    elif game.is_board_full() or depth == 0:
        return None, 0  # Draw or depth limit reached

    if is_maximizing:
        max_eval = -float("inf")
        best_column = random.choice([c for c in range(game.columns) if game.is_valid_location(c)])
        for col in range(game.columns):
            if game.is_valid_location(col):
                row = game.get_next_open_row(col)
                game.drop_piece(row, col, 'X')  # Assuming 'X' is the AI
                eval = minimax_move(game, depth - 1, False, alpha, beta)[1]
                game.board[row][col] = ' '  # Undo move
                if eval > max_eval:
                    max_eval = eval
                    best_column = col
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return best_column, max_eval
    else:
        min_eval = float("inf")
        best_column = random.choice([c for c in range(game.columns) if game.is_valid_location(c)])
        for col in range(game.columns):
            if game.is_valid_location(col):
                row = game.get_next_open_row(col)
                game.drop_piece(row, col, 'O')  # Assuming 'O' is the opponent
                eval = minimax_move(game, depth - 1, True, alpha, beta)[1]
                game.board[row][col] = ' '  # Undo move
                if eval < min_eval:
                    min_eval = eval
                    best_column = col
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return best_column, min_eval


def choose_ai_move(difficulty, game):
    if difficulty == '1':
        return random_move(game)
    elif difficulty == '2':
        return minimax_move(game, depth=4, is_maximizing=True)
