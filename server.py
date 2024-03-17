# Alamin Masharqa           ID:207358326
import socket
import threading
from game_logic import Connect4  # Remove print_board from the import
from ai_logic import choose_ai_move
from utils import validate_positive_input
import time

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

def send_post_game_summary(conn, game):
    # Construct the post-game summary string
    summary = f"Game Summary:\n- Total Rounds: {game.rounds}\n"
    summary += f"- Wins Distribution: X has {game.wins['X']} wins, O has {game.wins['O']} wins\n"
    summary += f"- Clutch Factor: X's clutch moves {game.clutch_factor['X']}, O's clutch moves {game.clutch_factor['O']}\n"
    conn.send(summary.encode('utf-8'))

# Update the play_with_ai and start_game functions in server.py to call send_post_game_summary at the end of a game session.



def play_with_ai(conn, difficulty):
    game = Connect4()

    # Send initial game board and instructions
    conn.send(f"Game start. You are playing as 'X'.\n{game.get_board_string()}".encode('utf-8'))

    # Initialize variables for handling invalid inputs and freeze times
    invalid_input_count = 0
    freeze_time_seconds = 60  # Start with a 1-minute freeze time
    client_moves = 0  # Counter for the client's moves


    # Loop to handle "max moves to win" input with invalid input handling
    while True:
        conn.send("Enter the max moves to win (4-21): ".encode('utf-8'))
        max_moves_input = conn.recv(1024).decode('utf-8').strip()
        try:
            max_moves = int(max_moves_input)
            if 4 <= max_moves <= 21:
                print(f"Valid max moves to win: {max_moves}")
                conn.send(f"\n{game.get_board_string()}".encode('utf-8'))


                break  # Valid input received, exit loop
            else:
                raise ValueError  # Treat out-of-range values as invalid inputs
        except ValueError:
            invalid_input_count += 1
            if invalid_input_count % 5 == 0:
                # Freeze client interactions for the current freeze time
                conn.send(f"Too many invalid inputs. Please wait {freeze_time_seconds} seconds before trying again.".encode('utf-8'))
                time.sleep(freeze_time_seconds)
                # Double the freeze time for the next set of invalid inputs
                freeze_time_seconds *= 2
            else:
                conn.send("Invalid input detected. Please enter a numeric value between 4 and 21.\n".encode('utf-8'))
                continue  # Continue to prompt for valid input

    # Game loop for player moves and AI responses
    while True:

        client_moves += 1  # Increment the client's moves counter after each valid move
        if client_moves > max_moves:
            # If client moves exceed the max_moves, send a message and break the loop
            conn.send("You have exceeded the maximum number of allowed moves. Game over.\n".encode('utf-8'))
            break  # End the game session
        conn.send("Your move (column 0-6): ".encode('utf-8'))
        move_input = conn.recv(1024).decode('utf-8').strip()
        try:
            move = int(move_input)
            if game.is_valid_location(move):
                game.drop_piece(game.get_next_open_row(move), move, 'X')
                if game.check_win('X') or game.is_board_full():
                    conn.send(f"{game.get_board_string()}You won! Game over.\n".encode('utf-8') if game.check_win('X') else f"{game.get_board_string()}The game is a draw.\n".encode('utf-8'))
                    send_post_game_summary(conn, game)

                    break
                ai_move = choose_ai_move(difficulty, game)
                game.drop_piece(game.get_next_open_row(ai_move), ai_move, 'O')
                if game.check_win('O'):
                    conn.send(f"AI moved at column {ai_move}.\n{game.get_board_string()}AI won! Game over.\n".encode('utf-8'))
                    send_post_game_summary(conn, game)

                    break
                elif game.is_board_full():
                    conn.send(f"AI moved at column {ai_move}.\n{game.get_board_string()}The game is a draw.\n".encode('utf-8'))
                    break
                else:
                    conn.send(f"AI moved at column {ai_move}.\n{game.get_board_string()}\n".encode('utf-8'))
            else:
                conn.send("Invalid move. Please try again.\n".encode('utf-8'))
        except ValueError:
            conn.send("Invalid move detected. Please enter a numeric column (0-6).\n".encode('utf-8'))
    send_post_game_summary(conn, game)







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
                print("hereeeeeeeeee")
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
    send_post_game_summary(player1, game)
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
