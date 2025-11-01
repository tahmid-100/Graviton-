# game_board.py
# Game board logic and state management

import random
from models import Planet
from pathfinding import AStarPathfinder
from constants import BOARD_SIZE, MAX_TURNS, WIN_CONDITION_PLANETS


class GameBoard:
    """
    Manages the game state and board logic
    
    Responsibilities:
    - Board initialization
    - Turn management
    - Attack execution
    - Victory conditions
    - Ship generation
    """
    
    def __init__(self, ai_vs_ai=False):
        self.grid = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.planets = []
        self.turn = 0
        self.current_player = 'player'
        self.selected_planet = None
        self.game_over = False
        self.winner = None
        self.ai_vs_ai = ai_vs_ai  # New flag for AI vs AI mode
        
        self.initialize_board()
        self.pathfinder = AStarPathfinder(self)
    
    def initialize_board(self):
        """
        Initialize game board with planets
        
        Setup:
        - 16 planets (4x4 grid) with random sizes (1-3)
        - Player starts top-left (2 planets)
        - AI starts bottom-right (2 planets)
        """
        # Create 16 planets with random sizes
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                size = random.randint(1, 3)
                planet = Planet(x, y, size)
                self.grid[y][x] = planet
                self.planets.append(planet)
        
        # Assign starting planets (opposite corners)
        # Player gets top-left
        self.grid[0][0].owner = 'player'
        self.grid[0][0].ships = 10
        self.grid[0][1].owner = 'player'
        self.grid[0][1].ships = 8
        
        # AI gets bottom-right
        self.grid[3][3].owner = 'ai'
        self.grid[3][3].ships = 10
        self.grid[3][2].owner = 'ai'
        self.grid[3][2].ships = 8
    
    def get_planet_at(self, x, y):
        """Get planet at grid coordinates"""
        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
            return self.grid[y][x]
        return None
    
    def get_player_planets(self, owner):
        """Get all planets owned by a player"""
        return [p for p in self.planets if p.owner == owner]
    
    def generate_all_ships(self):
        """Generate 1 ship per planet per turn"""
        for planet in self.planets:
            planet.generate_ships()
    
    def attack(self, source, target, ship_count):
        """
        Execute an attack from source to target
        
        Attack rules:
        1. Must own source planet
        2. Must have enough ships (leave at least 1)
        3. If target is owned: Battle (attacker - defender)
        4. If target is neutral: Capture with remaining ships
        
        Returns: attack_info dict or False if invalid
        """
        # Validation
        if source.owner != self.current_player:
            return False
        if source.ships <= ship_count:
            return False
        if ship_count < 1:
            return False
        
        # Remove ships from source
        source.remove_ships(ship_count)
        
        # Store attack info for animation
        attack_info = {
            'source': source.get_position(),
            'target': target.get_position(),
            'attacker': source.owner
        }
        
        # Battle at target
        if target.owner == source.owner:
            # Reinforcement
            target.add_ships(ship_count)
        else:
            # Attack
            if ship_count > target.ships:
                # Attacker wins
                remaining = ship_count - target.ships
                target.owner = source.owner
                target.ships = remaining
            else:
                # Defender wins
                target.remove_ships(ship_count)
        
        return attack_info
    
    def end_turn(self):
        """
        End current turn
        
        Process:
        1. Generate ships on all owned planets
        2. Increment turn counter
        3. Switch current player
        4. Clear selection
        5. Check victory conditions
        """
        self.generate_all_ships()
        self.turn += 1
        self.current_player = 'ai' if self.current_player == 'player' else 'player'
        self.selected_planet = None
        self.check_game_over()
    
    def check_game_over(self):
        """
        Check victory conditions
        
        Win conditions:
        1. Opponent has 0 planets
        2. Player has ≥12 planets
        3. Turn limit reached (50 turns per player)
        """
        player_planets = len(self.get_player_planets('player'))
        ai_planets = len(self.get_player_planets('ai'))
        
        if player_planets == 0:
            self.game_over = True
            self.winner = 'ai'
        elif ai_planets == 0:
            self.game_over = True
            self.winner = 'player'
        elif player_planets >= WIN_CONDITION_PLANETS:
            self.game_over = True
            self.winner = 'player'
        elif ai_planets >= WIN_CONDITION_PLANETS:
            self.game_over = True
            self.winner = 'ai'
        elif self.turn >= MAX_TURNS:
            self.game_over = True
            if player_planets > ai_planets:
                self.winner = 'player'
            elif ai_planets > player_planets:
                self.winner = 'ai'
            else:
                self.winner = 'tie'