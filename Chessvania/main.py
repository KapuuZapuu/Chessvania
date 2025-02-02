# main.py

from board import Board

DEBUG = True # Flag for debug output control

def parse_chess_notation(move):
    """
    Parse a move in chess notation (e.g., 'e2 e4') and convert it to board coordinates.
    """
    columns = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    try:
        start, end = move.split()
        start_pos = (8 - int(start[1]), columns[start[0]])
        end_pos = (8 - int(end[1]), columns[end[0]])

        if DEBUG: print(f"[DEBUG] main.py - parse_chess_notation: Parsed move: {start_pos} to {end_pos}")

        return start_pos, end_pos
    except (KeyError, ValueError, IndexError):
        print("Invalid input. Use format 'e2 e4'.")
        return None, None

def main():
    board = Board()
    print("\nWelcome to Chessvania!")
    print("Enter moves in standard chess notation (e.g., 'e2 e4'). Type 'quit' to exit.")
    board.render_board()

    while True:
        user_input = input("Enter your move: ").strip().lower()
        if user_input == "quit":
            print("Thanks for playing!")
            break

        start, end = parse_chess_notation(user_input)
        if start and end:
            if board.move_piece(start, end):
                print("\nMove successful!")
                board.render_board()
            else:
                print("\nInvalid move!")

if __name__ == "__main__":
    main()