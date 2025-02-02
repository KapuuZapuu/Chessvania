# Chess v1.0 by Hassan Khan
# 2025

# ---

# Global variables:
last_move = None # To track the last move
castling_rights = {"white_ks": True, "white_qs": True, "black_ks": True, "black_qs": True} # Tracks king/rook movement for castling
board_states = {}  # Dictionary to store board states and their counts
halfmove_clock = 0  # Tracks half-moves since the last pawn move or capture (for 50-move rule)

# ---

# Chess board setup:
board = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p", "p", "p", "p", "p", "p", "p", "p"],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    ["P", "P", "P", "P", "P", "P", "P", "P"],
    ["R", "N", "B", "Q", "K", "B", "N", "R"]
]  # Uppercase = white, lowercase = black

piece_symbols = {
    "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚", "p": "♟",
    "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔", "P": "♙",
    ".": " "
}

def get_board_state():
    state = "".join("".join(row) for row in board)  # Flatten the board into a string
    state += f"_{castling_rights['white_ks']}_{castling_rights['white_qs']}"
    state += f"_{castling_rights['black_ks']}_{castling_rights['black_qs']}"
    state += f"_{last_move}"  # Include last move for en passant
    return state

def update_board_state():
    state = get_board_state()
    if state in board_states:
        board_states[state] += 1
    else:
        board_states[state] = 1

# ---

# Utility functions:
def is_path_clear(start_x, start_y, end_x, end_y):
    dx = (end_x - start_x) and (end_x - start_x) // abs(end_x - start_x)
    dy = (end_y - start_y) and (end_y - start_y) // abs(end_y - start_y)
    x, y = start_x + dx, start_y + dy
    while (x, y) != (end_x, end_y):
        if board[y][x] != ".":
            return False
        x += dx
        y += dy
    return True

# Move validation for each piece:
def is_valid_pawn_move(piece, start_x, start_y, end_x, end_y):
    direction = -1 if piece == "P" else 1
    start_row = 6 if piece == "P" else 1
    if start_x == end_x:  # Forward move
        if (end_y - start_y) == direction:  # One square
            return board[end_y][end_x] == "."
        elif (end_y - start_y) == 2 * direction and start_y == start_row:  # Two squares
            return board[end_y][end_x] == "." and board[start_y + direction][end_x] == "."
    elif abs(start_x - end_x) == 1 and (end_y - start_y) == direction:  # Capture
        return board[end_y][end_x].islower() if piece == "P" else board[end_y][end_x].isupper()
    return False

def is_valid_rook_move(start_x, start_y, end_x, end_y):
    return (start_x == end_x or start_y == end_y) and is_path_clear(start_x, start_y, end_x, end_y)

def is_valid_knight_move(start_x, start_y, end_x, end_y):
    dx, dy = abs(end_x - start_x), abs(end_y - start_y)
    return (dx, dy) in [(2, 1), (1, 2)]

def is_valid_bishop_move(start_x, start_y, end_x, end_y):
    return abs(start_x - end_x) == abs(start_y - end_y) and is_path_clear(start_x, start_y, end_x, end_y)

def is_valid_queen_move(start_x, start_y, end_x, end_y):
    return is_valid_rook_move(start_x, start_y, end_x, end_y) or is_valid_bishop_move(start_x, start_y, end_x, end_y)

def is_valid_king_move(start_x, start_y, end_x, end_y):
    if max(abs(start_x - end_x), abs(start_y - end_y)) == 1:
        return True
    return is_castling_valid(board[start_y][start_x], start_x, start_y, end_x, end_y)

# Determine valid moves:
def is_valid_move(piece, start_x, start_y, end_x, end_y):
    # Check if capturing own piece
    if board[end_y][end_x].isupper() if piece.isupper() else board[end_y][end_x].islower():
        return False
    
    # Check specific piece movement rules
    if piece.upper() == "P":
        if not is_valid_pawn_move(piece, start_x, start_y, end_x, end_y):
            return False
    elif piece.upper() == "R":
        if not is_valid_rook_move(start_x, start_y, end_x, end_y):
            return False
    elif piece.upper() == "N":
        if not is_valid_knight_move(start_x, start_y, end_x, end_y):
            return False
    elif piece.upper() == "B":
        if not is_valid_bishop_move(start_x, start_y, end_x, end_y):
            return False
    elif piece.upper() == "Q":
        if not is_valid_queen_move(start_x, start_y, end_x, end_y):
            return False
    elif piece.upper() == "K":
        if not is_valid_king_move(start_x, start_y, end_x, end_y):
            return False
    else:
        return False

    # Simulate the move
    original_piece = board[end_y][end_x]
    board[start_y][start_x] = "."
    board[end_y][end_x] = piece

    # Check if the king is in check
    turn = "white" if piece.isupper() else "black"
    in_check = is_king_in_check(turn)

    # Revert the move
    board[start_y][start_x] = piece
    board[end_y][end_x] = original_piece

    return not in_check

# ---

def is_king_in_check(turn):
    king = "K" if turn == "white" else "k"
    king_pos = [(x, y) for y, row in enumerate(board) for x, piece in enumerate(row) if piece == king]
    if not king_pos:
        return False  # King not found (edge case).
    king_x, king_y = king_pos[0]
    opponent_pieces = [
        (x, y) for y, row in enumerate(board)
        for x, piece in enumerate(row)
        if (piece.islower() if turn == "white" else piece.isupper())
    ]
    return any(
        is_valid_move(board[py][px], px, py, king_x, king_y)
        for px, py in opponent_pieces
    )

def has_valid_moves(turn):
    for y, row in enumerate(board):
        for x, piece in enumerate(row):
            if piece.isupper() if turn == "white" else piece.islower():
                for ey in range(8):
                    for ex in range(8):
                        if is_valid_move(piece, x, y, ex, ey):
                            return True
    return False

def check_game_state(turn):
    for state, count in board_states.items():
        if count >= 3:
            return "threefold_repetition"
    if halfmove_clock >= 100:
        return "fifty_move_rule"
    if is_king_in_check(turn):
        if not has_valid_moves(turn):
            return "checkmate"
        return "check"
    elif not has_valid_moves(turn):
        return "stalemate"
    return "ongoing"

# ---

def promote_pawn(end_x, end_y):
    piece = board[end_y][end_x]
    if (piece == "P" and end_y == 0) or (piece == "p" and end_y == 7):
        while True:
            promotion = input("Promote pawn to (Q/R/B/N): ").upper()
            if promotion in ["Q", "R", "B", "N"]:
                board[end_y][end_x] = promotion if piece == "P" else promotion.lower()
                break
            else:
                print("Invalid choice. Choose Q, R, B, or N.")

# ---

def is_castling_valid(piece, start_x, start_y, end_x, end_y):
    # Castling only applies to kings and specific movement
    if piece not in ["K", "k"] or abs(end_x - start_x) != 2 or start_y != end_y:
        return False

    # Determine castling side and rights
    is_white = piece == "K"
    if is_white:
        if end_x > start_x:  # King-side castling
            if not castling_rights["white_ks"]:
                return False
        else:  # Queen-side castling
            if not castling_rights["white_qs"]:
                return False
    else:
        if end_x > start_x:  # King-side castling
            if not castling_rights["black_ks"]:
                return False
        else:  # Queen-side castling
            if not castling_rights["black_qs"]:
                return False

    # Check if the path is clear
    rook_x = 7 if end_x > start_x else 0
    if not is_path_clear(start_x, start_y, rook_x, start_y):
        return False

    # Ensure king does not pass through or end on a square under attack
    direction = 1 if end_x > start_x else -1
    for step in range(start_x, end_x + direction, direction):
        simulated_x = step
        simulated_y = start_y
        # Temporarily move the king to the square
        board[start_y][start_x] = "."
        board[simulated_y][simulated_x] = piece
        if is_king_in_check("white" if is_white else "black"):
            # Restore the board state
            board[start_y][start_x] = piece
            board[simulated_y][simulated_x] = "."
            return False
        # Restore the king's position
        board[start_y][start_x] = piece
        board[simulated_y][simulated_x] = "."

    return True

# ---

def is_en_passant_valid(piece, start_x, start_y, end_x, end_y):
    global last_move
    if piece.upper() != "P":
        return False
    if abs(start_x - end_x) == 1 and end_y - start_y == (-1 if piece == "P" else 1):
        if last_move and last_move == (end_x, start_y):
            return True
    return False

# ---

# Render board:
def render_board():
    col_labels = "    a   b   c   d   e   f   g   h"
    print("  " + "+ - " * 8 + "+")
    for i, row in enumerate(board):
        row_label = 8 - i
        visual_row = "| " + " | ".join(piece_symbols[piece] for piece in row) + " |"
        print(f"{row_label} {visual_row}")
        print("  " + "+ - " * 8 + "+")
    print(f"{col_labels}\n")

# Move piece function:
def move_piece(start, end, turn):
    global last_move, halfmove_clock
    
    # Check if both start and end positions are exactly 2 characters long
    if len(start) != 2 or len(end) != 2:
        print("Invalid input-- either your move is out of bounds or incomplete. Please enter a valid move.\n")
        return False

    start_x, start_y = ord(start[0]) - 97, 8 - int(start[1])
    end_x, end_y = ord(end[0]) - 97, 8 - int(end[1])

    # Validate if indices are within bounds
    if (
        not ('a' <= start[0].lower() <= 'h' and '1' <= start[1] <= '8') or
        not ('a' <= end[0].lower() <= 'h' and '1' <= end[1] <= '8') or
        not (0 <= start_x < 8 and 0 <= start_y < 8 and 0 <= end_x < 8 and 0 <= end_y < 8)
    ):
        print("Move out of bounds. Please enter a valid move.\n")
        return False

    piece = board[start_y][start_x]

    if not piece or (piece.isupper() and turn == "black") or (piece.islower() and turn == "white"):
        print("It's not your turn!\n")
        return False

    # Handle castling
    if piece.upper() == "K" and abs(start_x - end_x) == 2:
        if is_castling_valid(piece, start_x, start_y, end_x, end_y):
            rook_x = 0 if end_x < start_x else 7
            new_rook_x = 3 if end_x < start_x else 5
            # Move the rook
            board[start_y][new_rook_x] = board[start_y][rook_x]
            board[start_y][rook_x] = "."
            # Move the king
            board[end_y][end_x] = piece
            board[start_y][start_x] = "."
            # Update castling rights
            if piece == "K":
                castling_rights["white_ks"] = False
                castling_rights["white_qs"] = False
            else:
                castling_rights["black_ks"] = False
                castling_rights["black_qs"] = False
            halfmove_clock += 1  # No capture or pawn move in castling-- increment variable accordingly
            return True

    # Validate the move or en passant
    if is_valid_move(piece, start_x, start_y, end_x, end_y) or is_en_passant_valid(piece, start_x, start_y, end_x, end_y):
        # Handle en passant
        if is_en_passant_valid(piece, start_x, start_y, end_x, end_y):
            board[start_y][end_x] = "."  # Remove the captured pawn
            halfmove_clock = 0  # Reset variable due to capture

        # Update the last move for potential en passant tracking
        last_move = (end_x, end_y) if piece.upper() == "P" and abs(start_y - end_y) == 2 else None

        # Check for captures for 50-move rule update:
        if board[end_y][end_x] != ".":
            halfmove_clock = 0 # Reset due to capture
        # Check for pawn moves
        elif piece.upper() == "P":
            halfmove_clock = 0 # Reset due to pawn move
        else:
            halfmove_clock += 1 # Increment otherwise

        # Move the piece
        board[end_y][end_x] = piece
        board[start_y][start_x] = "."

        # Update castling rights if necessary
        if piece.upper() == "K":
            if piece == "K":
                castling_rights["white_ks"] = False
                castling_rights["white_qs"] = False
            else:
                castling_rights["black_ks"] = False
                castling_rights["black_qs"] = False
        elif piece.upper() == "R":
            if start_x == 0:  # Left rook
                if start_y == 7:
                    castling_rights["white_qs"] = False
                elif start_y == 0:
                    castling_rights["black_qs"] = False
            elif start_x == 7:  # Right rook
                if start_y == 7:
                    castling_rights["white_ks"] = False
                elif start_y == 0:
                    castling_rights["black_ks"] = False

        # Handle pawn promotion
        if piece.upper() == "P" and (end_y == 0 or end_y == 7):
            promote_pawn(end_x, end_y)

        return True

    print("Invalid move!\n")
    return False

# ---

# Main game loop:
def main():
    print("\nWelcome to the console chess demo!\n")
    turn = "white"
    move_number = 1 # Initialize move number
    update_board_state() # Record the initial board state
    render_board()
    
    while True:
        # Print the move number if it's White's turn
        if turn == "white":
            print(f"Move {move_number}:")
        
        game_state = check_game_state(turn) # Check the game state at the start of the turn
        if game_state == "check":
            print("Check!")
        elif game_state == "checkmate":
            print(f"Checkmate! {'Black' if turn == 'white' else 'White'} wins!")
            break
        elif game_state == "stalemate":
            print("Stalemate! The game is a draw!")
            break
        elif game_state == "threefold_repetition":
            print("Threefold repetition! The game is a draw!")
            break
        elif game_state == "fifty_move_rule":
            print("50-move rule! The game is a draw!")
            break
        
        print(f"{turn.capitalize()}'s turn.")
        
        user_input = input("Enter your move (e.g., 'e2 e4') or 'quit' to exit: ").strip()
        if user_input.lower() == "quit":
            print("Thanks for playing!\n")
            break
        
        try:
            start, end = user_input.split()
            if move_piece(start, end, turn):
                update_board_state()  # Record the board state after the move
                print("\nAfter move:")
                render_board()
                # Update move number after Black's turn
                if turn == "black":
                    move_number += 1
                # Switch turn
                turn = "black" if turn == "white" else "white"
        except ValueError:
            print("Invalid input. Please enter moves in the format 'e2 e4'.\n")

# Run the game:
main()