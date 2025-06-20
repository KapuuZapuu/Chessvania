# piece.py

from rich.text import Text
from rich import print  # Import Rich print

DEBUG = True # Flag for debug output control (change here to enable/disable debug messages)

class Piece:
    def __init__(self, color):
        """
        Initialize a generic chess piece.
        """
        self.color = color  # 'white' or 'black'
        self.position = None  # Position on the board (e.g., (row, col))
        self.has_moved = False
        self.ability_cooldown = {}  # Track cooldowns per ability

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
        self.upgraded_abilities = {}  # Store ability functions
        self.upgrade_color = None     # For rendering purposes
        self.ability_default_cooldowns = {}  # e.g., {"super_rare_diagonal": 5}
        # ability_cooldown is inherited from Piece

    def valid_moves(self, board):
        moves = []
        direction = -1 if self.color == 'white' else 1
        row, col = self.position  # Unpack position tuple

        # Standard forward move (1 square ahead)
        if board.is_empty(row + direction, col):
            moves.append((row + direction, col))
        # Initial two-square move (only if it hasn't moved yet)
        if not self.has_moved:
            if board.is_empty(row + direction, col) and board.is_empty(row + direction * 2, col):
                moves.append((row + direction * 2, col))
        # Capture moves diagonally
        for diag in [-1, 1]:
            target = (row + direction, col + diag)
            if board.is_enemy_piece(target, self.color):
                moves.append(target)
        # Include any upgrade moves
        self.generated_ability_moves = {}  # Reset before generating moves

        for ability_name, ability_function in self.upgraded_abilities.items():
            if callable(ability_function):
                new_moves = ability_function(board, {}, simulate=True)
                for m in new_moves:
                    self.generated_ability_moves[m] = ability_name
                moves.extend(new_moves)

        return moves

    # RARE: Pawn can start with a 3-jump  
    def rare_three_jump(self, board, state, simulate=False):
        direction = -1 if self.color == "white" else 1
        row, col = self.position
        if not self.has_moved and all(board.is_empty(row + i * direction, col) for i in range(1, 4)):
            return [(row + 3 * direction, col)]
        return []

    # SUPER RARE: Pawn can move diagonally even if no piece (with a cooldown)
    def super_rare_diagonal(self, board, state, simulate=False):
        ability_name = "super_rare_diagonal"
        # Retrieve the last-used move count (or -10 by default)
        last_used = self.ability_cooldown.get(ability_name, -10)
        default_cooldown = self.ability_default_cooldowns.get(ability_name, 5)

        if board.move_count - last_used < default_cooldown:
            return []  # Ability is still on cooldown

        moves = []
        direction = -1 if self.color == "white" else 1
        row, col = self.position
        for diag in [-1, 1]:
            target = (row + direction, col + diag)
            if board.is_valid_position(target):
                moves.append(target)

        # Only register cooldown if this is a real move usage
        if not simulate:
            self.ability_cooldown[ability_name] = board.move_count

        return moves

    # EPIC: Pawn can start with a 4-jump  
    def epic_four_jump(self, board, state, simulate=False):
        direction = -1 if self.color == "white" else 1
        row, col = self.position
        if not self.has_moved and all(board.is_empty(row + i * direction, col) for i in range(1, 5)):
            return [(row + 4 * direction, col)]
        return []

    # MYTHIC: Reduce special move cooldown (affects super_rare_diagonal)
    def mythic_cooldown_reduction(self, board, state, simulate=False):
        # Update the default cooldown for super_rare_diagonal if it exists
        if "super_rare_diagonal" in self.ability_default_cooldowns:
            self.ability_default_cooldowns["super_rare_diagonal"] = 3
        return []

    # LEGENDARY: Pawn can move backwards  
    def legendary_move_backward(self, board, state, simulate=False):
        direction = -1 if self.color == "white" else 1
        row, col = self.position
        if board.is_valid_position((row - direction, col)) and board.is_empty(row - direction, col):
            return [(row - direction, col)]
        return []

    def upgrade(self, ability, board=None):
        """
        Upgrade the Pawn so that it gains new abilities.
        """
        upgrade_order = ["rare", "super_rare", "epic", "mythic", "legendary"]
        upgrade_colors = {
            "rare": "green",
            "super_rare": "blue",
            "epic": "purple",
            "mythic": "red",
            "legendary": "yellow"
        }
    
        if ability not in upgrade_order:
            print(f"[ERROR] Invalid upgrade: {ability}")
            return

        current_index = upgrade_order.index(ability)
    
        for i in range(current_index + 1):
            level = upgrade_order[i]
            if level not in self.upgraded_abilities:
                if level == "rare":
                    self.upgraded_abilities["rare_three_jump"] = lambda board, state, simulate=False: self.rare_three_jump(board, state, simulate)
                elif level == "super_rare":
                    self.ability_default_cooldowns["super_rare_diagonal"] = 5
                    self.upgraded_abilities["super_rare_diagonal"] = lambda board, state, simulate=False: self.super_rare_diagonal(board, state, simulate)
                    if board:
                        self.ability_cooldown["super_rare_diagonal"] = board.move_count
                elif level == "epic":
                    self.upgraded_abilities["epic_four_jump"] = lambda board, state, simulate=False: self.epic_four_jump(board, state, simulate)
                elif level == "mythic":
                    self.upgraded_abilities["mythic_cooldown_reduction"] = lambda board, state, simulate=False: self.mythic_cooldown_reduction(board, state, simulate)
                    if board:
                        self.mythic_cooldown_reduction(board, None)
                elif level == "legendary":
                    self.upgraded_abilities["legendary_move_backward"] = lambda board, state, simulate=False: self.legendary_move_backward(board, state, simulate)
                
                self.upgrade_color = upgrade_colors[level]

        print(f"[bold {upgrade_colors[ability]}]{self.__class__.__name__} upgraded to {ability.upper()} with all prior abilities![/bold {upgrade_colors[ability]}]")

    def get_cooldown_status(self, board):
        """
        Returns a list of strings reporting the cooldown status for each ability.
        For example: ["super_rare_diagonal: ready", "other_ability: 2 moves"]
        """
        statuses = []
        for ability, last_used in self.ability_cooldown.items():
            if ability in self.ability_default_cooldowns:
                default = self.ability_default_cooldowns[ability]
                remaining = default - (board.move_count - last_used)
                if remaining <= 0:
                    status = "ready"
                else:
                    status = f"{remaining} move{'s' if remaining != 1 else ''}"
                statuses.append(f"{ability}: {status}")
        return statuses

# ---

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.upgraded_abilities = {}
        self.upgrade_color = None
        self.ability_default_cooldowns = {}
        self.generated_ability_moves = {}

    def valid_moves(self, board):
        moves = []
        row, col = self.position
        base_offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for dr, dc in base_offsets:
            new_pos = (row + dr, col + dc)
            if board.is_valid_position(new_pos) and not board.is_friendly_piece(new_pos, self.color):
                moves.append(new_pos)

        # Include ability-based moves
        self.generated_ability_moves = {}
        for ability_name, ability_fn in self.upgraded_abilities.items():
            if callable(ability_fn):
                new_moves = ability_fn(board, {}, simulate=True)
                for m in new_moves:
                    self.generated_ability_moves[m] = ability_name
                moves.extend(new_moves)

        return moves

    # --- Abilities ---

    # RARE: One-square diagonal moves
    def rare_diagonal(self, board, state, simulate=False):
        row, col = self.position
        diagonals = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return [
            (row + dr, col + dc)
            for dr, dc in diagonals
            if board.is_valid_position((row + dr, col + dc)) and not board.is_friendly_piece((row + dr, col + dc), self.color)
        ]

    # SUPER RARE: Temporary invulnerability (manual trigger with same square)
    def super_rare_invulnerability(self, board, state, simulate=False):
        ability_name = "super_rare_invulnerability"
        last_used = self.ability_cooldown.get(ability_name, -10)
        default_cooldown = self.ability_default_cooldowns.get(ability_name, 5)

        # Cooldown enforcement
        if not simulate and board.move_count - last_used < default_cooldown:
            if DEBUG: print(f"[DEBUG] Knight - {ability_name} is still on cooldown.")
            print(f"{self.__class__.__name__} cannot activate {ability_name} for {default_cooldown - (board.move_count - last_used)} more move(s).")
            return []

        if not simulate:
            self.invulnerable_turns = 2
            self.ability_cooldown[ability_name] = board.move_count
            if DEBUG: print(f"[DEBUG] Knight - {ability_name} activated! Knight is invulnerable for 2 turns.")

        return []


    # EPIC: Extended knight move (e.g., L+diagonal)
    def epic_diagonal_extension(self, board, state, simulate=False):
        """
        Extends the knight's movement one square further in the same direction as each normal L-shaped move.
        """
        row, col = self.position
        extended_moves = []

        # Vector directions of standard knight moves
        knight_vectors = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for dr, dc in knight_vectors:
            # Extend the vector by 1 unit (so 2→3, 1→2, etc.)
            ext_row = row + dr + (1 if dr > 0 else -1 if dr < 0 else 0)
            ext_col = col + dc + (1 if dc > 0 else -1 if dc < 0 else 0)
            new_pos = (ext_row, ext_col)

            if board.is_valid_position(new_pos) and not board.is_friendly_piece(new_pos, self.color):
                extended_moves.append(new_pos)

        return extended_moves

    # MYTHIC: Reduce invulnerability cooldown
    def mythic_reduce_invuln_cd(self, board, state, simulate=False):
        if "super_rare_invulnerability" in self.ability_default_cooldowns:
            self.ability_default_cooldowns["super_rare_invulnerability"] = 3
        return []

    # LEGENDARY: One-square cardinal movement
    def legendary_cardinal(self, board, state, simulate=False):
        row, col = self.position
        deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return [
            (row + dr, col + dc)
            for dr, dc in deltas
            if board.is_valid_position((row + dr, col + dc)) and not board.is_friendly_piece((row + dr, col + dc), self.color)
        ]

    # --- Upgrade Mechanism ---
    def upgrade(self, ability, board=None):
        upgrade_order = ["rare", "super_rare", "epic", "mythic", "legendary"]
        upgrade_colors = {
            "rare": "green",
            "super_rare": "blue",
            "epic": "purple",
            "mythic": "red",
            "legendary": "yellow"
        }

        if ability not in upgrade_order:
            print(f"[ERROR] Invalid upgrade: {ability}")
            return

        current_index = upgrade_order.index(ability)

        for i in range(current_index + 1):
            level = upgrade_order[i]
            if level not in self.upgraded_abilities:
                if level == "rare":
                    self.upgraded_abilities["rare_diagonal"] = lambda board, state, simulate=False: self.rare_diagonal(board, state, simulate)
                elif level == "super_rare":
                    self.ability_default_cooldowns["super_rare_invulnerability"] = 5
                    self.upgraded_abilities["super_rare_invulnerability"] = lambda board, state, simulate=False: self.super_rare_invulnerability(board, state, simulate)
                    if board:
                        self.ability_cooldown["super_rare_invulnerability"] = board.move_count
                elif level == "epic":
                    self.upgraded_abilities["epic_diagonal_extension"] = lambda board, state, simulate=False: self.epic_diagonal_extension(board, state, simulate)
                elif level == "mythic":
                    self.upgraded_abilities["mythic_reduce_invuln_cd"] = lambda board, state, simulate=False: self.mythic_reduce_invuln_cd(board, state, simulate)
                    if board:
                        self.mythic_reduce_invuln_cd(board, None)
                elif level == "legendary":
                    self.upgraded_abilities["legendary_cardinal"] = lambda board, state, simulate=False: self.legendary_cardinal(board, state, simulate)
                
                self.upgrade_color = upgrade_colors[level]

        print(f"[bold {upgrade_colors[ability]}]{self.__class__.__name__} upgraded to {ability.upper()} with all prior abilities![/bold {upgrade_colors[ability]}]")

    def get_cooldown_status(self, board):
        statuses = []
        for ability, last_used in self.ability_cooldown.items():
            if ability in self.ability_default_cooldowns:
                default = self.ability_default_cooldowns[ability]
                remaining = default - (board.move_count - last_used)
                if remaining <= 0:
                    status = "ready"
                else:
                    status = f"{remaining} move{'s' if remaining != 1 else ''}"
                statuses.append(f"{ability}: {status}")
        return statuses

    def is_invulnerable(self, board):
        return hasattr(self, "invulnerable_until") and board.move_count < self.invulnerable_until

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
                row, col = target  # Unpack the tuple
                if board.is_valid_position(target) and not board.is_occupied(row, col):
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
                row, col = target  # Unpack the tuple
                if board.is_valid_position(target) and not board.is_occupied(row, col):
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
                row, col = target  # Unpack the tuple
                if board.is_valid_position(target) and not board.is_occupied(row, col):
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
            row, col = target  # Unpack the tuple
            if board.is_valid_position(target) and (board.is_empty(row, col) or board.is_enemy_piece((row, col), self.color)):
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
