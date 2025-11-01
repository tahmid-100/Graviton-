# minimax_ai.py
# Minimax AI with Alpha-Beta Pruning

from fuzzy_logic import FuzzyLogic
from models import Planet
from constants import BOARD_SIZE


class MinimaxAI:
    """
    Minimax AI with Alpha-Beta Pruning
    
    Algorithm:
    1. Generate possible moves
    2. Simulate each move
    3. Recursively evaluate opponent's best response
    4. Choose move that maximizes AI's minimum guaranteed score
    
    Alpha-Beta Pruning:
    - Alpha: Best score AI can guarantee (maximize)
    - Beta: Best score player can guarantee (minimize)
    - Prune branches where beta ≤ alpha
    """
    
    def __init__(self, board, difficulty='medium', owner='ai'):
        self.board = board
        self.difficulty = difficulty
        self.fuzzy = FuzzyLogic(board)
        # Owner this AI controls: 'ai' (red) or 'player' (blue)
        self.owner = owner
        
        # Set search depth based on difficulty
        if difficulty == 'easy':
            self.max_depth = 1  # Only look 1 move ahead
        elif difficulty == 'medium':
            self.max_depth = 2  # Look 2 moves ahead
        else:  # hard
            self.max_depth = 3  # Look 3 moves ahead
    
    def evaluate_board(self, board):
        """
        Evaluate board state from AI's perspective
        Higher score = better for AI
        
        Evaluation factors:
        - Planet count (100 points each)
        - Total ships (10 points each)
        - Production capacity (50 points per size)
        - Center control (30 points)
        - Neutral planets available (5 points each)
        """
        # Evaluate from this AI instance's owner perspective
        owner = self.owner
        opponent = 'player' if owner == 'ai' else 'ai'

        owner_planets = board.get_player_planets(owner)
        opponent_planets = board.get_player_planets(opponent)

        # Check terminal states
        if len(owner_planets) == 0:
            return -10000  # owner lost
        if len(opponent_planets) == 0:
            return 10000  # owner won
        if len(owner_planets) >= 12:
            return 10000  # owner won by domination
        if len(opponent_planets) >= 12:
            return -10000  # opponent won by domination

        score = 0

        # Planet count advantage
        score += (len(owner_planets) - len(opponent_planets)) * 100

        # Total ships advantage
        owner_total_ships = sum(p.ships for p in owner_planets)
        opponent_total_ships = sum(p.ships for p in opponent_planets)
        score += (owner_total_ships - opponent_total_ships) * 10

        # Planet size/production advantage
        owner_production = sum(p.size for p in owner_planets)
        opponent_production = sum(p.size for p in opponent_planets)
        score += (owner_production - opponent_production) * 50

        # Control of center (strategic positions)
        center_positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        owner_center = sum(1 for p in owner_planets if p.get_position() in center_positions)
        opponent_center = sum(1 for p in opponent_planets if p.get_position() in center_positions)
        score += (owner_center - opponent_center) * 30

        # Neutral planets available (opportunity)
        neutral_count = len([p for p in board.planets if p.owner is None])
        score += neutral_count * 5

        return score
    
    def get_possible_moves(self, board, player):
        """
        Generate all possible moves for a player using fuzzy logic
        
        Process:
        1. For each owned planet with ships
        2. Find closest targets using A*
        3. Evaluate each target with fuzzy logic
        4. Get recommended ship count
        5. Sort by aggressiveness
        """
        moves = []
        owned_planets = board.get_player_planets(player)
        
        for source in owned_planets:
            if source.ships <= 1:
                continue
            
            # Find potential targets using A*
            all_targets = [p for p in board.planets if p != source]
            closest_targets = board.pathfinder.find_closest_planets(source, all_targets, 8)
            
            for target, distance in closest_targets:
                # Use fuzzy logic to evaluate attack
                aggressiveness = self.fuzzy.evaluate_attack(source, target, player)
                
                # Get recommended ship count
                recommended_ships = self.fuzzy.get_ship_count_recommendation(
                    source, target, player, aggressiveness
                )
                
                if recommended_ships > 0:
                    moves.append((source, target, recommended_ships, aggressiveness))
        
        # Sort moves by aggressiveness (higher = more priority)
        moves.sort(key=lambda x: x[3], reverse=True)
        
        return moves
    
    def simulate_move(self, board, source, target, ships):
        """
        Create a new board state after simulating a move
        
        Returns: new board with move applied
        """
        # Deep copy the board
        new_board = self.copy_board(board)
        
        # Find corresponding planets in new board
        new_source = new_board.grid[source.y][source.x]
        new_target = new_board.grid[target.y][target.x]
        
        # Simulate the attack
        new_source.remove_ships(ships)
        
        if new_target.owner == new_source.owner:
            # Reinforcement
            new_target.add_ships(ships)
        else:
            # Attack
            if ships > new_target.ships:
                remaining = ships - new_target.ships
                new_target.owner = new_source.owner
                new_target.ships = remaining
            else:
                new_target.remove_ships(ships)
        
        return new_board
    
    def copy_board(self, board):
        """Create a deep copy of the board for simulation"""
        from game_board import GameBoard
        
        new_board = GameBoard.__new__(GameBoard)
        new_board.grid = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        new_board.planets = []
        new_board.turn = board.turn
        new_board.current_player = board.current_player
        new_board.selected_planet = None
        new_board.game_over = False
        new_board.winner = None
        
        # Copy planets
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                old_planet = board.grid[y][x]
                new_planet = Planet(x, y, old_planet.size, old_planet.owner)
                new_planet.ships = old_planet.ships
                new_planet.max_ships = old_planet.max_ships
                new_board.grid[y][x] = new_planet
                new_board.planets.append(new_planet)
        
        from pathfinding import AStarPathfinder
        new_board.pathfinder = AStarPathfinder(new_board)
        return new_board
    
    def minimax(self, board, depth, alpha, beta, is_maximizing):
        """
        Minimax algorithm with alpha-beta pruning
        
        Parameters:
        - depth: Remaining search depth
        - alpha: Best score AI can guarantee (maximize)
        - beta: Best score player can guarantee (minimize)
        - is_maximizing: True = AI's turn, False = Player's turn
        
        Returns: (evaluation_score, best_move)
        
        Process:
        1. Base case: depth=0 or game over → evaluate board
        2. Get all possible moves
        3. For each move:
           - Simulate move
           - Recursively evaluate (depth-1, swap maximizing)
           - Update alpha/beta
           - Prune if beta ≤ alpha
        4. Return best score and move
        """
        # Terminal state or max depth reached
        if depth == 0 or board.game_over:
            return self.evaluate_board(board), None

        # Determine which side is the maximizing side for this AI instance
        current_player = self.owner if is_maximizing else ('player' if self.owner == 'ai' else 'ai')
        possible_moves = self.get_possible_moves(board, current_player)

        # No moves available
        if not possible_moves:
            return self.evaluate_board(board), None

        best_move = None

        if is_maximizing:
            # Owner's turn - maximize score
            max_eval = float('-inf')

            for move in possible_moves:
                source, target, ships, aggressiveness = move
                new_board = self.simulate_move(board, source, target, ships)

                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, False)

                # Bonus for higher aggressiveness (encourages decisive play)
                eval_score += aggressiveness * 10

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = (source, target, ships)

                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff

            return max_eval, best_move

        else:
            # Opponent's turn - minimize score
            min_eval = float('inf')

            for move in possible_moves:
                source, target, ships, aggressiveness = move
                new_board = self.simulate_move(board, source, target, ships)

                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, True)

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = (source, target, ships)

                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff

            return min_eval, best_move
    
    def get_best_move(self):
        """
        Get the best move for AI using minimax
        
        Returns: (source_planet, target_planet, ship_count)
        """
        score, best_move = self.minimax(
            self.board, 
            self.max_depth, 
            float('-inf'),  # Initial alpha
            float('inf'),   # Initial beta
            True  # AI is maximizing
        )
        return best_move