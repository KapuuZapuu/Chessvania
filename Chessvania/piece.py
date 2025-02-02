# piece.py

DEBUG = True # Flag for debug output control

class Piece:
    def __init__(self, color):
        """
        Initialize a generic chess piece.
        """
        self.color = color  # 'white' or 'black'
        self.position = None  # Position on the board (e.g., (row, col))
        self.has_moved = False

    def valid_moves(self, board):
        """
        Calculate valid moves for the piece (to be overridden by subclasses).
        """
        raise NotImplementedError("This method should be implemented in the subclass.")

    def move(self, new_position):
        """
        Move the piece to a new position.
        """
        self.position = new_position
        self.has_moved = True

    def __repr__(self):
        return f"{self.__class__.__name__}({self.color}, Position: {self.position})"

# ---

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.upgraded_abilities = []

    def valid_moves(self, board):
        moves = []
        direction = 1 if self.color == 'white' else -1
        row, col = self.position  # Unpack position tuple
        
        # Debug: Print current position and direction
        print(f"[DEBUG] piece.py - (Pawn) valid_moves: Pawn at {self.position} moving {direction} steps (direction)")

        # Standard forward move (1 square ahead)
        if board.is_empty(row + direction, col):
            print(f"[DEBUG] piece.py - (Pawn) valid_moves: Standard move to {(row + direction, col)} is valid")
            moves.append((row + direction, col))
        else:
            print(f"[DEBUG] piece.py - (Pawn) valid_moves: Standard move to {(row + direction, col)} is blocked or invalid")

        # Initial two-square move (only if it hasn't moved yet)
        if not self.has_moved:
            # Check if both the square directly ahead and two squares ahead are empty
            if board.is_empty(row + direction, col) and board.is_empty(row + direction * 2, col):
                print(f"[DEBUG] piece.py - (Pawn) valid_moves: Initial two-square move to {(row + direction * 2, col)} is valid")
                moves.append((row + direction * 2, col))
            else:
                print(f"[DEBUG] piece.py - (Pawn) valid_moves: Initial two-square move to {(row + direction * 2, col)} is blocked or invalid")

        # Capture moves diagonally (check for enemy pieces)
        for diag in [-1, 1]:
            target = (row + direction, col + diag)
            if board.is_enemy_piece(target, self.color):
                print(f"[DEBUG] piece.py - (Pawn) valid_moves: Capture move to {target} is valid")
                moves.append(target)

        # Include any upgrades' moves
        for ability in self.upgraded_abilities:
            generated_moves = ability.generate_moves(self, board)
            print(f"[DEBUG] piece.py - (Pawn) valid_moves: Upgraded ability generated moves: {generated_moves}")
            moves.extend(generated_moves)

        # Debug: Print all valid moves at the end of method
        print(f"[DEBUG] piece.py - (Pawn) valid_moves: Valid moves for pawn at {self.position}: {moves}")
        
        return moves

    def upgrade(self, ability):
        """
        Add a new ability to this pawn.
        """
        self.upgraded_abilities.append(ability)

# ---

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.upgraded_abilities = []

    def valid_moves(self, board):
        moves = []
        directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

        for direction in directions:
            target = (self.position[0] + direction[0], self.position[1] + direction[1])
            if board.is_valid_position(target) and (board.is_empty(target) or board.is_enemy_piece(target, self.color)):
                moves.append(target)

        # Include upgrades' moves
        for ability in self.upgraded_abilities:
            moves.extend(ability.generate_moves(self, board))

        return moves

    def upgrade(self, ability):
        """
        Add a new ability to this knight.
        """
        self.upgraded_abilities.append(ability)

# ---

class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.upgraded_abilities = []

    def valid_moves(self, board):
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Diagonal directions

        for direction in directions:
            for i in range(1, 8):  # Bishop can move up to 7 squares in any diagonal direction
                target = (self.position[0] + direction[0] * i, self.position[1] + direction[1] * i)
                if board.is_valid_position(target) and not board.is_occupied(target):
                    moves.append(target)
                elif board.is_enemy_piece(target, self.color):
                    moves.append(target)
                    break
                else:
                    break

        # Include upgrades' moves
        for ability in self.upgraded_abilities:
            moves.extend(ability.generate_moves(self, board))

        return moves

    def upgrade(self, ability):
        """
        Add a new ability to this bishop.
        """
        self.upgraded_abilities.append(ability)

# ---

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.upgraded_abilities = []

    def valid_moves(self, board):
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Vertical and Horizontal directions

        for direction in directions:
            for i in range(1, 8):  # Rook can move up to 7 squares in any direction
                target = (self.position[0] + direction[0] * i, self.position[1] + direction[1] * i)
                if board.is_valid_position(target) and not board.is_occupied(target):
                    moves.append(target)
                elif board.is_enemy_piece(target, self.color):
                    moves.append(target)
                    break
                else:
                    break

        # Include upgrades' moves
        for ability in self.upgraded_abilities:
            moves.extend(ability.generate_moves(self, board))

        return moves

    def upgrade(self, ability):
        """
        Add a new ability to this rook.
        """
        self.upgraded_abilities.append(ability)

# ---

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.upgraded_abilities = []

    def valid_moves(self, board):
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]  # All 8 directions (diagonal, vertical, horizontal)

        for direction in directions:
            for i in range(1, 8):  # Queen can move up to 7 squares in any direction
                target = (self.position[0] + direction[0] * i, self.position[1] + direction[1] * i)
                if board.is_valid_position(target) and not board.is_occupied(target):
                    moves.append(target)
                elif board.is_enemy_piece(target, self.color):
                    moves.append(target)
                    break
                else:
                    break

        # Include upgrades' moves
        for ability in self.upgraded_abilities:
            moves.extend(ability.generate_moves(self, board))

        return moves

    def upgrade(self, ability):
        """
        Add a new ability to this queen.
        """
        self.upgraded_abilities.append(ability)

# ---

class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.upgraded_abilities = []

    def valid_moves(self, board):
        moves = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]  # 8 possible king directions

        for direction in directions:
            target = (self.position[0] + direction[0], self.position[1] + direction[1])
            if board.is_valid_position(target) and (board.is_empty(target) or board.is_enemy_piece(target, self.color)):
                moves.append(target)

        # Include upgrades' moves
        for ability in self.upgraded_abilities:
            moves.extend(ability.generate_moves(self, board))

        return moves

    def upgrade(self, ability):
        """
        Add a new ability to this king.
        """
        self.upgraded_abilities.append(ability)