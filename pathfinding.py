# pathfinding.py
# A* pathfinding algorithm implementation

import heapq
from math import sqrt
from constants import BOARD_SIZE


class AStarPathfinder:
    """A* algorithm for finding optimal paths between planets"""
    
    def __init__(self, board):
        self.board = board
    
    def heuristic(self, pos1, pos2):
        """Manhattan distance heuristic - admissible and consistent"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def euclidean_distance(self, pos1, pos2):
        """Euclidean distance for accurate movement cost"""
        return sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def get_neighbors(self, pos):
        """Get all valid neighbor positions (8-directional movement)"""
        x, y = pos
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                    neighbors.append((nx, ny))
        return neighbors
    
    def find_path(self, start_pos, end_pos):
        """
        A* algorithm to find shortest path between two positions
        
        Returns: (path, cost) where path is list of positions
        
        Algorithm steps:
        1. Initialize open set with start position
        2. While open set not empty:
           - Pop position with lowest f_score
           - If reached goal, return path
           - Explore neighbors
           - Calculate g_score (cost from start)
           - Calculate f_score (g + heuristic)
           - Add to open set if better path found
        """
        if start_pos == end_pos:
            return [start_pos], 0
        
        # Priority queue: (f_score, counter, position, g_score, path)
        counter = 0
        start_g = 0
        start_f = start_g + self.heuristic(start_pos, end_pos)
        open_set = [(start_f, counter, start_pos, start_g, [start_pos])]
        closed_set = set()
        
        while open_set:
            f_score, _, current_pos, g_score, path = heapq.heappop(open_set)
            
            if current_pos in closed_set:
                continue
            
            if current_pos == end_pos:
                return path, g_score
            
            closed_set.add(current_pos)
            
            for neighbor in self.get_neighbors(current_pos):
                if neighbor in closed_set:
                    continue
                
                # Calculate movement cost (euclidean distance)
                move_cost = self.euclidean_distance(current_pos, neighbor)
                new_g = g_score + move_cost
                new_f = new_g + self.heuristic(neighbor, end_pos)
                new_path = path + [neighbor]
                
                counter += 1
                heapq.heappush(open_set, (new_f, counter, neighbor, new_g, new_path))
        
        # No path found (shouldn't happen on full grid)
        return [], float('inf')
    
    def get_distance(self, planet1, planet2):
        """Get A* distance between two planets"""
        path, cost = self.find_path(planet1.get_position(), planet2.get_position())
        return cost
    
    def find_closest_planets(self, source_planet, target_planets, max_count=5):
        """
        Find closest planets to source using A*
        Returns: List of (planet, distance) sorted by distance
        """
        distances = []
        for target in target_planets:
            if target != source_planet:
                dist = self.get_distance(source_planet, target)
                distances.append((target, dist))
        
        distances.sort(key=lambda x: x[1])
        return distances[:max_count]
    
    def get_strategic_distance(self, planet1, planet2, owner):
        """
        Enhanced distance calculation considering strategic factors
        Lower values = more strategic target
        
        Factors:
        - Base distance (from A*)
        - Planet size (bigger = more valuable)
        - Current ownership (enemy weak planets prioritized)
        """
        base_distance = self.get_distance(planet1, planet2)
        target_value = planet2.size
        
        if planet2.owner == owner:
            # Reinforcing own planet - lower priority
            strategic_distance = base_distance * 1.5
        elif planet2.owner is None:
            # Neutral planet - valuable for expansion
            strategic_distance = base_distance / (target_value + 1)
        else:
            # Enemy planet - consider strength
            if planet2.ships < planet1.ships:
                # Weak enemy planet - high priority target
                strategic_distance = base_distance / (target_value + 1)
            else:
                # Strong enemy planet - lower priority
                strategic_distance = base_distance * 1.5
        
        return strategic_distance