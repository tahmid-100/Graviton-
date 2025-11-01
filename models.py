# models.py
# Core game models and data structures

class Planet:
    """Represents a planet on the game board"""
    
    def __init__(self, x, y, size, owner=None):
        self.x = x  # Grid position
        self.y = y  # Grid position
        self.size = size  # 1, 2, or 3 (determines production rate)
        self.owner = owner  # None, 'player', or 'ai'
        self.ships = 0
        self.max_ships = size * 3  # Capacity based on size
        
    def get_position(self):
        """Returns (x, y) tuple"""
        return (self.x, self.y)
    
    def add_ships(self, count):
        """Add ships without exceeding capacity"""
        self.ships = min(self.ships + count, self.max_ships)
    
    def remove_ships(self, count):
        """Remove ships, minimum 0"""
        self.ships = max(0, self.ships - count)
        
    def generate_ships(self):
        """Generate 1 ship per turn if owned"""
        if self.owner in ['player', 'ai']:
            self.add_ships(1)
    
    def __repr__(self):
        return f"Planet({self.x},{self.y},size={self.size},owner={self.owner},ships={self.ships})"