import socket

def display_main_menu(sock):
    menu_options = sock.recv(1024).decode('utf-8')
    print(menu_options)
    choice = input("Enter your choice: ")
    sock.send(choice.encode('utf-8'))
    return choice

def play_game(sock):
    waiting_for_move = True  # Flag to control when to prompt for user input
    while True:
        server_msg = sock.recv(1024).decode('utf-8')
        print(server_msg)

        if "Your move" in server_msg:
            if waiting_for_move:
                move = input("Enter your move (column 0-6): ")
                sock.send(move.encode('utf-8'))
                # waiting_for_move = False  # After sending a move, wait for the server's response
        elif "AI moved at column" in server_msg or "Your move at column" in server_msg:
            waiting_for_move = True  # After AI moves, wait for the user's next move
        elif "won!" in server_msg or "The game is a draw." in server_msg:
            break





def main():
    host = '127.0.0.1'
    port = 5555
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        print("Connected to the Connect 4 server.")

        choice = display_main_menu(sock)
        if choice == '1':  # Play with the server (AI)
            difficulty = input("Choose difficulty:\n1: Easy\n2: Hard\nEnter your choice: ")
            sock.send(difficulty.encode('utf-8'))
            play_game(sock)
        elif choice == '2':  # Play with another player
            play_game(sock)
        elif choice == '3':  # Exit
            print("Exiting the game. Goodbye!")

if __name__ == "__main__":
    main()
