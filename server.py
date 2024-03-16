import socket
import threading
from game_logic import Connect4  # Remove print_board from the import
from ai_logic import choose_ai_move
from utils import validate_positive_input

HOST = '127.0.0.1'
PORT = 5555
MAX_CONNECTIONS = 5

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(MAX_CONNECTIONS)
print("Server started, listening for connections...")

connections = []
games = {}
waiting_list = []

def handle_client(conn, addr):
    global connections, games, waiting_list
    conn.send("Welcome to Connect4! Choose an option:\n1: Play with the Server\n2: Play with Another Player\n3: Exit".encode('utf-8'))

    choice = conn.recv(1024).decode('utf-8').strip()
    if choice == '1':
        difficulty = conn.recv(1024).decode('utf-8').strip()
        play_with_ai(conn, difficulty)
    elif choice == '2':
        match_player(conn, addr)
    elif choice == '3':
        conn.close()
        return

def match_player(conn, addr):
    global waiting_list
    print(f"{addr} is waiting for a match.")
    waiting_list.append(conn)
    if len(waiting_list) >= 2:
        player1 = waiting_list.pop(0)
        player2 = waiting_list.pop(0)
        start_game(player1, player2)
    else:
        conn.send("Waiting for another player...".encode('utf-8'))

def play_with_ai(conn, difficulty):
    game = Connect4()
    while True:
        # Change print_board(game.board) to game.display_board()
        # Since display_board prints directly, you cannot send it over a socket.
        # Consider sending the board state as a string if needed.
        move = int(conn.recv(1024).decode('utf-8').strip())
        game.drop_piece(game.get_next_open_row(move), move, 'X')  # Assume 'X' is the player's piece
        if game.check_win('X'):
            conn.send("You won!".encode('utf-8'))
            break
        ai_move = choose_ai_move(difficulty, game)
        if ai_move is not None:  # Ensure ai_move is valid before making the move
            game.drop_piece(game.get_next_open_row(ai_move), ai_move, 'O')  # Assume 'O' is the AI's piece
            if game.check_win('O'):
                conn.send("AI won!".encode('utf-8'))
                break
        # Need to convert the board to a string format to send it over the socket
        # conn.send(f"AI moved to {ai_move}. Your turn.\n{stringify_board(game)}".encode('utf-8'))


def start_game(player1, player2):
    game = Connect4()
    current_turn = 1
    players = {1: player1, 2: player2}
    
    # Notify both players that the game has started
    for player in players.values():
        player.send("Game has started. You are now playing against another player.".encode('utf-8'))
    
    while True:
        # Get the current game board's string representation
        board_str = game.get_board_string()
        
        # Send current game board to both players
        for player in players.values():
            player.send(f"Current board:\n{board_str}".encode('utf-8'))
        
        # Handle current player's move
        current_player = players[current_turn]
        current_player.send("Your move (column 0-6): ".encode('utf-8'))
        column = int(current_player.recv(1024).decode('utf-8').strip())
        
        # Validate move
        if not game.is_valid_location(column):
            current_player.send("Invalid move. Try again.".encode('utf-8'))
            continue
        
        # Make move
        row = game.get_next_open_row(column)
        game.drop_piece(row, column, 'X' if current_turn == 1 else 'O')
        
        # Check for win or draw
        if game.check_win('X' if current_turn == 1 else 'O'):
            for player in players.values():
                if player == current_player:
                    player.send("Congratulations, you won!".encode('utf-8'))
                else:
                    player.send(f"Player {current_turn} has won the game!".encode('utf-8'))
            break
        elif game.is_board_full():
            for player in players.values():
                player.send("The game board is full. It's a draw!".encode('utf-8'))
            break
        
        # Switch turns
        current_turn = 3 - current_turn

    # Close connections at the end of the game
    player1.close()
    player2.close()


def accept_connections():
    while True:
        conn, addr = server.accept()
        if len(connections) >= MAX_CONNECTIONS:
            conn.send("Server is full. Try again later.".encode('utf-8'))
            conn.close()
        else:
            print(f"Connection from {addr}")
            connections.append(conn)
            threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    accept_connections()
