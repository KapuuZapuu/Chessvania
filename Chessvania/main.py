# main.py

from board import Board
from menus import show_main_menu
from piece import Pawn, Knight, Bishop, Rook, Queen, King
from rich.console import Console
from rich.text import Text

DEBUG = True # Flag for debug output control (change here to enable/disable debug messages)

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
    dev_mode = show_main_menu()  # Get game mode from menu
    if dev_mode is None:
        return  # Exit if user selects "Quit"
    
    board = Board()
    print("Enter moves in standard chess notation (e.g., 'e2 e4'). Type 'quit' to exit.")
    if dev_mode:
        print("Dev Mode Enabled: Type 'upgrade' to instantly upgrade a piece.")
    board.render_board()

    while True:
        print(f"\n{board.current_turn.capitalize()}'s turn.")
        user_input = input("Enter your move: ").strip().lower()

        if user_input == "quit":
            print("Thanks for playing!")
            break
        elif dev_mode and user_input == "upgrade":
            dev_upgrade_piece(board)
            continue

        start, end = parse_chess_notation(user_input)
        if start and end:
            if board.move_piece(start, end):
                print("\nMove successful!")
                board.render_board()
            else:
                print("\nInvalid move!")

def dev_upgrade_piece(board):
    """
    Enables instant piece upgrades in Dev Mode.
    """
    print("\nEnter the coordinates of the piece to upgrade (e.g., 'e2'):")
    pos = input("Piece Position: ").strip().lower()

    if len(pos) != 2 or pos[0] not in "abcdefgh" or not pos[1].isdigit():
        print("Invalid position format.")
        return

    col = ord(pos[0]) - ord('a')  # Convert letter to column index (a=0, h=7)
    row = 8 - int(pos[1])         # Convert rank to board row index (1=7, 8=0)

    if not board.is_valid_position((row, col)) or board.board[row][col] is None:
        print("No piece at that position.")
        return

    piece = board.board[row][col]

    # Upgrade menu definitions per class
    upgrade_menus = {
        Pawn: [
            "Rare (3-jump)",
            "Super Rare (Diagonal Move, 5-turn cooldown)",
            "Epic (4-jump)",
            "Mythic (Diagonal Move Cooldown Reduction: 5 -> 3)",
            "Legendary (Move Backwards)"
        ],
        Knight: [
            "Rare (Diagonal Step)",
            "Super Rare (Invulnerability for 2 moves, 5-turn cooldown)",
            "Epic (Extended Knight Move)",
            "Mythic (Cooldown reduced to 3 turns)",
            "Legendary (Cardinal Step)"
        ]
        # Add other pieces here later (e.g., Bishop, Rook)
    }

    # Find matching menu based on piece type
    menu = None
    for piece_type, options in upgrade_menus.items():
        if isinstance(piece, piece_type):
            menu = options
            break

    if not menu:
        print("This piece type does not support upgrades.")
        return

    print("\nChoose an upgrade:")
    for i, label in enumerate(menu, 1):
        print(f"{i}. {label}")

    choice = input("Enter upgrade number: ").strip()
    upgrades = {
        "1": "rare",
        "2": "super_rare",
        "3": "epic",
        "4": "mythic",
        "5": "legendary"
    }

    if choice in upgrades:
        piece.upgrade(upgrades[choice], board)

        # Force cooldowns or ability state to initialize
        _ = piece.valid_moves(board)

        print(f"\n{piece.__class__.__name__} at {pos} upgraded to {upgrades[choice].capitalize()}!")
        board.render_board()
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()
