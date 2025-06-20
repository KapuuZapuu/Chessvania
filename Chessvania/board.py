# board.py

from piece import Rook, Knight, Bishop, Queen, King, Pawn  # Import all the piece classes
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

console = Console()
DEBUG = True # Flag for debug output control (change here to enable/disable debug messages)

piece_symbols = {
    "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚", "p": "♟", # Lowercase: black pieces
    "R": "♜", "N": "♞", "B": "♝", "Q": "♛", "K": "♚", "P": "♟", # Uppercase: white pieces
    ".": " "
}

piece_symbol_keys = {
    "Pawn": "p",
    "Knight": "n",
    "Bishop": "b",
    "Rook": "r",
    "Queen": "q",
    "King": "k"
}

# ---

class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]  # 8x8 board initialized to None
        self.current_turn = "white" # White starts
        self.move_count = 0  # Track total moves
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
        Print the chess board with visual formatting and color-coded piece symbols using Rich.
        """
        col_labels = "    a   b   c   d   e   f   g   h"
        console.print("  " + "+ - " * 8 + "+", style="white")

        for i, row in enumerate(self.board):
            row_label = 8 - i
            visual_row = []
    
            for piece in row:
                if piece is None:
                    visual_row.append(" ")
                else:
                    # Determine the piece symbol (using uppercase for white, lowercase for black)
                    key = piece_symbol_keys.get(piece.__class__.__name__, "?")
                    piece_symbol = piece_symbols.get(key, "?")
                    if piece.color == "white":
                        piece_symbol = piece_symbol.upper()
                    else:
                        piece_symbol = piece_symbol.lower()

                    # Get the color either from the upgrade or default to white/black
                    if hasattr(piece, "upgrade_color") and piece.upgrade_color:
                        piece_color = piece.upgrade_color
                    else:
                        piece_color = "white" if piece.color == "white" else "black"
                    visual_row.append(f"[{piece_color}]{piece_symbol}[/]")
    
            console.print(f"{row_label} | " + " | ".join(visual_row) + " |", style="white")
            console.print("  " + "+ - " * 8 + "+", style="white")
    
        console.print(f"[bold white]{col_labels}[/]")

        # Build the abilities/cooldowns info
        cooldowns_lines = []
        for row in self.board:
            for piece in row:
                if piece is not None and hasattr(piece, "get_cooldown_status"):
                    statuses = piece.get_cooldown_status(self)
                    if statuses:  # Only show if there are any statuses to report
                        pos_notation = self.pos_to_notation(piece.position)
                        cooldowns_lines.append(f"{piece.__class__.__name__} at {pos_notation}: " + ", ".join(statuses))

        # Create a panel with a title for abilities/cooldowns
        if cooldowns_lines:
            panel_text = "\n".join(cooldowns_lines)
        else:
            panel_text = "No active abilities/cooldowns."

        console.print(Panel(panel_text, title="Abilities/Cooldowns", style="cyan"))

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
    
    def is_friendly_piece(self, position, color):
        """
        Check if the given position contains a friendly piece.
        """
        row, col = position
        if not self.is_valid_position((row, col)):
            return False
        piece = self.board[row][col]
        return piece is not None and piece.color == color

    def is_enemy_piece(self, position, color):
        """
        Check if the piece at the given position is an enemy piece.
        """
        if not self.is_valid_position(position):
            return False  # Out-of-bounds positions are not enemy pieces
        row, col = position
        piece = self.board[row][col]
        return piece is not None and piece.color != color

    def switch_turn(self):
        """
        Switch the turn between 'white' and 'black'.
        """
        self.current_turn = "black" if self.current_turn == "white" else "white"

    def pos_to_notation(self, position):
        """
        Convert a (row, col) tuple to chess notation.
        Example: (6, 4) -> "e2"
        """
        row, col = position
        if not self.is_valid_position(position):
            return "??"  # Return invalid notation if position is out of bounds

        notation_col = chr(ord('a') + col)  # Convert column index to letter
        notation_row = str(8 - row)  # Convert row index to chess notation

        return notation_col + notation_row

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
        
        # Check if the selected piece is the correct color
        if piece.color != self.current_turn:
            print(f"Invalid move: It's {self.current_turn}'s turn!")
            return False
        
        # Handle same-tile manual ability activation (e.g., invulnerability)
        if from_pos == to_pos:
            if hasattr(piece, 'upgraded_abilities'):
                if "super_rare_invulnerability" in piece.upgraded_abilities:
                    if DEBUG: print(f"[DEBUG] board.py - Activating manual ability for {piece.__class__.__name__} at {from_pos}")
                    piece.upgraded_abilities["super_rare_invulnerability"](self, {}, simulate=False)

                    if self.current_turn == "black":
                        self.move_count += 1
                    self.switch_turn()
                    return True
            print("Invalid move: Can't activate ability this way.")
            return False

        # Get the valid moves for the piece
        valid_moves = piece.valid_moves(self)
        if not valid_moves:
            if DEBUG: print(f"[ERROR] No valid moves returned by {piece.__class__.__name__} at {from_pos}")
            return False
        
        if DEBUG: print(f"[DEBUG] board.py - move_piece: Valid moves for {piece.__class__.__name__} at {from_pos}: {valid_moves}")

        if to_pos not in valid_moves:
            print(f"Invalid move from {from_pos} to {to_pos}")
            return False
        
        # If trying to activate ability manually by "moving" to same square
        if from_pos == to_pos and hasattr(piece, 'manual_abilities'):
            print(f"[DEBUG] board.py - Activating manual ability for {piece.__class__.__name__} at {from_pos}")
            for name in piece.manual_abilities:
                ability_fn = piece.upgraded_abilities.get(name)
                if callable(ability_fn):
                    moves = ability_fn(self, {}, simulate=False)
                    if not moves:  # Ability failed (e.g., on cooldown)
                        print(f"{piece.__class__.__name__} cannot activate {name.replace('_', ' ')} right now.")
                        return False
            return True  # Ability activated successfully, but piece stays in place

        # Move the piece
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        piece.move(to_pos)

        if hasattr(piece, 'generated_ability_moves'):
            used_ability = piece.generated_ability_moves.get((to_row, to_col))
            if used_ability:
                ability_fn = piece.upgraded_abilities.get(used_ability)
                if callable(ability_fn):
                    ability_fn(self, {}, simulate=False)

        # Switch turns after move
        if self.current_turn == "black":
            self.move_count += 1  # Full turn completed (white + black)
        self.switch_turn()

        return True
