# board.py

from piece import Rook, Knight, Bishop, Queen, King, Pawn  # Import all the piece classes

DEBUG = True # Flag for debug output control

piece_symbols = {
    "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚", "p": "♟",
    "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔", "P": "♙",
    ".": " "
}

# ---

class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]  # 8x8 board initialized to None
        self.setup_pieces()

    def setup_pieces(self):
        """
        Initialize the board with all the pieces in their starting positions.
        """
        # White pieces
        for col in range(8):
            self.board[6][col] = Pawn('white')
            self.board[6][col].position = (6, col)  # Set position for pawns

        self.board[7][0] = Rook('white')
        self.board[7][0].position = (7, 0)
        self.board[7][1] = Knight('white')
        self.board[7][1].position = (7, 1)
        self.board[7][2] = Bishop('white')
        self.board[7][2].position = (7, 2)
        self.board[7][3] = Queen('white')
        self.board[7][3].position = (7, 3)
        self.board[7][4] = King('white')
        self.board[7][4].position = (7, 4)
        self.board[7][5] = Bishop('white')
        self.board[7][5].position = (7, 5)
        self.board[7][6] = Knight('white')
        self.board[7][6].position = (7, 6)
        self.board[7][7] = Rook('white')
        self.board[7][7].position = (7, 7)

        # Black pieces
        for col in range(8):
            self.board[1][col] = Pawn('black')
            self.board[1][col].position = (1, col)  # Set position for pawns

        self.board[0][0] = Rook('black')
        self.board[0][0].position = (0, 0)
        self.board[0][1] = Knight('black')
        self.board[0][1].position = (0, 1)
        self.board[0][2] = Bishop('black')
        self.board[0][2].position = (0, 2)
        self.board[0][3] = Queen('black')
        self.board[0][3].position = (0, 3)
        self.board[0][4] = King('black')
        self.board[0][4].position = (0, 4)
        self.board[0][5] = Bishop('black')
        self.board[0][5].position = (0, 5)
        self.board[0][6] = Knight('black')
        self.board[0][6].position = (0, 6)
        self.board[0][7] = Rook('black')
        self.board[0][7].position = (0, 7)

    def render_board(self):
        """
        Print the chess board with visual formatting and piece symbols.
        """
        col_labels = "    a   b   c   d   e   f   g   h"
        print("  " + "+ - " * 8 + "+")
    
        piece_to_symbol = {
            "Pawn": "P", "Rook": "R", "Knight": "N", "Bishop": "B", "Queen": "Q", "King": "K"
        }

        for i, row in enumerate(self.board):
            row_label = 8 - i
            visual_row = "| " + " | ".join(
                piece_symbols.get(
                    piece_to_symbol.get(piece.__class__.__name__, ".").lower() 
                    if piece and piece.color == 'black' else 
                    piece_to_symbol.get(piece.__class__.__name__, ".").upper()
                    if piece else ".", " "
                )
                for piece in row
            ) + " |"
            print(f"{row_label} {visual_row}")
            print("  " + "+ - " * 8 + "+")
    
        print(f"{col_labels}\n")

    def is_valid_position(self, position):
        row, col = position
        valid = 0 <= row < 8 and 0 <= col < 8
        
        if DEBUG: print(f"[DEBUG] board.py - is_valid_position: Checking position {position}: {'Valid' if valid else 'Invalid'}")

        return valid

    def is_empty(self, row, col):
        """
        Check if a given position is empty.
        """
        if not self.is_valid_position((row, col)):
            return False  # Treat out-of-bounds as not empty
        return self.board[row][col] is None


    def is_occupied(self, row, col):
        """
        Check if a given position is occupied (by either white or black).
        """
        return self.board[row][col] is not None

    def is_enemy_piece(self, position, color):
        """
        Check if the piece at the given position is an enemy piece.
        """
        if not self.is_valid_position(position):
            return False  # Out-of-bounds positions are not enemy pieces
        row, col = position
        piece = self.board[row][col]
        return piece is not None and piece.color != color


    def move_piece(self, from_pos, to_pos):
        """
        Move a piece from one position to another, if the move is valid.
        """
        if not self.is_valid_position(from_pos) or not self.is_valid_position(to_pos):
            print(f"Invalid move: Out-of-bounds position {from_pos} or {to_pos}")
            return False

        from_row, from_col = from_pos
        to_row, to_col = to_pos

        # Check if there is a piece at the source position
        piece = self.board[from_row][from_col]
        if piece is None:
            print(f"No piece at position {from_pos}")
            return False

        # Get the valid moves for the piece
        valid_moves = piece.valid_moves(self)
        
        if DEBUG: print(f"[DEBUG] board.py - move_piece: Valid moves for {piece.__class__.__name__} at {from_pos}: {valid_moves}")

        if to_pos not in valid_moves:
            print(f"Invalid move from {from_pos} to {to_pos}")
            return False

        # Move the piece
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        piece.move(to_pos)

        return True


