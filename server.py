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
    conn.send(f"Game start. You are playing as 'X'.\n{game.get_board_string()}".encode('utf-8'))
    
    while True:
        # Wait for client's move
        conn.send("Your move (column 0-6): ".encode('utf-8'))
        move = int(conn.recv(1024).decode('utf-8').strip())

        if not game.is_valid_location(move):
            conn.send("Invalid move. Please try again.\n".encode('utf-8'))
            continue
        
        # Process client's move
        row = game.get_next_open_row(move)
        game.drop_piece(row, move, 'X')
        if game.check_win('X') or game.is_board_full():
            message = f"{game.get_board_string()}"
            message += "You won! Game over." if game.check_win('X') else "The game is a draw."
            conn.send(message.encode('utf-8'))
            break

        # AI makes its move
        ai_move = choose_ai_move(difficulty, game)
        row = game.get_next_open_row(ai_move)
        game.drop_piece(row, ai_move, 'O')
        
        # Send updated board and check for win/draw
        message = f"AI moved at column {ai_move}.\n{game.get_board_string()}"
        if game.check_win('O'):
            message += "AI won! Game over."
        elif game.is_board_full():
            message += "The game is a draw."
        conn.send(message.encode('utf-8'))





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
