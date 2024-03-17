class Connect4:
    def __init__(self, rows=6, columns=7):
        self.rows = rows
        self.columns = columns
        self.board = [[' ' for _ in range(columns)] for _ in range(rows)]
        self.rounds = 0  # Track the number of rounds in the game
        self.wins = {'X': 0, 'O': 0}  # Wins distribution between players
        self.clutch_factor = {'X': 0, 'O': 0}  # Track clutch moves

    def is_clutch_move(self, column, piece):
        # Temporarily make the move
        row = self.get_next_open_row(column)
        self.board[row][column] = piece
        
        if self.check_win(piece):
            # If after making the move, the player wins, it's not a clutch move
            # Undo the move
            self.board[row][column] = ' '
            return False
        
        opponent_piece = 'O' if piece == 'X' else 'X'
        for col in range(self.columns):
            if self.is_valid_location(col):
                opponent_row = self.get_next_open_row(col)
                self.board[opponent_row][col] = opponent_piece
                if self.check_win(opponent_piece):
                    # If the opponent could have won and the player's move prevented it,
                    # it's a clutch move. Undo both moves and return True.
                    self.board[opponent_row][col] = ' '
                    self.board[row][column] = ' '
                    return True
                # Undo the opponent's simulated move
                self.board[opponent_row][col] = ' '
        
        # Undo the player's move
        self.board[row][column] = ' '
        return False




    def increment_round(self):
        self.rounds += 1

    def register_win(self, piece):
        if piece in self.wins:
            self.wins[piece] += 1

    def update_clutch_factor(self, piece):
        if piece in self.clutch_factor:
            self.clutch_factor[piece] += 1


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
        if self.is_clutch_move(column, piece):
            self.update_clutch_factor(piece)
        self.board[row][column] = piece
        self.increment_round()  # Keep this as previously suggested


    def check_win(self, piece):
        # Check horizontal locations
        for c in range(self.columns - 3):
            for r in range(self.rows):
                if all(self.board[r][c + i] == piece for i in range(4)):
                    # self.register_win(piece)
                    return True

        # Check vertical locations
        for c in range(self.columns):
            for r in range(self.rows - 3):
                if all(self.board[r + i][c] == piece for i in range(4)):
                    # self.register_win(piece)
                    return True

        # Check positively sloped diagonals
        for c in range(self.columns - 3):
            for r in range(self.rows - 3):
                if all(self.board[r + i][c + i] == piece for i in range(4)):
                    # self.register_win(piece)
                    return True

        # Check negatively sloped diagonals
        for c in range(self.columns - 3):
            for r in range(3, self.rows):
                if all(self.board[r - i][c + i] == piece for i in range(4)):
                    # self.register_win(piece)
                    return True
        return False
    

    def is_board_full(self):
        return all(self.board[0][c] != ' ' for c in range(self.columns))
