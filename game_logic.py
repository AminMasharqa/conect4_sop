class Connect4:
    def __init__(self, rows=6, columns=7):
        self.rows = rows
        self.columns = columns
        self.board = [[' ' for _ in range(columns)] for _ in range(rows)]
        self.current_turn = 'X'  # Initialize current turn to 'X'
        self.last_move = None  # To track the last move made

    def print_board(self):
        # Print column numbers for reference
        print("  " + " ".join(str(i) for i in range(self.columns)))
        # Print the board
        for row in self.board:
            print('|' + '|'.join(row) + '|')
        # Print a bottom border
        print('+---' * self.columns + '+')
    
    # In the Connect4 class in game_logic.py
    def get_board_string(self):
        board_str = "  " + " ".join(str(i) for i in range(self.columns)) + "\n"
        for row in self.board:
            board_str += '|' + '|'.join(row) + '|' + "\n"
        board_str += '+---' * self.columns + '+\n'
        return board_str
    
    # In Connect4 class in game_logic.py
    def can_make_move(self, col):
        return 0 <= col < self.columns and self.board[0][col] == ' '



    def is_valid_location(self, column):
        return self.board[0][column] == ' '

    def get_next_open_row(self, column):
        for r in range(self.rows - 1, -1, -1):
            if self.board[r][column] == ' ':
                return r
        return None

    def drop_piece(self, row, column, piece):
        self.board[row][column] = piece
        self.last_move = (row, column, piece)

    def check_win(self, piece):
        # Check horizontal locations
        for c in range(self.columns - 3):
            for r in range(self.rows):
                if all(self.board[r][c + i] == piece for i in range(4)):
                    return True

        # Check vertical locations
        for c in range(self.columns):
            for r in range(self.rows - 3):
                if all(self.board[r + i][c] == piece for i in range(4)):
                    return True

        # Check positively sloped diagonals
        for c in range(self.columns - 3):
            for r in range(self.rows - 3):
                if all(self.board[r + i][c + i] == piece for i in range(4)):
                    return True

        # Check negatively sloped diagonals
        for c in range(self.columns - 3):
            for r in range(3, self.rows):
                if all(self.board[r - i][c + i] == piece for i in range(4)):
                    return True

        return False

    def is_board_full(self):
        return all(self.board[0][c] != ' ' for c in range(self.columns))
