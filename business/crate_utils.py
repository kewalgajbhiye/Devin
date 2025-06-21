"""
Crate handling utilities for freight and transport calculations
"""

class CrateUtils:
    def __init__(self):
        self.crate_types = {
            'Jute Bags - 50 KG': {'capacity': 50, 'base_rate': 5.0},
            'Plastic Crates - 20 KG': {'capacity': 20, 'base_rate': 3.0},
            'Gunny Bags - 40 KG': {'capacity': 40, 'base_rate': 4.0},
            'Cardboard Boxes - 10 KG': {'capacity': 10, 'base_rate': 2.0},
            'Mesh Bags - 25 KG': {'capacity': 25, 'base_rate': 3.5}
        }
    
    def get_crate_types(self):
        """Get available crate types"""
        return list(self.crate_types.keys())
    
    def get_crate_capacity(self, crate_type):
        """Get capacity of crate type"""
        return self.crate_types.get(crate_type, {}).get('capacity', 0)
    
    def get_base_rate(self, crate_type):
        """Get base rate for crate type"""
        return self.crate_types.get(crate_type, {}).get('base_rate', 0)
    
    def calculate_crate_bhada(self, total_crates, crate_type, rate_per_crate=None):
        """Calculate crate bhada (freight charges)"""
        if rate_per_crate is None:
            rate_per_crate = self.get_base_rate(crate_type)
        
        return total_crates * rate_per_crate
    
    def calculate_required_crates(self, total_weight, crate_type):
        """Calculate required number of crates for given weight"""
        capacity = self.get_crate_capacity(crate_type)
        if capacity == 0:
            return 0
        
        import math
        return math.ceil(total_weight / capacity)
    
    def calculate_freight_by_distance(self, total_crates, distance_km, rate_per_km=1.5):
        """Calculate freight charges based on distance"""
        return total_crates * distance_km * rate_per_km
    
    def get_crate_rental_charges(self, total_crates, days, rental_rate_per_day=2.0):
        """Calculate crate rental charges"""
        return total_crates * days * rental_rate_per_day
